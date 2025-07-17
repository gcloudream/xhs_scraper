"""
Session and cookie management for enhanced anti-detection
会话和Cookie管理模块，增强反检测能力
"""
import json
import time
import random
import pickle
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

logger = logging.getLogger(__name__)


class CookieManager:
    """Cookie管理器"""
    
    def __init__(self, cookie_dir: str = "cookies"):
        self.cookie_dir = Path(cookie_dir)
        self.cookie_dir.mkdir(exist_ok=True)
        self.current_session = None
        
        # Cookie池
        self.cookie_pools = {
            'xiaohongshu': [],
            'backup': []
        }
        
        self._load_cookie_pools()
    
    def _load_cookie_pools(self):
        """加载Cookie池"""
        try:
            cookie_files = list(self.cookie_dir.glob("session_*.json"))
            
            for cookie_file in cookie_files:
                try:
                    with open(cookie_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    # 检查Cookie是否还有效
                    if self._is_session_valid(session_data):
                        self.cookie_pools['xiaohongshu'].append(session_data)
                    else:
                        # 移动到备用池
                        self.cookie_pools['backup'].append(session_data)
                        
                except Exception as e:
                    logger.warning(f"加载Cookie文件失败 {cookie_file}: {e}")
            
            logger.info(f"加载了 {len(self.cookie_pools['xiaohongshu'])} 个有效会话")
            
        except Exception as e:
            logger.error(f"加载Cookie池失败: {e}")
    
    def _is_session_valid(self, session_data: Dict) -> bool:
        """检查会话是否有效"""
        try:
            # 检查时间戳
            created_time = session_data.get('created_time', 0)
            if time.time() - created_time > 86400 * 7:  # 7天过期
                return False
            
            # 检查必要的Cookie
            cookies = session_data.get('cookies', [])
            required_cookies = ['sessionid', 'csrf_token', 'user_id']
            
            cookie_names = [cookie.get('name', '') for cookie in cookies]
            has_required = any(req in ' '.join(cookie_names) for req in required_cookies)
            
            return has_required and len(cookies) > 5
            
        except Exception:
            return False
    
    def get_random_session(self) -> Optional[Dict]:
        """获取随机会话"""
        if not self.cookie_pools['xiaohongshu']:
            logger.warning("没有可用的会话")
            return None
        
        # 优先选择最近成功的会话
        valid_sessions = [s for s in self.cookie_pools['xiaohongshu'] if s.get('success_count', 0) > 0]
        
        if valid_sessions:
            session = random.choice(valid_sessions)
        else:
            session = random.choice(self.cookie_pools['xiaohongshu'])
        
        logger.info(f"选择会话: {session.get('session_id', 'unknown')}")
        return session
    
    def save_session(self, driver, session_id: str = None) -> str:
        """保存当前会话"""
        if not session_id:
            session_id = f"session_{int(time.time())}_{random.randint(1000, 9999)}"
        
        try:
            # 获取当前Cookie
            cookies = driver.get_cookies()
            
            # 获取用户代理
            user_agent = driver.execute_script("return navigator.userAgent;")
            
            # 获取其他浏览器信息
            browser_info = self._get_browser_info(driver)
            
            session_data = {
                'session_id': session_id,
                'cookies': cookies,
                'user_agent': user_agent,
                'browser_info': browser_info,
                'created_time': time.time(),
                'last_used': time.time(),
                'success_count': 0,
                'failure_count': 0,
                'domain': 'xiaohongshu.com'
            }
            
            # 保存到文件
            session_file = self.cookie_dir / f"{session_id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            # 添加到池中
            self.cookie_pools['xiaohongshu'].append(session_data)
            self.current_session = session_data
            
            logger.info(f"会话已保存: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"保存会话失败: {e}")
            return ""
    
    def load_session(self, driver, session_data: Dict) -> bool:
        """加载会话到浏览器"""
        try:
            # 先访问目标网站
            driver.get("https://www.xiaohongshu.com")
            time.sleep(2)
            
            # 清除现有Cookie
            driver.delete_all_cookies()
            
            # 添加保存的Cookie
            cookies = session_data.get('cookies', [])
            for cookie in cookies:
                try:
                    # 清理Cookie数据
                    clean_cookie = {
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie.get('domain', '.xiaohongshu.com'),
                        'path': cookie.get('path', '/'),
                    }
                    
                    # 添加可选字段
                    if 'expiry' in cookie:
                        clean_cookie['expiry'] = cookie['expiry']
                    if 'secure' in cookie:
                        clean_cookie['secure'] = cookie['secure']
                    if 'httpOnly' in cookie:
                        clean_cookie['httpOnly'] = cookie['httpOnly']
                    
                    driver.add_cookie(clean_cookie)
                    
                except Exception as e:
                    logger.debug(f"添加Cookie失败: {cookie.get('name', 'unknown')} - {e}")
                    continue
            
            # 刷新页面使Cookie生效
            driver.refresh()
            time.sleep(3)
            
            # 更新会话状态
            session_data['last_used'] = time.time()
            self.current_session = session_data
            
            logger.info(f"会话加载成功: {session_data.get('session_id', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"加载会话失败: {e}")
            return False
    
    def _get_browser_info(self, driver) -> Dict:
        """获取浏览器信息"""
        try:
            info = driver.execute_script("""
                return {
                    platform: navigator.platform,
                    language: navigator.language,
                    languages: navigator.languages,
                    cookieEnabled: navigator.cookieEnabled,
                    onLine: navigator.onLine,
                    hardwareConcurrency: navigator.hardwareConcurrency,
                    deviceMemory: navigator.deviceMemory || 'unknown',
                    screen: {
                        width: screen.width,
                        height: screen.height,
                        colorDepth: screen.colorDepth
                    },
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
                };
            """)
            return info
        except Exception:
            return {}
    
    def update_session_success(self, success: bool):
        """更新会话成功/失败计数"""
        if self.current_session:
            if success:
                self.current_session['success_count'] = self.current_session.get('success_count', 0) + 1
            else:
                self.current_session['failure_count'] = self.current_session.get('failure_count', 0) + 1
            
            self.current_session['last_used'] = time.time()
            
            # 如果失败次数太多，移动到备用池
            if self.current_session['failure_count'] > 5:
                if self.current_session in self.cookie_pools['xiaohongshu']:
                    self.cookie_pools['xiaohongshu'].remove(self.current_session)
                    self.cookie_pools['backup'].append(self.current_session)
                    logger.warning(f"会话 {self.current_session['session_id']} 失败次数过多，移至备用池")
    
    def cleanup_expired_sessions(self):
        """清理过期会话"""
        current_time = time.time()
        
        for pool_name, sessions in self.cookie_pools.items():
            original_count = len(sessions)
            
            # 移除过期会话
            sessions[:] = [s for s in sessions if current_time - s.get('created_time', 0) < 86400 * 7]
            
            removed_count = original_count - len(sessions)
            if removed_count > 0:
                logger.info(f"从 {pool_name} 池中移除了 {removed_count} 个过期会话")
        
        # 删除过期的会话文件
        try:
            for session_file in self.cookie_dir.glob("session_*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    if current_time - session_data.get('created_time', 0) > 86400 * 7:
                        session_file.unlink()
                        logger.debug(f"删除过期会话文件: {session_file}")
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"清理会话文件失败: {e}")


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.cookie_manager = CookieManager()
        self.current_session_id = None
        self.session_start_time = None
        self.request_count = 0
        self.error_count = 0
        self.last_activity_time = None
        
        # 会话轮换策略
        self.max_requests_per_session = random.randint(50, 100)
        self.max_session_duration = random.randint(1800, 3600)  # 30-60分钟
        self.max_errors_per_session = 5
    
    def start_session(self, driver) -> bool:
        """开始新会话"""
        logger.info("开始新的爬取会话...")
        
        # 尝试加载现有会话
        session_data = self.cookie_manager.get_random_session()
        
        if session_data:
            if self.cookie_manager.load_session(driver, session_data):
                self.current_session_id = session_data['session_id']
                logger.info(f"使用现有会话: {self.current_session_id}")
            else:
                # 加载失败，创建新会话
                self.current_session_id = self._create_new_session(driver)
        else:
            # 没有可用会话，创建新的
            self.current_session_id = self._create_new_session(driver)
        
        self.session_start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.last_activity_time = time.time()
        
        return bool(self.current_session_id)
    
    def _create_new_session(self, driver) -> str:
        """创建新会话"""
        logger.info("创建新的爬取会话...")
        
        try:
            # 访问主页建立基础会话
            driver.get("https://www.xiaohongshu.com")
            time.sleep(random.uniform(3, 6))
            
            # 模拟一些基础浏览行为
            self._simulate_initial_browsing(driver)
            
            # 保存会话
            session_id = self.cookie_manager.save_session(driver)
            
            if session_id:
                logger.info(f"新会话创建成功: {session_id}")
                return session_id
            else:
                logger.error("创建新会话失败")
                return ""
                
        except Exception as e:
            logger.error(f"创建新会话时出错: {e}")
            return ""
    
    def _simulate_initial_browsing(self, driver):
        """模拟初始浏览行为"""
        try:
            # 滚动页面
            for _ in range(random.randint(2, 4)):
                scroll_distance = random.randint(300, 800)
                driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                time.sleep(random.uniform(1, 3))
            
            # 随机点击一些无害的元素
            try:
                clickable_elements = driver.find_elements(By.XPATH, "//button | //a | //div[@role='button']")
                if clickable_elements:
                    safe_elements = [elem for elem in clickable_elements[:5] if self._is_safe_element(elem)]
                    if safe_elements:
                        random.choice(safe_elements).click()
                        time.sleep(random.uniform(1, 2))
            except Exception:
                pass  # 忽略点击错误
            
        except Exception as e:
            logger.debug(f"模拟初始浏览行为时出错: {e}")
    
    def _is_safe_element(self, element) -> bool:
        """检查元素是否安全点击"""
        try:
            element_text = element.text.lower()
            element_class = element.get_attribute('class') or ''
            
            # 避免危险的按钮
            dangerous_keywords = ['login', '登录', 'register', '注册', 'submit', '提交', 'delete', '删除']
            
            return not any(keyword in element_text or keyword in element_class.lower() 
                          for keyword in dangerous_keywords)
        except:
            return False
    
    def should_rotate_session(self) -> bool:
        """检查是否应该轮换会话"""
        current_time = time.time()
        
        # 检查请求数量
        if self.request_count >= self.max_requests_per_session:
            logger.info(f"达到最大请求数 ({self.request_count}), 需要轮换会话")
            return True
        
        # 检查会话时长
        if self.session_start_time and current_time - self.session_start_time >= self.max_session_duration:
            logger.info(f"会话时长过长 ({current_time - self.session_start_time:.0f}秒), 需要轮换会话")
            return True
        
        # 检查错误数量
        if self.error_count >= self.max_errors_per_session:
            logger.info(f"错误数量过多 ({self.error_count}), 需要轮换会话")
            return True
        
        # 检查活动间隔
        if self.last_activity_time and current_time - self.last_activity_time > 300:  # 5分钟无活动
            logger.info("长时间无活动, 建议轮换会话")
            return True
        
        return False
    
    def record_request(self, success: bool = True):
        """记录请求"""
        self.request_count += 1
        self.last_activity_time = time.time()
        
        if not success:
            self.error_count += 1
        
        # 更新Cookie管理器中的统计
        self.cookie_manager.update_session_success(success)
    
    def end_session(self, driver):
        """结束会话"""
        if self.current_session_id:
            logger.info(f"结束会话: {self.current_session_id}")
            
            # 最后保存一次会话状态
            try:
                self.cookie_manager.save_session(driver, self.current_session_id)
            except Exception as e:
                logger.warning(f"保存最终会话状态失败: {e}")
            
            # 清理过期会话
            self.cookie_manager.cleanup_expired_sessions()
            
            # 重置状态
            self.current_session_id = None
            self.session_start_time = None
            self.request_count = 0
            self.error_count = 0
            self.last_activity_time = None
    
    def get_session_stats(self) -> Dict:
        """获取会话统计信息"""
        current_time = time.time()
        
        stats = {
            'current_session_id': self.current_session_id,
            'request_count': self.request_count,
            'error_count': self.error_count,
            'session_duration': current_time - self.session_start_time if self.session_start_time else 0,
            'success_rate': (self.request_count - self.error_count) / max(1, self.request_count),
            'available_sessions': len(self.cookie_manager.cookie_pools['xiaohongshu']),
            'backup_sessions': len(self.cookie_manager.cookie_pools['backup'])
        }
        
        return stats


class ProxySessionManager:
    """代理会话管理器"""
    
    def __init__(self, proxy_file: str = None):
        self.proxy_file = proxy_file
        self.proxies = []
        self.current_proxy_index = 0
        self.proxy_stats = {}
        
        if proxy_file:
            self._load_proxies()
    
    def _load_proxies(self):
        """加载代理列表"""
        try:
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                self.proxies = [line.strip() for line in f.readlines() if line.strip()]
            
            # 初始化代理统计
            for proxy in self.proxies:
                self.proxy_stats[proxy] = {
                    'success_count': 0,
                    'failure_count': 0,
                    'last_used': 0,
                    'response_time': []
                }
            
            logger.info(f"加载了 {len(self.proxies)} 个代理")
            
        except Exception as e:
            logger.error(f"加载代理文件失败: {e}")
    
    def get_best_proxy(self) -> Optional[str]:
        """获取最佳代理"""
        if not self.proxies:
            return None
        
        # 计算每个代理的得分
        proxy_scores = {}
        current_time = time.time()
        
        for proxy in self.proxies:
            stats = self.proxy_stats[proxy]
            
            # 成功率
            total_requests = stats['success_count'] + stats['failure_count']
            success_rate = stats['success_count'] / max(1, total_requests)
            
            # 时间衰减（最近使用的代理得分稍低，避免过度使用）
            time_decay = max(0.5, 1.0 - (current_time - stats['last_used']) / 3600)
            
            # 响应时间
            avg_response_time = sum(stats['response_time'][-10:]) / max(1, len(stats['response_time'][-10:]))
            response_score = max(0.1, 1.0 - avg_response_time / 10.0)  # 假设10秒为最差响应时间
            
            # 综合得分
            score = success_rate * 0.6 + (1 - time_decay) * 0.2 + response_score * 0.2
            proxy_scores[proxy] = score
        
        # 选择得分最高的代理
        best_proxy = max(proxy_scores.keys(), key=lambda p: proxy_scores[p])
        
        # 更新使用时间
        self.proxy_stats[best_proxy]['last_used'] = current_time
        
        logger.info(f"选择代理: {best_proxy} (得分: {proxy_scores[best_proxy]:.3f})")
        return best_proxy
    
    def record_proxy_result(self, proxy: str, success: bool, response_time: float = 0):
        """记录代理使用结果"""
        if proxy in self.proxy_stats:
            if success:
                self.proxy_stats[proxy]['success_count'] += 1
                if response_time > 0:
                    self.proxy_stats[proxy]['response_time'].append(response_time)
                    # 只保留最近10次的响应时间
                    if len(self.proxy_stats[proxy]['response_time']) > 10:
                        self.proxy_stats[proxy]['response_time'] = self.proxy_stats[proxy]['response_time'][-10:]
            else:
                self.proxy_stats[proxy]['failure_count'] += 1
    
    def get_proxy_stats(self) -> Dict:
        """获取代理统计信息"""
        stats = {
            'total_proxies': len(self.proxies),
            'active_proxies': 0,
            'avg_success_rate': 0.0
        }
        
        if self.proxies:
            success_rates = []
            for proxy, proxy_stats in self.proxy_stats.items():
                total = proxy_stats['success_count'] + proxy_stats['failure_count']
                if total > 0:
                    stats['active_proxies'] += 1
                    success_rates.append(proxy_stats['success_count'] / total)
            
            if success_rates:
                stats['avg_success_rate'] = sum(success_rates) / len(success_rates)
        
        return stats