"""
Configuration settings for Xiaohongshu scraper
"""
import os
from typing import List, Dict, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class ScrapingConfig(BaseSettings):
    """Scraping configuration with validation"""
    
    # Browser settings
    headless: bool = Field(default=True, description="Run browser in headless mode")
    window_width: int = Field(default=1920, ge=800, le=3840)
    window_height: int = Field(default=1080, ge=600, le=2160)
    user_agent_rotation: bool = Field(default=True, description="Enable user agent rotation")
    
    # Anti-detection settings
    request_delay_min: float = Field(default=2.0, ge=0.5, le=10.0)
    request_delay_max: float = Field(default=5.0, ge=1.0, le=20.0)
    scroll_delay_min: float = Field(default=1.0, ge=0.1, le=5.0)
    scroll_delay_max: float = Field(default=3.0, ge=0.5, le=10.0)
    human_behavior_enabled: bool = Field(default=True, description="Enable human behavior simulation")
    
    # Retry and timeout settings
    max_retries: int = Field(default=3, ge=1, le=10)
    timeout: int = Field(default=30, ge=10, le=120)
    page_load_timeout: int = Field(default=60, ge=15, le=300)
    
    # Scraping limits
    max_posts_per_keyword: int = Field(default=50, ge=1, le=500)
    max_scroll_attempts: int = Field(default=5, ge=1, le=20)
    max_keywords: int = Field(default=10, ge=1, le=50)
    
    # Data settings
    output_csv: bool = Field(default=True, description="Save data to CSV")
    output_json: bool = Field(default=True, description="Save data to JSON")
    output_directory: str = Field(default="output", description="Output directory for data files")
    
    # Proxy settings
    use_proxy: bool = Field(default=False, description="Enable proxy usage")
    proxy_file: Optional[str] = Field(default="proxies.txt", description="Path to proxy file")
    proxy_rotation: bool = Field(default=True, description="Enable proxy rotation")
    
    # Search settings
    default_keywords: List[str] = Field(
        default=["今日基金", "基金知识", "基金投资", "基金理财", "基金入门"],
        description="Default search keywords"
    )
    
    # Quality filters
    min_title_length: int = Field(default=3, ge=1, le=50)
    min_description_length: int = Field(default=5, ge=1, le=100)
    spam_keywords: List[str] = Field(
        default=["广告", "推广", "微信", "QQ", "加我", "联系我", "代理", "招商"],
        description="Keywords to filter out spam content"
    )
    required_keywords: List[str] = Field(
        default=["基金", "投资", "理财", "收益", "净值", "定投", "股票", "债券", "货币", "ETF"],
        description="Keywords that valid posts should contain"
    )
    
    class Config:
        env_file = ".env"
        env_prefix = "SCRAPER_"
        case_sensitive = False


class UserAgentConfig:
    """Realistic user agent configurations"""
    
    CHROME_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    EDGE_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
    ]
    
    FIREFOX_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
    ]
    
    @classmethod
    def get_all_agents(cls) -> List[str]:
        """Get all available user agents"""
        return cls.CHROME_AGENTS + cls.EDGE_AGENTS + cls.FIREFOX_AGENTS


class SelectorConfig:
    """CSS/XPath selectors for different page elements"""
    
    POST_SELECTORS = [
        "//div[contains(@class, 'note-item')]",
        "//div[contains(@class, 'note-card')]",
        "//section[contains(@class, 'note')]",
        "//div[contains(@data-testid, 'note')]",
        "//div[contains(@class, 'NoteCard')]",
        "//div[contains(@class, 'Card')]",
        "//div[contains(@class, 'search-result-item')]",
        "//div[contains(@class, 'result-item')]"
    ]
    
    TITLE_SELECTORS = [
        ".//span[contains(@class, 'title')]",
        ".//a[contains(@class, 'title')]",
        ".//div[contains(@class, 'title')]",
        ".//h1", ".//h2", ".//h3",
        ".//span[contains(@class, 'desc')]",
        ".//div[contains(@class, 'content')]"
    ]
    
    AUTHOR_SELECTORS = [
        ".//span[contains(@class, 'author')]",
        ".//a[contains(@class, 'author')]",
        ".//div[contains(@class, 'user')]",
        ".//span[contains(@class, 'username')]",
        ".//div[contains(@class, 'name')]"
    ]
    
    NOTE_TEXT_SELECTORS = [
        ".//div[contains(@class, 'note-text')]",
        ".//span[contains(@class, 'note-text')]",
        ".//div[contains(@class, 'note-content')]",
        ".//div[contains(@class, 'text-content')]",
        ".//div[contains(@class, 'desc-content')]",
        ".//div[contains(@class, 'note-desc')]",
        ".//p[contains(@class, 'note-text')]",
        ".//div[contains(@class, 'content-text')]"
    ]
    
    AUTHOR_FOLLOWERS_SELECTORS = [
        ".//span[contains(@class, 'followers')]",
        ".//div[contains(@class, 'followers')]",
        ".//span[contains(@class, 'fans')]",
        ".//div[contains(@class, 'fans')]",
        ".//span[contains(text(), '粉丝')]",
        ".//div[contains(text(), '粉丝')]",
        ".//span[contains(@class, 'follower-count')]",
        ".//div[contains(@class, 'user-stats')]//span[contains(text(), '粉丝')]",
        ".//div[contains(@class, 'author-info')]//span[contains(text(), '粉丝')]"
    ]
    
    POST_TIME_SELECTORS = [
        ".//time",
        ".//span[contains(@class, 'time')]",
        ".//div[contains(@class, 'time')]",
        ".//span[contains(@class, 'date')]",
        ".//div[contains(@class, 'date')]",
        ".//span[contains(@class, 'publish-time')]",
        ".//div[contains(@class, 'publish-time')]",
        ".//span[contains(@class, 'post-time')]",
        ".//div[contains(@class, 'create-time')]",
        ".//span[contains(text(), '小时前')]",
        ".//span[contains(text(), '分钟前')]",
        ".//span[contains(text(), '今天')]",
        ".//span[contains(text(), '昨天')]",
        ".//div[contains(@class, 'timestamp')]"
    ]
    
    CAPTCHA_SELECTORS = [
        "//div[contains(@class, 'captcha')]",
        "//img[contains(@src, 'captcha')]",
        "//div[contains(text(), '验证码')]",
        "//div[contains(text(), 'verification')]",
        "//div[contains(@class, 'verify')]",
        "//div[contains(@class, 'slider')]"
    ]


# Global configuration instance
config = ScrapingConfig()

# Ensure output directory exists
Path(config.output_directory).mkdir(exist_ok=True)