"""
Enhanced anti-detection module for Xiaohongshu scraper
高级反检测模块，专门用于教育目的的基金知识学习
"""
import random
import time
import json
import base64
from typing import Dict, List, Tuple, Optional
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
from datetime import datetime, timedelta


class FingerprintSpoofing:
    """浏览器指纹伪装类"""
    
    # 真实的浏览器指纹数据库
    REALISTIC_FINGERPRINTS = [
        {
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'platform': 'Win32',
            'language': 'zh-CN',
            'screen': {'width': 1920, 'height': 1080, 'colorDepth': 24},
            'timezone': 'Asia/Shanghai',
            'webgl_vendor': 'Google Inc. (NVIDIA)',
            'webgl_renderer': 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)',
            'hardware_concurrency': 16,
            'device_memory': 8
        },
        {
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'platform': 'MacIntel',
            'language': 'zh-CN',
            'screen': {'width': 2560, 'height': 1440, 'colorDepth': 24},
            'timezone': 'Asia/Shanghai',
            'webgl_vendor': 'Intel Inc.',
            'webgl_renderer': 'Intel(R) Iris(TM) Plus Graphics 655',
            'hardware_concurrency': 8,
            'device_memory': 16
        },
        {
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'platform': 'Win32',
            'language': 'zh-CN',
            'screen': {'width': 1366, 'height': 768, 'colorDepth': 24},
            'timezone': 'Asia/Shanghai',
            'webgl_vendor': 'Google Inc. (AMD)',
            'webgl_renderer': 'ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)',
            'hardware_concurrency': 12,
            'device_memory': 16
        }
    ]
    
    @classmethod
    def get_random_fingerprint(cls) -> Dict:
        """获取随机指纹"""
        base_fingerprint = random.choice(cls.REALISTIC_FINGERPRINTS).copy()
        
        # 添加随机变化
        base_fingerprint['screen']['width'] += random.randint(-50, 50)
        base_fingerprint['screen']['height'] += random.randint(-30, 30)
        
        return base_fingerprint
    
    @classmethod
    def generate_canvas_fingerprint(cls) -> str:
        """生成Canvas指纹"""
        # 模拟真实的Canvas渲染结果
        canvas_texts = [
            "BrowserLeaks,com <canvas> 1.0",
            "Cwm fjordbank glyphs vext quiz 🔏",
            "The quick brown fox jumps over the lazy dog"
        ]
        
        text = random.choice(canvas_texts)
        # 生成一个伪随机的Canvas指纹
        fake_hash = str(hash(text + str(random.randint(1000, 9999))))
        return fake_hash[-8:]  # 返回8位指纹
    
    @classmethod
    def generate_webgl_fingerprint(cls) -> Dict:
        """生成WebGL指纹"""
        vendors = [
            "Google Inc. (NVIDIA)",
            "Google Inc. (AMD)", 
            "Google Inc. (Intel)",
            "Intel Inc.",
            "AMD"
        ]
        
        renderers = [
            "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "Intel(R) Iris(TM) Plus Graphics 655",
            "ANGLE (Intel, Intel(R) HD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)"
        ]
        
        return {
            'vendor': random.choice(vendors),
            'renderer': random.choice(renderers),
            'version': f"OpenGL ES {random.choice(['2.0', '3.0'])} (ANGLE {random.randint(2, 5)}.{random.randint(0, 9)}.{random.randint(1000, 9999)})"
        }


