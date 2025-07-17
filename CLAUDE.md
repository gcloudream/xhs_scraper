# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Xiaohongshu (Little Red Book) educational scraper designed for learning about fund investment knowledge. The project provides both basic and enhanced versions with advanced anti-detection capabilities.

**IMPORTANT**: This project is for educational purposes only - learning about fund investment from social media content.

## Development Commands

### Install Dependencies

**Basic version:**
```bash
pip3 install -r requirements.txt
```

**Enhanced version (recommended):**
```bash
pip3 install -r requirements_enhanced.txt
```

### Running the Scrapers

**Basic scraper:**
```bash
python3 xiaohongshu_fund_scraper.py
```

**Enhanced scraper (recommended):**
```bash
python3 enhanced_xiaohongshu_scraper.py
```

### Development Setup

1. Ensure Chrome browser is installed and up to date
2. Python 3.7+ required
3. Minimum 4GB RAM (8GB recommended)
4. Stable internet connection

## Project Architecture

### Core Components

1. **Main Scrapers**
   - `xiaohongshu_fund_scraper.py` - Basic version scraper
   - `enhanced_xiaohongshu_scraper.py` - Advanced version with anti-detection

2. **Anti-Detection System** (`anti_detection.py`)
   - Browser fingerprint spoofing (WebGL, Canvas, Audio)
   - Human behavior simulation with Bézier curves
   - Network fingerprint masking
   - Adaptive timing strategies

3. **Adaptive Selectors** (`adaptive_selectors.py`)
   - Dynamic element discovery system
   - Success rate tracking for selectors
   - Intelligent caching with performance data
   - Multiple fallback strategies

4. **Session Management** (`session_manager.py`)
   - Cookie pool management
   - Session rotation based on requests/time/errors
   - Proxy integration support
   - Persistent session state

5. **CAPTCHA Handling** (`captcha_solver.py`)
   - Multi-type CAPTCHA support (slide, click, rotate, puzzle)
   - Human-like operation simulation
   - Fallback strategies (refresh, back, manual)
   - Learning mechanism based on success rates

6. **Configuration** (`config.py`)
   - Pydantic-based configuration with validation
   - Environment variable support
   - Quality filters and spam detection
   - Comprehensive selector definitions

7. **Logging** (`logger.py`)
   - Enhanced logging system with colors
   - Performance monitoring
   - Structured output for debugging

### Data Flow

1. **Initialization**: Load configuration → Initialize anti-detection → Setup session management
2. **Navigation**: Human-like browser behavior → Handle CAPTCHAs → Adaptive element selection
3. **Data Extraction**: Use multiple selector strategies → Filter content quality → Apply deduplication
4. **Output**: Save to CSV/JSON → Generate statistics → Clean up resources

### Key Design Patterns

- **Modular Architecture**: Each major function is separated into its own module
- **Adaptive Behavior**: Systems learn and adapt based on success rates
- **Defensive Programming**: Multiple fallback strategies for robustness
- **Educational Focus**: Content filtering specifically for fund-related educational material

## Configuration Options

The `ScrapingConfig` class in `config.py` provides comprehensive configuration:

- **Browser Settings**: Headless mode, window size, user agent rotation
- **Anti-Detection**: Request delays, scroll timing, human behavior simulation
- **Scraping Limits**: Posts per keyword, scroll attempts, keyword limits
- **Quality Filters**: Spam keywords, required keywords, minimum lengths
- **Output Options**: CSV/JSON formats, output directory

## File Outputs

### Basic Version
- `fund_posts_enhanced.csv` - Scraped data in CSV format
- `fund_posts_enhanced.json` - Scraped data in JSON format

### Enhanced Version
- `output/enhanced_fund_posts_YYYYMMDD_HHMMSS.csv` - Timestamped CSV data
- `output/enhanced_fund_posts_YYYYMMDD_HHMMSS.json` - Timestamped JSON data
- `output/scraping_stats_YYYYMMDD_HHMMSS.json` - Performance statistics

### Cache Files
- `selector_cache.json` - Adaptive selector performance data
- `cookies/` - Session and cookie storage

## Development Notes

### Testing
No formal test framework is currently implemented. Test manually by:
1. Running with `headless=False` to observe behavior
2. Checking output files for data quality
3. Monitoring logs for errors or unusual behavior

### Debugging
- Set `headless=False` in config to see browser actions
- Check log output for detailed operation info
- Clear `selector_cache.json` if selectors become outdated
- Monitor `output/scraping_stats_*.json` for performance metrics

### Performance Considerations
- Memory usage can be high with large datasets
- Adjust `max_posts_per_keyword` to manage resources
- Use headless mode for better performance
- Monitor proxy performance if using proxy rotation

### Common Issues
1. **ChromeDriver version mismatch** - Update Chrome browser
2. **CAPTCHA failures** - Set `headless=False` for manual handling
3. **Selector failures** - Clear selector cache to force relearning
4. **Memory issues** - Reduce batch sizes and use headless mode

## Educational Purpose Compliance

This scraper is designed specifically for educational use in learning about fund investment:
- Content filtering ensures only fund-related educational content
- Respectful request timing to avoid server overload
- Quality filters remove promotional/spam content
- Deduplication prevents redundant data collection