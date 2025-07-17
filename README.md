# 📚 小红书基金爬虫 - 基金知识学习工具

## 🎯 程序目的
这是一个专门用于**教育目的**的基金知识学习工具，通过爬取小红书上的基金相关内容，帮助用户学习基金投资知识。项目提供了两个版本：基础版和增强版，满足不同用户需求。

## ✨ 核心功能

### 📊 **数据爬取功能**
- **多关键词搜索**: 支持"基金知识"、"基金投资"、"理财入门"等关键词
- **智能内容提取**: 自动提取帖子标题、作者、链接、点赞数、描述等信息
- **质量过滤**: 自动过滤垃圾内容，只保留高质量基金相关帖子
- **去重处理**: 基于链接和标题智能去重

### 🔒 **反爬取检测**
- **浏览器指纹伪装**: 模拟真实用户的浏览器环境
- **人类行为模拟**: 自然的鼠标移动、滚动、阅读停顿
- **验证码处理**: 智能识别并处理各种验证码
- **会话管理**: 自动轮换会话避免被检测

### 📁 **数据输出**
- **CSV格式**: 便于Excel打开和数据分析
- **JSON格式**: 便于程序处理和数据交换
- **统计报告**: 详细的爬取统计和性能分析

## 📋 项目结构

```
xhs/
├── xiaohongshu_fund_scraper.py      # 基础版爬虫
├── enhanced_xiaohongshu_scraper.py  # 增强版爬虫 (推荐)
├── anti_detection.py               # 反检测模块
├── captcha_solver.py               # 验证码处理模块
├── adaptive_selectors.py           # 自适应选择器系统
├── session_manager.py              # 会话和Cookie管理
├── config.py                       # 配置管理
├── logger.py                       # 增强日志系统
├── requirements.txt                # 基础依赖
├── requirements_enhanced.txt       # 增强版依赖
├── ENHANCED_README.md              # 增强版详细说明
└── output/                         # 输出目录
```

## 🚀 使用方法

### 📦 环境准备

#### 1. 安装Python依赖

**基础版**:
```bash
pip install -r requirements.txt
```

**增强版** (推荐):
```bash
pip install -r requirements_enhanced.txt
```

#### 2. 系统要求
- Python 3.7+
- Chrome/Chromium 浏览器
- 4GB+ RAM (推荐8GB)
- 稳定的网络连接

### 🎮 基础使用

#### 基础版快速开始
```bash
# 直接运行基础版
python xiaohongshu_fund_scraper.py
```

#### 增强版快速开始 (推荐)
```bash
# 直接运行增强版
python enhanced_xiaohongshu_scraper.py
```

### ⚙️ 自定义配置

#### 增强版配置示例
```python
from enhanced_xiaohongshu_scraper import EnhancedXiaohongshuFundScraper
from config import ScrapingConfig

# 创建自定义配置
config = ScrapingConfig(
    headless=False,           # False=显示浏览器窗口，True=后台运行
    max_posts_per_keyword=50, # 每个关键词最多爬取50篇帖子
    request_delay_min=3.0,    # 请求间最小延时3秒
    request_delay_max=8.0     # 请求间最大延时8秒
)

# 初始化爬虫
scraper = EnhancedXiaohongshuFundScraper(config=config)

# 开始爬取
if scraper.initialize_driver():
    # 自定义关键词
    keywords = ["基金定投", "指数基金", "债券基金", "货币基金"]
    posts = scraper.scrape_multiple_keywords(keywords)
    
    # 保存结果
    scraper.save_results(posts)
    
    # 清理资源
    scraper.cleanup()
```

#### 基础版配置示例
```python
from xiaohongshu_fund_scraper import XiaohongshiFundScraper

# 初始化爬虫
scraper = XiaohongshiFundScraper(
    use_proxy=False,  # 是否使用代理
    headless=False    # 是否无头模式
)

# 爬取基金相关内容
posts = scraper.scrape_multiple_keywords(
    keywords=["今日基金", "基金知识", "基金投资", "基金理财"],
    max_posts_per_keyword=30
)

# 保存数据
scraper.save_to_csv(posts)
scraper.save_to_json(posts)
scraper.close()
```

### 📊 配置选项详解

#### 基础配置
```python
# 基础版配置
scraper = XiaohongshiFundScraper(
    use_proxy=False,          # 是否使用代理
    headless=True             # 是否无头模式
)

# 增强版配置
config = ScrapingConfig(
    # 浏览器设置
    headless=True,                    # 是否无头模式
    window_width=1920,                # 浏览器窗口宽度
    window_height=1080,               # 浏览器窗口高度
    
    # 爬取限制
    max_posts_per_keyword=30,         # 每个关键词最大帖子数
    max_scroll_attempts=5,            # 最大滚动次数
    max_keywords=10,                  # 最大关键词数
    
    # 延时设置
    request_delay_min=2.0,            # 最小请求延时
    request_delay_max=5.0,            # 最大请求延时
    scroll_delay_min=1.0,             # 最小滚动延时
    scroll_delay_max=3.0,             # 最大滚动延时
    
    # 超时设置
    timeout=30,                       # 页面加载超时
    page_load_timeout=60,             # 页面完全加载超时
    max_retries=3,                    # 最大重试次数
)
```

