import json
import typing
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any ,List

import psycopg2
from psycopg2 import pool

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'beautispider',
    'port': 13732
}


@dataclass
class Task:
    id: str
    context: dict
    status: int


class TaskStatus(Enum):
    """
    任务状态枚举
    """
    PENDING = 1
    RUNNING = 2
    COMPLETED = 3
    FAILED = 4


# Custom JSON Encoder for dataclasses
class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if hasattr(obj, "__dataclass_fields__"):  # Check if it's a dataclass
            return asdict(obj)  # Convert to dictionary
        return super().default(obj)  # Fallback to default behavior


class TaskPool:
    def __init__(self, db_config=None):
        self.db_config = db_config or DB_CONFIG
        self.connection_pool = None
        self.init_db()

    def get_connection(self):
        """
        从连接池获取数据库连接
        """
        if self.connection_pool is None:
            self.init_db()
        return self.connection_pool.getconn()

    def return_connection(self, conn):
        """
        将连接返回连接池
        """
        if self.connection_pool:
            self.connection_pool.putconn(conn)

    def init_db(self):
        """
        初始化数据库表和连接池
        """
        # 初始化连接池
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20, **self.db_config)

        conn = self.get_connection()
        cursor = conn.cursor()

        # 创建content_items表
        create_table_query = """
                             create table if not exists task_pool
                             (
                                 id         text not null
                                     constraint task_pool_id_uindex
                                         primary key,
                                 context    text not null,
                                 status     integer,
                                 created_at timestamp default CURRENT_TIMESTAMP,
                                 last_run   timestamp default CURRENT_TIMESTAMP
                             ); \
                             """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        self.return_connection(conn)



    def has_task(self, id:str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM task_pool WHERE id = %s", (id,))
        result= cursor.fetchone() is not None
        cursor.close()
        self.return_connection(conn)
        return result

    def push_task(self, id: str, context: object):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO task_pool (id, context, status) "
                       "VALUES (%s, %s, %s) "
                       "ON CONFLICT DO NOTHING",
                       (id, json.dumps(context, cls=DataclassJSONEncoder), TaskStatus.PENDING.value))
        conn.commit()
        cursor.close()
        self.return_connection(conn)

    def pop_task(self, failed: bool = False) -> Task:
        # 修改: 使用 OR 条件来包含失败任务
        if failed:
            # 如果 failed 为 True，获取 PENDING 或 FAILED 状态的任务
            status_condition = (TaskStatus.PENDING.value, TaskStatus.FAILED.value)
            status_query = "status = %s OR status = %s"
        else:
            # 如果 failed 为 False，只获取 PENDING 状态的任务
            status_condition = (TaskStatus.PENDING.value,)
            status_query = "status = %s"
            
        conn = self.get_connection()
        cursor = conn.cursor()
        # 使用SELECT FOR UPDATE来确保操作的原子性
        # 修改: 使用新的状态查询条件
        cursor.execute(f"""
                       SELECT id,context,status 
                       FROM task_pool 
                       WHERE {status_query}
                       ORDER BY created_at ASC 
                       LIMIT 1 
                       FOR UPDATE
                       """,
                       status_condition)
        result = cursor.fetchone()
        if result is None:
            cursor.close()
            self.return_connection(conn)
            raise Exception("No pending tasks available")
            
        id, context_json, status_number = result
        task = Task(id, json.loads(context_json), status_number)
        
        # 在同一事务中更新任务状态
        cursor.execute("UPDATE task_pool SET status = %s WHERE id = %s", 
                      (TaskStatus.RUNNING.value, task.id))
        conn.commit()
        cursor.close()
        self.return_connection(conn)
        return task

    def pop_tasks(self, limit: int, failed: bool = False) -> List[Task]:
        """
        批量获取任务
        
        Args:
            limit: 获取任务的最大数量
            failed: 是否获取失败的任务
            
        Returns:
            任务列表
        """
        # 修改: 使用 OR 条件来包含失败任务
        if failed:
            # 如果 failed 为 True，获取 PENDING 或 FAILED 状态的任务
            status_condition = (TaskStatus.PENDING.value, TaskStatus.FAILED.value)
            status_query = "status = %s OR status = %s"
        else:
            # 如果 failed 为 False，只获取 PENDING 状态的任务
            status_condition = (TaskStatus.PENDING.value,)
            status_query = "status = %s"
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 使用SELECT FOR UPDATE来确保操作的原子性
        # 修改: 使用新的状态查询条件
        cursor.execute(f"""
                       SELECT id,context,status 
                       FROM task_pool 
                       WHERE {status_query}
                       ORDER BY created_at ASC 
                       LIMIT %s
                       FOR UPDATE
                       """,
                       status_condition + (limit,))
        
        results = cursor.fetchall()
        if not results:
            cursor.close()
            self.return_connection(conn)
            return []
        
        tasks = []
        task_ids = []
        
        # 解析任务数据
        for result in results:
            id, context_json, status_number = result
            task = Task(id, json.loads(context_json), status_number)
            tasks.append(task)
            task_ids.append(task.id)
        
        # 在同一事务中批量更新任务状态
        cursor.execute("UPDATE task_pool SET status = %s WHERE id = ANY(%s)", 
                      (TaskStatus.RUNNING.value, task_ids))
        conn.commit()
        cursor.close()
        self.return_connection(conn)
        return tasks

    def has_pending_task(self) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM task_pool WHERE status = %s LIMIT 1", (TaskStatus.PENDING.value,))
        result = cursor.fetchone()
        cursor.close()
        self.return_connection(conn)
        return result is not None

    def submit_task(self, id: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE task_pool SET status = %s, last_run = CURRENT_TIMESTAMP WHERE id = %s",
                       (TaskStatus.COMPLETED.value, id))
        conn.commit()
        cursor.close()
        self.return_connection(conn)

    def fail_task(self, id: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE task_pool SET status = %s WHERE id = %s",
                       (TaskStatus.FAILED.value, id))
        conn.commit()
        cursor.close()
        self.return_connection(conn)

    def get_task_status(self, id: str) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM task_pool WHERE id = %s", (id,))

        status = cursor.fetchone()[0]
        cursor.close()
        self.return_connection(conn)
        return status

    def auto_fail_tasks(self):
        """
        将7天前未完成的任务标记为失败状态
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        # 更新7天前状态不是COMPLETED的任务为FAILED状态
        cursor.execute("""
                       UPDATE task_pool
                       SET status = %s
                       WHERE status = %s
                         AND last_run < CURRENT_TIMESTAMP - INTERVAL '7 days'
                       """, (TaskStatus.FAILED.value, TaskStatus.RUNNING.value))
        conn.commit()
        cursor.close()
        self.return_connection(conn)