class HumanBehaviorSimulator:
    """人类行为模拟器"""
    
    def __init__(self, driver, action_chains):
        self.driver = driver
        self.action_chains = action_chains
        self.reading_speed = random.uniform(200, 400)  # 每分钟字数
        self.mouse_precision = random.uniform(0.7, 0.95)  # 鼠标精度
        self.reaction_time = random.uniform(0.2, 0.8)  # 反应时间
        
    def natural_mouse_movement(self, element) -> None:
        """自然的鼠标移动"""
        try:
            # 获取元素位置
            location = element.location
            size = element.size
            
            # 计算目标点（添加随机偏移）
            target_x = location['x'] + size['width'] // 2 + random.randint(-20, 20)
            target_y = location['y'] + size['height'] // 2 + random.randint(-10, 10)
            
            # 获取当前鼠标位置（模拟）
            current_x = random.randint(100, 800)
            current_y = random.randint(100, 600)
            
            # 生成贝塞尔曲线路径
            path_points = self._generate_bezier_path(
                (current_x, current_y), 
                (target_x, target_y), 
                num_points=random.randint(5, 15)
            )
            
            # 执行移动
            action = ActionChains(self.driver)
            for i, (x, y) in enumerate(path_points):
                if i == 0:
                    continue
                
                # 计算相对移动
                offset_x = x - (current_x if i == 1 else path_points[i-1][0])
                offset_y = y - (current_y if i == 1 else path_points[i-1][1])
                
                action.move_by_offset(offset_x, offset_y)
                
                # 添加随机停顿
                if random.random() < 0.3:
                    action.pause(random.uniform(0.01, 0.05))
            
            action.perform()
            
        except Exception as e:
            # 回退到简单移动
            self.action_chains.move_to_element(element).perform()
    
    def _generate_bezier_path(self, start: Tuple[int, int], end: Tuple[int, int], num_points: int = 10) -> List[Tuple[int, int]]:
        """生成贝塞尔曲线路径"""
        # 控制点
        control1_x = start[0] + (end[0] - start[0]) * 0.25 + random.randint(-50, 50)
        control1_y = start[1] + (end[1] - start[1]) * 0.25 + random.randint(-30, 30)
        
        control2_x = start[0] + (end[0] - start[0]) * 0.75 + random.randint(-50, 50)
        control2_y = start[1] + (end[1] - start[1]) * 0.75 + random.randint(-30, 30)
        
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            
            # 三次贝塞尔曲线公式
            x = int((1-t)**3 * start[0] + 3*(1-t)**2*t * control1_x + 
                   3*(1-t)*t**2 * control2_x + t**3 * end[0])
            y = int((1-t)**3 * start[1] + 3*(1-t)**2*t * control1_y + 
                   3*(1-t)*t**2 * control2_y + t**3 * end[1])
            
            points.append((x, y))
        
        return points
    
    def natural_scrolling(self, distance: int = None) -> None:
        """自然的滚动行为"""
        if distance is None:
            distance = random.randint(300, 800)
        
        # 分段滚动，模拟真实阅读行为
        segments = random.randint(3, 8)
        segment_distance = distance // segments
        
        for i in range(segments):
            # 变化滚动速度
            current_segment = segment_distance + random.randint(-50, 50)
            
            # 执行滚动
            self.driver.execute_script(f"window.scrollBy(0, {current_segment});")
            
            # 模拟阅读停顿
            reading_pause = random.uniform(0.5, 2.5)
            if i < segments - 1:  # 最后一段不停顿
                time.sleep(reading_pause)
                
                # 偶尔向上滚动一点（回看行为）
                if random.random() < 0.2:
                    back_scroll = random.randint(50, 150)
                    self.driver.execute_script(f"window.scrollBy(0, -{back_scroll});")
                    time.sleep(random.uniform(0.3, 0.8))
                    self.driver.execute_script(f"window.scrollBy(0, {back_scroll});")
    
    def simulate_reading_time(self, text_length: int) -> float:
        """计算模拟阅读时间"""
        if text_length <= 0:
            return random.uniform(0.5, 1.5)
        
        # 基于阅读速度计算时间
        base_time = (text_length / self.reading_speed) * 60  # 转换为秒
        
        # 添加随机因子
        variation = random.uniform(0.7, 1.5)
        reading_time = base_time * variation
        
        # 限制在合理范围内
        return max(1.0, min(reading_time, 30.0))
    
    def random_page_interaction(self) -> None:
        """随机页面交互"""
        interactions = [
            self._random_mouse_movement,
            self._simulate_highlight_text,
            self._simulate_back_button,
            self._simulate_page_focus
        ]
        
        # 随机选择交互
        if random.random() < 0.3:  # 30%概率进行交互
            interaction = random.choice(interactions)
            try:
                interaction()
            except:
                pass  # 忽略交互错误
    
    def _random_mouse_movement(self) -> None:
        """随机鼠标移动"""
        action = ActionChains(self.driver)
        for _ in range(random.randint(2, 5)):
            offset_x = random.randint(-200, 200)
            offset_y = random.randint(-100, 100)
            action.move_by_offset(offset_x, offset_y)
            action.pause(random.uniform(0.1, 0.5))
        action.perform()
    
    def _simulate_highlight_text(self) -> None:
        """模拟文本选择"""
        try:
            # 查找文本元素
            text_elements = self.driver.find_elements(By.XPATH, "//p | //span | //div[text()]")
            if text_elements:
                element = random.choice(text_elements[:10])  # 只选前10个避免过多元素
                
                # 双击选择文本
                action = ActionChains(self.driver)
                action.double_click(element).perform()
                time.sleep(random.uniform(0.5, 1.5))
                
                # 点击其他地方取消选择
                action.click(element).perform()
        except:
            pass
    
    def _simulate_back_button(self) -> None:
        """模拟后退按钮点击（但不真正后退）"""
        # 只是模拟鼠标移动到后退按钮位置
        action = ActionChains(self.driver)
        action.move_by_offset(50, 50)  # 大概的后退按钮位置
        action.pause(random.uniform(0.2, 0.5))
        action.perform()
    
    def _simulate_page_focus(self) -> None:
        """模拟页面焦点切换"""
        try:
            # 点击页面空白区域
            body = self.driver.find_element(By.TAG_NAME, "body")
            action = ActionChains(self.driver)
            action.click(body).perform()
        except:
            pass


