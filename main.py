import os
import sys
import time
import json
import yaml
import random
import logging
import datetime
import importlib.util
import subprocess
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from clear import logout_dari_google, hapus_cookies_menyeluruh, hapus_semua_data_browser, reset_browser_state
from colorama import Fore, init
import psutil 


# Initialize Colorama
init(autoreset=True)

# Colors for terminal text
B = Fore.BLUE
W = Fore.WHITE
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW




def banner():
    print(rf"""
{R}___.{W}( -_•){Y}▄︻テحكـ━一💥{R}__  .__  .__        __    
{R}\_ |__ _____    ____ |  | _|  | |__| ____ |  | __
{R} | __ \\__  \ _/ ___\|  |/ /  | |  |/    \|  |/ /
{R} | \_\ \/ __ \\  \___|    <|  |_|  |   |  \    < 
{R} |___  (____  /\___  >__|_ \____/__|___|  /__|_ \
{R}     \/     \/     \/     \/            \/     \/
{G}════════════ {W}SEO Website Optimization {G}════════════
""")


def clear_terminal():
    """
    Membersihkan terminal untuk semua OS (Windows, Linux, macOS)
    """
    try:
        # Windows
        if os.name == 'nt':
            os.system('cls')
        # Linux/macOS
        else:
            os.system('clear')
    except Exception as e:
        print(f"{R}Gagal membersihkan terminal: {e}{W}")


class NullLogger:
    """Logger yang tidak menulis ke file sama sekali - hanya console"""
    
    def __init__(self):
        pass
    
    def info(self, message):
        print(message)  # Hanya print ke console
    
    def error(self, message):
        print(f"{R}{message}{W}")  # Console dengan warna merah
    
    def warning(self, message):
        print(f"{Y}{message}{W}")  # Console dengan warna kuning
    
    def debug(self, message):
        print(f"{B}{message}{W}")  # Console dengan warna biru
    
    def critical(self, message):
        print(f"{R}{message}{W}") 


class CleanConsoleLogger:
    """Logger dengan output console bersih dan file lengkap"""
    
    def __init__(self, log_file='bot.log', level='INFO'):
        # Setup file logger
        self.file_logger = logging.getLogger('bot_file_logger')
        self.file_logger.setLevel(getattr(logging, level))
        
        # Clear existing handlers
        self.file_logger.handlers.clear()
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.file_logger.addHandler(file_handler)
        self.file_logger.propagate = False
    
    def info(self, message):
        print(message)  # Console bersih
        self.file_logger.info(message)  # File dengan timestamp
    
    def error(self, message):
        print(message)  # Console bersih
        self.file_logger.error(message)  # File dengan timestamp
    
    def warning(self, message):
        print(message)  # Console bersih
        self.file_logger.warning(message)  # File dengan timestamp

import re
from enum import Enum

class LinkFormat(Enum):
    HTML = "html"           # <a href="url">text</a>
    MARKDOWN = "markdown"   # [text](url)
    BBCODE = "bbcode"      # [url=link]text[/url]
    PLAIN = "plain"        # text: url
    TEXT_ONLY = "text"     # hanya text tanpa link


