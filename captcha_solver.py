"""
Enhanced CAPTCHA solving module for educational purposes
增强的验证码处理模块，专门用于教育目的的基金知识学习
"""
import time
import random
import cv2
import numpy as np
from PIL import Image
import base64
import io
from typing import Tuple, Optional, List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

logger = logging.getLogger(__name__)


class CaptchaSolver:
    """验证码求解器"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.action_chains = ActionChains(driver)
        
        # 验证码类型检测器
        self.captcha_detectors = {
            'slider': self._detect_slider_captcha,
            'click': self._detect_click_captcha,
            'rotate': self._detect_rotate_captcha,
            'text': self._detect_text_captcha,
            'puzzle': self._detect_puzzle_captcha
        }
        
        # 验证码求解器
        self.captcha_solvers = {
            'slider': self._solve_slider_captcha,
            'click': self._solve_click_captcha,
            'rotate': self._solve_rotate_captcha,
            'text': self._solve_text_captcha,
            'puzzle': self._solve_puzzle_captcha
        }
    
    def detect_and_solve_captcha(self) -> bool:
        """检测并解决验证码"""
        logger.info("开始检测验证码...")
        
        # 等待页面稳定
        time.sleep(2)
        
        # 检测验证码类型
        captcha_type = self._detect_captcha_type()
        
        if not captcha_type:
            logger.info("未检测到验证码")
            return True
        
        logger.info(f"检测到验证码类型: {captcha_type}")
        
        # 尝试解决验证码
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                logger.info(f"尝试解决验证码 (第{attempt + 1}次)")
                
                if self.captcha_solvers[captcha_type]():
                    logger.info("验证码解决成功")
                    time.sleep(2)  # 等待验证完成
                    
                    # 检查是否还有验证码
                    if not self._detect_captcha_type():
                        return True
                    else:
                        logger.warning("验证码仍然存在，继续尝试")
                        continue
                else:
                    logger.warning(f"验证码解决失败 (第{attempt + 1}次)")
                    
            except Exception as e:
                logger.error(f"解决验证码时出错: {e}")
            
            # 失败后等待一段时间再试
            if attempt < max_attempts - 1:
                time.sleep(random.uniform(3, 6))
        
        logger.error("所有验证码解决尝试都失败了")
        return False
    
    def _detect_captcha_type(self) -> Optional[str]:
        """检测验证码类型"""
        for captcha_type, detector in self.captcha_detectors.items():
            if detector():
                return captcha_type
        return None
    
    def _detect_slider_captcha(self) -> bool:
        """检测滑动验证码"""
        slider_selectors = [
            "//div[contains(@class, 'slider')]",
            "//div[contains(@class, 'slide')]",
            "//div[contains(@id, 'slider')]",
            "//div[contains(@class, 'captcha-slider')]",
            "//div[contains(text(), '滑动') or contains(text(), '拖动')]",
            "//span[contains(@class, 'slider')]",
            "//button[contains(@class, 'slider')]"
        ]
        
        for selector in slider_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    return True
            except NoSuchElementException:
                continue
        
        return False
    
    def _detect_click_captcha(self) -> bool:
        """检测点击验证码"""
        click_selectors = [
            "//div[contains(text(), '点击') or contains(text(), '选择')]",
            "//div[contains(@class, 'click-captcha')]",
            "//div[contains(@class, 'image-captcha')]",
            "//canvas[contains(@class, 'captcha')]"
        ]
        
        for selector in click_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    return True
            except NoSuchElementException:
                continue
        
        return False
    
    def _detect_rotate_captcha(self) -> bool:
        """检测旋转验证码"""
        rotate_selectors = [
            "//div[contains(text(), '旋转') or contains(text(), '转动')]",
            "//div[contains(@class, 'rotate')]",
            "//canvas[contains(@class, 'rotate')]"
        ]
        
        for selector in rotate_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    return True
            except NoSuchElementException:
                continue
        
        return False
    
    def _detect_text_captcha(self) -> bool:
        """检测文字验证码"""
        text_selectors = [
            "//input[contains(@placeholder, '验证码')]",
            "//input[contains(@name, 'captcha')]",
            "//input[contains(@id, 'captcha')]",
            "//img[contains(@src, 'captcha')]"
        ]
        
        for selector in text_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    return True
            except NoSuchElementException:
                continue
        
        return False
    
    def _detect_puzzle_captcha(self) -> bool:
        """检测拼图验证码"""
        puzzle_selectors = [
            "//div[contains(@class, 'puzzle')]",
            "//canvas[contains(@class, 'puzzle')]",
            "//div[contains(text(), '拖拽') or contains(text(), '拼图')]"
        ]
        
        for selector in puzzle_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    return True
            except NoSuchElementException:
                continue
        
        return False
    
    def _solve_slider_captcha(self) -> bool:
        """解决滑动验证码"""
        try:
            # 查找滑块和轨道
            slider_selectors = [
                "//div[contains(@class, 'slider-button')]",
                "//span[contains(@class, 'slider')]",
                "//div[contains(@class, 'slide-button')]",
                "//button[contains(@class, 'slider')]"
            ]
            
            slider_element = None
            for selector in slider_selectors:
                try:
                    slider_element = self.driver.find_element(By.XPATH, selector)
                    if slider_element.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if not slider_element:
                logger.error("未找到滑块元素")
                return False
            
            # 查找滑动轨道
            track_selectors = [
                "//div[contains(@class, 'slider-track')]",
                "//div[contains(@class, 'slide-track')]",
                "//div[contains(@class, 'captcha-slider')]"
            ]
            
            track_element = None
            for selector in track_selectors:
                try:
                    track_element = self.driver.find_element(By.XPATH, selector)
                    if track_element.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            # 如果没找到轨道，尝试从滑块的父元素获取
            if not track_element:
                try:
                    track_element = slider_element.find_element(By.XPATH, ".//ancestor::div[contains(@class, 'slider') or contains(@class, 'captcha')][1]")
                except:
                    # 最后的备用方案，使用固定距离
                    track_width = 300
            
            if track_element:
                track_width = track_element.size['width']
            else:
                track_width = 300  # 默认宽度
            
            # 计算滑动距离（通常需要滑动到70-90%的位置）
            slide_distance = int(track_width * random.uniform(0.75, 0.95))
            
            # 执行人性化滑动
            return self._perform_human_like_slide(slider_element, slide_distance)
            
        except Exception as e:
            logger.error(f"解决滑动验证码时出错: {e}")
            return False
    
    def _perform_human_like_slide(self, slider_element, distance: int) -> bool:
        """执行人性化的滑动操作"""
        try:
            action = ActionChains(self.driver)
            
            # 移动到滑块并按下
            action.move_to_element(slider_element)
            action.click_and_hold(slider_element)
            
            # 人性化滑动：分段移动，带有随机停顿和速度变化
            segments = random.randint(8, 15)  # 分成多段
            segment_distance = distance / segments
            
            for i in range(segments):
                # 计算当前段的距离（添加随机变化）
                if i == segments - 1:
                    # 最后一段，确保到达目标位置
                    current_distance = distance - sum([segment_distance] * (segments - 1))
                else:
                    current_distance = segment_distance + random.uniform(-5, 5)
                
                # 移动鼠标
                action.move_by_offset(current_distance, random.uniform(-2, 2))
                
                # 随机停顿（模拟人类思考和调整）
                if random.random() < 0.3:  # 30%概率停顿
                    pause_time = random.uniform(0.05, 0.2)
                    action.pause(pause_time)
                
                # 模拟手抖（轻微回退再前进）
                if random.random() < 0.2 and i > 2:  # 20%概率手抖
                    shake_distance = random.uniform(2, 8)
                    action.move_by_offset(-shake_distance, 0)
                    action.pause(random.uniform(0.03, 0.08))
                    action.move_by_offset(shake_distance, 0)
            
            # 释放鼠标
            action.release()
            action.perform()
            
            # 等待验证结果
            time.sleep(random.uniform(1, 3))
            
            return True
            
        except Exception as e:
            logger.error(f"执行滑动操作时出错: {e}")
            return False
    
    def _solve_click_captcha(self) -> bool:
        """解决点击验证码"""
        try:
            # 查找验证码图片
            img_selectors = [
                "//img[contains(@class, 'captcha')]",
                "//canvas[contains(@class, 'captcha')]",
                "//div[contains(@class, 'captcha-image')]//img"
            ]
            
            captcha_img = None
            for selector in img_selectors:
                try:
                    captcha_img = self.driver.find_element(By.XPATH, selector)
                    if captcha_img.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if not captcha_img:
                logger.error("未找到验证码图片")
                return False
            
            # 简单的点击策略：随机点击几个位置
            img_width = captcha_img.size['width']
            img_height = captcha_img.size['height']
            
            # 生成随机点击点
            click_points = []
            num_clicks = random.randint(1, 3)  # 随机点击1-3次
            
            for _ in range(num_clicks):
                x_offset = random.randint(int(img_width * 0.1), int(img_width * 0.9))
                y_offset = random.randint(int(img_height * 0.1), int(img_height * 0.9))
                click_points.append((x_offset, y_offset))
            
            # 执行点击
            action = ActionChains(self.driver)
            for x_offset, y_offset in click_points:
                action.move_to_element_with_offset(captcha_img, x_offset, y_offset)
                action.click()
                action.pause(random.uniform(0.5, 1.5))
            
            action.perform()
            
            # 查找确认按钮
            confirm_selectors = [
                "//button[contains(text(), '确认') or contains(text(), '确定')]",
                "//div[contains(text(), '确认') or contains(text(), '确定')]",
                "//button[contains(@class, 'confirm')]"
            ]
            
            for selector in confirm_selectors:
                try:
                    confirm_btn = self.driver.find_element(By.XPATH, selector)
                    if confirm_btn.is_displayed():
                        confirm_btn.click()
                        break
                except NoSuchElementException:
                    continue
            
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"解决点击验证码时出错: {e}")
            return False
    
    def _solve_rotate_captcha(self) -> bool:
        """解决旋转验证码"""
        try:
            # 查找旋转元素
            rotate_selectors = [
                "//div[contains(@class, 'rotate')]",
                "//canvas[contains(@class, 'rotate')]",
                "//img[contains(@class, 'rotate')]"
            ]
            
            rotate_element = None
            for selector in rotate_selectors:
                try:
                    rotate_element = self.driver.find_element(By.XPATH, selector)
                    if rotate_element.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if not rotate_element:
                logger.error("未找到旋转验证码元素")
                return False
            
            # 随机旋转角度
            rotation_angles = [90, 180, 270]  # 常见的旋转角度
            target_angle = random.choice(rotation_angles)
            
            # 模拟旋转操作（这里只是示例，实际需要根据具体实现调整）
            action = ActionChains(self.driver)
            
            # 点击并拖拽旋转
            center_x = rotate_element.size['width'] // 2
            center_y = rotate_element.size['height'] // 2
            
            action.move_to_element_with_offset(rotate_element, center_x, center_y)
            action.click_and_hold()
            
            # 模拟旋转移动
            for angle in range(0, target_angle, 15):  # 分步旋转
                x_offset = int(30 * np.cos(np.radians(angle)))
                y_offset = int(30 * np.sin(np.radians(angle)))
                action.move_by_offset(x_offset, y_offset)
                action.pause(0.1)
            
            action.release()
            action.perform()
            
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"解决旋转验证码时出错: {e}")
            return False
    
    def _solve_text_captcha(self) -> bool:
        """解决文字验证码（需要人工介入）"""
        try:
            # 查找验证码输入框
            input_selectors = [
                "//input[contains(@placeholder, '验证码')]",
                "//input[contains(@name, 'captcha')]",
                "//input[contains(@id, 'captcha')]"
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    input_element = self.driver.find_element(By.XPATH, selector)
                    if input_element.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if not input_element:
                logger.error("未找到验证码输入框")
                return False
            
            # 文字验证码通常需要人工识别
            logger.warning("检测到文字验证码，需要人工处理")
            
            # 在非headless模式下提示用户输入
            if not self._is_headless():
                captcha_text = input("请输入验证码: ")
                if captcha_text:
                    input_element.clear()
                    input_element.send_keys(captcha_text)
                    
                    # 查找提交按钮
                    submit_selectors = [
                        "//button[contains(text(), '提交') or contains(text(), '确认')]",
                        "//input[@type='submit']",
                        "//button[@type='submit']"
                    ]
                    
                    for selector in submit_selectors:
                        try:
                            submit_btn = self.driver.find_element(By.XPATH, selector)
                            if submit_btn.is_displayed():
                                submit_btn.click()
                                break
                        except NoSuchElementException:
                            continue
                    
                    time.sleep(2)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"解决文字验证码时出错: {e}")
            return False
    
    def _solve_puzzle_captcha(self) -> bool:
        """解决拼图验证码"""
        try:
            # 拼图验证码通常比较复杂，这里提供基础框架
            logger.info("检测到拼图验证码，尝试简单解决方案")
            
            # 查找拼图元素
            puzzle_selectors = [
                "//div[contains(@class, 'puzzle')]",
                "//canvas[contains(@class, 'puzzle')]"
            ]
            
            puzzle_element = None
            for selector in puzzle_selectors:
                try:
                    puzzle_element = self.driver.find_element(By.XPATH, selector)
                    if puzzle_element.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if not puzzle_element:
                logger.error("未找到拼图验证码元素")
                return False
            
            # 简单的拖拽尝试
            action = ActionChains(self.driver)
            
            # 从拼图左边拖到右边
            start_x = puzzle_element.size['width'] * 0.1
            end_x = puzzle_element.size['width'] * 0.8
            y_pos = puzzle_element.size['height'] * 0.5
            
            action.move_to_element_with_offset(puzzle_element, start_x, y_pos)
            action.click_and_hold()
            action.move_to_element_with_offset(puzzle_element, end_x, y_pos)
            action.release()
            action.perform()
            
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"解决拼图验证码时出错: {e}")
            return False
    
    def _is_headless(self) -> bool:
        """检查是否为headless模式"""
        try:
            # 尝试获取窗口大小来判断是否为headless模式
            window_size = self.driver.get_window_size()
            return False  # 如果能获取窗口大小，说明不是headless
        except:
            return True  # 如果获取失败，可能是headless模式


class SmartCaptchaHandler:
    """智能验证码处理器"""
    
    def __init__(self, driver):
        self.driver = driver
        self.solver = CaptchaSolver(driver)
        self.captcha_history = []
        self.success_rate = 0.0
    
    def handle_captcha_with_fallback(self) -> bool:
        """带有回退策略的验证码处理"""
        logger.info("开始智能验证码处理...")
        
        # 记录开始时间
        start_time = time.time()
        
        # 首先尝试自动解决
        auto_success = self.solver.detect_and_solve_captcha()
        
        if auto_success:
            self._record_captcha_result(True, time.time() - start_time)
            return True
        
        # 自动解决失败，尝试刷新页面
        logger.info("自动解决失败，尝试刷新页面")
        try:
            self.driver.refresh()
            time.sleep(random.uniform(3, 6))
            
            # 再次检查是否还有验证码
            if not self.solver._detect_captcha_type():
                self._record_captcha_result(True, time.time() - start_time)
                return True
                
        except Exception as e:
            logger.warning(f"刷新页面失败: {e}")
        
        # 尝试返回上一页
        logger.info("尝试返回上一页")
        try:
            self.driver.back()
            time.sleep(random.uniform(2, 4))
            
            if not self.solver._detect_captcha_type():
                self._record_captcha_result(True, time.time() - start_time)
                return True
                
        except Exception as e:
            logger.warning(f"返回上一页失败: {e}")
        
        # 最后的手动处理选项
        if not self.solver._is_headless():
            logger.warning("自动处理失败，需要手动干预")
            user_input = input("验证码无法自动处理，请手动处理后输入'y'继续，或输入'n'跳过: ")
            if user_input.lower() == 'y':
                self._record_captcha_result(True, time.time() - start_time)
                return True
        
        # 所有方法都失败
        self._record_captcha_result(False, time.time() - start_time)
        logger.error("所有验证码处理方法都失败了")
        return False
    
    def _record_captcha_result(self, success: bool, duration: float):
        """记录验证码处理结果"""
        self.captcha_history.append({
            'timestamp': time.time(),
            'success': success,
            'duration': duration
        })
        
        # 只保留最近50个记录
        if len(self.captcha_history) > 50:
            self.captcha_history = self.captcha_history[-50:]
        
        # 更新成功率
        if self.captcha_history:
            recent_successes = sum(1 for record in self.captcha_history if record['success'])
            self.success_rate = recent_successes / len(self.captcha_history)
        
        logger.info(f"验证码处理结果: {'成功' if success else '失败'}, "
                   f"耗时: {duration:.2f}秒, "
                   f"历史成功率: {self.success_rate:.2%}")
    
    def get_captcha_stats(self) -> dict:
        """获取验证码处理统计信息"""
        if not self.captcha_history:
            return {'total': 0, 'success_rate': 0.0, 'avg_duration': 0.0}
        
        total = len(self.captcha_history)
        successes = sum(1 for record in self.captcha_history if record['success'])
        avg_duration = sum(record['duration'] for record in self.captcha_history) / total
        
        return {
            'total': total,
            'success_rate': successes / total,
            'avg_duration': avg_duration
        }