class IntelligentDelayStrategy:
    """智能延时策略"""
    
    def __init__(self):
        self.request_history = []
        self.success_rate = 1.0
        self.last_captcha_time = None
        self.current_delay_multiplier = 1.0
        
    def calculate_delay(self, request_type: str = "normal") -> float:
        """计算智能延时"""
        base_delays = {
            "normal": (2.0, 5.0),
            "search": (3.0, 8.0),
            "scroll": (1.0, 3.0),
            "click": (0.5, 2.0),
            "page_load": (5.0, 12.0)
        }
        
        min_delay, max_delay = base_delays.get(request_type, base_delays["normal"])
        
        # 基础延时
        base_delay = random.uniform(min_delay, max_delay)
        
        # 根据成功率调整
        if self.success_rate < 0.7:
            self.current_delay_multiplier = min(3.0, self.current_delay_multiplier * 1.2)
        elif self.success_rate > 0.9:
            self.current_delay_multiplier = max(0.8, self.current_delay_multiplier * 0.95)
        
        # 如果最近遇到验证码，增加延时
        if self.last_captcha_time:
            time_since_captcha = time.time() - self.last_captcha_time
            if time_since_captcha < 300:  # 5分钟内
                self.current_delay_multiplier *= 1.5
        
        # 时间段调整（模拟人类作息）
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # 工作时间，模拟更快操作
            time_multiplier = 0.8
        elif 22 <= current_hour or current_hour <= 6:  # 深夜，模拟更慢操作
            time_multiplier = 1.5
        else:
            time_multiplier = 1.0
        
        final_delay = base_delay * self.current_delay_multiplier * time_multiplier
        
        # 添加正态分布随机性
        noise = np.random.normal(0, final_delay * 0.1)
        final_delay = max(0.5, final_delay + noise)
        
        return final_delay
    
    def record_request(self, success: bool, had_captcha: bool = False) -> None:
        """记录请求结果"""
        self.request_history.append({
            'timestamp': time.time(),
            'success': success,
            'had_captcha': had_captcha
        })
        
        # 只保留最近100个记录
        if len(self.request_history) > 100:
            self.request_history = self.request_history[-100:]
        
        # 更新成功率
        recent_requests = [r for r in self.request_history if time.time() - r['timestamp'] < 3600]  # 最近1小时
        if recent_requests:
            self.success_rate = sum(1 for r in recent_requests if r['success']) / len(recent_requests)
        
        # 记录验证码时间
        if had_captcha:
            self.last_captcha_time = time.time()


