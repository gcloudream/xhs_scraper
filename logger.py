"""
Enhanced logging system for Xiaohongshu scraper
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class ColoredFormatter(logging.Formatter):
    """Colored console formatter"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class ScrapingLogger:
    """Enhanced logging system with structured logging capabilities"""
    
    def __init__(self, name: str = "xiaohongshu_scraper", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create main logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        self._setup_handlers()
        
        # Statistics tracking
        self.stats = {
            'start_time': datetime.now(),
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'captchas_encountered': 0,
            'posts_scraped': 0,
            'errors': []
        }
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for all logs
        log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Error handler for errors only
        error_file = self.log_dir / f"{self.name}_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional structured data"""
        self.logger.info(message)
        if kwargs:
            self.logger.debug(f"Additional data: {json.dumps(kwargs, ensure_ascii=False)}")
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message)
        if kwargs:
            self.logger.debug(f"Additional data: {json.dumps(kwargs, ensure_ascii=False)}")
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception"""
        self.logger.error(message)
        if exception:
            self.logger.error(f"Exception: {str(exception)}", exc_info=True)
        if kwargs:
            self.logger.error(f"Additional data: {json.dumps(kwargs, ensure_ascii=False)}")
        
        # Track error
        self.stats['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'exception': str(exception) if exception else None,
            'data': kwargs
        })
        self.stats['failed_requests'] += 1
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message)
        if kwargs:
            self.logger.debug(f"Additional data: {json.dumps(kwargs, ensure_ascii=False)}")
    
    def log_request(self, url: str, success: bool = True):
        """Log request statistics"""
        self.stats['requests_made'] += 1
        if success:
            self.stats['successful_requests'] += 1
            self.debug(f"Request successful: {url}")
        else:
            self.stats['failed_requests'] += 1
            self.warning(f"Request failed: {url}")
    
    def log_captcha(self, solved: bool = False):
        """Log captcha encounter"""
        self.stats['captchas_encountered'] += 1
        if solved:
            self.info("Captcha encountered and solved")
        else:
            self.warning("Captcha encountered but not solved")
    
    def log_post_scraped(self, title: str, keyword: str):
        """Log successful post scraping"""
        self.stats['posts_scraped'] += 1
        self.info(f"Post scraped: {title[:50]}...", keyword=keyword)
    
    def log_session_start(self, config_data: dict):
        """Log session start with configuration"""
        self.info("Scraping session started")
        self.debug("Configuration", config=config_data)
    
    def log_session_end(self):
        """Log session end with statistics"""
        duration = datetime.now() - self.stats['start_time']
        
        self.info("Scraping session completed")
        self.info(f"Session duration: {duration}")
        self.info(f"Total requests: {self.stats['requests_made']}")
        self.info(f"Successful requests: {self.stats['successful_requests']}")
        self.info(f"Failed requests: {self.stats['failed_requests']}")
        self.info(f"Captchas encountered: {self.stats['captchas_encountered']}")
        self.info(f"Posts scraped: {self.stats['posts_scraped']}")
        
        # Save detailed statistics
        stats_file = self.log_dir / f"session_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            stats_copy = self.stats.copy()
            stats_copy['start_time'] = stats_copy['start_time'].isoformat()
            stats_copy['end_time'] = datetime.now().isoformat()
            stats_copy['duration_seconds'] = duration.total_seconds()
            json.dump(stats_copy, f, ensure_ascii=False, indent=2)
        
        self.info(f"Detailed statistics saved to: {stats_file}")
    
    def get_stats(self) -> dict:
        """Get current statistics"""
        return self.stats.copy()


# Global logger instance
logger = ScrapingLogger()