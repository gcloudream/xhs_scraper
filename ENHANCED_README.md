# 增强版小红书基金爬虫 🚀

专门用于**教育目的**的基金知识学习工具，具备先进的反爬取检测能力。

## ✨ 主要特性

### 🔒 高级反检测系统
- **浏览器指纹伪装**: WebGL、Canvas、音频指纹随机化
- **行为模拟**: 人类式鼠标移动、自然滚动、阅读停顿
- **网络指纹**: 请求头优化、TLS指纹伪装
- **智能延时**: 基于成功率的自适应延时策略

### 🧠 智能验证码处理
- **多类型支持**: 滑动、点击、旋转、拼图验证码
- **人性化操作**: 贝塞尔曲线鼠标轨迹、手抖模拟
- **回退策略**: 自动刷新、页面返回、手动处理
- **学习机制**: 基于历史成功率优化策略

### 🎯 自适应选择器系统
- **动态发现**: 自动发现新的页面元素选择器
- **成功率跟踪**: 基于历史表现选择最佳选择器
- **智能缓存**: 选择器性能数据持久化存储
- **故障恢复**: 多重备用选择器保证稳定性

### 📊 会话和Cookie管理
- **会话池**: 多会话轮换避免检测
- **Cookie持久化**: 自动保存和恢复浏览状态
- **智能轮换**: 基于请求数、时长、错误率自动切换
- **代理集成**: 支持HTTP/SOCKS5代理轮换

## 📋 系统要求

- Python 3.7+
- Chrome/Chromium 浏览器
- 4GB+ RAM (推荐8GB)
- 稳定的网络连接

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements_enhanced.txt
```

### 2. 基本使用

```python
from enhanced_xiaohongshu_scraper import EnhancedXiaohongshuFundScraper
from config import ScrapingConfig

# 创建配置
config = ScrapingConfig(
    headless=False,           # 是否无头模式
    max_posts_per_keyword=30, # 每个关键词最大帖子数
    request_delay_min=3.0,    # 最小延时
    request_delay_max=8.0     # 最大延时
)

# 初始化爬虫
scraper = EnhancedXiaohongshuFundScraper(config=config)

# 初始化WebDriver
scraper.initialize_driver()

# 开始爬取
keywords = ["基金知识", "基金投资", "理财入门"]
posts = scraper.scrape_multiple_keywords(keywords)

# 保存结果
scraper.save_results(posts)

# 清理资源
scraper.cleanup()
```

### 3. 高级配置

```python
# 使用代理
scraper = EnhancedXiaohongshuFundScraper(
    config=config,
    use_proxy=True,
    proxy_file="proxies.txt"  # 一行一个代理
)

# 自定义配置
config = ScrapingConfig(
    headless=True,
    max_posts_per_keyword=50,
    max_scroll_attempts=8,
    request_delay_min=2.0,
    request_delay_max=6.0,
    user_agent_rotation=True,
    human_behavior_enabled=True
)
```

## 📁 项目结构

```
xhs/
├── enhanced_xiaohongshu_scraper.py  # 主爬虫程序
├── anti_detection.py               # 反检测模块
├── captcha_solver.py               # 验证码处理模块
├── adaptive_selectors.py           # 自适应选择器系统
├── session_manager.py              # 会话和Cookie管理
├── config.py                       # 配置管理
├── logger.py                       # 增强日志系统
├── requirements_enhanced.txt       # 依赖包列表
└── output/                         # 输出目录
    ├── enhanced_fund_posts_*.csv   # CSV数据
    ├── enhanced_fund_posts_*.json  # JSON数据
    └── scraping_stats_*.json       # 统计信息
```

## ⚙️ 配置选项

### 基础配置
- `headless`: 是否无头模式运行
- `max_posts_per_keyword`: 每个关键词最大帖子数
- `max_scroll_attempts`: 最大滚动尝试次数
- `timeout`: 页面加载超时时间

### 反检测配置
- `request_delay_min/max`: 请求延时范围
- `scroll_delay_min/max`: 滚动延时范围
- `user_agent_rotation`: 是否轮换User-Agent
- `human_behavior_enabled`: 是否启用人类行为模拟

### 质量过滤
- `min_title_length`: 最小标题长度
- `spam_keywords`: 垃圾内容关键词
- `required_keywords`: 必需包含的关键词

## 📊 输出格式

### CSV输出
- title: 帖子标题
- author: 作者名称
- link: 帖子链接
- likes: 点赞数
- description: 帖子描述
- keyword: 搜索关键词
- scraped_time: 爬取时间
- scraper_version: 爬虫版本

### 统计信息
- session_stats: 会话统计
- selector_stats: 选择器性能
- captcha_stats: 验证码处理统计
- proxy_stats: 代理使用统计

## 🛡️ 反爬策略详解

### 1. 浏览器指纹伪装
```javascript
// 自动注入的反检测脚本示例
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [...]});
// WebGL指纹随机化
// Canvas指纹伪装
// 音频指纹干扰
```

### 2. 行为模拟
- **鼠标轨迹**: 贝塞尔曲线生成自然路径
- **滚动行为**: 分段滚动，模拟阅读停顿
- **页面交互**: 随机点击、文本选择、焦点切换
- **时间模式**: 根据时间段调整行为速度

### 3. 网络层优化
- **请求头**: 完整的浏览器请求头模拟
- **Cookie管理**: 智能Cookie池和轮换
- **连接复用**: 保持长连接减少检测
- **代理轮换**: 基于性能的智能代理选择

### 4. 验证码应对
- **类型识别**: 自动识别验证码类型
- **策略选择**: 不同类型使用不同解决策略
- **人性化操作**: 模拟真实用户操作习惯
- **失败处理**: 多重回退机制

## 🔧 故障排除

### 常见问题

1. **WebDriver初始化失败**
   ```bash
   # 更新Chrome浏览器到最新版本
   # 或手动下载ChromeDriver
   ```

2. **验证码无法处理**
   ```python
   # 设置非headless模式进行手动处理
   config.headless = False
   ```

3. **选择器失效**
   ```python
   # 清除选择器缓存
   import os
   os.remove("selector_cache.json")
   ```

4. **代理连接失败**
   ```python
   # 检查代理格式和可用性
   # 格式: http://ip:port 或 socks5://ip:port
   ```

### 性能优化

1. **内存使用**
   - 定期清理会话缓存
   - 限制并发请求数量
   - 使用headless模式

2. **网络优化**
   - 使用高质量代理
   - 调整延时策略
   - 启用请求复用

3. **稳定性提升**
   - 增加重试次数
   - 扩大延时范围
   - 使用会话轮换

## 📈 监控和日志

### 日志级别
- `INFO`: 基本运行信息
- `WARNING`: 可能的问题
- `ERROR`: 严重错误
- `DEBUG`: 详细调试信息

### 性能监控
```python
# 获取实时统计
stats = scraper.session_manager.get_session_stats()
print(f"成功率: {stats['success_rate']:.2%}")
print(f"会话时长: {stats['session_duration']:.0f}秒")
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## ⚠️ 免责声明

本工具仅用于**教育目的**的基金知识学习，请遵守相关网站的robots.txt和服务条款。使用者应当：

- 合理控制爬取频率
- 尊重网站服务条款
- 不用于商业目的
- 遵守当地法律法规

## 📄 许可证

MIT License

## 🙋‍♂️ 支持

如有问题，请查看：
1. 本README文档
2. 代码注释
3. 日志输出
4. Issue跟踪

---

**祝您学习愉快！💫**