class EnhancedAntiDetection:
    """增强的反检测主类"""
    
    def __init__(self):
        self.fingerprint = FingerprintSpoofing.get_random_fingerprint()
        self.delay_strategy = IntelligentDelayStrategy()
        self.session_cookies = {}
        self.behavioral_simulator = None
        
    def setup_chrome_options(self, headless: bool = True) -> Options:
        """设置增强的Chrome选项"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless=new')
        
        # 基础反检测参数
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 高级反检测参数
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
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
        
        # 性能优化
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-gpu-logging')
        chrome_options.add_argument('--silent')
        
        # 指纹伪装
        chrome_options.add_argument(f'--user-agent={self.fingerprint["user_agent"]}')
        chrome_options.add_argument(f'--window-size={self.fingerprint["screen"]["width"]},{self.fingerprint["screen"]["height"]}')
        chrome_options.add_argument('--window-position=0,0')
        chrome_options.add_argument(f'--lang={self.fingerprint["language"]}')
        
        # 高级首选项
        prefs = {
            'intl.accept_languages': f'{self.fingerprint["language"]},zh,en-US,en',
            'profile.default_content_setting_values': {
                'notifications': 2,
                'images': 1,
                'plugins': 1,
                'popups': 2,
                'geolocation': 2,
                'media_stream': 2,
            },
            'profile.managed_default_content_settings': {
                'images': 1
            },
            'profile.default_content_settings': {
                'popups': 0
            },
            'profile.password_manager_enabled': False,
            'credentials_enable_service': False
        }
        chrome_options.add_experimental_option('prefs', prefs)
        
        return chrome_options
    
    def inject_anti_detection_scripts(self, driver) -> None:
        """注入反检测脚本"""
        fingerprint = self.fingerprint
        
        # 基础反检测脚本
        anti_detection_script = f"""
        // 移除webdriver标识
        Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
        delete navigator.__proto__.webdriver;
        
        // 伪装插件
        Object.defineProperty(navigator, 'plugins', {{
            get: () => [
                {{name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'}},
                {{name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'}},
                {{name: 'Native Client', filename: 'internal-nacl-plugin'}}
            ]
        }});
        
        // 伪装语言
        Object.defineProperty(navigator, 'languages', {{
            get: () => ['{fingerprint["language"]}', 'zh', 'en-US', 'en']
        }});
        
        // 伪装权限
        Object.defineProperty(navigator, 'permissions', {{
            get: () => ({{
                query: () => Promise.resolve({{state: 'granted'}})
            }})
        }});
        
        // 伪装平台
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{fingerprint["platform"]}'
        }});
        
        // 伪装硬件信息
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {fingerprint["hardware_concurrency"]}
        }});
        
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {fingerprint["device_memory"]}
        }});
        
        // 伪装连接信息
        Object.defineProperty(navigator, 'connection', {{
            get: () => ({{
                effectiveType: '4g',
                downlink: 10,
                rtt: 50
            }})
        }});
        
        // 伪装屏幕信息
        Object.defineProperty(screen, 'width', {{
            get: () => {fingerprint["screen"]["width"]}
        }});
        
        Object.defineProperty(screen, 'height', {{
            get: () => {fingerprint["screen"]["height"]}
        }});
        
        Object.defineProperty(screen, 'colorDepth', {{
            get: () => {fingerprint["screen"]["colorDepth"]}
        }});
        
        // 伪装Chrome对象
        window.chrome = {{
            runtime: {{}},
            app: {{
                isInstalled: false,
                InstallState: {{
                    DISABLED: 'disabled',
                    INSTALLED: 'installed',
                    NOT_INSTALLED: 'not_installed'
                }},
                RunningState: {{
                    CANNOT_RUN: 'cannot_run',
                    READY_TO_RUN: 'ready_to_run',
                    RUNNING: 'running'
                }}
            }}
        }};
        """
        
        # WebGL指纹伪装
        webgl_fingerprint = FingerprintSpoofing.generate_webgl_fingerprint()
        webgl_script = f"""
        // WebGL指纹伪装
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return '{webgl_fingerprint["vendor"]}';
            }}
            if (parameter === 37446) {{
                return '{webgl_fingerprint["renderer"]}';
            }}
            if (parameter === 7938) {{
                return '{webgl_fingerprint["version"]}';
            }}
            return getParameter.call(this, parameter);
        }};
        """
        
        # Canvas指纹伪装
        canvas_fingerprint = FingerprintSpoofing.generate_canvas_fingerprint()
        canvas_script = f"""
        // Canvas指纹伪装
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function() {{
            const result = originalToDataURL.apply(this, arguments);
            // 添加轻微的随机变化
            return result.substring(0, result.length - 10) + '{canvas_fingerprint}';
        }};
        """
        
        # 音频指纹伪装
        audio_script = """
        // 音频指纹伪装
        const audioContext = window.AudioContext || window.webkitAudioContext;
        if (audioContext) {
            const originalCreateAnalyser = audioContext.prototype.createAnalyser;
            audioContext.prototype.createAnalyser = function() {
                const analyser = originalCreateAnalyser.call(this);
                const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
                analyser.getFloatFrequencyData = function(array) {
                    originalGetFloatFrequencyData.call(this, array);
                    // 添加轻微的随机噪声
                    for (let i = 0; i < array.length; i++) {
                        array[i] += Math.random() * 0.0001;
                    }
                };
                return analyser;
            };
        }
        """
        
        # 执行所有脚本
        try:
            driver.execute_script(anti_detection_script)
            driver.execute_script(webgl_script)
            driver.execute_script(canvas_script)
            driver.execute_script(audio_script)
        except Exception as e:
            print(f"Warning: Failed to inject some anti-detection scripts: {e}")
    
    def setup_behavioral_simulator(self, driver) -> None:
        """设置行为模拟器"""
        action_chains = ActionChains(driver)
        self.behavioral_simulator = HumanBehaviorSimulator(driver, action_chains)
    
    def get_delay(self, request_type: str = "normal") -> float:
        """获取智能延时"""
        return self.delay_strategy.calculate_delay(request_type)
    
    def record_request_result(self, success: bool, had_captcha: bool = False) -> None:
        """记录请求结果"""
        self.delay_strategy.record_request(success, had_captcha)