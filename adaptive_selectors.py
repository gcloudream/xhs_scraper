"""
Adaptive selector system for handling dynamic web elements
自适应选择器系统，应对动态网页元素变化
"""
import time
import random
import json
import re
from typing import List, Dict, Optional, Tuple, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class SelectorCandidate:
    """选择器候选项"""
    selector: str
    by_type: str  # 'xpath', 'css', 'class', 'id'
    priority: int  # 优先级，数字越小优先级越高
    success_rate: float = 0.0  # 成功率
    last_used: float = 0.0  # 最后使用时间
    element_count: int = 0  # 元素数量
    
    def calculate_score(self) -> float:
        """计算选择器得分"""
        # 基础得分：优先级倒数
        base_score = 1.0 / (self.priority + 1)
        
        # 成功率权重
        success_weight = self.success_rate * 0.8
        
        # 时间衰减（最近使用的得分更高）
        time_decay = max(0.1, 1.0 - (time.time() - self.last_used) / 3600)  # 1小时衰减
        
        # 元素数量权重（有元素但不要太多）
        count_weight = 0.5 if self.element_count > 0 else 0.0
        if self.element_count > 20:  # 元素太多可能不准确
            count_weight *= 0.5
        
        return base_score + success_weight + time_decay * 0.2 + count_weight * 0.3


