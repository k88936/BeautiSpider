"""
测试数据库模块
"""

from crawler import ContentItem
from db import save_content_item, get_content_item


def test_db_operations():
    """
    测试数据库操作功能
    """

    # 创建测试用的ContentItem对象
    content_item = ContentItem(
        src="XIUREN秀人网",
        id="[秀人XIUREN] 2023.05.18 NO.6757 熊小诺",
        download="https://xz.ku138.cc/piccc/2023/zip/230801/484916908851114276.zip"
    )
    
    url = "https://www.ku138.cc/b/9/4849.html"  # 示例URL
    images_dir = "4f73d1e0c1d7e0d1e3a0f3e32c1291e2"  # 示例图片目录
    
    # 保存ContentItem到数据库
    print("保存ContentItem到数据库...")
    success = save_content_item(content_item)
    
    if success:
        print("ContentItem保存成功!")
    else:
        print("ContentItem保存失败!")
        return
    
    # 从数据库获取ContentItem
    print("从数据库获取ContentItem...")
    retrieved_item = get_content_item(content_item.id)
    
    if retrieved_item:
        print("成功从数据库获取ContentItem:")
        print(f"ID: {retrieved_item.id}")
        print(f"Source: {retrieved_item.src}")
        print(f"Download: {retrieved_item.download}")
        print(f"Images: {retrieved_item.images}")
        print(f"Created At: {retrieved_item.created_at}")
    else:
        print("未能从数据库获取ContentItem")


if __name__ == "__main__":
    test_db_operations()