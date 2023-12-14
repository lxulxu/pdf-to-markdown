通过PyMuPDF和PADDLE OCR提取PDF中文本、图片和表格创建markdown，基于Python 3.10 64-bit。

## 效果
<a href=''><img src='https://raw.githubusercontent.com/lxulxu/MarkdownPic/master/20221124/pdf2md.6lesgfxtb6c0.jpg'></a>

## 安装依赖
1. 安装PaddlePaddle，参考https://www.paddlepaddle.org.cn/documentation/docs/zh/install/pip/windows-pip.html

2. `pip install -r requirements.txt`

## 命令行参数

可通过`python start.py -h`查看

- `-i`:PDF是否为扫描版，默认选项y（扫描版会通过OCR提取文字，非扫描版通过PyMuPDF API提取文字）
- `-f`:单个文件或文件夹，仅支持一级目录

例如`python start.py -i n -f samples`

## 限制
- 仅支持中英文（由于PyMuPDF存在问题偶尔会出现乱码）
- 仅支持单栏布局
- 不支持页眉和页脚
- 不支持各种文本样式（包括颜色、加粗、斜体等）

……（其他待发现问题）
