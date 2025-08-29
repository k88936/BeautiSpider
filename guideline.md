# Overall
* all steps should be independent and provided as pure function lib (NO OOP), properly split functions to different files.
* use data-only classes as the data type
* give a test for lib: a url of LIST ->crawl and extract list view-> for each item, crawl and extract content view -> post process meta data -> save metadata to db and save images to disk 
* config should be in a separate file
# Crawl
* the extract MUST NOT use regex, use beautifulsoup to extract exactly
## List View

* a basic request is enough for this page
* example [see](list.example.html)


```html
<a href="https://www.ku138.cc/b/82/35893.html" title="[MICAT套图] 2019.09.12 Vol.086 潘琳" target="_blank">
    <img style="width:224px;height:322px;" src="https://img.ku138.cc/piccc/2019/img/191104/04152226-04047.jpg"
         alt="[MICAT套图] 2019.09.12 Vol.086 潘琳">
    <div class="list-tit list-tit-short"><p>[MICAT套图] 2019.09.12 Vol.086 潘琳</p></div>
    <span class="time">38P</span>
</a>
```
for EVERY item like this, extract to
```json
[
  {
    "url": "https://www.ku138.cc/b/82/35893.html",
    "id": "[MICAT套图] 2019.09.12 Vol.086 潘琳"
  }
]
```

## Content View

* a basic request is enough for this page
* example [see](content.example.html)

```html
<span><i></i>当前位置 ：</span> <a href="https://www.ku138.cc/" title="图片吧">主页</a> &gt; <a
        href="https://www.ku138.cc/b/tag/">标签分类</a> &gt; <a href="https://www.ku138.cc/b/9/" title="XIUREN秀人网">XIUREN秀人网</a> &gt; [秀人XIUREN] 2023.04.28 NO.6661 乔一一
```

```html
<div class="Title111">
    <h1>所属栏目：<a href="https://www.ku138.cc/b/9/" title="XIUREN秀人网打包下载">XIUREN秀人网</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;下载地址：<a
            href="https://xz.ku138.cc/piccc/2023/zip/230711/166416890628766629.zip"
            target="_blank">点击打包下载本套图</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;在线视频：
        <script type="text/javascript">wuduo3()</script>
        <a href="https://www.559duo.cc/a/2/9332.html" target="_blank"><font color="#FF0000"
                                                                            data-darkreader-inline-color=""
                                                                            style="--darkreader-inline-color: var(--darkreader-text-ff0000, #ff1a1a);">点击播放</font></a>
```

extract to

```json
{
  "src": "XIUREN秀人网",
  "id": "[秀人XIUREN] 2023.04.28 NO.6661 乔一一",
  "download": "https://xz.ku138.cc/piccc/2023/zip/230711/166416890628766629.zip"
}
```
# post process
for every item, download the zip of image and extract, save the raw images to disk (using a hash(id) as the dir name)
# Data Storage
### db setting
[see](database/docker-compose.yaml)
### data structure
using JSON to represent
```json
{
  "id": "[秀人XIUREN] 2023.04.28 NO.6661 乔一一",
  "src": "XIUREN秀人网",
  "url": "https://www.ku138.cc/b/9/35893.html",
  "download": "https://xz.ku138.cc/piccc/2023/zip/230711/166416890628766629.zip",
  "images": "the/saved/dir/NAME_NOT_FULL_PATH"
}
```