class AdaptiveSelectorManager:
    """自适应选择器管理器"""
    
    def __init__(self, cache_file: str = "selector_cache.json"):
        self.cache_file = Path(cache_file)
        self.selector_cache = self._load_cache()
        
        # 小红书帖子选择器库
        self.post_selectors = [
            # 最新的选择器（更高优先级）
            SelectorCandidate("//div[@data-notecard]", "xpath", 1),
            SelectorCandidate("//div[contains(@class, 'note-item') and .//img]", "xpath", 2),
            SelectorCandidate("//section[contains(@class, 'note') and @data-note-id]", "xpath", 3),
            SelectorCandidate("//div[contains(@class, 'NoteCard')]", "xpath", 4),
            SelectorCandidate("//div[contains(@class, 'search-result-item')]", "xpath", 5),
            
            # 通用选择器
            SelectorCandidate("//a[contains(@href, '/explore/')]/..", "xpath", 6),
            SelectorCandidate("//div[contains(@class, 'feeds-page')]//div[contains(@class, 'note')]", "xpath", 7),
            SelectorCandidate("//div[contains(@class, 'grid-item') and .//img]", "xpath", 8),
            
            # 备用选择器
            SelectorCandidate("//article", "xpath", 9),
            SelectorCandidate("//div[@role='article']", "xpath", 10),
            SelectorCandidate("//div[contains(@class, 'item') and .//img and .//span[text()]]", "xpath", 11),
            
            # CSS选择器
            SelectorCandidate("div[data-notecard]", "css", 12),
            SelectorCandidate("div.note-item", "css", 13),
            SelectorCandidate("section.note", "css", 14),
        ]
        
        # 标题选择器库
        self.title_selectors = [
            SelectorCandidate(".//span[contains(@class, 'title')]", "xpath", 1),
            SelectorCandidate(".//a[contains(@class, 'title')]", "xpath", 2),
            SelectorCandidate(".//div[contains(@class, 'title')]", "xpath", 3),
            SelectorCandidate(".//h1 | .//h2 | .//h3", "xpath", 4),
            SelectorCandidate(".//span[contains(@class, 'desc')]", "xpath", 5),
            SelectorCandidate(".//div[contains(@class, 'content')]", "xpath", 6),
            SelectorCandidate(".//p[contains(@class, 'title')]", "xpath", 7),
            SelectorCandidate(".//div[contains(@class, 'text')]//span[string-length(text()) > 5]", "xpath", 8),
            SelectorCandidate(".//a[@href]//span[string-length(text()) > 5]", "xpath", 9),
        ]
        
        # 作者选择器库
        self.author_selectors = [
            SelectorCandidate(".//span[contains(@class, 'author')]", "xpath", 1),
            SelectorCandidate(".//a[contains(@class, 'author')]", "xpath", 2),
            SelectorCandidate(".//div[contains(@class, 'user')]", "xpath", 3),
            SelectorCandidate(".//span[contains(@class, 'username')]", "xpath", 4),
            SelectorCandidate(".//div[contains(@class, 'name')]", "xpath", 5),
            SelectorCandidate(".//div[contains(@class, 'avatar')]/..//span[text()]", "xpath", 6),
            SelectorCandidate(".//img[contains(@alt, '头像')]/..//span[text()]", "xpath", 7),
        ]
        
        # 链接选择器库
        self.link_selectors = [
            SelectorCandidate(".//a[@href and contains(@href, '/explore/')]", "xpath", 1),
            SelectorCandidate(".//a[@href and contains(@href, '/discovery/')]", "xpath", 2),
            SelectorCandidate(".//a[@href]", "xpath", 3),
            SelectorCandidate(".//div[@data-href]", "xpath", 4),
            SelectorCandidate(".//span[@data-href]", "xpath", 5),
        ]
    
    def _load_cache(self) -> Dict:
        """加载选择器缓存"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    logger.info(f"加载了 {len(cache_data)} 个缓存选择器")
                    return cache_data
            except Exception as e:
                logger.warning(f"加载选择器缓存失败: {e}")
        return {}
    
    def _save_cache(self):
        """保存选择器缓存"""
        try:
            cache_data = {}
            for selector_type, selectors in [
                ('post', self.post_selectors),
                ('title', self.title_selectors),
                ('author', self.author_selectors),
                ('link', self.link_selectors)
            ]:
                cache_data[selector_type] = [
                    {
                        'selector': s.selector,
                        'by_type': s.by_type,
                        'priority': s.priority,
                        'success_rate': s.success_rate,
                        'last_used': s.last_used,
                        'element_count': s.element_count
                    }
                    for s in selectors
                ]
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info("选择器缓存已保存")
        except Exception as e:
            logger.error(f"保存选择器缓存失败: {e}")
    
    def find_elements_adaptive(self, driver, selector_type: str, timeout: int = 10) -> List[Any]:
        """自适应查找元素"""
        selector_lists = {
            'post': self.post_selectors,
            'title': self.title_selectors,
            'author': self.author_selectors,
            'link': self.link_selectors
        }
        
        if selector_type not in selector_lists:
            raise ValueError(f"不支持的选择器类型: {selector_type}")
        
        selectors = selector_lists[selector_type]
        
        # 按得分排序选择器
        sorted_selectors = sorted(selectors, key=lambda s: s.calculate_score(), reverse=True)
        
        logger.info(f"尝试查找 {selector_type} 元素，共 {len(sorted_selectors)} 个选择器")
        
        for i, selector_candidate in enumerate(sorted_selectors):
            try:
                logger.debug(f"尝试选择器 {i+1}/{len(sorted_selectors)}: {selector_candidate.selector[:50]}...")
                
                by_type_map = {
                    'xpath': By.XPATH,
                    'css': By.CSS_SELECTOR,
                    'class': By.CLASS_NAME,
                    'id': By.ID
                }
                
                by_type = by_type_map.get(selector_candidate.by_type, By.XPATH)
                
                # 尝试查找元素
                wait = WebDriverWait(driver, min(timeout, 5))  # 每个选择器最多等待5秒
                elements = wait.until(EC.presence_of_all_elements_located((by_type, selector_candidate.selector)))
                
                if elements:
                    # 过滤可见元素
                    visible_elements = [elem for elem in elements if self._is_element_visible(elem)]
                    
                    if visible_elements:
                        # 更新选择器统计
                        selector_candidate.success_rate = min(1.0, selector_candidate.success_rate + 0.1)
                        selector_candidate.last_used = time.time()
                        selector_candidate.element_count = len(visible_elements)
                        
                        logger.info(f"找到 {len(visible_elements)} 个 {selector_type} 元素 (选择器: {selector_candidate.selector[:50]}...)")
                        self._save_cache()
                        return visible_elements
                
            except TimeoutException:
                # 更新失败率
                selector_candidate.success_rate = max(0.0, selector_candidate.success_rate - 0.05)
                logger.debug(f"选择器超时: {selector_candidate.selector[:50]}...")
                continue
            except Exception as e:
                selector_candidate.success_rate = max(0.0, selector_candidate.success_rate - 0.1)
                logger.debug(f"选择器错误: {selector_candidate.selector[:50]}... - {e}")
                continue
        
        logger.warning(f"所有 {selector_type} 选择器都失败了")
        return []
    
    def find_element_in_parent_adaptive(self, parent_element, selector_type: str) -> Optional[Any]:
        """在父元素中自适应查找子元素"""
        selector_lists = {
            'title': self.title_selectors,
            'author': self.author_selectors,
            'link': self.link_selectors
        }
        
        if selector_type not in selector_lists:
            return None
        
        selectors = selector_lists[selector_type]
        sorted_selectors = sorted(selectors, key=lambda s: s.calculate_score(), reverse=True)
        
        for selector_candidate in sorted_selectors[:5]:  # 只尝试前5个最佳选择器
            try:
                by_type_map = {
                    'xpath': By.XPATH,
                    'css': By.CSS_SELECTOR,
                    'class': By.CLASS_NAME,
                    'id': By.ID
                }
                
                by_type = by_type_map.get(selector_candidate.by_type, By.XPATH)
                element = parent_element.find_element(by_type, selector_candidate.selector)
                
                if element and self._is_element_visible(element):
                    # 更新统计
                    selector_candidate.success_rate = min(1.0, selector_candidate.success_rate + 0.05)
                    selector_candidate.last_used = time.time()
                    return element
                    
            except (NoSuchElementException, Exception):
                selector_candidate.success_rate = max(0.0, selector_candidate.success_rate - 0.02)
                continue
        
        return None
    
    def _is_element_visible(self, element) -> bool:
        """检查元素是否可见"""
        try:
            return element.is_displayed() and element.size['height'] > 0 and element.size['width'] > 0
        except:
            return False
    
    def discover_new_selectors(self, driver, selector_type: str) -> List[str]:
        """发现新的选择器"""
        logger.info(f"开始发现新的 {selector_type} 选择器...")
        
        discovered_selectors = []
        
        # 基于页面结构分析的选择器发现
        try:
            # 获取页面源码进行分析
            page_source = driver.page_source
            
            if selector_type == 'post':
                # 分析帖子容器的模式
                patterns = [
                    r'class="([^"]*note[^"]*)"',
                    r'class="([^"]*card[^"]*)"',
                    r'class="([^"]*item[^"]*)"',
                    r'data-([^=]*note[^=]*)=',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    for match in matches[:3]:  # 只取前3个
                        if isinstance(match, str) and len(match) > 3:
                            new_selector = f"//div[contains(@class, '{match}')]"
                            if new_selector not in [s.selector for s in self.post_selectors]:
                                discovered_selectors.append(new_selector)
            
            elif selector_type == 'title':
                # 分析标题元素的模式
                patterns = [
                    r'class="([^"]*title[^"]*)"',
                    r'class="([^"]*desc[^"]*)"',
                    r'class="([^"]*content[^"]*)"',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    for match in matches[:3]:
                        if isinstance(match, str) and len(match) > 3:
                            new_selector = f".//span[contains(@class, '{match}')]"
                            if new_selector not in [s.selector for s in self.title_selectors]:
                                discovered_selectors.append(new_selector)
            
            # 添加发现的选择器到候选列表
            for selector in discovered_selectors[:5]:  # 最多添加5个
                new_candidate = SelectorCandidate(
                    selector=selector,
                    by_type="xpath",
                    priority=len(self.post_selectors) + 1,  # 给新选择器较低的优先级
                    success_rate=0.5  # 初始成功率
                )
                
                if selector_type == 'post':
                    self.post_selectors.append(new_candidate)
                elif selector_type == 'title':
                    self.title_selectors.append(new_candidate)
                
                logger.info(f"发现新选择器: {selector}")
        
        except Exception as e:
            logger.error(f"发现新选择器时出错: {e}")
        
        return discovered_selectors
    
    def optimize_selectors(self):
        """优化选择器库"""
        logger.info("开始优化选择器库...")
        
        for selector_type, selectors in [
            ('post', self.post_selectors),
            ('title', self.title_selectors),
            ('author', self.author_selectors),
            ('link', self.link_selectors)
        ]:
            # 移除表现很差的选择器
            original_count = len(selectors)
            selectors[:] = [s for s in selectors if s.success_rate > 0.1 or s.priority <= 5]
            
            # 按成功率重新排序
            selectors.sort(key=lambda s: s.calculate_score(), reverse=True)
            
            # 更新优先级
            for i, selector in enumerate(selectors):
                selector.priority = i + 1
            
            removed_count = original_count - len(selectors)
            if removed_count > 0:
                logger.info(f"移除了 {removed_count} 个表现不佳的 {selector_type} 选择器")
        
        self._save_cache()
    
    def get_selector_stats(self) -> Dict:
        """获取选择器统计信息"""
        stats = {}
        
        for selector_type, selectors in [
            ('post', self.post_selectors),
            ('title', self.title_selectors),
            ('author', self.author_selectors),
            ('link', self.link_selectors)
        ]:
            total_selectors = len(selectors)
            active_selectors = len([s for s in selectors if s.success_rate > 0.1])
            avg_success_rate = sum(s.success_rate for s in selectors) / total_selectors if total_selectors > 0 else 0
            
            stats[selector_type] = {
                'total': total_selectors,
                'active': active_selectors,
                'avg_success_rate': avg_success_rate
            }
        
        return stats


class SmartElementExtractor:
    """智能元素提取器"""
    
    def __init__(self, driver):
        self.driver = driver
        self.selector_manager = AdaptiveSelectorManager()
    
    def extract_post_data_smart(self, post_element) -> Optional[Dict]:
        """智能提取帖子数据"""
        try:
            post_data = {}
            
            # 提取标题
            title_element = self.selector_manager.find_element_in_parent_adaptive(post_element, 'title')
            if title_element:
                title_text = self._extract_text_smart(title_element)
                post_data['title'] = title_text if title_text and len(title_text) > 3 else "未知标题"
            else:
                post_data['title'] = "未知标题"
            
            # 提取作者
            author_element = self.selector_manager.find_element_in_parent_adaptive(post_element, 'author')
            if author_element:
                author_text = self._extract_text_smart(author_element)
                post_data['author'] = author_text if author_text else "未知作者"
            else:
                post_data['author'] = "未知作者"
            
            # 提取链接
            link_element = self.selector_manager.find_element_in_parent_adaptive(post_element, 'link')
            if link_element:
                href = link_element.get_attribute("href") or link_element.get_attribute("data-href")
                if href:
                    post_data['link'] = href if href.startswith("http") else f"https://www.xiaohongshu.com{href}"
                else:
                    post_data['link'] = ""
            else:
                post_data['link'] = ""
            
            # 提取其他信息
            post_data['likes'] = self._extract_likes_smart(post_element)
            post_data['description'] = self._extract_description_smart(post_element, post_data['title'])
            
            return post_data
            
        except Exception as e:
            logger.error(f"智能提取帖子数据时出错: {e}")
            return None
    
    def _extract_text_smart(self, element) -> str:
        """智能提取文本"""
        try:
            # 尝试不同的文本提取方法
            text_candidates = [
                element.text,
                element.get_attribute("textContent"),
                element.get_attribute("innerText"),
                element.get_attribute("title"),
                element.get_attribute("alt"),
            ]
            
            for text in text_candidates:
                if text and text.strip() and len(text.strip()) > 2:
                    return text.strip()
            
            return ""
            
        except Exception:
            return ""
    
    def _extract_likes_smart(self, post_element) -> str:
        """智能提取点赞数"""
        like_patterns = [
            ".//span[contains(@class, 'like')]",
            ".//div[contains(@class, 'like')]",
            ".//span[contains(@class, 'count')]",
            ".//div[contains(@class, 'interact')]//span[contains(text(), '')]",
            ".//span[matches(text(), '[0-9]+')]",
        ]
        
        for pattern in like_patterns:
            try:
                like_element = post_element.find_element(By.XPATH, pattern)
                like_text = self._extract_text_smart(like_element)
                
                # 检查是否包含数字
                if like_text and any(char.isdigit() for char in like_text):
                    return like_text
            except:
                continue
        
        return "0"
    
    def _extract_description_smart(self, post_element, title: str) -> str:
        """智能提取描述"""
        desc_patterns = [
            ".//div[contains(@class, 'desc')]",
            ".//p[contains(@class, 'desc')]",
            ".//span[contains(@class, 'content')]",
            ".//div[contains(@class, 'text')]",
            ".//p[contains(@class, 'content')]",
        ]
        
        for pattern in desc_patterns:
            try:
                desc_element = post_element.find_element(By.XPATH, pattern)
                desc_text = self._extract_text_smart(desc_element)
                
                if desc_text and len(desc_text) > 5 and desc_text != title:
                    return desc_text
            except:
                continue
        
        # 如果没有找到描述，使用标题
        return title if title != "未知标题" else ""