class BacklinkBot:
    def __init__(self, config_path: str = "config.yaml", headless_override: bool = False, gui_override: bool = False):
        self.config = self.load_config(config_path)
        self.headless_override = headless_override
        self.gui_override = gui_override
        self.setup_logging()
        self.templates_cache = self.load_cache()
        self.element_cache = self.load_element_cache()
        self.driver = None
        self.comments_list = self.load_comments()  # ✅ TAMBAH INI

    def get_chrome_version(self):
        """Deteksi versi Chrome yang terinstal"""
        try:
            # Windows
            if os.name == 'nt':
                try:
                    # Method 1: Registry
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                    version, _ = winreg.QueryValueEx(key, "version")
                    winreg.CloseKey(key)
                    major_version = int(version.split('.')[0])
                    self.logger.info(f"🔍 Versi Chrome terdeteksi: {version} (major: {major_version})")
                    return major_version
                except Exception as e1:
                    try:
                        # Method 2: Command line
                        result = subprocess.run([
                            'reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon',
                            '/v', 'version'
                        ], capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            version_match = re.search(r'version\s+REG_SZ\s+(\d+)', result.stdout)
                            if version_match:
                                major_version = int(version_match.group(1))
                                self.logger.info(f"🔍 Versi Chrome terdeteksi: {major_version}")
                                return major_version
                    except Exception as e2:
                        pass
            
            # Linux/Mac
            else:
                commands = [
                    ['google-chrome', '--version'],
                    ['google-chrome-stable', '--version'],
                    ['chromium-browser', '--version'],
                    ['chromium', '--version'],
                    ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version']
                ]
                
                for cmd in commands:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            version_match = re.search(r'(\d+)\.', result.stdout)
                            if version_match:
                                major_version = int(version_match.group(1))
                                self.logger.info(f"🔍 Versi Chrome terdeteksi: {major_version}")
                                return major_version
                    except Exception as e:
                        continue
            
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error detecting Chrome version: {e}")
            return None

    def setup_driver(self):
        """Setup Chrome driver dengan konfigurasi anti-detection yang lebih baik"""
        try:
            banner()
            self.logger.info("🚀 Menginisialisasi Chrome driver...")
            
            
            chrome_version = self.get_chrome_version()
            
            options = uc.ChromeOptions()
            browser_config = self.config.get('browser', {})
            
            # Mode browser
            if self.gui_override:
                headless_mode = False
                self.logger.info("🖥️ Mode GUI dipaksa aktif (override config)")
            elif self.headless_override:
                headless_mode = True
                self.logger.info("🔇 Mode Headless dipaksa aktif (override config)")
            else:
                headless_mode = browser_config.get('headless', False)
            
            # BASIC ANTI-DETECTION OPTIONS (Compatible dengan semua versi)
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            # SAFE OPTIONS untuk Chrome 137+
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins-discovery')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            
            # USER AGENT
            natural_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
            options.add_argument(f'--user-agent={natural_user_agent}')
            
            # LANGUAGE & LOCALE
            options.add_argument('--lang=en-US,en')
            options.add_argument('--accept-lang=en-US,en;q=0.9')
            
            if headless_mode:
                options.add_argument('--headless')
            
            # PREFS (Safe untuk semua versi)
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "geolocation": 2,
                    "media_stream": 2,
                },
                "profile.managed_default_content_settings": {
                    "images": 1
                },
                "profile.default_content_settings": {
                    "popups": 0
                }
            }
            options.add_experimental_option("prefs", prefs)
            
            # VERSION-AWARE EXPERIMENTAL OPTIONS
            try:
                # Hanya untuk Chrome < 130 (versi lama)
                if chrome_version and chrome_version < 130:
                    options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    options.add_experimental_option('useAutomationExtension', False)
                    self.logger.info(f"🔧 Using legacy options for Chrome {chrome_version}")
                else:
                    # Chrome 130+ - gunakan options yang lebih aman
                    options.add_argument('--disable-automation')
                    options.add_argument('--disable-extensions-except')
                    self.logger.info(f"🔧 Using modern options for Chrome {chrome_version}")
            except Exception as e:
                self.logger.warning(f"⚠️ Error setting experimental options: {e}")
            
            try:
                if chrome_version:
                    self.driver = uc.Chrome(
                        options=options,
                        version_main=chrome_version,
                        use_subprocess=True
                    )
                else:
                    self.driver = uc.Chrome(options=options)
                
                # ANTI-DETECTION SCRIPTS (Safe untuk semua versi)
                try:
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
                    self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error executing anti-detection scripts: {e}")
                
                self.setup_window_size()
                self.logger.info("✅ Chrome driver berhasil diinisialisasi")
                return True
                
            except Exception as e:
                self.logger.warning(f"⚠️ Error dengan konfigurasi utama: {e}")
                # Fallback ke konfigurasi MINIMAL dan AMAN
                return self._setup_fallback_driver(headless_mode)
                
        except Exception as e:
            self.logger.error(f"❌ Error setup driver: {str(e)}")
            return False

    def _setup_fallback_driver(self, headless_mode: bool) -> bool:
        """Setup driver dengan konfigurasi minimal yang pasti aman"""
        try:
            self.logger.info("🔄 Mencoba konfigurasi minimal...")
            
            options = uc.ChromeOptions()
            
            # HANYA OPTIONS YANG PASTI AMAN
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            if headless_mode:
                options.add_argument('--headless')
            
            # Coba tanpa version detection
            self.driver = uc.Chrome(options=options)
            
            if self.driver:
                self.logger.info("✅ Chrome driver berhasil diinisialisasi dengan konfigurasi minimal")
                return True
            else:
                self.logger.error("❌ Gagal inisialisasi driver bahkan dengan config minimal")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Fallback driver setup failed: {e}")
            self.driver = None
            return False


    def setup_window_size(self):
        """Setup ukuran dan posisi window browser"""
        try:
            browser_config = self.config.get('browser', {})
            
            if not self.headless_override and not browser_config.get('headless', False):
                # Dapatkan resolusi layar
                screen_width = self.driver.execute_script("return window.screen.width")
                screen_height = self.driver.execute_script("return window.screen.height")
                
                # Atur ukuran jendela browser (80% dari layar)
                window_width = int(screen_width * 0.8)
                window_height = screen_height
                
                # Atur posisi jendela
                position_x = 0
                position_y = 0
                
                # Apply settings
                self.driver.set_window_size(window_width, window_height)
                self.driver.set_window_position(position_x, position_y)
                
                self.logger.info(f"🖥️ Window size: {window_width}x{window_height} at ({position_x},{position_y})")
            else:
                # Headless mode - set default size
                window_size = browser_config.get('window_size', '1280,720')
                width, height = window_size.split(',')
                self.driver.set_window_size(int(width), int(height))
                self.logger.info(f"🔇 Headless window size: {window_size}")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error setting window size: {e}")

    def perform_browser_cleanup(self, template_name: str = None):
        """Perform browser cleanup berdasarkan template config"""
        try:
            if not template_name:
                return False
            
            # Load template config
            template_path = os.path.join("templates", template_name)
            config_file = os.path.join(template_path, "config.yaml")
            
            if not os.path.exists(config_file):
                return False
            
            with open(config_file, 'r', encoding='utf-8') as file:
                template_config = yaml.safe_load(file)
            
            # Cek apakah cleanup enabled
            cleanup_config = template_config.get('settings', {}).get('browser_cleanup', {})
            
            if not cleanup_config.get('enabled', False):
                self.logger.info(f"🔧 Browser cleanup disabled untuk template {template_name}")
                return False
            
            # Cek timing
            when_cleanup = cleanup_config.get('when', 'never')
            if when_cleanup == 'never':
                return False
            
            self.logger.info(f"🧹 Memulai browser cleanup untuk template {template_name}")
            
            methods = cleanup_config.get('methods', {})
            cleanup_success = True
            
            # 1. Logout dari Google
            if methods.get('logout_google', False):
                try:
                    if logout_dari_google(self.driver, self.logger):
                        self.logger.info("✅ Logout Google berhasil")
                    else:
                        self.logger.warning("⚠️ Logout Google gagal")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error logout Google: {e}")
                    cleanup_success = False
            
            # 2. Hapus cookies
            if methods.get('clear_cookies', False):
                try:
                    if hapus_cookies_menyeluruh(self.driver, self.logger):
                        self.logger.info("✅ Clear cookies berhasil")
                    else:
                        self.logger.warning("⚠️ Clear cookies gagal")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error clear cookies: {e}")
                    cleanup_success = False
            
            # 3. Hapus browser data
            if methods.get('clear_browser_data', False):
                try:
                    if hapus_semua_data_browser(self.driver, self.logger):
                        self.logger.info("✅ Clear browser data berhasil")
                    else:
                        self.logger.warning("⚠️ Clear browser data gagal")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error clear browser data: {e}")
                    cleanup_success = False
            
            # 4. Reset browser state
            if methods.get('reset_browser_state', False):
                try:
                    if reset_browser_state(self.driver, self.logger):
                        self.logger.info("✅ Reset browser state berhasil")
                    else:
                        self.logger.warning("⚠️ Reset browser state gagal")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error reset browser state: {e}")
                    cleanup_success = False
            
            # Delay setelah cleanup
            delay_after = cleanup_config.get('delay_after_cleanup', 3)
            if delay_after > 0:
                self.logger.info(f"⏳ Delay setelah cleanup: {delay_after} detik")
                time.sleep(delay_after)
            
            if cleanup_success:
                self.logger.info("✅ Browser cleanup selesai")
                # self.logger.info(f"{G}{"─" *60}")
            else:
                self.logger.warning("⚠️ Browser cleanup selesai dengan beberapa error")
            
            return cleanup_success
            
        except Exception as e:
            self.logger.error(f"❌ Error dalam browser cleanup: {e}")
            return False

    def should_cleanup_after_url(self, template_name: str = None) -> bool:
        """Cek apakah perlu cleanup setelah URL"""
        try:
            if not template_name:
                return False
            
            template_path = os.path.join("templates", template_name)
            config_file = os.path.join(template_path, "config.yaml")
            
            if not os.path.exists(config_file):
                return False
            
            with open(config_file, 'r', encoding='utf-8') as file:
                template_config = yaml.safe_load(file)
            
            cleanup_config = template_config.get('settings', {}).get('browser_cleanup', {})
            
            return (cleanup_config.get('enabled', False) and 
                   cleanup_config.get('when', 'never') == 'after_each_url')
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error checking cleanup config: {e}")
            return False

    def load_config(self, config_path: str) -> Dict:
        """Load konfigurasi dari file YAML"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"❌ File konfigurasi {config_path} tidak ditemukan")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML: {e}")
            sys.exit(1)

    # def setup_logging(self):
    #     """Setup clean console logger"""
    #     log_config = self.config.get('logging', {})
    #     log_level = log_config.get('level', 'INFO')
    #     log_file = log_config.get('file', 'bot.log')
        
    #     self.logger = CleanConsoleLogger(log_file, log_level)

    def setup_logging(self):
        """Setup clean console logger"""
        log_config = self.config.get('logging', {})
        
        # ✅ CEK DISABLED FLAG
        if log_config.get('disabled', False):
            print(f"{G}🚫 File logging disabled - console only mode{W}")
            self.logger = NullLogger()
            
            # ✅ HAPUS FILE bot.log JIKA ADA
            if os.path.exists('bot.log'):
                try:
                    os.remove('bot.log')
                    print(f"{G}🗑️ Existing bot.log file removed{W}")
                except Exception as e:
                    print(f"{Y}⚠️ Could not remove bot.log: {e}{W}")
            
            return
        
        # ✅ LOGGING NORMAL JIKA TIDAK DISABLED
        log_level = log_config.get('level', 'INFO')
        log_file = log_config.get('file', 'bot.log')
        
        print(f"{G}📝 File logging enabled - writing to {log_file}{W}")
        self.logger = CleanConsoleLogger(log_file, log_level)


    def get_processed_urls(self, source_file="list.txt"):
        """Ambil daftar URLs yang sudah berhasil diproses dari results folder"""
        processed_urls = set()
        
        try:
            results_dir = "results"
            if not os.path.exists(results_dir):
                return processed_urls
            
            # Ambil semua folder results dan urutkan (terbaru dulu)
            folders = [f for f in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, f))]
            if not folders:
                return processed_urls
            
            # Sort folders berdasarkan timestamp (format: YYYYMMDD_HHMMSS)
            folders.sort(reverse=True)
            
            print(f"{G}🔍 Checking processed URLs from recent sessions (source: {source_file})...{W}")
            
            # Cek beberapa session terakhir untuk memastikan tidak ada yang terlewat
            for folder in folders[:3]:  # Cek 3 session terakhir
                success_file = os.path.join(results_dir, folder, f"success_{folder}.txt")
                
                if os.path.exists(success_file):
                    with open(success_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            url = line.strip()
                            if url and url.startswith('http'):
                                processed_urls.add(url)
                    
                    print(f"{Y}📁 Session {folder}: {len(processed_urls)} URLs found{W}")
            
            return processed_urls
            
        except Exception as e:
            print(f"{R}⚠️ Error reading processed URLs: {e}{W}")
            return set()

    def load_urls_with_resume(self, file_path="list.txt"):
        """Load URLs dengan resume functionality"""
        try:
            # 1. Baca semua URLs dari list.txt
            if not os.path.exists(file_path):
                print(f"{R}❌ File {file_path} tidak ditemukan{W}")
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                all_urls = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]
            
            if not all_urls:
                print(f"{R}❌ Tidak ada URL valid di {file_path}{W}")
                return []
            
            # 2. Cek URLs yang sudah berhasil diproses
            processed_urls = self.get_processed_urls(file_path)
            
            # 3. Filter URLs yang belum diproses
            remaining_urls = []
            skipped_count = 0
            
            for url in all_urls:
                if url in processed_urls:
                    skipped_count += 1
                else:
                    remaining_urls.append(url)
            
            # 4. Display summary
            print(f"{G}{'='*60}{W}")
            print(f"{G}📊 RESUME ANALYSIS SUMMARY{W}")
            print(f"{G}{'='*60}{W}")
            print(f"{W}📁 Source file: {G}{file_path}{W}")
            print(f"{W}📋 Total URLs in file: {G}{len(all_urls)}{W}")
            print(f"{W}✅ Already processed: {G}{len(processed_urls)}{W}")
            print(f"{W}⏭️ Skipped (already done): {Y}{skipped_count}{W}")
            print(f"{W}⏳ Remaining to process: {G}{len(remaining_urls)}{W}")
            print(f"{G}{'='*60}{W}")
            
            if skipped_count > 0:
                print(f"{Y}🔄 RESUME MODE: Skipping {skipped_count} already processed URLs{W}")
                print(f"{G}🚀 Starting from URL #{skipped_count + 1}{W}")
            else:
                print(f"{G}🆕 FRESH START: Processing all URLs{W}")
            
            print(f"{G}{'='*60}{W}")
            
            return remaining_urls
            
        except Exception as e:
            print(f"{R}❌ Error loading URLs with resume: {e}{W}")
            return []


    def show_resume_preview(self, remaining_urls, all_urls):
        """Tampilkan preview URLs yang akan diproses"""
        if not remaining_urls:
            print(f"{G}✅ ALL URLS COMPLETED! No remaining URLs to process.{W}")
            return
        
        processed_count = len(all_urls) - len(remaining_urls)
        
        print(f"{Y}📋 NEXT URLS TO PROCESS:{W}")
        print(f"{Y}{'─'*60}{W}")
        
        # Tampilkan 5 URL pertama yang akan diproses
        preview_count = min(5, len(remaining_urls))
        for i, url in enumerate(remaining_urls[:preview_count]):
            url_number = processed_count + i + 1
            print(f"{W}  {G}{url_number:2d}.{W} {url}")
        
        if len(remaining_urls) > preview_count:
            print(f"{W}  {Y}... and {len(remaining_urls) - preview_count} more URLs{W}")
        
        print(f"{Y}{"─" *60}")


    def confirm_resume_process(self, remaining_urls, file_path="list.txt"):
        """Konfirmasi sebelum memulai proses resume"""
        if not remaining_urls:
            print(f"{G}✅ ALL URLS in {file_path} COMPLETED!{W}")
            return False
        
        try:
            print(f"\n{Y}❓ Do you want to continue processing the remaining URLs from {file_path}?{W}")
            print(f"{W}   Press {G}ENTER{W} to continue, or {R}Ctrl+C{W} to cancel...")
            
            input()  # Wait for user input
            clear_terminal()
            return True
            
        except KeyboardInterrupt:
            print(f"\n{Y}🛑 Process cancelled by user{W}")
            return False

    def load_cache(self) -> Dict:
        """Load template cache"""
        if not self.config.get('cache', {}).get('enabled', True):
            return {}
        
        cache_file = self.config['cache']['file']
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except Exception as e:
                self.logger.warning(f"Error loading cache: {e}")
        return {}

    def load_element_cache(self) -> Dict:
        """Load element cache"""
        if not self.config.get('cache', {}).get('enabled', True):
            return {}
        
        cache_file = self.config.get('cache', {}).get('element_cache_file', 'cache/element_cache.json')
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as file:
                    cache_data = json.load(file)
                    return self.clean_expired_element_cache(cache_data)
            except Exception as e:
                self.logger.warning(f"Error loading element cache: {e}")
        return {}

    def clean_expired_element_cache(self, cache_data: Dict) -> Dict:
        """Bersihkan element cache yang expired"""
        element_ttl = self.config.get('cache', {}).get('element_ttl', 7200)
        
        # Jika TTL = 0, tidak ada yang expired (permanent cache)
        if element_ttl == 0:
            return cache_data
        
        current_time = time.time()
        
        cleaned_cache = {}
        for domain, domain_data in cache_data.items():
            cleaned_domain_data = {}
            for element_type, element_data in domain_data.items():
                if current_time - element_data.get('timestamp', 0) < element_ttl:
                    cleaned_domain_data[element_type] = element_data
            
            if cleaned_domain_data:
                cleaned_cache[domain] = cleaned_domain_data
        
        return cleaned_cache

    def save_cache(self):
        """Simpan template cache"""
        if not self.config.get('cache', {}).get('enabled', True):
            return
        
        cache_file = self.config['cache']['file']
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        try:
            with open(cache_file, 'w', encoding='utf-8') as file:
                json.dump(self.templates_cache, file, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving cache: {e}")


    def get_cached_selector(self, domain: str, element_type: str) -> Optional[str]:
        """Ambil selector dari element cache - output minimal"""
        try:
            if domain in self.element_cache:
                if element_type in self.element_cache[domain]:
                    cache_entry = self.element_cache[domain][element_type]
                    element_ttl = self.config.get('cache', {}).get('element_ttl', 7200)
                    
                    # Jika TTL = 0, cache permanent (tidak pernah expired)
                    if element_ttl == 0:
                        # ✅ HAPUS LOG - tidak perlu
                        return cache_entry['selector']
                    
                    current_time = time.time()
                    if current_time - cache_entry['timestamp'] < element_ttl:
                        # ✅ HAPUS LOG - tidak perlu
                        return cache_entry['selector']
                    else:
                        # Expired, hapus dari cache
                        del self.element_cache[domain][element_type]
                        if not self.element_cache[domain]:
                            del self.element_cache[domain]
                        self.save_element_cache()
            
            # ✅ HAPUS LOG "No cached selector" - tidak perlu
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error getting cached selector: {e}")
            return None


    def cache_selector(self, domain: str, element_type: str, selector: str):
        """Simpan selector ke element cache - output minimal"""
        try:
            if domain not in self.element_cache:
                self.element_cache[domain] = {}
            
            self.element_cache[domain][element_type] = {
                'selector': selector,
                'timestamp': time.time()
            }
            
            self.save_element_cache()
            # ✅ HANYA LOG SELECTOR YANG DITEMUKAN
            self.logger.info(f"selector untuk {domain} {element_type}: {selector}")
            
        except Exception as e:
            self.logger.error(f"❌ Error caching selector: {e}")


    def save_element_cache(self):
        """Simpan element cache tanpa log detail"""
        if not self.config.get('cache', {}).get('enabled', True):
            return
        
        try:
            cache_file = self.config.get('cache', {}).get('element_cache_file', 'cache/element_cache.json')
            
            # ✅ PASTIKAN DIREKTORI ADA
            cache_dir = os.path.dirname(cache_file)
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir, exist_ok=True)
            
            # ✅ SAVE CACHE TANPA LOG
            with open(cache_file, 'w', encoding='utf-8') as file:
                json.dump(self.element_cache, file, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"❌ Error saving element cache: {e}")
            
            # ✅ FALLBACK SAVE
            try:
                fallback_file = "element_cache_fallback.json"
                with open(fallback_file, 'w', encoding='utf-8') as file:
                    json.dump(self.element_cache, file, indent=2, ensure_ascii=False)
            except Exception as e2:
                self.logger.error(f"❌ Fallback save failed: {e2}")

    def detect_website_template(self, url: str) -> Optional[str]:
        """Deteksi template website dengan output yang disederhanakan"""
        domain = urlparse(url).netloc.lower()
        
        # Cek cache terlebih dahulu
        if domain in self.templates_cache:
            template_name = self.templates_cache[domain]
            return template_name
        
        self.wait_for_content_loaded()
        
        templates_dir = "templates"
        if not os.path.exists(templates_dir):
            return None
        
        available_templates = [f for f in os.listdir(templates_dir) if os.path.isdir(os.path.join(templates_dir, f))]
        
        for template_name in available_templates:
            template_path = os.path.join(templates_dir, template_name)
            config_file = os.path.join(template_path, "config.yaml")
            
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as file:
                        template_config = yaml.safe_load(file)
                    
                    # 1. Cek domain yang sudah terdaftar
                    if self.is_domain_match(domain, template_config.get('domains', [])):
                        self.templates_cache[domain] = template_name
                        self.save_cache()
                        return template_name
                    
                    # 2. Auto-detection
                    if self.test_template_compatibility_simple(template_name, template_config):
                        self.add_domain_to_template_silent(template_name, domain, template_config)
                        self.templates_cache[domain] = template_name
                        self.save_cache()
                        return template_name
                        
                except Exception as e:
                    pass
        
        return None



    def test_template_compatibility_simple(self, template_name: str, template_config: Dict) -> bool:
        """Test template compatibility dengan output minimal"""
        try:
            # ✅ KHUSUS untuk Wix
            if template_name == "Wix":
                return self.test_wix_detection_silent(template_config)
            
            # ✅ KHUSUS untuk WordPress
            elif template_name == "Wordpress":
                return self.test_wordpress_detection_advanced(template_config)
            
            # UNTUK TEMPLATE LAIN
            else:
                selectors = template_config.get('selectors', {})
                found_elements = 0
                total_elements = 0
                
                critical_selectors = ['comment_form', 'name_field', 'email_field', 'comment_field']
                
                for selector_name in critical_selectors:
                    if selector_name in selectors:
                        total_elements += 1
                        selector = selectors[selector_name]
                        
                        try:
                            elements = self.driver.find_elements("css selector", selector)
                            if elements and elements[0].is_displayed():
                                found_elements += 1
                        except Exception as e:
                            pass
                
                if total_elements > 0:
                    compatibility_score = found_elements / total_elements
                    return compatibility_score >= 0.5
                else:
                    return False
            
        except Exception as e:
            return False


    def test_wordpress_detection_advanced(self, template_config: Dict) -> bool:
        """Enhanced WordPress detection - SILENT MODE"""
        try:
            found_indicators = 0
            page_source = self.driver.page_source.lower()
            current_url = self.driver.current_url.lower()
            
            # ✅ CEK URL PATTERNS
            url_patterns = [
                "wp-content", 
                "wp-includes", 
                "wordpress", 
                "/wp-json/", 
                "wp-admin",
                "wp-comments-post.php"
            ]
            
            for pattern in url_patterns:
                if pattern in current_url or pattern in page_source:
                    found_indicators += 1
                    break
            
            # ✅ CEK COMMENT FORM SELECTORS
            comment_selectors = [
                "#commentform", 
                "#respond", 
                ".comment-form", 
                "form[action*='comment']",
                "form[action*='wp-comments-post']"
            ]
            for selector in comment_selectors:
                try:
                    elements = self.driver.find_elements("css selector", selector)
                    if elements and elements[0].is_displayed():
                        found_indicators += 1
                        break
                except:
                    continue
            
            return found_indicators >= 1
            
        except Exception as e:
            return False

    def test_wix_detection_silent(self, template_config: Dict) -> bool:
        """Test Wix detection tanpa verbose log"""
        try:
            meta_generator = self.driver.find_element("css selector", "meta[name='generator']")
            content = meta_generator.get_attribute("content")
            return content and "Wix.com Website Builder" in content
        except:
            return False

    def add_domain_to_template_silent(self, template_name: str, domain: str, template_config: Dict) -> bool:
        """Tambahkan domain ke template tanpa verbose log"""
        try:
            template_path = os.path.join("templates", template_name)
            config_file = os.path.join(template_path, "config.yaml")
            
            # Backup original config (silent)
            backup_file = config_file + ".backup"
            if not os.path.exists(backup_file):
                import shutil
                shutil.copy2(config_file, backup_file)
            
            # Tambahkan domain ke list
            if 'domains' not in template_config:
                template_config['domains'] = []
            
            if domain not in template_config['domains']:
                template_config['domains'].append(domain)
                
                # Simpan kembali ke file
                with open(config_file, 'w', encoding='utf-8') as file:
                    yaml.dump(template_config, file, 
                            default_flow_style=False, 
                            allow_unicode=True,
                            sort_keys=False,
                            indent=2)
                return True
            
            return True
            
        except Exception as e:
            return False




    def test_wix_detection(self, template_config: Dict) -> bool:
        """Test khusus untuk deteksi Wix berdasarkan meta generator SAJA"""
        try:
            self.logger.info("🔍 Testing Wix detection...")
            
            # HANYA cek meta generator - tidak ada yang lain
            try:
                meta_generator = self.driver.find_element("css selector", "meta[name='generator']")
                content = meta_generator.get_attribute("content")
                if content and "Wix.com Website Builder" in content:
                    self.logger.info(f"✅ Wix meta generator ditemukan: {content}")
                    return True
                else:
                    self.logger.info(f"❌ Meta generator bukan Wix: {content}")
                    return False
            except Exception as e:
                self.logger.info(f"❌ Meta generator tidak ditemukan: {e}")
                return False
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error testing Wix detection: {e}")
            return False


    def test_template_compatibility(self, template_name: str, template_config: Dict) -> bool:
        """Test apakah template cocok dengan website saat ini - UPDATED"""
        try:
            self.logger.info(f"🧪 Testing template {template_name}...")
        
            # KHUSUS untuk Wix - Hanya cek meta generator tag
            if template_name == "Wix":
                if self.test_wix_detection(template_config):
                    self.logger.info(f"✅ Template {template_name} COCOK (Wix meta tag detected)")
                    return True
                else:
                    self.logger.info(f"❌ Template {template_name} TIDAK COCOK (No Wix meta tag)")
                    return False
        
            # UNTUK TEMPLATE LAIN (WordPress, Forum, dll) - Gunakan logic selector testing
            else:
                selectors = template_config.get('selectors', {})
                found_elements = 0
                total_elements = 0
            
                # Test selector utama
                critical_selectors = ['comment_form', 'name_field', 'email_field', 'comment_field']
            
                for selector_name in critical_selectors:
                    if selector_name in selectors:
                        total_elements += 1
                        selector = selectors[selector_name]
                    
                        try:
                            elements = self.driver.find_elements("css selector", selector)
                            if elements and elements[0].is_displayed():
                                found_elements += 1
                                self.logger.info(f"✅ Ditemukan {selector_name}: {selector}")
                            else:
                                self.logger.info(f"❌ Tidak ditemukan {selector_name}: {selector}")
                        except Exception as e:
                            self.logger.info(f"❌ Error testing {selector_name}: {e}")
            
                # Hitung compatibility score untuk template non-Wix
                if total_elements > 0:
                    compatibility_score = found_elements / total_elements
                    self.logger.info(f"📊 Compatibility score: {compatibility_score:.2f} ({found_elements}/{total_elements})")
                    return compatibility_score >= 0.5
                else:
                    self.logger.info(f"❌ No critical selectors found for {template_name}")
                    return False
            
        except Exception as e:
            self.logger.error(f"❌ Error testing template {template_name}: {e}")
            return False


    def add_domain_to_template(self, template_name: str, domain: str, template_config: Dict) -> bool:
        """Tambahkan domain ke template config (auto-learning)"""
        try:
            template_path = os.path.join("templates", template_name)
            config_file = os.path.join(template_path, "config.yaml")
            
            # Backup original config
            backup_file = config_file + ".backup"
            if not os.path.exists(backup_file):
                import shutil
                shutil.copy2(config_file, backup_file)
                self.logger.info(f"💾 Backup config dibuat: {backup_file}")
            
            # Tambahkan domain ke list
            if 'domains' not in template_config:
                template_config['domains'] = []
            
            if domain not in template_config['domains']:
                template_config['domains'].append(domain)
                
                # Simpan kembali ke file dengan format yang rapi
                with open(config_file, 'w', encoding='utf-8') as file:
                    yaml.dump(template_config, file, 
                             default_flow_style=False, 
                             allow_unicode=True,
                             sort_keys=False,
                             indent=2)
                
                self.logger.info(f"📚 AUTO-LEARNED: Domain {domain} ditambahkan ke template {template_name}")
                return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error menambahkan domain ke template: {e}")
            return False

    def smart_selector_detection(self, template_config: Dict) -> Dict:
        """Deteksi selector yang lebih akurat untuk website saat ini"""
        try:
            self.logger.info("🔍 Mencari selector yang lebih akurat...")
            
            # Selector alternatif untuk comment form
            comment_form_selectors = [
                "#commentform",
                "#respond", 
                ".comment-form",
                "form[id*='comment']",
                "form[class*='comment']",
                "#comment-form",
                ".commentform"
            ]
            
            # Selector alternatif untuk name field
            name_field_selectors = [
                "input[name='author']",
                "input[name='name']", 
                "input[id*='author']",
                "input[id*='name']",
                "input[placeholder*='name' i]",
                "input[placeholder*='nama' i]"
            ]
            
            # Selector alternatif untuk email field
            email_field_selectors = [
                "input[name='email']",
                "input[type='email']",
                "input[id*='email']",
                "input[placeholder*='email' i]"
            ]
            
            # Selector alternatif untuk comment field
            comment_field_selectors = [
                "textarea[name='comment']",
                "textarea[id*='comment']",
                "textarea[placeholder*='comment' i]",
                "textarea[placeholder*='komentar' i]",
                "#comment",
                ".comment-textarea"
            ]
            
            improved_selectors = {}
            
            # Test dan pilih selector terbaik
            for field_name, selectors_list in [
                ('comment_form', comment_form_selectors),
                ('name_field', name_field_selectors), 
                ('email_field', email_field_selectors),
                ('comment_field', comment_field_selectors)
            ]:
                for selector in selectors_list:
                    try:
                        elements = self.driver.find_elements("css selector", selector)
                        if elements and elements[0].is_displayed():
                            improved_selectors[field_name] = selector
                            self.logger.info(f"🎯 Selector terbaik untuk {field_name}: {selector}")
                            break
                    except:
                        continue
            
            return improved_selectors
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error dalam smart selector detection: {e}")
            return {}

    def update_template_selectors(self, template_name: str, improved_selectors: Dict):
        """Update template dengan selector yang lebih akurat"""
        try:
            if not improved_selectors:
                return
                
            template_path = os.path.join("templates", template_name)
            config_file = os.path.join(template_path, "config.yaml")
            
            with open(config_file, 'r', encoding='utf-8') as file:
                template_config = yaml.safe_load(file)
            
            # Update selectors
            if 'selectors' not in template_config:
                template_config['selectors'] = {}
                
            for field_name, selector in improved_selectors.items():
                template_config['selectors'][field_name] = selector
                self.logger.info(f"🔄 Updated {field_name} selector: {selector}")
            
            # Simpan kembali
            with open(config_file, 'w', encoding='utf-8') as file:
                yaml.dump(template_config, file, 
                         default_flow_style=False, 
                         allow_unicode=True,
                         sort_keys=False,
                         indent=2)
            
            self.logger.info(f"✅ Template {template_name} selectors updated")
            
        except Exception as e:
            self.logger.error(f"❌ Error updating template selectors: {e}")

    def is_domain_match(self, domain: str, domain_patterns: List[str]) -> bool:
        """Cek apakah domain cocok dengan pattern"""
        for pattern in domain_patterns:
            if pattern.startswith('*'):
                if domain.endswith(pattern[1:]):
                    return True
            elif pattern in domain:
                return True
        return False

    def load_template(self, template_name: str) -> Optional[Dict]:
        """Load template files"""
        template_path = os.path.join("templates", template_name)
        
        try:
            # Load actions module
            actions_file = os.path.join(template_path, "actions.py")
            if os.path.exists(actions_file):
                spec = importlib.util.spec_from_file_location("actions", actions_file)
                actions_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(actions_module)
            else:
                self.logger.error(f"File actions.py tidak ditemukan di {template_path}")
                return None
            
            # Load signature
            signature_file = os.path.join(template_path, "signature.yaml")
            signature_data = {}
            if os.path.exists(signature_file):
                with open(signature_file, 'r', encoding='utf-8') as file:
                    signature_data = yaml.safe_load(file)
            
            # Load comment template
            comment_template_file = os.path.join(template_path, "comment_template.txt")
            comment_template = ""
            if os.path.exists(comment_template_file):
                with open(comment_template_file, 'r', encoding='utf-8') as file:
                    comment_template = file.read()
            
            return {
                'actions': actions_module,
                'signature': signature_data,
                'comment_template': comment_template
            }
            
        except Exception as e:
            self.logger.error(f"Error loading template {template_name}: {str(e)}")
            return None



    def process_url(self, url: str, comment_data: Dict) -> bool:
        """Proses satu URL dengan smart waiting"""
        try:
            # ✅ LOG PROGRESS DENGAN TEMPLATE DETECTION DIGABUNG
            self.logger.info(f"📊 Progress: processing {url}")
            
            # Buka halaman
            self.driver.get(url)
            
            # Smart waiting untuk halaman selesai loading
            self.wait_for_page_load()
            
            # Deteksi template (SILENT)
            template_name = self.detect_website_template(url)
            
            if not template_name:
                # ✅ GABUNGKAN LOG JIKA TIDAK ADA TEMPLATE
                self.logger.error(f"🔍 Sedang memilih template : ❌ Tidak dapat mendeteksi template")
                return False
            
            # ✅ GABUNGKAN LOG TEMPLATE DETECTION
            self.logger.info(f"🔍 Sedang memilih template : Menggunakan template {G}{template_name}{W}")
            
            # Load template
            template = self.load_template(template_name)
            if not template or 'actions' not in template:
                self.logger.error(f"❌ Gagal load template {template_name}")
                return False
            
            # Post comment dengan retry untuk Wix
            if template_name == "Wix":
                success = template['actions'].post_comment_with_retry_limit(
                    self.driver,
                    comment_data,
                    template.get('comment_template', ''),
                    template.get('signature', {}),
                    self,
                    max_retries=3
                )
            else:
                success = template['actions'].post_comment(
                    self.driver,
                    comment_data,
                    template.get('comment_template', ''),
                    template.get('signature', {}),
                    self
                )
            
            if success:
                # ✅ HAPUS LOG DUPLIKASI INI
                # self.logger.info(f"✅ Berhasil posting komentar")
                pass
            else:
                self.logger.error(f"❌ Gagal posting komentar di {url}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error saat memproses {url}: {str(e)}")
            return False

    def wait_for_page_load(self, timeout: int = 30):
        """Smart waiting untuk halaman selesai loading"""
        try:
            self.logger.info("⏳ Menunggu halaman selesai loading...")
            
            # Wait untuk document ready
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            self.logger.info("✅ Document ready")
            
            # Wait untuk jQuery selesai (jika ada)
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda driver: driver.execute_script("return typeof jQuery === 'undefined' || jQuery.active === 0")
                )
                self.logger.info("✅ jQuery ready")
            except:
                pass  # jQuery mungkin tidak ada
            
            # Wait untuk loading indicators hilang
            self.wait_for_loading_indicators()
            
            # Extra delay untuk memastikan
            time.sleep(random.uniform(2, 4))
            self.logger.info("✅ Halaman siap diproses")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Timeout waiting for page load: {e}")
            # Fallback ke delay biasa
            time.sleep(random.uniform(5, 8))

    def wait_for_loading_indicators(self):
        """Wait untuk loading indicators hilang"""
        loading_selectors = [
            ".loading",
            ".loader",
            ".spinner",
            "#loading",
            "[class*='loading']",
            "[id*='loading']",
            ".preloader",
            "#preloader"
        ]
        
        for selector in loading_selectors:
            try:
                # Wait sampai loading indicator hilang
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                self.logger.info(f"✅ Loading indicator hilang: {selector}")
            except:
                pass  # Loading indicator mungkin tidak ada


    def wait_for_content_loaded(self):
        """Wait untuk content utama muncul - output minimal"""
        content_selectors = [
            "article",
            ".post",
            ".content",
            "#content",
            "main",
            ".main",
            "#main"
        ]
        
        for selector in content_selectors:
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                # ✅ HAPUS LOG INI UNTUK OUTPUT YANG LEBIH CLEAN
                # self.logger.info(f"✅ Content loaded: {selector}")
                return True
            except:
                continue
    
        # ✅ KEEP WARNING (untuk debugging)
        self.logger.warning("⚠️ Content selector tidak ditemukan, lanjut anyway")
        return False


    def save_results(self, success_urls: List[str], failed_urls: List[str], no_template_urls: List[str]):
        """Simpan hasil proses"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = os.path.join("results", timestamp)
        os.makedirs(results_dir, exist_ok=True)
        
        # File success
        success_file = os.path.join(results_dir, f"success_{timestamp}.txt")
        with open(success_file, 'w', encoding='utf-8') as f:
            for url in success_urls:
                f.write(f"{url}\n")
            self.logger.info(f"✅ {len(success_urls)} URL berhasil disimpan ke: {success_file}")
        
        # File failed (sama seperti sebelumnya)
        failed_file = os.path.join(results_dir, f"failed_{timestamp}.txt")
        with open(failed_file, 'w', encoding='utf-8') as f:
            for url in failed_urls:
                f.write(f"{url}\n")
            self.logger.info(f"❌ {len(failed_urls)} URL gagal disimpan ke: {failed_file}")
        
        # File no template (sama seperti sebelumnya)
        no_template_file = os.path.join(results_dir, f"no_template_{timestamp}.txt")
        with open(no_template_file, 'w', encoding='utf-8') as f:
            for url in no_template_urls:
                domain = urlparse(url).netloc.lower()
                f.write(f"{url}  # Domain: {domain}\n")
            self.logger.info(f"⚠️ {len(no_template_urls)} URL tanpa template disimpan ke: {no_template_file}")
        
        # File summary dengan URL tracking info
        summary_file = os.path.join(results_dir, f"summary_{timestamp}.txt")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Summary Report dengan URL Tracking - {datetime.datetime.now()}\n")
            f.write(f"# =====================================================\n\n")
            f.write(f"Total URL diproses: {len(success_urls) + len(failed_urls) + len(no_template_urls)}\n")
            f.write(f"✅ Berhasil: {len(success_urls)}\n")
            f.write(f"❌ Gagal: {len(failed_urls)}\n")
            f.write(f"⚠️ Tanpa Template: {len(no_template_urls)}\n\n")
            
            total_processed = len(success_urls) + len(failed_urls)
            if total_processed > 0:
                success_rate = len(success_urls) / total_processed * 100
                f.write(f"Success Rate: {success_rate:.1f}%\n\n")
            
            # URL Tracking Summary
            if success_urls:
                f.write("URL Tracking Summary:\n")
                f.write("====================\n")
                url_changed_count = 0
                for data in success_urls:
                    if data['original_url'] != data['final_url']:
                        url_changed_count += 1
            
                f.write(f"Total URL berubah setelah submit: {url_changed_count}/{len(success_urls)}\n")
                f.write(f"Persentase redirect: {url_changed_count/len(success_urls)*100:.1f}%\n\n")
            
                # Sample URL changes
                f.write("Sample URL Changes:\n")
                f.write("==================\n")
                change_count = 0
                for data in success_urls:
                    if data['original_url'] != data['final_url'] and change_count < 5:
                        f.write(f"Original: {data['original_url']}\n")
                        f.write(f"Final:    {data['final_url']}\n")
                        f.write(f"Time:     {data['timestamp']}\n\n")
                        change_count += 1
            
            # Domain yang perlu template baru
            if no_template_urls:
                f.write("Domain yang perlu template baru:\n")
                f.write("===============================\n")
                domains = set()
                for url in no_template_urls:
                    domains.add(urlparse(url).netloc.lower())
                for domain in sorted(domains):
                    f.write(f"- {domain}\n")
        
        self.logger.info(f"📊 Summary dengan URL tracking disimpan ke: {summary_file}")

    

    def detect_comment_format_support(self, template_name: str = None) -> LinkFormat:
        """Deteksi format link yang didukung website - UPDATED"""
        try:
            # ✅ GUNAKAN TEMPLATE_NAME PARAMETER LANGSUNG
            if template_name == "Wordpress":
                return LinkFormat.HTML
            elif template_name == "Wix":
                return LinkFormat.TEXT_ONLY
            
            # Cek dari template config
            if template_name:
                template_path = os.path.join("templates", template_name)
                config_file = os.path.join(template_path, "config.yaml")
                
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as file:
                        template_config = yaml.safe_load(file)
                    
                    # Cek setting link format
                    link_format = template_config.get('settings', {}).get('link_format', 'auto')
                    if link_format != 'auto':
                        return LinkFormat(link_format)
            
            # Auto-detect berdasarkan website
            current_url = self.driver.current_url
            domain = urlparse(current_url).netloc.lower()
            
            # Forum sites - biasanya BBCode
            if any(forum in domain for forum in ['forum', 'board', 'community']):
                return LinkFormat.BBCODE
            
            # GitHub/GitLab - Markdown
            if any(git in domain for git in ['github', 'gitlab', 'bitbucket']):
                return LinkFormat.MARKDOWN
            
            # Default: Test HTML support
            if self.test_html_support():
                return LinkFormat.HTML
            else:
                return LinkFormat.PLAIN
                
        except Exception as e:
            return LinkFormat.PLAIN




    def test_html_support(self) -> bool:
        """Test apakah website support HTML dalam komentar"""
        try:
            # Cari textarea komentar
            comment_field = self.driver.find_element("css selector", "textarea[name='comment']")
            
            # Cek atribut yang mengindikasikan HTML support
            field_class = comment_field.get_attribute("class") or ""
            field_id = comment_field.get_attribute("id") or ""
            
            # Indikator HTML editor
            html_indicators = [
                "rich", "editor", "wysiwyg", "tinymce", "ckeditor", 
                "html", "formatted", "markup"
            ]
            
            field_text = (field_class + " " + field_id).lower()
            for indicator in html_indicators:
                if indicator in field_text:
                    return True
            
            # Cek apakah ada toolbar editor
            try:
                toolbar_selectors = [
                    ".mce-toolbar", ".cke_toolbar", ".ql-toolbar",
                    "[class*='editor-toolbar']", "[class*='rich-editor']"
                ]
                
                for selector in toolbar_selectors:
                    if self.driver.find_elements("css selector", selector):
                        return True
            except:
                pass
                
            return False
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error testing HTML support: {e}")
            return False

    def process_comment_links(self, comment: str, link_format: LinkFormat = LinkFormat.PLAIN) -> str:
        """Process keyword links sesuai format yang didukung - SILENT MODE"""
        try:
            # ✅ TAMBAHAN: Skip processing untuk TEXT_ONLY (raw format)
            if link_format == LinkFormat.TEXT_ONLY:
                return comment  # Return raw comment dengan {text|url} utuh
            
            # Pattern untuk mendeteksi {keyword|url}
            pattern = r'\{([^|]+)\|([^}]+)\}'
            
            def replace_link(match):
                keyword = match.group(1).strip()
                url = match.group(2).strip()
                
                if link_format == LinkFormat.HTML:
                    return f'<a href="{url}" target="_blank">{keyword}</a>'
                elif link_format == LinkFormat.MARKDOWN:
                    return f'[{keyword}]({url})'
                elif link_format == LinkFormat.BBCODE:
                    return f'[url={url}]{keyword}[/url]'
                elif link_format == LinkFormat.PLAIN:
                    return f'{keyword} ({url})'
                else:
                    return f'{keyword} - {url}'
            
            # Replace semua keyword links
            processed_comment = re.sub(pattern, replace_link, comment)
            
            # ✅ HAPUS LOG VERBOSE - tidak ada log sama sekali
            
            return processed_comment
            
        except Exception as e:
            # ✅ SILENT ERROR - tidak ada log
            return comment


        
    #     return processed_comment

    def get_random_comment(self, template_name: str = None) -> str:
        """Ambil komentar random dengan format link yang sesuai - SILENT MODE"""
        if not self.comments_list:
            return "Thanks for sharing this valuable information!"
        
        # Pilih komentar random
        raw_comment = random.choice(self.comments_list)
        
        # Deteksi format link yang didukung
        link_format = self.detect_comment_format_support(template_name)
        
        # Process keyword links sesuai format
        processed_comment = self.process_comment_links(raw_comment, link_format)
        
        # ✅ HAPUS SEMUA LOG VERBOSE
        # Tidak ada log sama sekali
    
        return processed_comment


    def validate_comment_format(self, comment: str) -> bool:
        """Validasi format komentar dengan links"""
        try:
            # Cek apakah ada format link yang salah
            pattern = r'\{([^|]*)\|([^}]*)\}'
            matches = re.findall(pattern, comment)
            
            for keyword, url in matches:
                if not keyword.strip():
                    self.logger.warning(f"⚠️ Keyword kosong dalam: {comment[:30]}...")
                    return False
                
                if not url.strip() or not url.startswith(('http://', 'https://')):
                    self.logger.warning(f"⚠️ URL tidak valid '{url}' dalam: {comment[:30]}...")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error validating comment: {e}")
            return True  # Default allow

    def load_comments(self) -> List[str]:
        """Load komentar dari file dengan validasi"""
        try:
            comment_file = self.config['comment_data'].get('comment_file', 'komen.txt')
            
            if not os.path.exists(comment_file):
                self.logger.warning(f"⚠️ File komentar {comment_file} tidak ditemukan")
                return ["Thanks for sharing this valuable information!"]
            
            with open(comment_file, 'r', encoding='utf-8') as file:
                comments = []
                line_number = 0
                
                for line in file:
                    line_number += 1
                    line = line.strip()
                    
                    if line and not line.startswith('#'):
                        # Validasi format
                        if self.validate_comment_format(line):
                            comments.append(line)
                        else:
                            self.logger.warning(f"⚠️ Skip line {line_number}: format tidak valid")
            
            if not comments:
                self.logger.warning(f"⚠️ File {comment_file} kosong atau semua format salah")
                return ["Thanks for sharing this valuable information!"]
            
            # Count total links
            total_links = 0
            for comment in comments:
                total_links += len(re.findall(r'\{[^|]+\|[^}]+\}', comment))
            
            self.logger.info(f"📝 Loaded {len(comments)} komentar dengan {total_links} keyword links dari {comment_file}")
            return comments
            
        except Exception as e:
            self.logger.error(f"❌ Error loading comments: {e}")
            return ["Thanks for sharing this valuable information!"]

    def preview_comments(self):
        """Preview komentar yang akan digunakan"""
        self.logger.info("👀 Preview komentar yang tersedia:")
        
        for i, comment in enumerate(self.comments_list[:5], 1):  # Show first 5
            processed = self.process_comment_links(comment)
            self.logger.info(f"  {i}. Raw: {comment}")
            if processed != comment:
                self.logger.info(f"     Processed: {processed}")
        
        if len(self.comments_list) > 5:
            self.logger.info(f"  ... dan {len(self.comments_list) - 5} komentar lainnya")

    def prepare_comment_data(self, template_name: str = None) -> Dict:
        """Siapkan data komentar dengan random comment dan format yang sesuai"""
        comment_data = self.config['comment_data'].copy()
        
        # Ganti comment dengan random comment (dengan format link yang sesuai)
        comment_data['comment'] = self.get_random_comment(template_name)
        
        return comment_data


    def run(self, urls: List[str]):
        """Jalankan bot dengan real-time incremental saving"""
        if not urls:
            self.logger.error(f"❌ Tidak ada URL untuk diproses")
            return
        
        try:
            self.setup_driver()
            
            delay = self.config['app']['delay_between_comments']
            
            self.logger.info(f"🚀 Memulai proses untuk {G}{len(urls)} {W}URL")
            self.logger.info(f"📝 Total {G}{len(self.comments_list)} {W}komentar tersedia")
            self.logger.info(f"💾 {G}Real-time incremental saving aktif{W}")
            self.logger.info(f"{G}{'─' *60}")
            
            # ✅ COUNTER UNTUK STATISTIK AKHIR
            success_count = 0
            failed_count = 0
            no_template_count = 0
            
            for i, url in enumerate(urls, 1):
                current_template = None
                
                try:
                    # Buka halaman
                    self.driver.get(url)
                    time.sleep(random.uniform(3, 6))
                    
                    self.logger.info(f"📊 Progress: {G}{i}{W}/{G}{len(urls)} {W}- {Y}{url}")
                    
                    # Deteksi template (SILENT)
                    template_name = self.detect_website_template(url)
                    
                    if not template_name:
                        self.logger.info(f"🔍 Sedang memilih template : ❌ Tidak ada template yang cocok")
                        
                        # ✅ SAVE LANGSUNG
                        self.save_results_with_url_tracking({
                            'status': 'no_template',
                            'url': url
                        })
                        no_template_count += 1
                        continue
                    
                    self.logger.info(f"🔍 Sedang memilih template : Menggunakan template {G}{template_name}{W}")
                    
                    current_template = template_name
                    
                    # Load template
                    template = self.load_template(template_name)
                    if not template or 'actions' not in template:
                        self.logger.error(f"❌ Gagal load template {template_name}")
                        
                        # ✅ SAVE LANGSUNG
                        self.save_results_with_url_tracking({
                            'status': 'failed',
                            'url': url
                        })
                        failed_count += 1
                        continue
                    
                    # Siapkan comment data
                    comment_data = self.prepare_comment_data(template_name)
                    
                    # POST COMMENT
                    if template_name == "Wix":
                        result = template['actions'].post_comment_with_retry_limit(
                            self.driver,
                            comment_data,
                            template.get('comment_template', ''),
                            template.get('signature', {}),
                            self,
                            max_retries=3
                        )
                    else:
                        result = template['actions'].post_comment(
                            self.driver,
                            comment_data,
                            template.get('comment_template', ''),
                            template.get('signature', {}),
                            self
                        )
                    
                    # Handle return value
                    if isinstance(result, tuple):
                        success, final_url = result
                    else:
                        success = result
                        final_url = self.driver.current_url
                    
                    if success:
                        success_data = {
                            'original_url': url,
                            'final_url': final_url,
                            'timestamp': datetime.datetime.now().isoformat(),
                            'comment': comment_data['comment'][:100] + '...' if len(comment_data['comment']) > 100 else comment_data['comment'],
                            'detection_method': 'simplified_detection'
                        }
                        
                        # ✅ SAVE LANGSUNG
                        self.save_results_with_url_tracking({
                            'status': 'success',
                            'url': url,
                            'final_url': final_url,
                            'detail': success_data
                        })
                        success_count += 1
                        
                        self.logger.info(f"✅ {G}Berhasil posting komentar")
                        self.logger.info(f"{G}{'─' *60}")
                    else:
                        # ✅ SAVE LANGSUNG
                        self.save_results_with_url_tracking({
                            'status': 'failed',
                            'url': url
                        })
                        failed_count += 1
                
                except Exception as e:
                    self.logger.error(f"❌ Error memproses {url}: {str(e)}")
                    
                    # ✅ SAVE LANGSUNG
                    self.save_results_with_url_tracking({
                        'status': 'failed',
                        'url': url
                    })
                    failed_count += 1
                
                # Browser cleanup (tidak diubah)
                try:
                    if current_template and self.should_cleanup_after_url(current_template):
                        self.perform_browser_cleanup(current_template)
                except Exception as cleanup_error:
                    self.logger.warning(f"⚠️ Error dalam cleanup: {cleanup_error}")
                
                # Delay antar URL
                if i < len(urls):
                    self.logger.info(f"⏳ Menunggu {delay} detik...")
                    self.logger.info(f"{G}{'─' *60}")
                    time.sleep(delay)
            
            # ✅ BUAT SUMMARY di akhir
            self.create_final_summary()
            
            # Log final
            total_processed = success_count + failed_count
            if total_processed > 0:
                success_rate = success_count / total_processed * 100
                self.logger.info(f"🎯 Selesai! Berhasil: {G}{success_count}{W}/{G}{total_processed} {W}({G}{success_rate:.1f}{Y}%{W})")
            else:
                self.logger.info(f"🎯 Selesai! Tidak ada URL yang bisa diproses")
            
            if no_template_count > 0:
                self.logger.info(f"⚠️ {no_template_count} URL perlu template baru")
            
            self.logger.info(f"💾 {G}Hasil tersimpan di: {self.results_dir}")
            
        except Exception as e:
            self.logger.error(f"❌ Error menjalankan bot: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

    def save_results_with_url_tracking(self, url_data: dict):
        """Simpan hasil dengan URL tracking detail - Incremental saving only"""
        
        # ✅ SETUP SESSION FOLDER (jika belum ada)
        if not hasattr(self, 'session_timestamp') or not self.session_timestamp:
            self.session_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.results_dir = os.path.join("results", self.session_timestamp)
            os.makedirs(self.results_dir, exist_ok=True)
            self.logger.info(f"💾 Session folder: {self.results_dir}")
        
        try:
            status = url_data['status']
            url = url_data['url']
            
            if status == "success":
                success_file = os.path.join(self.results_dir, f"success_{self.session_timestamp}.txt")
                success_json_file = os.path.join(self.results_dir, f"success_detail_{self.session_timestamp}.json")
                
                # Append ke success file
                with open(success_file, 'a', encoding='utf-8') as f:
                    final_url = url_data.get('final_url', url)
                    f.write(f"{final_url}\n")
                
                # Update JSON file
                existing_data = []
                if os.path.exists(success_json_file):
                    try:
                        with open(success_json_file, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                    except:
                        existing_data = []
                
                existing_data.append(url_data.get('detail', {}))
                
                with open(success_json_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"💾 ✅ URL berhasil tersimpan")
                
            elif status == "failed":
                failed_file = os.path.join(self.results_dir, f"failed_{self.session_timestamp}.txt")
                with open(failed_file, 'a', encoding='utf-8') as f:
                    f.write(f"{url}\n")
                self.logger.info(f"💾 ❌ URL gagal tersimpan")
                
            elif status == "no_template":
                no_template_file = os.path.join(self.results_dir, f"no_template_{self.session_timestamp}.txt")
                domain = urlparse(url).netloc.lower()
                with open(no_template_file, 'a', encoding='utf-8') as f:
                    f.write(f"{url}  # Domain: {domain}\n")
                self.logger.info(f"💾 ⚠️ URL tanpa template tersimpan")
                
        except Exception as e:
            self.logger.error(f"❌ Error incremental save: {e}")

    # ✅ TAMBAH METHOD BARU INI
    def create_final_summary(self):
        """Buat summary file di akhir proses"""
        try:
            if not hasattr(self, 'results_dir') or not self.results_dir:
                return
                
            summary_file = os.path.join(self.results_dir, f"summary_{self.session_timestamp}.txt")
            
            # Hitung statistik dari file yang sudah ada
            success_count = 0
            failed_count = 0
            no_template_count = 0
            
            success_file = os.path.join(self.results_dir, f"success_{self.session_timestamp}.txt")
            failed_file = os.path.join(self.results_dir, f"failed_{self.session_timestamp}.txt")
            no_template_file = os.path.join(self.results_dir, f"no_template_{self.session_timestamp}.txt")
            
            # Count lines in each file
            for file_path, counter in [(success_file, 'success'), (failed_file, 'failed'), (no_template_file, 'no_template')]:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        count = sum(1 for line in f if line.strip())
                        if counter == 'success':
                            success_count = count
                        elif counter == 'failed':
                            failed_count = count
                        elif counter == 'no_template':
                            no_template_count = count
            
            # Buat summary
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"# Real-time Summary Report - {datetime.datetime.now()}\n")
                f.write(f"# ==========================================\n\n")
                f.write(f"Total URL diproses: {success_count + failed_count + no_template_count}\n")
                f.write(f"✅ Berhasil: {success_count}\n")
                f.write(f"❌ Gagal: {failed_count}\n")
                f.write(f"⚠️ Tanpa Template: {no_template_count}\n\n")
                
                total_processed = success_count + failed_count
                if total_processed > 0:
                    success_rate = success_count / total_processed * 100
                    f.write(f"Success Rate: {success_rate:.1f}%\n\n")
                
                f.write(f"Mode: Real-time incremental saving\n")
                f.write(f"Session: {self.session_timestamp}\n")
                
                # Domain yang perlu template baru
                if no_template_count > 0:
                    f.write("\nDomain yang perlu template baru:\n")
                    if os.path.exists(no_template_file):
                        domains = set()
                        with open(no_template_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                if '#' in line:
                                    domain = line.split('#')[1].replace('Domain:', '').strip()
                                    domains.add(domain)
                        for domain in sorted(domains):
                            f.write(f"- {domain}\n")
            
            self.logger.info(f"📊 Final summary disimpan: {summary_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Error creating final summary: {e}")




def load_urls_from_file(file_path: str) -> List[str]:
        """Load URLs dari file"""
        urls = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        urls.append(line)
        except FileNotFoundError:
            print(f"❌ File {file_path} tidak ditemukan")
        except Exception as e:
            print(f"❌ Error membaca file {file_path}: {e}")
        
        return urls

def main():
    """Main function"""
    banner()
    # print(f"{R}═" * 60)
    
    # Parse arguments
    headless_mode = False
    gui_mode = False
    urls = []
    source_file = None
    use_resume = True
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--headless":
            headless_mode = True
            print("🔇 Mode Headless diaktifkan")
        elif arg == "--gui":
            gui_mode = True
            print("🖥️ Mode GUI dipaksa aktif")
        elif arg == "--no-resume":
            use_resume = False
            print("🚫 Resume feature disabled")
        elif arg == "test" and i + 1 < len(sys.argv):
            url = sys.argv[i + 1]
            urls = [url]
            use_resume = False
            i += 1
        elif arg == "list" and i + 1 < len(sys.argv):
            source_file = sys.argv[i + 1]
            i += 1
        elif not arg.startswith('--'):
            print("✅ Argumen yang dapat digunakan")
            print("Usage:")
            print("  python main.py                                           # Mode GUI default, Menggunakan list.txt")
            print("  python main.py list <file>                               # Gunakan file URL custom dengan filter")
            print("  python main.py test <url>                                # Test satu URL saja")
            print("  python main.py --headless                                # Mode background tanpa tampilan browser")
            print("  python main.py --gui                                     # Paksa mode GUI (ada tampilan browser)")
            print("  python main.py --no-resume                               # Load semua URLs tanpa filter")
            print("")
            print("Contoh:")
            print("  python main.py list urls.txt                             # Filter URLs yang sudah diproses")
            print("  python main.py --no-resume list urls.txt                 # Load semua URLs dari awal")
            print("  python main.py --headless list urls.txt                  # Background mode dengan filter")
            print("  python main.py test https://example.com/blog/post        # Test satu URL")
            print("")
            print("Options:")
            print("  --headless    Jalankan browser di background (tanpa tampilan)")
            print("  --gui         Mode GUI (mengaktifkan tampilan browser)")
            print("  --no-resume   Load semua URLs dari awal (tidak filter yang sudah diproses)")
            print("")
            print("Resume Feature:")
            print("  🔄 Default: Filter URLs yang sudah berhasil diproses")
            print("  🚫 --no-resume: Load semua URLs tanpa melihat riwayat")

            return
        
        i += 1
    
    # ✅ TAMBAH RESUME LOGIC DI SINI
    bot = BacklinkBot(headless_override=headless_mode, gui_override=gui_mode)
    
    # Default ke list.txt dengan resume jika tidak ada URL
    if not urls:
        if not source_file:
            source_file = "list.txt"
        
        if use_resume:
            print(f"{G}🔄 Using resume functionality for {source_file}{W}")
            
            # ✅ GUNAKAN RESUME FEATURE
            urls = bot.load_urls_with_resume(source_file)
            
            if not urls:
                print(f"{G}🎉 ALL URLS in {source_file} COMPLETED! Nothing to process.{W}")
                return
            
            # Load semua URLs untuk preview
            with open(source_file, 'r', encoding='utf-8') as f:
                all_urls = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]
            
            # Tampilkan preview
            bot.show_resume_preview(urls, all_urls)
            
            # Konfirmasi user
            if not bot.confirm_resume_process(urls, source_file):
                return
        else:
            print(f"{Y}📁 Loading all URLs from {source_file} (no resume){W}")
            urls = load_urls_from_file(source_file)
    
    if not urls:
        print("❌ Tidak ada URL untuk diproses")
        return
    

    bot.run(urls)  

if __name__ == "__main__":
    clear_terminal()
    main()