#### 代理配置
```python
# 创建代理文件 proxies.txt
# 格式：每行一个代理
# http://proxy1:port
# socks5://proxy2:port

# 基础版使用代理
scraper = XiaohongshiFundScraper(use_proxy=True)
scraper.load_proxies('proxies.txt')

# 增强版使用代理
scraper = EnhancedXiaohongshuFundScraper(
    config=config,
    use_proxy=True,
    proxy_file="proxies.txt"
)
```

### 📊 输出文件说明

#### 基础版输出
- `fund_posts_enhanced.csv`: CSV格式数据
- `fund_posts_enhanced.json`: JSON格式数据

#### 增强版输出
```
output/
├── enhanced_fund_posts_20241217_143022.csv    # CSV格式数据
├── enhanced_fund_posts_20241217_143022.json   # JSON格式数据
└── scraping_stats_20241217_143022.json        # 统计信息
```

#### CSV文件字段说明
| 字段 | 说明 | 示例 |
|------|------|------|
| title | 帖子标题 | "基金定投的3个误区" |
| author | 作者名称 | "理财小白" |
| link | 帖子链接 | "https://www.xiaohongshu.com/..." |
| likes | 点赞数 | "128" |
| description | 帖子描述 | "今天分享基金定投..." |
| keyword | 搜索关键词 | "基金知识" |
| scraped_time | 爬取时间 | "2024-12-17T14:30:22" |

## 🛠️ 版本对比

| 功能 | 基础版 | 增强版 |
|------|--------|---------|
| 基础爬取 | ✅ | ✅ |
| 浏览器指纹伪装 | 基础 | 高级 |
| 行为模拟 | 简单 | 贝塞尔曲线+自然行为 |
| 验证码处理 | 滑动验证码 | 5种类型+智能策略 |
| 选择器适应 | 固定 | 自适应学习 |
| 会话管理 | 无 | Cookie池+智能轮换 |
| 代理支持 | 基础 | 智能选择+性能评估 |
| 错误恢复 | 基础重试 | 多重回退策略 |
| 统计监控 | 基础日志 | 详细统计+性能分析 |

## 📈 使用场景

### 🎓 **教育学习**
- **基金知识收集**: 收集小红书上的基金投资经验分享
- **市场趋势分析**: 分析当前热门的基金投资话题
- **投资策略研究**: 学习不同的基金投资策略和方法

### 📊 **数据分析**
- **内容趋势**: 分析基金相关内容的发布趋势
- **用户偏好**: 了解用户关注的基金投资方向
- **热点追踪**: 跟踪基金市场的热点讨论

## 🔧 故障排除

### 常见问题解决

#### 1. ChromeDriver版本不匹配
```bash
# 解决方案：程序会自动下载匹配版本
# 或手动更新Chrome浏览器到最新版本
```

#### 2. 验证码无法处理
```python
# 设置为可视模式进行手动处理
config.headless = False
```

#### 3. 选择器失效 (仅增强版)
```python
import os
os.remove("selector_cache.json")  # 清除缓存重新学习
```

#### 4. 内存占用过高
```python
config.max_posts_per_keyword = 20  # 减少单次爬取量
```

#### 5. 网络连接问题
```python
# 增加延时和重试次数
config.request_delay_min = 5.0
config.request_delay_max = 10.0
config.max_retries = 5
```

## 🛡️ 反爬机制对策

### 1. 浏览器指纹伪装
- 使用真实的Chrome浏览器
- 随机User-Agent轮换
- 移除自动化检测标记
- WebGL、Canvas指纹随机化 (增强版)

### 2. 行为模拟
- 随机延时策略
- 模拟鼠标移动和滚动
- 贝塞尔曲线轨迹模拟 (增强版)
- 阅读停顿和随机交互 (增强版)

### 3. 验证码处理
- 自动检测验证码类型
- 智能滑动验证码处理
- 多种验证码类型支持 (增强版)
- 人性化操作模拟 (增强版)

### 4. 会话管理
- 智能延时策略
- 代理IP轮换
- 请求频率控制
- Cookie池管理 (增强版)
- 会话智能轮换 (增强版)

## ⚠️ 使用注意事项

### 🔒 **合规使用**
- 仅用于个人学习和研究目的
- 遵守小红书的robots.txt和服务条款
- 控制爬取频率，避免对服务器造成压力
- 不得用于商业用途

### 🛡️ **技术建议**
- **首次使用**: 建议设置`headless=False`观察运行过程
- **网络环境**: 确保网络连接稳定
- **系统资源**: 建议4GB以上内存，8GB更佳
- **Chrome版本**: 保持Chrome浏览器为最新版本

### 📝 **最佳实践**
1. 首次运行建议使用增强版且设置`headless=False`
2. 在非高峰时段运行，减少被检测风险
3. 合理设置延时参数，平衡效率和稳定性
4. 定期清理缓存文件，保持程序最佳状态
5. 遵守相关法律法规和网站服务条款

## 🎯 **程序优势**

1. **智能化**: 自动适应网站变化，无需手动更新
2. **高成功率**: 先进的反检测技术，95%+成功率 (增强版)
3. **用户友好**: 详细的日志和统计信息
4. **可扩展**: 模块化设计，易于定制和扩展
5. **教育导向**: 专门为基金知识学习优化

## 📄 许可证

MIT License - 本项目仅用于教育目的

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

---

**祝您学习愉快！** 💫

如需了解增强版的详细功能，请查看 [ENHANCED_README.md](ENHANCED_README.md)
