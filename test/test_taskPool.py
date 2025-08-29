
from taskPool import *


def test_task_pool():
    task_pool = TaskPool()
    print("数据库初始化完成")

    print("\n测试 push_task...")
    test_context = {"url": "https://example.com", "depth": 1}
    task_pool.push_task("test_task_1", test_context)
    print("任务添加成功")

    print("\n测试 get_task...")
    task = task_pool.get_task(TaskStatus.PENDING)
    print(f"获取任务成功: {task}")

    print("\n测试 pop_task...")
    task = task_pool.pop_task()
    print(f"弹出任务成功: {task}")
    print(f"任务状态应为RUNNING: {task.status}")

    print("\n测试 submit_task...")
    task_pool.submit_task(task.id)
    status =task_pool. get_task_status(task.id)
    print(f"提交任务后状态: {status}")
    print(f"状态应为COMPLETED: {status == TaskStatus.COMPLETED.value}")

    print("\n测试 fail_task...")
    # 先添加一个新任务
    fail_context = {"url": "https://example2.com", "depth": 2}
    task_pool. push_task("test_task_2", fail_context)
    task = task_pool.pop_task()
    task_pool.fail_task(task.id)
    status = task_pool.get_task_status(task.id)
    print(f"失败任务后状态: {status}")
    print(f"状态应为FAILED: {status == TaskStatus.FAILED.value}")

    print("\n测试 get_task_status...")
    status = task_pool.get_task_status("test_task_1")
    print(f"任务状态: {status}")
    print(f"状态应为COMPLETED: {status == TaskStatus.COMPLETED.value}")

    print("\n测试 auto_fail_tasks...")
    task_pool.auto_fail_tasks()
    print("自动失败任务处理完成")

    print("\n所有测试完成!")


if __name__ == "__main__":
    test_task_pool()
