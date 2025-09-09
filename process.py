import crawler
import db
from taskPool import TaskPool
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque

task_pool = TaskPool()

# 限制配置
MAX_CONNECTIONS = 5  # 最大并发连接数
BATCH_SIZE = 40
REQUESTS_PER_MINUTE = 30  # 每分钟最大请求数
MIN_REQUEST_INTERVAL = 60 / REQUESTS_PER_MINUTE  # 请求间隔时间

# 请求时间记录队列
request_times = deque()
request_lock = threading.Lock()

def rate_limited_request():
    """控制请求频率"""
    current_time = time.time()
    
    with request_lock:
        # 清除超过1分钟的请求记录
        while request_times and current_time - request_times[0] > 60:
            request_times.popleft()
        
        # 如果达到每分钟请求上限，等待
        if len(request_times) >= REQUESTS_PER_MINUTE:
            sleep_time = 60 - (current_time - request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # 记录本次请求时间
        request_times.append(current_time)

def process_task(task):
    """处理单个任务"""
    print("processing task:" + task.id)
    rate_limited_request()
    
    try:
        result = crawler.crawl_content_page(task.context['url'])
        crawler.post_process_content(result)
        db.save_content_item(result)
        task_pool.submit_task(task.id)
        return f"Task {task.id} completed"
    except Exception as e:
        task_pool.fail_task(task.id)
        return f"Task {task.id} failed: {str(e)}"

def main():

    # 使用线程池进行并发处理
    with ThreadPoolExecutor(max_workers=MAX_CONNECTIONS) as executor:
        # 提交所有任务
        while True:
            tasks = task_pool.pop_tasks(limit= BATCH_SIZE )
            # 修改: 如果获取到的任务数量为0，则结束循环
            if not tasks:
                break
                
            # 提交当前批次任务
            future_to_task = {}
            for task in tasks:
                future = executor.submit(process_task, task)
                future_to_task[future] = task.id
            
            # 等待当前批次任务完成
            # 处理完成的任务
            for future in as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    result = future.result()
                    print(result)
                except Exception as e:
                    print(f"Task {task_id} generated an exception: {e}")



if __name__ == "__main__":
    main()
