# Chat Analyzer - 聊天记录高频词&词云生成

一个功能强大的中文聊天记录分析工具，能够自动提取高频词汇、统计纯标点消息，并生成精美的词云可视化图表。

![](https://raw.githubusercontent.com/lsqkk/image/main/20251228171052190.png)

## 在线体验
网址：[Chat Analyzer / 夸克博客](https://lsqkk.github.io/tool/chat-analyzer)

> 说明：此网址使用和本仓库不同的划词器和不同的词云生成工具，且无需配置排除词，统计结果和词云和以下使用`main.py`生成的信息有所不同。

## 功能特性

### 核心分析功能
- **高频词统计**：智能识别聊天记录中的高频词汇
- **纯标点消息统计**：特别统计整行都是句号（。）或问号（？）的消息
- **智能分词**：基于jieba的精准中文分词
- **排除词过滤**：内置丰富的排除词库，支持用户自定义

### 可视化输出
- **词云生成**：根据词频生成美观的可视化词云
- **多格式输出**：同时生成详细分析结果、词汇列表和统计摘要
- **可配置样式**：支持自定义词云颜色、大小、字体等参数

### 高级特性
- **配置文件驱动**：所有参数通过配置文件管理，无需修改代码
- **进度显示**：处理大文件时显示实时进度
- **智能文件命名**：自动添加时间戳防止文件覆盖
- **跨平台支持**：支持Windows、macOS和Linux系统


## 项目结构

```
根目录/
├── main.py                 # 主程序
├── config.ini             # 配置文件（自动生成）
├── chat.txt                # 聊天记录文件
├── stopwords.txt          # 排除词列表（可选）
├── requirements.txt       # 依赖包列表
└── README.md             # 本说明文档
```

## 快速开始

### 1. 环境准备

```bash
# 克隆或下载项目
git clone https://github.com/lsqkk/chat-analyzer.git

# 安装依赖
pip install -r requirements.txt
```

### 2. 准备聊天记录

确保你的聊天记录是UTF-8编码的纯文本文件，例如：
```
[2024-01-01 10:00] 用户A: 你好！
[2024-01-01 10:01] 用户B: 你好，今天天气不错。
[2024-01-01 10:02] 用户A: 是啊，很适合出门。
...
```
或者：
```
你好！
你好，今天天气不错。
是啊，很适合出门。
...
```
任何形式的聊天记录均可，可在后续添加适当的排除词。

导出微信/QQ聊天记录不需要额外工具，选中消息不松手，按住键盘右侧的`pageup`键，约1分钟即可选中千行聊天记录，在`VSCode`中粘贴进`chat.txt`即可。注意，对于千行以上聊天记录，请勿直接使用系统自带（如`notepad++`）类编辑器直接粘贴，会卡很长时间。

### 3. 基础使用

```bash
# 分析聊天记录
python main.py chat.txt
```

其中`chat.txt`为你的聊天记录文件名，可直接粘贴在提供的`chat.txt`中。

## 配置文件详解

根目录下的 `config.ini` 文件，包含以下配置项：

```ini
[settings]
# 最小出现次数阈值
min_frequency = 20

# 是否开启纯标点统计（整行都是句号或问号）
enable_punctuation_stats = true

# 词云设置
wordcloud_max_words = 200      # 词云最大显示词汇数
wordcloud_width = 1200         # 词云图片宽度
wordcloud_height = 800         # 词云图片高度
wordcloud_background_color = white  # 背景颜色
font_path = C:/Windows/Fonts/simhei.ttf  # 字体路径

# 输出设置
show_wordcloud = true          # 是否显示词云图片
save_wordcloud = true          # 是否保存词云图片
```

### 字体路径参考
- **Windows**: `C:/Windows/Fonts/simhei.ttf` (黑体)
- **macOS**: `/System/Library/Fonts/PingFang.ttc` (苹方)
- **Linux**: `/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf`

## 高级用法

### 1. 自定义排除词

编辑 `stopwords.txt` 文件，添加需要排除的词汇：

```txt
# 排除词列表
# 每行一个词，以#开头的行是注释

的
了
在
是
我
你
他

# 添加自定义排除词
自定义词汇1
自定义词汇2
```

项目已提供了一个模板 `stopwords.txt` 文件，可根据实际情况继续添加排除词。

### 2. 调整分析参数

```bash
# 修改 config.ini 中的参数
min_frequency = 10      # 降低阈值，显示更多词汇
enable_punctuation_stats = false  # 关闭纯标点统计
wordcloud_max_words = 100         # 减少词云词汇数
```

### 3. 处理大文件

程序自动显示处理进度：
```
开始分析文件: chat_history.txt
已处理 1000 行...
已处理 2000 行...
文件分析完成，共处理 2567 行
```

## 输出文件说明

运行完成后，会生成以下文件：

### 1. 高频词分析结果_时间序列.txt
```
高频词分析结果 (出现次数 ≥ 20)
==================================================

特殊标点统计 (整行都是该标点):
----------------------------------------
[整行都是句号]:     45
[整行都是问号]:     23

高频词汇:
----------------------------------------
你好              156
谢谢              128
好的               97
问题               85
帮忙               76
...
```

### 2. 高频词汇表_时间序列.txt
```
你好
谢谢
好的
问题
帮忙
...
```

### 3. 分析摘要_时间序列.txt
```
聊天记录高频词分析摘要
==================================================

分析时间: 2024-01-15 14:30:25
最小出现次数阈值: 20
纯标点统计: 开启
发现的高频词数量: 56
使用的排除词数量: 187

特殊标点统计:
------------------------------
整行都是句号: 45次
整行都是问号: 23次

词汇长度分布:
  长度1: 12个
  长度2: 32个
  长度3: 8个
  长度4: 4个
```

### 4. 词云_时间序列.png
![](https://raw.githubusercontent.com/lsqkk/image/main/20251228171052190.png)

## 常见问题解决

### Q1: 字体文件找不到
**症状**: `OSError: cannot open resource`
**解决**: 修改 `config.ini` 中的 `font_path` 为系统存在的字体路径

### Q2: 编码错误
**症状**: `UnicodeDecodeError`
**解决**: 确保聊天记录文件保存为UTF-8编码

### Q3: 依赖安装失败
**症状**: `ModuleNotFoundError`
**解决**:
```bash
# 升级pip
pip install --upgrade pip

# 逐个安装依赖
pip install jieba
pip install wordcloud
pip install matplotlib
pip install pillow
```

### Q4: 词云不显示中文
**症状**: 词云显示方框或乱码
**解决**: 确保 `font_path` 指向正确的中文字体文件

## 扩展开发

### 添加新功能
程序采用模块化设计，易于扩展：

```python
# 示例：添加新的统计维度
class EnhancedChatAnalyzer(ChatFrequencyAnalyzer):
    def analyze_emotions(self, text):
        """情感分析扩展"""
        # 实现情感分析逻辑
        pass
```

### 支持更多文件格式
当前支持纯文本格式，可扩展支持：
- JSON格式聊天记录
- CSV格式导出数据
- 数据库直接查询

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

本项目采用MIT许可证。详见 [LICENSE](LICENSE) 文件。

## 支持与反馈

如有问题或建议，请：
1. 查看 [常见问题](#常见问题解决) 部分
2. 提交 [Issue](https://github.com/your-repo/issues)
3. 通过邮件联系维护者