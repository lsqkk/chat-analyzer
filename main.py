import re
import jieba
import collections
import os
import configparser
from typing import List, Dict, Tuple, Set
import argparse
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime

class ChatFrequencyAnalyzer:
    def __init__(self, config_file: str = "config.ini"):
        """
        初始化高频词分析器
        
        Args:
            config_file: 配置文件路径
        """
        self.config = self.load_config(config_file)
        self.min_frequency = self.config.getint('settings', 'min_frequency')
        self.enable_punctuation_stats = self.config.getboolean('settings', 'enable_punctuation_stats')
        self.stopwords = self.load_stopwords()
        
    def load_config(self, config_file: str) -> configparser.ConfigParser:
        """
        加载配置文件
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            配置对象
        """
        config = configparser.ConfigParser()
        
        # 默认配置
        defaults = {
            'settings': {
                'min_frequency': '20',
                'enable_punctuation_stats': 'true',
                'wordcloud_max_words': '200',
                'wordcloud_width': '1200',
                'wordcloud_height': '800',
                'wordcloud_background_color': 'white',
                'font_path': 'C:/Windows/Fonts/simhei.ttf',
                'show_wordcloud': 'true',
                'save_wordcloud': 'true'
            }
        }
        
        if os.path.exists(config_file):
            try:
                config.read(config_file, encoding='utf-8')
                print(f"已加载配置文件: {config_file}")
            except Exception as e:
                print(f"读取配置文件失败，使用默认配置: {e}")
                config.read_dict(defaults)
        else:
            print(f"配置文件 {config_file} 不存在，使用默认配置")
            config.read_dict(defaults)
            
            # 保存默认配置文件
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    config.write(f)
                print(f"已创建默认配置文件: {config_file}")
            except Exception as e:
                print(f"创建配置文件失败: {e}")
        
        return config
        
    def load_stopwords(self) -> set:
        """
        加载排除词列表
        
        首先尝试读取同级目录下的stopwords.txt文件
        如果文件不存在，则使用内置的常见排除词
        """
        stopwords_file = "stopwords.txt"
        
        # 内置常见排除词（如果文件不存在时使用）
        default_stopwords = {
            # 中文常用单字
            '的', '了', '和', '是', '就', '都', '而', '及', '与', '或',
            '在', '中', '了', '我', '你', '他', '她', '它', '们',
            '这', '那', '哪', '谁', '什么', '怎么', '为什么',
            '啊', '哦', '嗯', '哈', '啦', '呀', '吧', '吗', '呢',
            '不', '没', '有', '是', '也', '都', '又', '再',
            '上', '下', '左', '右', '前', '后', '里', '外',
            '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
            '很', '最', '太', '更', '非常', '特别',
            
            # 英文字母
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            
            # 阿拉伯数字
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            
            # 常见标点和符号
            '.', ',', '。', '，', '!', '！', '?', '？', ':', '：', ';', '；',
            '(', ')', '（', '）', '[', ']', '{', '}', '<', '>',
            '"', "'", '「', '」', '『', '』', '、',
            ' ', '\t', '\n', '\r',
            
            # 其他常见无意义词
            '这个', '那个', '一个', '一些', '一种', '一样',
            '时候', '时间', '开始', '然后', '最后',
            '可以', '可能', '可是', '但是', '虽然', '如果',
            '因为', '所以', '然后', '而且', '那么',
            '这样', '那样', '怎么', '什么', '为什么',
            '有点', '有些', '有点', '有些',
            '自己', '别人', '大家', '有人',
            '知道', '觉得', '认为', '以为',
            '看到', '听见', '听到', '想到',
            '今天', '明天', '昨天', '现在', '以前', '以后',
            '还有', '还有', '还是', '还有',
            '这里', '那里', '哪里', '这边', '那边',
            '的话', '的说', '的是', '了了',
        }
        
        if os.path.exists(stopwords_file):
            try:
                with open(stopwords_file, 'r', encoding='utf-8') as f:
                    words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    user_stopwords = set(words)
                    print(f"从 stopwords.txt 加载了 {len(user_stopwords)} 个排除词")
                    # 合并默认排除词和用户自定义排除词
                    return default_stopwords.union(user_stopwords)
            except Exception as e:
                print(f"读取 stopwords.txt 失败，使用内置排除词: {e}")
        
        print(f"使用内置排除词，共 {len(default_stopwords)} 个词")
        return default_stopwords
    
    def preprocess_text(self, text: str) -> str:
        """
        预处理文本
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        # 移除URL
        text = re.sub(r'https?://\S+', '', text)
        # 移除邮箱
        text = re.sub(r'\S+@\S+', '', text)
        # 移除特殊字符，但保留中文、英文、数字和基本标点
        text = re.sub(r'[^\w\u4e00-\u9fff\s\.\,\!\?，。！？]', '', text)
        # 合并多个空格
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_words(self, text: str) -> List[str]:
        """
        从文本中提取词汇
        
        Args:
            text: 文本内容
            
        Returns:
            词汇列表
        """
        # 使用jieba进行分词
        words = jieba.lcut(text)
        
        # 过滤空字符串和纯空格
        words = [word.strip() for word in words if word.strip()]
        
        return words
    
    def analyze_chat_file(self, file_path: str) -> Tuple[Dict[str, int], Dict[str, int]]:
        """
        分析聊天记录文件
        
        Args:
            file_path: 聊天记录文件路径
            
        Returns:
            (词汇频率字典, 特殊标点统计字典)
        """
        word_freq = collections.Counter()
        total_lines = 0
        
        # 特殊标点统计：一整行都是这些标点
        special_punctuations = {
            '句号': '。',
            '问号': '？'
        }
        special_counts = {name: 0 for name in special_punctuations}
        
        print(f"开始分析文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    # 显示进度
                    if line_num % 1000 == 0:
                        print(f"已处理 {line_num} 行...")
                    
                    # 检查整行是否都是特殊标点
                    stripped_line = line.strip()
                    
                    # 如果开启纯标点统计
                    if self.enable_punctuation_stats:
                        # 检查是否整行都是句号
                        if stripped_line == '。':
                            special_counts['句号'] += 1
                            continue
                        
                        # 检查是否整行都是问号
                        if stripped_line == '？':
                            special_counts['问号'] += 1
                            continue
                        
                        # 检查是否整行都是句号（可能有多个）
                        if all(char == '。' for char in stripped_line) and len(stripped_line) > 0:
                            special_counts['句号'] += 1
                            continue
                        
                        # 检查是否整行都是问号（可能有多个）
                        if all(char == '？' for char in stripped_line) and len(stripped_line) > 0:
                            special_counts['问号'] += 1
                            continue
                    
                    # 预处理文本
                    processed_line = self.preprocess_text(line)
                    if not processed_line:
                        continue
                    
                    # 提取词汇
                    words = self.extract_words(processed_line)
                    
                    # 统计频率
                    for word in words:
                        word_freq[word] += 1
                    
                    total_lines = line_num
                    
            print(f"文件分析完成，共处理 {total_lines} 行")
            return dict(word_freq), special_counts
            
        except FileNotFoundError:
            print(f"错误: 文件 {file_path} 不存在")
            return {}, {}
        except UnicodeDecodeError:
            print("错误: 文件编码不是UTF-8，请确保文件使用UTF-8编码")
            return {}, {}
    
    def filter_and_sort(self, word_freq: Dict[str, int], special_counts: Dict[str, int]) -> List[Tuple[str, int]]:
        """
        过滤和排序结果，包括特殊标点
        
        Args:
            word_freq: 词汇频率字典
            special_counts: 特殊标点统计字典
            
        Returns:
            排序后的词汇频率列表
        """
        # 过滤排除词和低于阈值的词
        filtered_freq = {
            word: freq for word, freq in word_freq.items() 
            if (word not in self.stopwords) and (freq >= self.min_frequency)
        }
        
        # 添加特殊标点到结果中（如果达到阈值且开启统计）
        if self.enable_punctuation_stats:
            for name, count in special_counts.items():
                if count >= self.min_frequency:
                    # 使用有意义的名称代替标点符号本身
                    display_name = f"[整行都是{name}]"
                    filtered_freq[display_name] = count
        
        # 按频率降序排序
        sorted_freq = sorted(filtered_freq.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_freq
    
    def save_results(self, sorted_freq: List[Tuple[str, int]], special_counts: Dict[str, int]) -> Tuple[str, str, str]:
        """
        保存分析结果
        
        Args:
            sorted_freq: 排序后的词汇频率列表
            special_counts: 特殊标点统计字典
            
        Returns:
            (详细结果文件, 词汇表文件, 摘要文件)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        detailed_file = f"高频词分析结果_{timestamp}.txt"
        vocab_file = f"高频词汇表_{timestamp}.txt"
        summary_file = f"分析摘要_{timestamp}.txt"
        
        # 保存详细结果
        with open(detailed_file, 'w', encoding='utf-8') as f:
            f.write(f"高频词分析结果 (出现次数 ≥ {self.min_frequency})\n")
            f.write("=" * 50 + "\n\n")
            
            # 先显示特殊标点的统计（如果有）
            if self.enable_punctuation_stats and any(count >= self.min_frequency for count in special_counts.values()):
                f.write("特殊标点统计 (整行都是该标点):\n")
                f.write("-" * 40 + "\n")
                for name, count in special_counts.items():
                    if count >= self.min_frequency:
                        f.write(f"[整行都是{name}]: {count:>6}\n")
                f.write("\n")
            
            # 显示高频词
            f.write("高频词汇:\n")
            f.write("-" * 40 + "\n")
            for word, freq in sorted_freq:
                # 跳过特殊标点（已经在上面显示过了）
                if not word.startswith('[整行都是'):
                    f.write(f"{word:<15} {freq:>6}\n")
        
        print(f"详细结果已保存到: {detailed_file}")
        
        # 保存纯词汇列表（用于其他用途）
        with open(vocab_file, 'w', encoding='utf-8') as f:
            for word, _ in sorted_freq:
                # 跳过特殊标记
                if not word.startswith('[整行都是'):
                    f.write(f"{word}\n")
        
        print(f"纯词汇列表已保存到: {vocab_file}")
        
        # 保存统计摘要
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("聊天记录高频词分析摘要\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"最小出现次数阈值: {self.min_frequency}\n")
            f.write(f"纯标点统计: {'开启' if self.enable_punctuation_stats else '关闭'}\n")
            f.write(f"发现的高频词数量: {len(sorted_freq)}\n")
            f.write(f"使用的排除词数量: {len(self.stopwords)}\n\n")
            
            # 特殊标点统计
            if self.enable_punctuation_stats:
                f.write("特殊标点统计:\n")
                f.write("-" * 30 + "\n")
                for name, count in special_counts.items():
                    f.write(f"整行都是{name}: {count}次\n")
                f.write("\n")
            
            # 统计不同长度词汇的分布
            length_dist = {}
            for word, freq in sorted_freq:
                # 跳过特殊标记
                if not word.startswith('[整行都是'):
                    length = len(word)
                    length_dist[length] = length_dist.get(length, 0) + 1
            
            f.write("词汇长度分布:\n")
            for length in sorted(length_dist.keys()):
                f.write(f"  长度{length}: {length_dist[length]}个\n")
        
        print(f"分析摘要已保存到: {summary_file}")
        
        return detailed_file, vocab_file, summary_file
    
    def generate_wordcloud(self, sorted_freq: List[Tuple[str, int]], special_counts: Dict[str, int]) -> str:
        """
        生成词云图片
        
        Args:
            sorted_freq: 排序后的词汇频率列表
            special_counts: 特殊标点统计字典
            
        Returns:
            词云图片文件路径
        """
        try:
            # 准备词频数据，排除特殊标点标记
            word_freq = {}
            for word, freq in sorted_freq:
                # 跳过特殊标点标记
                if not word.startswith('[整行都是'):
                    word_freq[word] = freq
            
            if not word_freq:
                print("没有足够的数据生成词云")
                return None
            
            # 获取词云配置
            max_words = self.config.getint('settings', 'wordcloud_max_words')
            width = self.config.getint('settings', 'wordcloud_width')
            height = self.config.getint('settings', 'wordcloud_height')
            bg_color = self.config.get('settings', 'wordcloud_background_color')
            font_path = self.config.get('settings', 'font_path')
            
            # 检查字体文件是否存在
            if not os.path.exists(font_path):
                print(f"警告: 字体文件 {font_path} 不存在，尝试使用默认字体")
                font_path = None
            
            # 生成词云
            print("正在生成词云...")
            wc = WordCloud(
                font_path=font_path,
                width=width,
                height=height,
                background_color=bg_color,
                max_words=max_words
            )
            
            wc.generate_from_frequencies(word_freq)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            wordcloud_file = f"词云_{timestamp}.png"
            
            # 保存词云图片
            if self.config.getboolean('settings', 'save_wordcloud'):
                wc.to_file(wordcloud_file)
                print(f"词云图片已保存到: {wordcloud_file}")
            
            # 显示词云
            if self.config.getboolean('settings', 'show_wordcloud'):
                plt.figure(figsize=(10, 8))
                plt.imshow(wc, interpolation="bilinear")
                plt.axis("off")
                plt.title("聊天记录词云", fontsize=16)
                plt.tight_layout()
                plt.show()
            
            return wordcloud_file
            
        except Exception as e:
            print(f"生成词云失败: {e}")
            import traceback
            traceback.print_exc()
            return None

def create_exclude_list():
    """创建排除词列表文件模板"""
    exclude_file = "stopwords.txt"
    
    if os.path.exists(exclude_file):
        print(f"排除词文件 {exclude_file} 已存在")
        return exclude_file
    
    template = """# 排除词列表
# 每行一个词，支持中文、英文、数字等
# 以#开头的行会被忽略

# 常用中文单字
的
了
在
是
我
你
他
们
这
那

# 英文字母
a
b
c
d
e

# 阿拉伯数字
0
1
2
3

# 标点符号
.
,
!

# 添加您想要排除的其他词...
"""
    
    with open(exclude_file, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"已创建排除词模板文件: {exclude_file}")
    print("请编辑此文件添加您想要排除的词汇")
    return exclude_file

def create_default_config():
    """创建默认配置文件"""
    config_file = "config.ini"
    
    if os.path.exists(config_file):
        print(f"配置文件 {config_file} 已存在")
        return config_file
    
    config = configparser.ConfigParser()
    config['settings'] = {
        'min_frequency': '20',
        'enable_punctuation_stats': 'true',
        'wordcloud_max_words': '200',
        'wordcloud_width': '1200',
        'wordcloud_height': '800',
        'wordcloud_background_color': 'white',
        'font_path': 'C:/Windows/Fonts/simhei.ttf',
        'show_wordcloud': 'true',
        'save_wordcloud': 'true'
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        config.write(f)
    
    print(f"已创建默认配置文件: {config_file}")
    return config_file

def main():
    parser = argparse.ArgumentParser(description='聊天记录高频词分析工具')
    parser.add_argument('input_file', nargs='?', help='聊天记录文件路径')
    parser.add_argument('-c', '--create-exclude', action='store_true',
                       help='创建排除词模板文件')
    parser.add_argument('--create-config', action='store_true',
                       help='创建配置文件模板')
    parser.add_argument('--config', default='config.ini',
                       help='指定配置文件路径 (默认: config.ini)')
    
    args = parser.parse_args()
    
    # 创建排除词模板文件（如果需要）
    if args.create_exclude:
        create_exclude_list()
        return
    
    # 创建配置文件模板（如果需要）
    if args.create_config:
        create_default_config()
        return
    
    # 检查输入文件
    if not args.input_file:
        print("错误: 需要提供聊天记录文件路径")
        print("使用方法: python main.py <聊天记录文件>")
        return
    
    if not os.path.exists(args.input_file):
        print(f"错误: 输入文件 {args.input_file} 不存在")
        return
    
    # 初始化分析器
    analyzer = ChatFrequencyAnalyzer(config_file=args.config)
    
    print(f"使用配置文件: {args.config}")
    print(f"最小出现次数阈值: {analyzer.min_frequency}")
    print(f"纯标点统计: {'开启' if analyzer.enable_punctuation_stats else '关闭'}")
    print("-" * 50)
    
    # 分析文件
    word_freq, special_counts = analyzer.analyze_chat_file(args.input_file)
    
    if not word_freq:
        print("分析失败或文件为空")
        return
    
    # 显示特殊标点统计
    if analyzer.enable_punctuation_stats:
        print("\n特殊标点统计 (整行都是该标点):")
        print("-" * 40)
        for name, count in special_counts.items():
            if count > 0:
                print(f"整行都是{name}: {count}次")
    
    # 过滤和排序结果
    print("\n正在过滤和排序结果...")
    sorted_freq = analyzer.filter_and_sort(word_freq, special_counts)
    
    if not sorted_freq:
        print(f"没有找到出现次数 ≥ {analyzer.min_frequency} 且不在排除列表中的词汇")
        print("请尝试降低阈值或编辑排除词列表")
        return
    
    # 显示前20个结果（包括特殊标点）
    print(f"\n前20个高频项 (出现次数 ≥ {analyzer.min_frequency}):")
    print("-" * 40)
    
    # 分离特殊标点和高频词以便分别显示
    special_items = [(word, freq) for word, freq in sorted_freq if word.startswith('[整行都是')]
    word_items = [(word, freq) for word, freq in sorted_freq if not word.startswith('[整行都是')]
    
    # 显示特殊标点
    if special_items:
        print("特殊标点:")
        for i, (word, freq) in enumerate(special_items, 1):
            print(f"{i:2}. {word:<20} {freq:>6}")
        print()
    
    # 显示高频词
    print("高频词汇:")
    for i, (word, freq) in enumerate(word_items[:20], 1):
        print(f"{i:2}. {word:<15} {freq:>6}")
    
    # 保存分析结果（三个文本文件）
    print(f"\n正在保存分析结果...")
    detailed_file, vocab_file, summary_file = analyzer.save_results(sorted_freq, special_counts)
    
    # 生成词云图片
    print("\n正在生成词云...")
    wordcloud_file = analyzer.generate_wordcloud(sorted_freq, special_counts)
    
    # 显示所有生成的文件
    print("\n" + "=" * 50)
    print("分析完成！生成的文件:")
    print(f"1. 详细分析结果: {detailed_file}")
    print(f"2. 高频词汇表: {vocab_file}")
    print(f"3. 分析摘要: {summary_file}")
    if wordcloud_file:
        print(f"4. 词云图片: {wordcloud_file}")
    print("=" * 50)

if __name__ == "__main__":
    # 初始化jieba分词
    jieba.initialize()
    
    print("聊天记录高频词分析工具 v2.0")
    print("=" * 60)
    print("功能说明:")
    print("  - 高频词分析与统计")
    print("  - 纯标点消息统计（整行都是句号或问号）")
    print("  - 生成词云图片")
    print("  - 配置文件支持")
    
    # 示例用法说明
    print("\n" + "=" * 60)
    print("使用方法:")
    print("  基本用法: python main.py 聊天记录.txt")
    print("  使用指定配置: python main.py 聊天记录.txt --config my_config.ini")
    print("  创建排除词模板: python main.py --create-exclude")
    print("  创建配置文件模板: python main.py --create-config")
    
    # 如果没有命令行参数，显示使用说明
    import sys
    if len(sys.argv) == 1:
        print("\n请提供聊天记录文件路径作为参数")
        print("或使用 --help 查看完整帮助信息")
    else:
        main()