# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urljoin, urlencode, quote
import csv
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import fake_useragent
import threading
from queue import Queue
import logging
from selenium.webdriver.common.keys import Keys
import re

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XiaohongshiFundScraper:
    def __init__(self, use_proxy=False, headless=True):
        self.ua = fake_useragent.UserAgent()
        self.use_proxy = use_proxy
        self.headless = headless
        self.proxies = []
        self.current_proxy_index = 0
        self.driver = None
        self.wait = None
        self.action_chains = None
        
        # 反爬配置
        self.request_delay = (2, 5)  # 请求延时范围
        self.scroll_delay = (1, 3)   # 滚动延时范围
        self.max_retries = 3
        self.timeout = 20
        
        # 存储数据
        self.scraped_data = []
        
        self.init_driver()
    
    def init_driver(self):
        """初始化Chrome driver"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')  # 使用新的headless模式
        
        # 更强的反检测设置
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        
        # 更多反检测参数
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-field-trial-config')
        chrome_options.add_argument('--disable-back-forward-cache')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--disable-translate')
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('--mute-audio')
        
        # 设置更真实的User-Agent
        ua_string = self.get_realistic_user_agent()
        chrome_options.add_argument(f'--user-agent={ua_string}')
        
        # 设置窗口大小和位置
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--window-position=0,0')
        
        # 设置语言和地区
        chrome_options.add_argument('--lang=zh-CN')
        chrome_options.add_experimental_option('prefs', {
            'intl.accept_languages': 'zh-CN,zh,en-US,en',
            'profile.default_content_setting_values': {
                'notifications': 2,  # 禁用通知
                'images': 1,  # 加载图片
                'plugins': 1,
                'popups': 2,  # 禁用弹窗
                'geolocation': 2,  # 禁用地理位置
                'media_stream': 2,  # 禁用媒体流
            },
            'profile.managed_default_content_settings': {
                'images': 1
            }
        })
        
        # 代理设置
        if self.use_proxy and self.proxies:
            proxy = self.get_next_proxy()
            chrome_options.add_argument(f'--proxy-server={proxy}')
        
        try:
            # 使用webdriver-manager自动下载chromedriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 执行更完整的反检测脚本
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en-US', 'en']});
                Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})});
                delete navigator.__proto__.webdriver;
                
                // 模拟真实的浏览器环境
                window.chrome = {runtime: {}};
                Object.defineProperty(navigator, 'connection', {get: () => ({effectiveType: '4g'})});
                Object.defineProperty(screen, 'colorDepth', {get: () => 24});
                Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
                Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            """)
            
            # 设置真实的用户代理
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": ua_string,
                "acceptLanguage": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "platform": "Win32"
            })
            
            # 设置时区
            self.driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {
                'timezoneId': 'Asia/Shanghai'
            })
            
            # 禁用图片加载以提高速度（可选）
            # self.driver.execute_cdp_cmd('Network.setBlockedURLs', {'urls': ['*.jpg', '*.jpeg', '*.png', '*.gif']})
            
            self.wait = WebDriverWait(self.driver, self.timeout)
            self.action_chains = ActionChains(self.driver)
            
            logger.info("Chrome driver initialized successfully with enhanced anti-detection")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    def get_realistic_user_agent(self):
        """获取更真实的User-Agent"""
        realistic_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]
        return random.choice(realistic_agents)
    
    def get_next_proxy(self):
        """获取下一个代理"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy
    
    def load_proxies(self, proxy_file):
        """加载代理列表"""
        try:
            with open(proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f.readlines()]
            logger.info(f"Loaded {len(self.proxies)} proxies")
        except Exception as e:
            logger.error(f"Failed to load proxies: {e}")
    
    def simulate_human_behavior(self):
        """模拟人类行为"""
        # 随机移动鼠标
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            self.action_chains.move_to_element(body).perform()
            
            # 随机滚动
            scroll_distance = random.randint(100, 500)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
            
            # 随机等待
            time.sleep(random.uniform(*self.scroll_delay))
            
        except Exception as e:
            logger.warning(f"Error in simulate_human_behavior: {e}")
    
    def wait_for_page_load(self):
        """等待页面加载完成"""
        try:
            # 等待页面基本元素加载
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 等待JavaScript执行完成
            self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            
            # 额外等待确保动态内容加载
            time.sleep(random.uniform(2, 4))
            
        except TimeoutException:
            logger.warning("Page load timeout")
    
    def safe_find_element(self, by, value, timeout=10):
        """安全地查找元素"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return None
    
    def safe_find_elements(self, by, value, timeout=10):
        """安全地查找多个元素"""
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
            return elements
        except TimeoutException:
            logger.warning(f"Elements not found: {by}={value}")
            return []
    
    def scroll_to_load_more(self, max_scrolls=5):
        """滚动加载更多内容"""
        logger.info("Scrolling to load more content...")
        
        for i in range(max_scrolls):
            # 获取当前页面高度
            current_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # 模拟人类行为
            self.simulate_human_behavior()
            
            # 等待新内容加载
            time.sleep(random.uniform(3, 6))
            
            # 检查是否有新内容加载
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == current_height:
                logger.info("No more content to load")
                break
            
            # 检查是否有加载更多按钮
            load_more_selectors = [
                "//button[contains(text(), '加载更多')]",
                "//div[contains(text(), '加载更多')]",
                "//button[contains(@class, 'load-more')]",
                "//div[contains(@class, 'load-more')]"
            ]
            
            for selector in load_more_selectors:
                load_more_btn = self.safe_find_element(By.XPATH, selector, timeout=2)
                if load_more_btn:
                    try:
                        self.driver.execute_script("arguments[0].click();", load_more_btn)
                        time.sleep(random.uniform(2, 4))
                        break
                    except Exception as e:
                        logger.warning(f"Failed to click load more: {e}")
    
    def search_fund_content(self, keyword="今日基金"):
        """搜索基金内容"""
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}&source=web_explore_feed"
        
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                logger.info(f"Searching for: {keyword} (attempt {retry_count + 1})")
                
                # 访问搜索页面
                self.driver.get(search_url)
                self.wait_for_page_load()
                
                # 检查是否被重定向或需要登录
                if "login" in self.driver.current_url or "signin" in self.driver.current_url:
                    logger.warning("Redirected to login page")
                    self.handle_login_redirect()
                
                # 检查是否有验证码
                if self.detect_captcha():
                    logger.warning("Captcha detected")
                    self.handle_captcha()
                
                # 滚动加载更多内容
                self.scroll_to_load_more()
                
                # 解析搜索结果
                posts = self.parse_search_results()
                
                if posts:
                    logger.info(f"Found {len(posts)} posts for keyword: {keyword}")
                    return posts
                else:
                    logger.warning(f"No posts found for keyword: {keyword}")
                    retry_count += 1
                    time.sleep(random.uniform(5, 10))
                    
            except Exception as e:
                logger.error(f"Error searching for {keyword}: {e}")
                retry_count += 1
                time.sleep(random.uniform(5, 10))
                
                # 重新初始化driver
                if retry_count < self.max_retries:
                    self.restart_driver()
        
        logger.error(f"Failed to search for {keyword} after {self.max_retries} attempts")
        return []
    
    def detect_captcha(self):
        """检测验证码"""
        captcha_indicators = [
            "//div[contains(@class, 'captcha')]",
            "//img[contains(@src, 'captcha')]",
            "//div[contains(text(), '验证码')]",
            "//div[contains(text(), 'verification')]",
            "//div[contains(@class, 'verify')]",
            "//canvas[contains(@class, 'captcha')]",
            "//div[contains(@class, 'slider')]",
            "//div[contains(text(), '请完成安全验证')]",
            "//div[contains(text(), '滑动验证')]",
            "//div[contains(@class, 'challenge')]",
            "//div[contains(@id, 'captcha')]",
            "//iframe[contains(@src, 'captcha')]"
        ]
        
        for indicator in captcha_indicators:
            if self.safe_find_element(By.XPATH, indicator, timeout=2):
                return True
        
        # 检查页面标题
        page_title = self.driver.title.lower()
        if any(keyword in page_title for keyword in ['验证', 'verification', 'captcha', 'challenge']):
            return True
            
        return False
    
    def handle_captcha(self):
        """智能处理验证码"""
        logger.info("Detected captcha, attempting to handle...")
        
        # 尝试查找滑动验证码
        slider_selectors = [
            "//div[contains(@class, 'slider-button')]",
            "//div[contains(@class, 'slide-button')]",
            "//div[contains(@class, 'slider-track')]//div",
            "//span[contains(text(), '滑动')]/..",
            "//div[contains(@class, 'captcha-slider')]"
        ]
        
        for selector in slider_selectors:
            slider = self.safe_find_element(By.XPATH, selector, timeout=3)
            if slider:
                try:
                    logger.info("Found slider captcha, attempting to solve...")
                    self.solve_slider_captcha(slider)
                    time.sleep(2)
                    
                    # 检查是否解决成功
                    if not self.detect_captcha():
                        logger.info("Slider captcha solved successfully")
                        return True
                except Exception as e:
                    logger.warning(f"Failed to solve slider captcha: {e}")
        
        # 尝试刷新页面绕过验证码
        logger.info("Attempting to refresh page to bypass captcha...")
        try:
            self.driver.refresh()
            self.wait_for_page_load()
            
            if not self.detect_captcha():
                logger.info("Successfully bypassed captcha by refreshing")
                return True
        except Exception as e:
            logger.warning(f"Failed to refresh page: {e}")
        
        # 尝试返回上一页
        try:
            self.driver.back()
            time.sleep(3)
            
            if not self.detect_captcha():
                logger.info("Successfully bypassed captcha by going back")
                return True
        except Exception as e:
            logger.warning(f"Failed to go back: {e}")
        
        # 最后手动处理
        logger.warning("Automatic captcha solving failed, requiring manual intervention")
        if not self.headless:
            input("请手动处理验证码，完成后按回车继续...")
            return True
        else:
            logger.error("Running in headless mode, cannot handle captcha manually")
            return False
    
    def solve_slider_captcha(self, slider_element):
        """解决滑动验证码"""
        try:
            # 获取滑动轨道
            track = slider_element.find_element(By.XPATH, ".//ancestor::div[contains(@class, 'track') or contains(@class, 'slider')]")
            track_width = track.size['width']
            
            # 模拟人类滑动行为
            action = ActionChains(self.driver)
            action.click_and_hold(slider_element)
            
            # 分段滑动，模拟真实行为
            segments = random.randint(3, 6)
            segment_width = track_width // segments
            
            for i in range(segments):
                offset = segment_width + random.randint(-5, 5)
                action.move_by_offset(offset, random.randint(-2, 2))
                time.sleep(random.uniform(0.1, 0.3))
            
            # 最后一段确保滑到底
            remaining = track_width - (segments * segment_width)
            action.move_by_offset(remaining, 0)
            action.release()
            action.perform()
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error solving slider captcha: {e}")
            raise
    
    def handle_login_redirect(self):
        """智能处理登录重定向"""
        logger.info("Detected login redirect, attempting to handle...")
        
        # 尝试查找跳过登录的按钮
        skip_selectors = [
            "//button[contains(text(), '跳过')]",
            "//a[contains(text(), '跳过')]",
            "//div[contains(text(), '跳过')]",
            "//span[contains(text(), '跳过')]",
            "//button[contains(text(), '稍后')]",
            "//a[contains(text(), '稍后')]",
            "//div[contains(@class, 'close')]",
            "//button[contains(@class, 'close')]",
            "//span[contains(@class, 'close')]"
        ]
        
        for selector in skip_selectors:
            skip_btn = self.safe_find_element(By.XPATH, selector, timeout=2)
            if skip_btn:
                try:
                    skip_btn.click()
                    time.sleep(2)
                    logger.info("Successfully skipped login")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to click skip button: {e}")
        
        # 尝试直接访问目标页面
        try:
            logger.info("Attempting to navigate directly to search page...")
            current_keyword = getattr(self, 'current_keyword', '今日基金')
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={quote(current_keyword)}&source=web_explore_feed"
            self.driver.get(search_url)
            self.wait_for_page_load()
            
            if "login" not in self.driver.current_url.lower():
                logger.info("Successfully navigated to search page")
                return True
        except Exception as e:
            logger.warning(f"Failed to navigate directly: {e}")
        
        # 尝试清除cookies并重新访问
        try:
            logger.info("Clearing cookies and retrying...")
            self.driver.delete_all_cookies()
            time.sleep(2)
            
            current_keyword = getattr(self, 'current_keyword', '今日基金')
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={quote(current_keyword)}&source=web_explore_feed"
            self.driver.get(search_url)
            self.wait_for_page_load()
            
            if "login" not in self.driver.current_url.lower():
                logger.info("Successfully bypassed login after clearing cookies")
                return True
        except Exception as e:
            logger.warning(f"Failed to clear cookies: {e}")
        
        # 手动处理
        if not self.headless:
            logger.warning("Automatic login bypass failed, requiring manual intervention")
            input("请手动处理登录，完成后按回车继续...")
            return True
        else:
            logger.error("Running in headless mode, cannot handle login manually")
            return False
    
    def parse_search_results(self):
        """解析搜索结果"""
        posts = []
        
        # 更全面的小红书帖子选择器
        post_selectors = [
            # 新版小红书选择器
            "//div[contains(@class, 'note-item')]",
            "//div[contains(@class, 'note-card')]",
            "//section[contains(@class, 'note')]",
            "//div[contains(@data-testid, 'note')]",
            "//div[contains(@class, 'NoteCard')]",
            "//div[contains(@class, 'Card')]",
            # 搜索结果页面选择器
            "//div[contains(@class, 'search-result-item')]",
            "//div[contains(@class, 'result-item')]",
            "//div[contains(@class, 'feeds-page')]//div[contains(@class, 'note')]",
            # 通用选择器
            "//a[contains(@href, '/explore/')]/..",
            "//a[contains(@href, '/discovery/')]/..",
            # 更精确的覆盖元素选择器
            "//a[contains(@class, 'cover')]/..",
            "//div[contains(@class, 'cover')]/..",
            # Flex布局相关
            "//div[contains(@class, 'flex') and contains(@class, 'note')]",
            "//div[contains(@class, 'grid-item')]",
            # 备用选择器
            "//article",
            "//div[@role='article']",
            "//div[contains(@class, 'item') and .//img]"
        ]
        
        post_elements = []
        successful_selector = None
        
        # 尝试不同的选择器策略
        for selector in post_selectors:
            try:
                elements = self.safe_find_elements(By.XPATH, selector, timeout=8)
                if elements and len(elements) >= 3:  # 至少找到3个元素才认为成功
                    post_elements = elements
                    successful_selector = selector
                    logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    break
                elif elements:
                    logger.info(f"Found only {len(elements)} elements with selector: {selector}")
            except Exception as e:
                logger.warning(f"Selector failed: {selector}, error: {e}")
                continue
        
        # 如果主要选择器都失败，尝试更通用的方法
        if not post_elements:
            logger.warning("Primary selectors failed, trying fallback methods")
            
            # 尝试通过图片元素反向查找
            img_elements = self.safe_find_elements(By.XPATH, "//img[contains(@src, 'sns-webpic')]", timeout=5)
            if img_elements:
                for img in img_elements[:20]:
                    try:
                        # 向上查找包含帖子信息的父元素
                        parent = img.find_element(By.XPATH, "./ancestor::div[contains(@class, 'note') or contains(@class, 'card') or contains(@class, 'item')][1]")
                        if parent:
                            post_elements.append(parent)
                    except:
                        continue
                
                if post_elements:
                    logger.info(f"Found {len(post_elements)} elements using image fallback method")
        
        if not post_elements:
            # 最后的尝试：查找所有可能的帖子容器
            container_selectors = [
                "//div[.//img and .//span[text()]]",
                "//div[contains(@class, 'item') and .//a[@href]]",
                "//div[@data-notecard or @data-note-id]"
            ]
            
            for selector in container_selectors:
                elements = self.safe_find_elements(By.XPATH, selector, timeout=3)
                if elements:
                    post_elements = elements
                    logger.info(f"Found {len(elements)} elements with fallback selector: {selector}")
                    break
        
        if not post_elements:
            logger.error("No post elements found with any selector")
            # 保存页面源码用于调试
            try:
                with open("debug_page_source.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                logger.info("Page source saved to debug_page_source.html for analysis")
            except:
                pass
            return posts
        
        logger.info(f"Successfully found {len(post_elements)} post elements")
        
        # 限制处理数量，避免过载
        max_posts = min(len(post_elements), 30)
        
        for i, element in enumerate(post_elements[:max_posts]):
            try:
                post_data = self.extract_post_data(element)
                if post_data and self.is_valid_post(post_data):
                    posts.append(post_data)
                    logger.info(f"Extracted post {i+1}: {post_data['title'][:50]}...")
                
                # 模拟人类行为
                if i % 5 == 0:
                    self.simulate_human_behavior()
                    
            except Exception as e:
                logger.error(f"Error extracting post {i+1}: {e}")
                continue
        
        return posts
    
    def is_valid_post(self, post_data):
        """验证帖子数据的有效性"""
        if not post_data:
            return False
        
        # 检查基本字段
        title = post_data.get('title', '').strip()
        description = post_data.get('description', '').strip()
        
        # 标题不能为空或默认值
        if not title or title == "未知标题" or len(title) < 3:
            return False
        
        # 过滤明显的广告或无关内容
        spam_keywords = ['广告', '推广', '微信', 'QQ', '加我', '联系我', '代理', '招商']
        for keyword in spam_keywords:
            if keyword in title or keyword in description:
                return False
        
        # 检查是否包含基金相关关键词
        fund_keywords = ['基金', '投资', '理财', '收益', '净值', '定投', '股票', '债券', '货币', 'ETF']
        has_fund_keyword = any(keyword in title or keyword in description for keyword in fund_keywords)
        
        return has_fund_keyword
    
    def extract_post_data(self, element):
        """提取单个帖子数据"""
        try:
            # 标题
            title_selectors = [
                ".//span[contains(@class, 'title')]",
                ".//a[contains(@class, 'title')]",
                ".//div[contains(@class, 'title')]",
                ".//h1", ".//h2", ".//h3",
                ".//span[contains(@class, 'desc')]",
                ".//div[contains(@class, 'content')]",
                ".//p[contains(@class, 'title')]"
            ]
            
            title = "未知标题"
            for selector in title_selectors:
                title_elem = self.safe_find_element_in_element(element, By.XPATH, selector)
                if title_elem:
                    title_text = title_elem.text.strip()
                    if title_text and len(title_text) > 3:
                        title = title_text
                        break
            
            # 作者
            author_selectors = [
                ".//span[contains(@class, 'author')]",
                ".//a[contains(@class, 'author')]",
                ".//div[contains(@class, 'user')]",
                ".//span[contains(@class, 'username')]",
                ".//div[contains(@class, 'name')]"
            ]
            
            author = "未知作者"
            for selector in author_selectors:
                author_elem = self.safe_find_element_in_element(element, By.XPATH, selector)
                if author_elem:
                    author_text = author_elem.text.strip()
                    if author_text:
                        author = author_text
                        break
            
            # 链接
            link_selectors = [
                ".//a[@href]",
                ".//div[@data-href]",
                ".//span[@data-href]"
            ]
            
            link = ""
            for selector in link_selectors:
                link_elem = self.safe_find_element_in_element(element, By.XPATH, selector)
                if link_elem:
                    href = link_elem.get_attribute("href") or link_elem.get_attribute("data-href")
                    if href:
                        link = href if href.startswith("http") else urljoin("https://www.xiaohongshu.com", href)
                        break
            
            # 点赞数
            like_selectors = [
                ".//span[contains(@class, 'like')]",
                ".//div[contains(@class, 'like')]",
                ".//span[contains(@class, 'count')]",
                ".//div[contains(@class, 'interact')]//span",
                ".//span[contains(@class, 'num')]"
            ]
            
            likes = "0"
            for selector in like_selectors:
                like_elem = self.safe_find_element_in_element(element, By.XPATH, selector)
                if like_elem:
                    likes_text = like_elem.text.strip()
                    if likes_text and any(char.isdigit() for char in likes_text):
                        likes = likes_text
                        break
            
            # 描述
            desc_selectors = [
                ".//div[contains(@class, 'desc')]",
                ".//p[contains(@class, 'desc')]",
                ".//span[contains(@class, 'content')]",
                ".//div[contains(@class, 'text')]",
                ".//p[contains(@class, 'content')]"
            ]
            
            description = ""
            for selector in desc_selectors:
                desc_elem = self.safe_find_element_in_element(element, By.XPATH, selector)
                if desc_elem:
                    desc_text = desc_elem.text.strip()
                    if desc_text and len(desc_text) > 5:
                        description = desc_text
                        break
            
            # 如果没有单独的描述，使用标题
            if not description and title != "未知标题":
                description = title
            
            return {
                'title': title,
                'author': author,
                'link': link,
                'likes': likes,
                'description': description,
                'scraped_time': datetime.now().isoformat(),
                'keyword': getattr(self, 'current_keyword', '')
            }
            
        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
            return None
    
    def safe_find_element_in_element(self, parent_element, by, value):
        """在父元素中安全查找子元素"""
        try:
            return parent_element.find_element(by, value)
        except:
            return None
    
    def restart_driver(self):
        """重启driver"""
        logger.info("Restarting driver...")
        
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
        
        time.sleep(random.uniform(3, 6))
        self.init_driver()
    
    def scrape_multiple_keywords(self, keywords=None, max_posts_per_keyword=50):
        """爬取多个关键词"""
        if keywords is None:
            keywords = ["今日基金", "基金知识", "基金投资", "基金入门", "基金理财"]
        
        all_posts = []
        
        for keyword in keywords:
            logger.info(f"Processing keyword: {keyword}")
            self.current_keyword = keyword
            
            try:
                posts = self.search_fund_content(keyword)
                
                # 限制每个关键词的帖子数量
                if len(posts) > max_posts_per_keyword:
                    posts = posts[:max_posts_per_keyword]
                
                all_posts.extend(posts)
                
                # 关键词间延时
                time.sleep(random.uniform(10, 20))
                
            except Exception as e:
                logger.error(f"Error processing keyword {keyword}: {e}")
                continue
        
        # 去重
        unique_posts = self.remove_duplicates(all_posts)
        
        return unique_posts
    
    def remove_duplicates(self, posts):
        """去重"""
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
        
        return unique_posts
    
    def save_to_csv(self, posts, filename="fund_posts_enhanced.csv"):
        """保存到CSV"""
        if not posts:
            logger.warning("No posts to save")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'author', 'link', 'likes', 'description', 'keyword', 'scraped_time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for post in posts:
                writer.writerow(post)
        
        logger.info(f"Saved {len(posts)} posts to {filename}")
    
    def save_to_json(self, posts, filename="fund_posts_enhanced.json"):
        """保存到JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(posts)} posts to {filename}")
    
    def close(self):
        """关闭driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver closed")

def main():
    scraper = None
    
    try:
        # 初始化爬虫
        scraper = XiaohongshiFundScraper(
            use_proxy=False,  # 如果有代理列表，设置为True
            headless=False    # 设置为True可以无头模式运行
        )
        
        # 如果有代理文件，取消注释下面这行
        # scraper.load_proxies('proxies.txt')
        
        logger.info("Starting fund content scraping...")
        
        # 爬取基金相关内容
        posts = scraper.scrape_multiple_keywords(
            keywords=["今日基金", "基金知识", "基金投资", "基金理财"],
            max_posts_per_keyword=30
        )
        
        if posts:
            logger.info(f"Successfully scraped {len(posts)} posts")
            
            # 保存数据
            scraper.save_to_csv(posts)
            scraper.save_to_json(posts)
            
            # 显示统计信息
            keywords_count = {}
            for post in posts:
                keyword = post.get('keyword', 'unknown')
                keywords_count[keyword] = keywords_count.get(keyword, 0) + 1
            
            print("\n=== 爬取统计 ===")
            print(f"总帖子数: {len(posts)}")
            print("各关键词分布:")
            for keyword, count in keywords_count.items():
                print(f"  {keyword}: {count}篇")
            
            # 显示示例帖子
            print("\n=== 示例帖子 ===")
            for i, post in enumerate(posts[:5], 1):
                print(f"{i}. {post['title']}")
                print(f"   作者: {post['author']}")
                print(f"   点赞: {post['likes']}")
                print(f"   关键词: {post['keyword']}")
                print(f"   描述: {post['description'][:100]}...")
                print(f"   链接: {post['link']}")
                print()
        
        else:
            logger.warning("No posts were scraped")
    
    except Exception as e:
        logger.error(f"Main execution error: {e}")
    
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    main()