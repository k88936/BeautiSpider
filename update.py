import time

import crawler
from process import task_pool


def update_list():
    for i in range(1, 50_000):
        url = f"https://www.ku138.cc/b/1/list_1_{i}.html"
        print(f"正在处理第{i}页: {url}")


        time.sleep(1)
        result = crawler.crawl_list_page(url)
        print(result)
        for item in result:
            # if task_pool.has_task(item.id):
            #     print("updated all")
            #     return
            task_pool.push_task(item.id, item)
            print("pushed task:" + item.id)

if __name__ == "__main__":
    update_list()