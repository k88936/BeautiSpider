"""
测试爬虫模块
"""

from crawler import crawl_content_page, crawl_list_page, ContentItem, post_process_content
import json


def test_crawl_list_page():
    example_url = 'https://www.ku138.cc/b/9/list_9_148.html'
    items = crawl_list_page(example_url)
    for item in items:
        print(f"URL: {item.url}, ID: {item.id}")

def test_post_process_content():
    """
    测试后处理功能
    """
    # 创建ContentItem对象进行测试
    content_item = ContentItem(
        src="XIUREN秀人网",
        id="[秀人XIUREN] 2023.05.18 NO.6757 熊小诺",
        download="https://xz.ku138.cc/piccc/2023/zip/230801/484916908851114276.zip"
    )

    # 示例URL
    url = "https://www.ku138.cc/b/9/4849.html"
    
    # 执行后处理
    save_dir = post_process_content(content_item)
    print(f"图片保存目录: {save_dir}")

def test_crawl_content_page():
    """
    测试内容页面爬取功能
    """
    # 测试URL
    url = "https://www.ku138.cc/b/9/48364.html"
    
    # 爬取内容页面
    content_item = crawl_content_page(url)
    
    # 打印结果
    print("Content Item:")
    print(f"src: {content_item.src}")
    print(f"id: {content_item.id}")
    print(f"download: {content_item.download}")
    
    # 转换为字典并打印JSON格式
    result = {
        "src": content_item.src,
        "id": content_item.id,
        "download": content_item.download
    }
    print("\nJSON format:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # test_crawl_list_page()
    # test_crawl_content_page()
    test_post_process_content()