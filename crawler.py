"""
爬虫模块 - 用于解析列表和内容页面
"""

from bs4 import BeautifulSoup
from typing import List
import requests
from urllib.parse import urljoin
from dataclasses import dataclass
import os
import hashlib
import zipfile
import io

# 添加数据库模块导入
DATA_DIR= "downloads"

@dataclass
class ListItem:
    url: str
    id: str


@dataclass
class ContentItem:
    src: str
    id: str
    download: str


def crawl_list_page(url: str) -> List[ListItem]:
    """
    爬取并解析列表页面，提取项目链接和标题
    
    Args:
        url: 列表页面URL
        
    Returns:
        包含url和id的字典列表
    """
    # 发送HTTP请求获取页面内容
    response = requests.get(url)
    response.encoding = 'gb2312'  # 根据网页指定的编码来设置

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找包含项目列表的容器
    items_container = soup.find('div', class_='m-list')
    if not items_container:
        return []

    # 查找所有<li>元素中的<a>标签
    items = items_container.find_all('a', target='_blank')

    result = []
    for item in items:
        # 提取href属性作为url
        href = item.get('href')
        # 提取title属性作为id
        title = item.get('title')

        if href and title:
            # 处理相对链接，转换为绝对链接
            absolute_url = urljoin(url, href)
            result.append(ListItem(absolute_url, title))

    return result


def crawl_content_page(url: str) -> ContentItem:
    """
    爬取并解析内容页面，提取相关信息
    
    Args:
        url: 内容页面URL
        
    Returns:
        ContentItem对象，包含src、id和download信息
    """
    # 发送HTTP请求获取页面内容
    response = requests.get(url)
    response.encoding = 'gb2312'  # 根据网页指定的编码来设置

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取当前位置信息，获取src
    breadcrumb = soup.find('div', class_='position')
    src = ""
    if breadcrumb:
        links = breadcrumb.find_all('a')
        if len(links) >= 3:
            src = links[2].get_text().strip()

    # 提取页面标题作为id
    id_text = ""
    if breadcrumb:
        # 获取导航路径中的最后一个文本节点，即页面标题
        full_text = breadcrumb.get_text()
        # 分割字符串并获取最后一个部分，然后清理空白字符
        parts = full_text.split('>')
        if len(parts) >= 4:
            id_text = parts[3].strip()

    # 提取下载链接
    download_link = ""
    title_div = soup.find('div', class_='Title111')
    if title_div:
        download_anchor = title_div.find('a', target='_blank', href=True)
        if download_anchor:
            download_link = download_anchor['href']

    return ContentItem(src, id_text, download_link)


def post_process_content(content_item: ContentItem):
    """
    后处理内容项目：下载ZIP文件并在内存中解压，然后保存图片到磁盘
    
    Args:
        content_item: ContentItem对象
    Returns:
        图片保存的目录路径
    """
    # 创建下载目录
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # 使用ID的哈希值作为目录名
    dir_name = hashlib.md5(content_item.id.encode('utf-8')).hexdigest()
    save_dir = os.path.join(DATA_DIR, dir_name)
    
    # 创建保存目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 如果下载链接存在，则下载并解压文件
    if content_item.download:
        print(f"正在下载: {content_item.download}")
        response = requests.get(content_item.download)
        response.raise_for_status()
        
        # 在内存中解压ZIP文件
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            print(f"ZIP文件包含 {len(zip_file.namelist())} 个文件")
            
            # 只提取图片文件
            for file_info in zip_file.infolist():
                # 获取文件名（去除路径信息）
                filename = os.path.basename(file_info.filename)
                
                # 只处理非空文件名且为图片的文件
                if filename and (filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg') or filename.lower().endswith('.png')):
                    # 提取文件到指定目录
                    file_info.filename = filename  # 去除路径信息
                    zip_file.extract(file_info, save_dir)
        
        print(f"图片文件已保存到: {save_dir}")