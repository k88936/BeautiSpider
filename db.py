"""
数据库操作模块 - 用于存储ContentItem数据到PostgreSQL数据库
"""
from enum import Enum

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional
from crawler import ContentItem
from dataclasses import dataclass
import hashlib
import os

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'beautispider',
    'port': 13732
}


@dataclass
class DBItem:
    id: str
    src: str
    download: str
    images: str
    created_at: str


def get_connection():
    """
    获取数据库连接
    """
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """
    初始化数据库表
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 创建content_items表
    create_table_query = """
                         create table if not exists content_items
                         (
                             id         text not null
                                 constraint content_items_id_uindex
                                     primary key,
                             src        text not null,
                             download   text,
                             images     text,
                             created_at timestamp default CURRENT_TIMESTAMP
                         );

                         create index if not exists content_items_src_index
                             on content_items (src); \
                         """

    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()


def save_content_item(content_item: ContentItem):
    """
    保存ContentItem到数据库
    
    Args:
        content_item: ContentItem对象
        url: 内容页面URL
        images_dir: 图片保存目录路径
        
    Returns:
        bool: 保存成功返回True，否则返回False
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 使用content_item.id作为主键
    item_id = content_item.id

    images_dir = hashlib.md5(content_item.id.encode('utf-8')).hexdigest()
    # 插入或更新数据
    insert_query = """
                   INSERT INTO content_items (id, src, download, images)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (id)
                       DO UPDATE SET src      = EXCLUDED.src,
                                     download = EXCLUDED.download,
                                     images   = EXCLUDED.images \
                   """

    cursor.execute(insert_query, (
        item_id,
        content_item.src,
        content_item.download,
        images_dir
    ))
    conn.commit()
    cursor.close()
    conn.close()


def get_content_item(item_id: str) -> DBItem:
    """
    根据ID获取ContentItem
    
    Args:
        item_id: ContentItem的ID
        
    Returns:
        DBItem: ContentItem数据，如果未找到返回None
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    select_query = "SELECT * FROM content_items WHERE id = %s"
    cursor.execute(select_query, (item_id,))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        # 将字典转换为DBItem对象
        return DBItem(
            id=result['id'],
            src=result['src'],
            download=result['download'],
            images=result['images'],
            created_at=str(result['created_at']) if result['created_at'] else ""
        )
    raise Exception("Item not found")


init_db()
