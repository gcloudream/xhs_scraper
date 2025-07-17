"""
Enhanced Xiaohongshu Fund Scraper with Advanced Anti-Detection
增强的小红书基金爬虫 - 专门用于教育目的的基金知识学习
"""
import time
import random
import json
import csv
from datetime import datetime
from urllib.parse import quote, urljoin
from typing import List, Dict, Optional
import logging
from pathlib import Path

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Enhanced modules
from anti_detection import EnhancedAntiDetection
from captcha_solver import SmartCaptchaHandler
from adaptive_selectors import AdaptiveSelectorManager, SmartElementExtractor
from session_manager import SessionManager, ProxySessionManager
from config import ScrapingConfig
from logger import ScrapingLogger

logger = ScrapingLogger("enhanced_xiaohongshu_scraper")


class EnhancedXiaohongshuFundScraper:
    """增强的小红书基金爬虫"""
    
    def __init__(self, config: ScrapingConfig = None, use_proxy: bool = False, proxy_file: str = None):
        self.config = config or ScrapingConfig()
        self.use_proxy = use_proxy
        self.proxy_file = proxy_file
        
        # 初始化组件
        self.anti_detection = EnhancedAntiDetection()
        self.session_manager = SessionManager()
        self.proxy_manager = ProxySessionManager(proxy_file) if proxy_file else None
        self.captcha_handler = None
        self.selector_manager = AdaptiveSelectorManager()
        self.element_extractor = None
        
        # WebDriver相关
        self.driver = None
        self.wait = None
        
        # 数据存储
        self.scraped_data = []
        self.session_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'captchas_solved': 0,
            'posts_scraped': 0,
            'session_rotations': 0
        }
        
        logger.log_session_start(self.config.dict())
    
    def initialize_driver(self) -> bool:
        """初始化WebDriver"""
        try:
            # 设置Chrome选项
            chrome_options = self.anti_detection.setup_chrome_options(self.config.headless)
            
            # 代理设置
            if self.use_proxy and self.proxy_manager:
                proxy = self.proxy_manager.get_best_proxy()
                if proxy:
                    chrome_options.add_argument(f'--proxy-server={proxy}')
                    logger.info(f"使用代理: {proxy}")
            
            # 创建WebDriver
            # service = Service(ChromeDriverManager().install())
            service = Service('./drivers/chromedriver.exe')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 设置等待和行为模拟器
            self.wait = WebDriverWait(self.driver, self.config.timeout)
            
            # 注入反检测脚本
            self.anti_detection.inject_anti_detection_scripts(self.driver)
            
            # 设置行为模拟器
            self.anti_detection.setup_behavioral_simulator(self.driver)
            
            # 初始化其他组件
            self.captcha_handler = SmartCaptchaHandler(self.driver)
            self.element_extractor = SmartElementExtractor(self.driver)
            
            # 启动会话
            if not self.session_manager.start_session(self.driver):
                logger.warning("会话启动失败，但继续运行")
            
            logger.info("WebDriver初始化成功")
            return True
            
        except Exception as e:
            logger.error("WebDriver初始化失败", exception=e)
            return False
    
    def search_fund_content(self, keyword: str) -> List[Dict]:
        """搜索基金内容"""
        logger.info(f"开始搜索关键词: {keyword}")
        
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}&source=web_explore_feed"
        posts = []
        
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"搜索尝试 {attempt + 1}/{self.config.max_retries}")
                
                # 记录请求
                self.session_stats['total_requests'] += 1
                self.session_manager.record_request()
                
                # 获取智能延时
                delay = self.anti_detection.get_delay('search')
                logger.debug(f"搜索前延时: {delay:.2f}秒")
                time.sleep(delay)
                
                # 访问搜索页面
                start_time = time.time()
                self.driver.get(search_url)
                self._wait_for_page_load()
                
                # 记录代理响应时间
                if self.proxy_manager:
                    response_time = time.time() - start_time
                    current_proxy = self._get_current_proxy()
                    if current_proxy:
                        self.proxy_manager.record_proxy_result(current_proxy, True, response_time)
                
                # 检查重定向和验证码
                if self._handle_redirects_and_captchas():
                    # 滚动加载内容
                    self._intelligent_scroll_and_load()
                    
                    # 解析搜索结果
                    posts = self._parse_search_results_enhanced()
                    
                    if posts:
                        logger.info(f"成功获取 {len(posts)} 个帖子")
                        self.session_stats['successful_requests'] += 1
                        self.anti_detection.record_request_result(True)
                        break
                    else:
                        logger.warning("未找到有效帖子")
                else:
                    logger.warning("页面加载或验证码处理失败")
                
            except Exception as e:
                logger.error(f"搜索出错 (尝试 {attempt + 1})", exception=e)
                self.session_stats['failed_requests'] += 1
                self.session_manager.record_request(False)
                self.anti_detection.record_request_result(False)
                
                # 记录代理失败
                if self.proxy_manager:
                    current_proxy = self._get_current_proxy()
                    if current_proxy:
                        self.proxy_manager.record_proxy_result(current_proxy, False)
                
                # 检查是否需要轮换会话
                if self.session_manager.should_rotate_session():
                    logger.info("轮换会话...")
                    self._rotate_session()
                
                # 失败后的恢复延时
                recovery_delay = self.anti_detection.get_delay('page_load') * (attempt + 1)
                time.sleep(recovery_delay)
        
        return posts
    
    def _wait_for_page_load(self):
        """等待页面加载"""
        try:
            # 等待基本元素
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 等待JavaScript完成
            self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            
            # 智能等待动态内容
            time.sleep(self.anti_detection.get_delay('page_load'))
            
        except TimeoutException:
            logger.warning("页面加载超时")
    
    def _handle_redirects_and_captchas(self) -> bool:
        """处理重定向和验证码"""
        try:
            current_url = self.driver.current_url.lower()
            
            # 检查登录重定向
            if "login" in current_url or "signin" in current_url:
                logger.warning("检测到登录重定向")
                if not self._handle_login_redirect():
                    return False
            
            # 检查验证码
            if self.captcha_handler.solver.detect_and_solve_captcha():
                self.session_stats['captchas_solved'] += 1
                self.anti_detection.record_request_result(True, True)
                logger.info("验证码处理成功")
            
            return True
            
        except Exception as e:
            logger.error("处理重定向和验证码时出错", exception=e)
            return False
    
    def _handle_login_redirect(self) -> bool:
        """处理登录重定向"""
        skip_strategies = [
            self._try_skip_login_buttons,
            self._try_direct_navigation,
            self._try_clear_cookies_and_retry
        ]
        
        for strategy in skip_strategies:
            try:
                if strategy():
                    logger.info("成功绕过登录")
                    return True
            except Exception as e:
                logger.debug(f"登录绕过策略失败: {strategy.__name__} - {e}")
                continue
        
        logger.error("所有登录绕过策略都失败了")
        return False
    
    def _try_skip_login_buttons(self) -> bool:
        """尝试点击跳过登录按钮"""
        skip_selectors = [
            "//button[contains(text(), '跳过') or contains(text(), '稍后')]",
            "//a[contains(text(), '跳过') or contains(text(), '稍后')]", 
            "//div[contains(@class, 'close') or contains(@class, 'skip')]//button",
            "//span[contains(@class, 'close')]"
        ]
        
        for selector in skip_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    element.click()
                    time.sleep(2)
                    return "login" not in self.driver.current_url.lower()
            except:
                continue
        
        return False
    
    def _try_direct_navigation(self) -> bool:
        """尝试直接导航"""
        try:
            target_url = "https://www.xiaohongshu.com/search_result?keyword=基金&source=web_explore_feed"
            self.driver.get(target_url)
            self._wait_for_page_load()
            return "login" not in self.driver.current_url.lower()
        except:
            return False
    
    def _try_clear_cookies_and_retry(self) -> bool:
        """尝试清除cookies并重试"""
        try:
            self.driver.delete_all_cookies()
            time.sleep(2)
            target_url = "https://www.xiaohongshu.com/search_result?keyword=基金&source=web_explore_feed"
            self.driver.get(target_url)
            self._wait_for_page_load()
            return "login" not in self.driver.current_url.lower()
        except:
            return False
    
    def _intelligent_scroll_and_load(self):
        """智能滚动和加载"""
        logger.info("开始智能滚动加载内容...")
        
        for scroll_attempt in range(self.config.max_scroll_attempts):
            try:
                # 获取当前页面高度
                current_height = self.driver.execute_script("return document.body.scrollHeight")
                
                # 使用行为模拟器进行自然滚动
                if self.anti_detection.behavioral_simulator:
                    self.anti_detection.behavioral_simulator.natural_scrolling()
                else:
                    # 备用滚动方法
                    scroll_distance = random.randint(400, 800)
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                
                # 模拟阅读时间
                reading_time = self.anti_detection.get_delay('scroll')
                time.sleep(reading_time)
                
                # 检查是否有新内容
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == current_height:
                    logger.info("没有更多内容加载")
                    break
                
                # 尝试点击"加载更多"按钮
                self._try_load_more_button()
                
                # 随机页面交互
                if self.anti_detection.behavioral_simulator and random.random() < 0.3:
                    self.anti_detection.behavioral_simulator.random_page_interaction()
                
            except Exception as e:
                logger.warning(f"滚动加载出错: {e}")
                break
    
    def _try_load_more_button(self):
        """尝试点击加载更多按钮"""
        load_more_selectors = [
            "//button[contains(text(), '加载更多') or contains(text(), '查看更多')]",
            "//div[contains(text(), '加载更多') or contains(text(), '查看更多')]",
            "//button[contains(@class, 'load-more')]",
            "//div[contains(@class, 'load-more')]"
        ]
        
        for selector in load_more_selectors:
            try:
                button = self.driver.find_element(By.XPATH, selector)
                if button.is_displayed():
                    # 使用JavaScript点击避免被拦截
                    self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(self.anti_detection.get_delay('click'))
                    break
            except:
                continue
    
    def _parse_search_results_enhanced(self) -> List[Dict]:
        """增强的搜索结果解析"""
        logger.info("开始解析搜索结果...")
        
        # 使用自适应选择器查找帖子元素
        post_elements = self.selector_manager.find_elements_adaptive(self.driver, 'post', timeout=15)
        
        if not post_elements:
            logger.warning("未找到帖子元素，尝试发现新选择器...")
            # 尝试发现新选择器
            new_selectors = self.selector_manager.discover_new_selectors(self.driver, 'post')
            if new_selectors:
                logger.info(f"发现 {len(new_selectors)} 个新选择器")
                # 重新尝试查找
                post_elements = self.selector_manager.find_elements_adaptive(self.driver, 'post', timeout=10)
        
        if not post_elements:
            logger.error("仍然未找到帖子元素")
            return []
        
        logger.info(f"找到 {len(post_elements)} 个帖子元素")
        
        posts = []
        max_posts = min(len(post_elements), self.config.max_posts_per_keyword)
        
        for i, element in enumerate(post_elements[:max_posts]):
            try:
                # 使用智能元素提取器
                post_data = self.element_extractor.extract_post_data_smart(element)
                
                if post_data and self._is_valid_fund_post(post_data):
                    # 添加额外信息
                    post_data.update({
                        'scraped_time': datetime.now().isoformat(),
                        'keyword': getattr(self, 'current_keyword', ''),
                        'scraper_version': 'enhanced_v2.0'
                    })
                    
                    posts.append(post_data)
                    self.session_stats['posts_scraped'] += 1
                    
                    logger.log_post_scraped(post_data['title'], post_data.get('keyword', ''))
                
                # 定期进行人类行为模拟
                if i % 5 == 0 and self.anti_detection.behavioral_simulator:
                    self.anti_detection.behavioral_simulator.random_page_interaction()
                    
            except Exception as e:
                logger.error(f"提取帖子 {i+1} 数据时出错", exception=e)
                continue
        
        logger.info(f"成功解析 {len(posts)} 个有效帖子")
        return posts
    
    def _is_valid_fund_post(self, post_data: Dict) -> bool:
        """验证是否为有效的基金帖子"""
        if not post_data:
            return False
        
        title = post_data.get('title', '').strip()
        description = post_data.get('description', '').strip()
        
        # 基本验证
        if not title or title == "未知标题" or len(title) < self.config.min_title_length:
            return False
        
        # 垃圾内容过滤
        combined_text = f"{title} {description}".lower()
        for spam_keyword in self.config.spam_keywords:
            if spam_keyword in combined_text:
                return False
        
        # 基金相关内容验证
        has_fund_keyword = any(keyword in combined_text for keyword in self.config.required_keywords)
        return has_fund_keyword
    
    def scrape_multiple_keywords(self, keywords: List[str] = None) -> List[Dict]:
        """爬取多个关键词"""
        if keywords is None:
            keywords = self.config.default_keywords
        
        logger.info(f"开始爬取 {len(keywords)} 个关键词")
        
        all_posts = []
        
        for i, keyword in enumerate(keywords):
            try:
                logger.info(f"处理关键词 {i+1}/{len(keywords)}: {keyword}")
                self.current_keyword = keyword
                
                # 检查是否需要轮换会话
                if self.session_manager.should_rotate_session():
                    self._rotate_session()
                
                # 搜索内容
                posts = self.search_fund_content(keyword)
                
                # 限制每个关键词的帖子数量
                if len(posts) > self.config.max_posts_per_keyword:
                    posts = posts[:self.config.max_posts_per_keyword]
                
                all_posts.extend(posts)
                
                # 关键词间的智能延时
                if i < len(keywords) - 1:  # 不是最后一个关键词
                    inter_keyword_delay = self.anti_detection.get_delay('search') * 2
                    logger.info(f"关键词间延时: {inter_keyword_delay:.2f}秒")
                    time.sleep(inter_keyword_delay)
                
            except Exception as e:
                logger.error(f"处理关键词 '{keyword}' 时出错", exception=e)
                continue
        
        # 去重和质量过滤
        unique_posts = self._remove_duplicates_and_filter(all_posts)
        
        logger.info(f"爬取完成，总共获得 {len(unique_posts)} 个唯一的高质量帖子")
        return unique_posts
    
    def _remove_duplicates_and_filter(self, posts: List[Dict]) -> List[Dict]:
        """去重和质量过滤"""
        seen_links = set()
        seen_titles = set()
        unique_posts = []
        
        for post in posts:
            link = post.get('link', '')
            title = post.get('title', '')
            
            # 基于链接去重
            if link and link not in seen_links:
                seen_links.add(link)
                unique_posts.append(post)
            # 基于标题去重（如果没有链接）
            elif not link and title and title not in seen_titles:
                seen_titles.add(title)
                unique_posts.append(post)
        
        # 按质量排序（可以根据点赞数、标题长度等）
        unique_posts.sort(key=lambda p: len(p.get('title', '')), reverse=True)
        
        return unique_posts
    
    def _rotate_session(self):
        """轮换会话"""
        try:
            logger.info("开始轮换会话...")
            self.session_stats['session_rotations'] += 1
            
            # 结束当前会话
            self.session_manager.end_session(self.driver)
            
            # 重新初始化driver
            if self.driver:
                self.driver.quit()
                time.sleep(random.uniform(5, 10))
            
            # 重新初始化
            if self.initialize_driver():
                logger.info("会话轮换成功")
            else:
                logger.error("会话轮换失败")
                
        except Exception as e:
            logger.error("轮换会话时出错", exception=e)
    
    def _get_current_proxy(self) -> Optional[str]:
        """获取当前代理"""
        try:
            if self.use_proxy and self.proxy_manager:
                # 这里可以从driver中获取当前使用的代理
                # 由于selenium无法直接获取，这里返回最近选择的代理
                return None  # 简化处理
        except:
            pass
        return None
    
    def save_results(self, posts: List[Dict]):
        """保存结果"""
        if not posts:
            logger.warning("没有数据需要保存")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # 保存为CSV
            if self.config.output_csv:
                csv_filename = f"enhanced_fund_posts_{timestamp}.csv"
                self._save_to_csv(posts, csv_filename)
            
            # 保存为JSON
            if self.config.output_json:
                json_filename = f"enhanced_fund_posts_{timestamp}.json"
                self._save_to_json(posts, json_filename)
            
            # 保存统计信息
            stats_filename = f"scraping_stats_{timestamp}.json"
            self._save_stats(stats_filename)
            
        except Exception as e:
            logger.error("保存结果时出错", exception=e)
    
    def _save_to_csv(self, posts: List[Dict], filename: str):
        """保存为CSV"""
        output_path = Path(self.config.output_directory) / filename
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            if posts:
                fieldnames = list(posts[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(posts)
        
        logger.info(f"CSV数据已保存到: {output_path}")
    
    def _save_to_json(self, posts: List[Dict], filename: str):
        """保存为JSON"""
        output_path = Path(self.config.output_directory) / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON数据已保存到: {output_path}")
    
    def _save_stats(self, filename: str):
        """保存统计信息"""
        output_path = Path(self.config.output_directory) / filename
        
        stats = {
            'session_stats': self.session_stats,
            'session_manager_stats': self.session_manager.get_session_stats(),
            'selector_stats': self.selector_manager.get_selector_stats(),
            'config': self.config.dict()
        }
        
        if self.proxy_manager:
            stats['proxy_stats'] = self.proxy_manager.get_proxy_stats()
        
        if self.captcha_handler:
            stats['captcha_stats'] = self.captcha_handler.get_captcha_stats()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"统计信息已保存到: {output_path}")
    
    def cleanup(self):
        """清理资源"""
        try:
            # 结束会话
            if self.session_manager:
                self.session_manager.end_session(self.driver)
            
            # 优化选择器
            if self.selector_manager:
                self.selector_manager.optimize_selectors()
            
            # 关闭driver
            if self.driver:
                self.driver.quit()
            
            # 记录会话结束
            logger.log_session_end()
            
        except Exception as e:
            logger.error("清理资源时出错", exception=e)
    
    def print_summary(self, posts: List[Dict]):
        """打印摘要信息"""
        print("\n" + "="*50)
        print("🎯 增强版小红书基金爬虫 - 运行摘要")
        print("="*50)
        
        print(f"📊 数据统计:")
        print(f"   总帖子数: {len(posts)}")
        print(f"   成功请求: {self.session_stats['successful_requests']}")
        print(f"   失败请求: {self.session_stats['failed_requests']}")
        print(f"   验证码解决: {self.session_stats['captchas_solved']}")
        print(f"   会话轮换: {self.session_stats['session_rotations']}")
        
        # 关键词分布
        if posts:
            keyword_counts = {}
            for post in posts:
                keyword = post.get('keyword', 'unknown')
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            print(f"\n📈 关键词分布:")
            for keyword, count in keyword_counts.items():
                print(f"   {keyword}: {count}篇")
        
        # 示例帖子
        if posts:
            print(f"\n📝 示例帖子 (前3篇):")
            for i, post in enumerate(posts[:3], 1):
                print(f"   {i}. {post['title'][:50]}...")
                print(f"      作者: {post['author']}")
                print(f"      点赞: {post['likes']}")
        
        # 性能统计
        session_stats = self.session_manager.get_session_stats()
        print(f"\n⚡ 性能统计:")
        print(f"   成功率: {session_stats.get('success_rate', 0):.2%}")
        print(f"   会话时长: {session_stats.get('session_duration', 0):.0f}秒")
        print(f"   可用会话: {session_stats.get('available_sessions', 0)}")
        
        print("="*50)


def main():
    """主函数"""
    scraper = None
    
    try:
        # 创建配置
        config = ScrapingConfig(
            headless=False,  # 设置为True可无头运行
            max_posts_per_keyword=30,
            max_scroll_attempts=5,
            request_delay_min=3.0,
            request_delay_max=8.0
        )
        
        # 初始化爬虫
        scraper = EnhancedXiaohongshuFundScraper(
            config=config,
            use_proxy=False,  # 设置为True并提供proxy_file以使用代理
            proxy_file=None   # "proxies.txt"
        )
        
        # 初始化WebDriver
        if not scraper.initialize_driver():
            logger.error("WebDriver初始化失败")
            return
        
        logger.info("开始增强版基金内容爬取...")
        
        # 爬取内容
        # keywords = ["今日基金", "基金知识", "基金投资", "基金理财", "基金入门"]
        keywords = ["今日基金"]
        posts = scraper.scrape_multiple_keywords(keywords)
        
        if posts:
            # 保存结果
            scraper.save_results(posts)
            
            # 打印摘要
            scraper.print_summary(posts)
            
        else:
            logger.warning("未获取到任何帖子")
    
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error("程序执行出错", exception=e)
    finally:
        if scraper:
            scraper.cleanup()


if __name__ == "__main__":
    main()