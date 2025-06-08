import time
import random
import os
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from colorama import Fore, init
from selenium.webdriver.common.keys import Keys  # ✅ Tambah ini di atas
import yaml

# Initialize Colorama
init(autoreset=True)

# Colors for terminal text
B = Fore.BLUE
W = Fore.WHITE
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW


current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# ✅ SIMPLIFIED IMPORT MESSAGES
try:
    from secureimg_solver import solve_secureimg_captcha
    SECUREIMG_AVAILABLE = True
    # ✅ HAPUS LOG VERBOSE - akan digabung di bawah
except ImportError as e:
    SECUREIMG_AVAILABLE = False

try:
    from recaptcha import solve_recaptcha_v2
    RECAPTCHA_AVAILABLE = True
    # ✅ HAPUS LOG VERBOSE - akan digabung di bawah
except ImportError as e:
    RECAPTCHA_AVAILABLE = False

# ✅ GABUNG SEMUA MODULE STATUS JADI 1 LINE
modules_loaded = []
if SECUREIMG_AVAILABLE:
    modules_loaded.append("secureimg solver")
if RECAPTCHA_AVAILABLE:
    modules_loaded.append("reCAPTCHA")

if modules_loaded:
    print(f"{G}✅ {' '.join(modules_loaded)} API config loaded successfully{W}")
else:
    print(f"{Y}⚠️ No CAPTCHA solvers available{W}")




def close_popups_once(driver, bot_instance):
    """Tutup popup maksimal 5 kali per popup - setelah itu diabaikan"""
    
    # ✅ INISIALISASI TRACKING JIKA BELUM ADA
    if not hasattr(driver, '_popup_close_count'):
        driver._popup_close_count = {}
    
    popup_selectors = [
        '.modal', '.popup', '.overlay', '.lightbox',
        '.newsletter-popup', '.email-popup', '.subscribe-popup',
        '.cookie-banner', '.cookie-consent', '#cookie-notice',
        '[class*="modal"]', '[class*="popup"]', '[class*="overlay"]',
        '[class*="newsletter"]', '[class*="subscribe"]', '[class*="cookie"]',
        # ✅ TAMBAH SELECTOR BORLABS COOKIE
        '[data-borlabs-cookie-actions="close-button"]',
        '.brlbs-cmpnt-close-button',
        '[class*="brlbs"]',
        '[class*="borlabs"]',
        'button[class*="close"]',
        '.close-button',
        '[data-dismiss="modal"]',
        '[aria-label*="close" i]',
        '[aria-label*="schließen" i]'  # German close
    ]
    
    closed_count = 0
    for selector in popup_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.is_displayed():
                    # ✅ BUAT UNIQUE KEY untuk popup
                    popup_key = f"{selector}_{element.get_attribute('class')}_{element.get_attribute('id')}"
                    
                    # ✅ CEK BERAPA KALI POPUP INI SUDAH DITUTUP
                    close_count = driver._popup_close_count.get(popup_key, 0)
                    
                    if close_count < 5:  # ✅ MAKSIMAL 5 KALI
                        try:
                            # ✅ SMART CLOSE METHOD
                            if any(x in selector.lower() for x in ['close-button', 'button', 'data-borlabs']):
                                # Click untuk button
                                driver.execute_script("arguments[0].click();", element)
                            else:
                                # Hide untuk container
                                driver.execute_script("arguments[0].style.display = 'none';", element)
                            
                            # ✅ INCREMENT COUNTER
                            driver._popup_close_count[popup_key] = close_count + 1
                            closed_count += 1
                            
                        except:
                            continue
                    else:
                        # ✅ POPUP SUDAH DITUTUP 5 KALI - ABAIKAN
                        if close_count == 5:  # Log hanya sekali
                            bot_instance.logger.info(f"🛑 Popup diabaikan (limit 5x): {selector}")
                            driver._popup_close_count[popup_key] = 6  # Mark sebagai ignored
        except:
            continue
    
    if closed_count > 0:
        bot_instance.logger.info(f"🚫 Menutup {closed_count} popup")
    
    return closed_count

# end popup Borlabs Cookie

def scroll_and_find_comment_form(driver, bot_instance, target_selectors, max_wait_time=180):
    """Scroll dan cari comment form (show button sudah di-handle sebelumnya)"""
    
    start_time = time.time()
    scroll_position = 0
    max_scroll = driver.execute_script("return document.body.scrollHeight")
    scroll_step = max_scroll // 10 if max_scroll > 1000 else 100
    
    while time.time() - start_time < max_wait_time:
        # ✅ CEK COMMENT FORM (tanpa show button handling - sudah dilakukan sebelumnya)
        for selector in target_selectors:
            try:
                form_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for form in form_elements:
                    if form.is_displayed():
                        # Scroll ke form
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", form)
                        time.sleep(random.uniform(1, 2))
                        
                        bot_instance.logger.info(f"✅ Comment form ditemukan")
                        return form
                        
            except Exception as e:
                continue
        
        # ✅ SCROLL DOWN
        scroll_position += scroll_step
        if scroll_position >= max_scroll:
            scroll_position = max_scroll
        
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        time.sleep(random.uniform(0.5, 1.0))
        
        # Update max scroll height (untuk dynamic content)
        new_max_scroll = driver.execute_script("return document.body.scrollHeight")
        if new_max_scroll > max_scroll:
            max_scroll = new_max_scroll
        
        if scroll_position >= max_scroll:
            break
    
    return None

def check_popup_after_form_found(driver, bot_instance):
    """Cek popup setelah form ditemukan - output minimal"""
    time.sleep(1)  # Tunggu popup muncul
    
    popup_selectors = [
        '.modal', '.popup', '.overlay',
        '[class*="modal"]', '[class*="popup"]', '[class*="overlay"]'
    ]
    
    popup_found = False
    for selector in popup_selectors:
        try:
            popups = driver.find_elements(By.CSS_SELECTOR, selector)
            for popup in popups:
                if popup.is_displayed():
                    popup_found = True
                    try:
                        # Tutup dengan JavaScript
                        driver.execute_script("arguments[0].style.display = 'none';", popup)
                        # ✅ HANYA LOG JIKA BERHASIL TUTUP
                        bot_instance.logger.info("✅ Popup ditutup")
                    except:
                        pass  # ✅ HAPUS LOG ERROR
                    break
        except:
            continue
 

def click_empty_area(driver, bot_instance):
    """
    Click di area kosong - hanya tampilkan summary
    """
    try:
        # ✅ SIMPAN STATE AWAL
        initial_windows = driver.window_handles
        initial_window_count = len(initial_windows)
        main_window = driver.current_window_handle
        initial_url = driver.current_url
        
        # Strategy: Click di koordinat aman
        window_size = driver.get_window_size()
        width = window_size['width']
        height = window_size['height']
        
        # Koordinat yang biasanya aman
        safe_coordinates = [
            (width // 8, height // 12),
            (width // 6, height // 10),
            (width // 10, height // 8),
            (width - 50, 30),
            (30, height - 50),
            (width - 30, height - 30)
        ]
        
        successful_clicks = 0
        new_tabs_detected = 0
        
        for i, (safe_x, safe_y) in enumerate(safe_coordinates):
            try:
                # ✅ HAPUS LOG DETAIL PER CLICK
                windows_before_click = driver.window_handles
                
                # Click menggunakan JavaScript
                click_result = driver.execute_script(f"""
                    var x = {safe_x};
                    var y = {safe_y};
                    var element = document.elementFromPoint(x, y);
                    
                    if (element &&
                        element.tagName !== 'A' &&
                        element.tagName !== 'BUTTON' &&
                        element.tagName !== 'INPUT' &&
                        !element.closest('a') &&
                        !element.closest('button') &&
                        !element.closest('[role="button"]') &&
                        !element.closest('.social-share') &&
                        !element.closest('.external-link')) {{
                        
                        var event = new MouseEvent('click', {{
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: x,
                            clientY: y
                        }});
                        element.dispatchEvent(event);
                        
                        return {{
                            success: true,
                            elementTag: element.tagName,
                            elementClass: element.className || 'no-class'
                        }};
                    }} else {{
                        return {{
                            success: false,
                            reason: element ? 'Interactive element detected: ' + element.tagName : 'No element found',
                            elementTag: element ? element.tagName : 'null'
                        }};
                    }}
                """)
                
                if click_result and click_result.get('success'):
                    successful_clicks += 1
                    
                    # ✅ TUNGGU DAN CEK NEW TAB
                    time.sleep(0.5)
                    windows_after_click = driver.window_handles
                    
                    if len(windows_after_click) > len(windows_before_click):
                        new_tabs_count = len(windows_after_click) - len(windows_before_click)
                        new_tabs_detected += new_tabs_count
                        
                        # ✅ TUTUP NEW TABS TANPA LOG DETAIL
                        tabs_closed = close_new_tabs_wordpress(driver, windows_before_click, main_window, None, f"EmptyClick-{i+1}")
                        
                        # ✅ CEK URL SETELAH CLOSE TABS
                        current_url = driver.current_url
                        if current_url != initial_url:
                            driver.get(initial_url)
                            time.sleep(1)
                
                # Small delay between clicks
                time.sleep(random.uniform(0.3, 0.7))
                
            except Exception as e:
                continue
        
        # ✅ FINAL CHECK & CLEANUP
        final_windows = driver.window_handles
        if len(final_windows) > initial_window_count:
            final_tabs_closed = close_new_tabs_wordpress(driver, initial_windows, main_window, None, "FinalCleanup")
        
        # ✅ ENSURE MAIN WINDOW FOCUS
        if driver.current_window_handle != main_window:
            try:
                driver.switch_to.window(main_window)
            except:
                available_windows = driver.window_handles
                if available_windows:
                    driver.switch_to.window(available_windows[0])
        
        # ✅ HANYA TAMPILKAN SUMMARY
        bot_instance.logger.info(f"📊 [EmptyClick] Summary:")
        bot_instance.logger.info(f"   ✅ Successful clicks: {successful_clicks}/{len(safe_coordinates)}")
        bot_instance.logger.info(f"   🚨 New tabs detected: {new_tabs_detected}")
        bot_instance.logger.info(f"   🗑️ All new tabs closed: {'Yes' if len(driver.window_handles) == initial_window_count else 'No'}")
        bot_instance.logger.info(f"   🌐 URL stable: {'Yes' if driver.current_url == initial_url else 'No'}")
        bot_instance.logger.info(f"   📍 Final URL: {driver.current_url}")
        
        return True
        
    except Exception as e:
        bot_instance.logger.error(f"❌ Error click area kosong: {str(e)}")
        return False




def close_new_tabs_wordpress(driver, initial_windows, main_window, logger, context=""):
    """
    ✅ FUNGSI BARU: Tutup semua tab baru yang muncul (WordPress specific)
    """
    try:
        current_windows = driver.window_handles
        new_tabs_closed = 0
        
        if logger:
            logger.info(f"🔍 [{context}] Checking for new tabs...")
            logger.info(f"📊 [{context}] Initial: {len(initial_windows)}, Current: {len(current_windows)}")
        
        # Cari dan tutup tab baru
        for window_handle in current_windows:
            if window_handle not in initial_windows:
                try:
                    # Switch ke tab baru
                    driver.switch_to.window(window_handle)
                    new_tabs_closed += 1
                    
                    # Get info tab baru
                    try:
                        tab_url = driver.current_url
                        tab_title = driver.title[:50] if driver.title else "No title"
                        if logger:
                            logger.warning(f"🗑️ [{context}] Closing new tab #{new_tabs_closed}")
                            logger.warning(f"📄 [{context}] URL: {tab_url}")
                            logger.warning(f"📄 [{context}] Title: {tab_title}")
                    except:
                        if logger:
                            logger.warning(f"🗑️ [{context}] Closing new tab #{new_tabs_closed} (info unavailable)")
                    
                    # Tutup tab
                    driver.close()
                    
                    if logger:
                        logger.info(f"✅ [{context}] Tab #{new_tabs_closed} berhasil ditutup")
                    
                except Exception as e:
                    if logger:
                        logger.error(f"❌ [{context}] Error closing tab: {e}")
        
        # Kembali ke main window
        try:
            driver.switch_to.window(main_window)
            if logger:
                logger.info(f"🔄 [{context}] Switched back to main window")
        except Exception as e:
            # Jika main window tidak ada, ambil window pertama yang tersisa
            remaining_windows = driver.window_handles
            if remaining_windows:
                driver.switch_to.window(remaining_windows[0])
                if logger:
                    logger.warning(f"⚠️ [{context}] Main window unavailable, switched to first available window")
            else:
                if logger:
                    logger.error(f"❌ [{context}] No windows available!")
        
        if new_tabs_closed > 0:
            if logger:
                logger.info(f"🎯 [{context}] Summary: {new_tabs_closed} new tab(s) closed")
        else:
            if logger:
                logger.info(f"ℹ️ [{context}] No new tabs found")
        
        return new_tabs_closed
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [{context}] Error in close_new_tabs_wordpress: {e}")
        return 0


def find_comment_form_direct(driver, target_selectors):
    """Cari comment form langsung tanpa scroll"""
    try:
        for selector in target_selectors:
            try:
                form_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for form in form_elements:
                    if form.is_displayed():
                        return form
            except:
                continue
        return None
    except:
        return None



def check_captcha(form_element, bot_instance):
    """Cek apakah ada captcha yang perlu diselesaikan - Clean output"""
    try:
        # ✅ HANYA 2 CAPTCHA TYPE YANG DIDUKUNG
        captcha_selectors = [
            '#secureimg',             # secureimg CAPTCHA
            '.g-recaptcha',           # reCAPTCHA v2
        ]
        
        bot_instance.logger.info("🔍 Scanning for CAPTCHA elements...")
        
        for selector in captcha_selectors:
            try:
                captcha = form_element.find_element(By.CSS_SELECTOR, selector)
                if captcha.is_displayed():
                    # ✅ LANGSUNG HANDLE TANPA LOG DUPLIKAT
                    
                    # ✅ HANDLE SECUREIMG CAPTCHA
                    if selector == '#secureimg':
                        if SECUREIMG_AVAILABLE:
                            bot_instance.logger.info("🖼️ #secureimg CAPTCHA detected - solving...")
                            success = solve_secureimg_captcha(bot_instance.driver, bot_instance.logger)
                            if success:
                                bot_instance.logger.info("✅ CAPTCHA berhasil diselesaikan")
                                return False  # Continue with form submission
                            else:
                                bot_instance.logger.error("❌ CAPTCHA gagal diselesaikan")
                                return True   # Skip form submission
                        else:
                            bot_instance.logger.warning("⚠️ secureimg solver not available")
                            return True
                    
                    # ✅ HANDLE RECAPTCHA
                    elif selector == '.g-recaptcha':
                        if RECAPTCHA_AVAILABLE:
                            bot_instance.logger.info("🎯 reCAPTCHA detected - solving...")
                            success = solve_recaptcha_v2(bot_instance.driver, bot_instance.logger)
                            if success:
                                bot_instance.logger.info("✅ CAPTCHA berhasil diselesaikan")
                                return False  # Continue
                            else:
                                bot_instance.logger.error("❌ CAPTCHA gagal diselesaikan")
                                return True   # Skip
                        else:
                            bot_instance.logger.warning("⚠️ reCAPTCHA module not available")
                            return True
                        
            except:
                continue
        
        # ✅ CEK SMART DETECTION UNTUK HIDDEN CAPTCHA
        hidden_captcha_type = detect_hidden_captcha(bot_instance.driver, bot_instance.logger)
        
        if hidden_captcha_type == 'secureimg':
            if SECUREIMG_AVAILABLE:
                bot_instance.logger.info("🖼️ #secureimg CAPTCHA detected - solving...")
                success = solve_secureimg_captcha(bot_instance.driver, bot_instance.logger)
                if success:
                    bot_instance.logger.info("✅ CAPTCHA berhasil diselesaikan")
                    return False
                else:
                    bot_instance.logger.error("❌ CAPTCHA gagal diselesaikan")
                    return True
            else:
                bot_instance.logger.warning("⚠️ secureimg solver not available")
                return True
        
        elif hidden_captcha_type == 'recaptcha':
            if RECAPTCHA_AVAILABLE:
                # ✅ SUDAH ADA LOG DARI detect_hidden_captcha - langsung solve
                success = solve_recaptcha_v2(bot_instance.driver, bot_instance.logger)
                if success:
                    bot_instance.logger.info("✅ CAPTCHA berhasil diselesaikan")
                    return False
                else:
                    bot_instance.logger.error("❌ CAPTCHA gagal diselesaikan")
                    return True
            else:
                bot_instance.logger.warning("⚠️ reCAPTCHA module not available")
                return True
        
        # ✅ TIDAK ADA CAPTCHA DITEMUKAN
        bot_instance.logger.info("✅ No CAPTCHA elements found")
        return False  # Continue with form submission
        
    except Exception as e:
        bot_instance.logger.warning(f"⚠️ Error checking CAPTCHA: {e}")
        return False  # Continue with form submission


def detect_hidden_captcha(driver, logger):
    """Detect hidden CAPTCHA - hanya secureimg & reCAPTCHA"""
    try:
        # ✅ 1. CEK SECUREIMG TERSEMBUNYI
        try:
            # Cek input[name="securitycode"] field
            securitycode = driver.find_element(By.CSS_SELECTOR, 'input[name="securitycode"]')
            if securitycode.is_displayed():
                logger.info("🎯 Found securitycode field - secureimg CAPTCHA detected")
                return 'secureimg'
        except:
            pass
        
        # ✅ 2. CEK RECAPTCHA TERSEMBUNYI
        try:
            # Cek iframe reCAPTCHA
            recaptcha_iframes = driver.find_elements(By.CSS_SELECTOR, 'iframe[src*="recaptcha"]')
            for iframe in recaptcha_iframes:
                if iframe.is_displayed():
                    logger.info("🎯 Found reCAPTCHA iframe - reCAPTCHA detected")
                    return 'recaptcha'
        except:
            pass
        
        # ✅ 3. CEK PAGE SOURCE
        try:
            page_source = driver.page_source.lower()
            if 'secureimg' in page_source and 'securitycode' in page_source:
                logger.info("🎯 Found secureimg in page source")
                return 'secureimg'
            elif 'recaptcha' in page_source and 'g-recaptcha' in page_source:
                logger.info("🎯 Found reCAPTCHA in page source")
                return 'recaptcha'
        except:
            pass
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Error detecting hidden CAPTCHA: {e}")
        return None



def post_comment(driver, comment_data, comment_template, signature_data, bot_instance):
    """Post comment dengan logika yang benar: cari form dulu, baru show button jika perlu"""
    try:
        original_url = driver.current_url
        
        bot_instance.logger.info("🔍 Mencari comment form...")
        
        # ✅ STEP 1: Cari form langsung dulu
        target_selectors = [
            "#commentform",
            "#respond",
            ".comment-form", 
            "form[id*='comment']",
            "form[class*='comment']",
            "#comment-form",
            ".commentform",
            "form[action*='comment']"
        ]
        
        comment_form = find_comment_form_direct(driver, target_selectors)
        
        if comment_form:
            bot_instance.logger.info("✅ Comment form ditemukan langsung")
        else:
            # ✅ STEP 2: Jika tidak ketemu, coba show button
            bot_instance.logger.info("🔍 Form tidak terlihat, mencoba show button...")
            if handle_show_comment_button(driver, bot_instance):
                # Cari lagi setelah show button
                comment_form = find_comment_form_direct(driver, target_selectors)
                
            if not comment_form:
                # ✅ STEP 3: Last resort - scroll dan cari
                bot_instance.logger.info("🔍 Scroll dan cari form...")
                comment_form = scroll_and_find_comment_form(driver, bot_instance, target_selectors)
        
        if not comment_form:
            bot_instance.logger.error("❌ Comment form tidak ditemukan")
            return False
        
        # ✅ Popup cleanup
        close_popups_once(driver, bot_instance)
        
        # ✅ Fill dan submit form
        success, final_url = fill_comment_form(
            driver, comment_form, comment_data, comment_template, signature_data, bot_instance
        )
        
        if success:
            return True, final_url
        else:
            # bot_instance.logger.error("❌ Gagal posting komentar")
            return False, original_url
            
    except Exception as e:
        bot_instance.logger.error(f"❌ Error posting comment: {str(e)}")
        return False, driver.current_url




def find_form_field_with_cache(form_element, field_keywords, bot_instance, element_type):
    """Cari field dalam form dengan element caching - no miss message"""
    from colorama import Fore as F
    W, G, Y, R = F.WHITE, F.GREEN, F.YELLOW, F.RED
    
    try:
        # Get domain untuk caching
        domain = urlparse(bot_instance.driver.current_url).netloc.lower()
        
        # ✅ CEK CACHE DULU
        cached_selector = bot_instance.get_cached_selector(domain, element_type)
        if cached_selector:
            try:
                field = form_element.find_element(By.CSS_SELECTOR, cached_selector)
                if field.is_displayed():
                    # ⚡ CACHE HIT dengan detail
                    bot_instance.logger.info(f"⚡ {G}CACHE HIT{W} - {domain} cache {element_type}")
                    return field
                else:
                    # ⚠️ CACHE STALE dengan detail
                    bot_instance.logger.warning(f"⚠️ {Y}CACHE STALE{W} - {domain} cache {element_type} tidak valid lagi")
            except:
                # ⚠️ CACHE STALE (selector error) dengan detail
                bot_instance.logger.warning(f"⚠️ {Y}CACHE STALE{W} - {domain} cache {element_type} tidak valid lagi")
        
        # ✅ SEARCH NEW SELECTOR (langsung tanpa log CACHE MISS)
        for keyword in field_keywords:
            selectors = [
                f'input[name*="{keyword}"]',
                f'input[id*="{keyword}"]',
                f'textarea[name*="{keyword}"]',
                f'textarea[id*="{keyword}"]',
                f'input[placeholder*="{keyword}" i]',
                f'textarea[placeholder*="{keyword}" i]'
            ]
            
            for selector in selectors:
                try:
                    field = form_element.find_element(By.CSS_SELECTOR, selector)
                    if field.is_displayed():
                        # ✅ CACHE SELECTOR YANG BERHASIL (TANPA LOG)
                        bot_instance.cache_selector(domain, element_type, selector)
                        return field
                except:
                    continue
        
        return None
        
    except Exception as e:
        return None



# baypass honeypot

def handle_honeypot_comment_field(form_element, bot_instance):
    """Handle honeypot protection untuk comment field - simplified output"""
    try:
        domain = urlparse(bot_instance.driver.current_url).netloc.lower()
        
        # 1. Cari semua textarea dalam form
        textareas = form_element.find_elements(By.TAG_NAME, 'textarea')
        
        if len(textareas) < 2:
            # Tidak ada honeypot, gunakan cara biasa
            return find_form_field_with_cache(
                form_element, ['comment', 'message', 'content'], 
                bot_instance, 'comment_field'
            )
        
        # ✅ HANYA LOG HONEYPOT TERDETEKSI
        bot_instance.logger.info(f"🍯 Honeypot terdeteksi melakukan bypass")
        
        # 2. Analisis setiap textarea (tanpa log detail)
        visible_textareas = []
        hidden_textareas = []
        
        for textarea in textareas:
            try:
                # Cek visibility dengan berbagai cara
                is_visible = (
                    textarea.is_displayed() and 
                    textarea.size['height'] > 10 and 
                    textarea.size['width'] > 10 and
                    'hidden' not in textarea.get_attribute('style').lower() and
                    'clip:rect' not in textarea.get_attribute('style').lower() and
                    textarea.get_attribute('aria-hidden') != 'true'
                )
                
                textarea_info = {
                    'element': textarea,
                    'name': textarea.get_attribute('name') or 'no-name',
                    'id': textarea.get_attribute('id') or 'no-id',
                    'style': textarea.get_attribute('style') or '',
                    'aria_hidden': textarea.get_attribute('aria-hidden') or 'false',
                    'is_visible': is_visible
                }
                
                if is_visible:
                    visible_textareas.append(textarea_info)
                else:
                    hidden_textareas.append(textarea_info)
                    
            except Exception as e:
                continue
        
        # 3. Pilih textarea yang benar (yang visible) - tanpa log detail
        if visible_textareas:
            target_textarea = visible_textareas[0]['element']
            target_name = visible_textareas[0]['name']
            target_id = visible_textareas[0]['id']
            
            # 4. Cache selector yang benar (tanpa log detail)
            if target_name != 'no-name':
                selector = f'textarea[name="{target_name}"]'
            elif target_id != 'no-id':
                selector = f'textarea[id="{target_id}"]'
            else:
                selector = 'textarea'
            
            bot_instance.cache_selector(domain, 'comment_field', selector)
            
            return target_textarea
        
        # 5. Fallback jika tidak ada yang visible (tanpa log)
        return textareas[0] if textareas else None
        
    except Exception as e:
        # Fallback ke cara biasa (tanpa log error)
        return find_form_field_with_cache(
            form_element, ['comment', 'message', 'content'], 
            bot_instance, 'comment_field'
        )

#end bypass honeypot

# checkbox

def handle_privacy_checkbox(form_element, bot_instance):
    """Handle privacy/GDPR checkbox dengan caching - selectors dari template config"""
    from colorama import Fore as F
    W, G, Y, R = F.WHITE, F.GREEN, F.YELLOW, F.RED
    
    try:
        domain = urlparse(bot_instance.driver.current_url).netloc.lower()
        
        # ✅ CEK CACHE DULU
        cached_selector = bot_instance.get_cached_selector(domain, 'privacy_checkbox')
        if cached_selector:
            try:
                checkbox = form_element.find_element(By.CSS_SELECTOR, cached_selector)
                if checkbox.is_displayed():
                    # ⚡ CACHE HIT
                    bot_instance.logger.info(f"⚡ {G}CACHE HIT{W} - {domain} cache privacy_checkbox")
                    
                    if not checkbox.is_selected():
                        checkbox.click()
                        bot_instance.logger.info(f"✅ Privacy checkbox checked")
                        # time.sleep(random.uniform(0.5, 1.0))
                        time.sleep(random.uniform(0.1, 0.3))
                    else:
                        bot_instance.logger.info(f"ℹ️ Privacy checkbox already checked")
                    return True
                else:
                    # ⚠️ CACHE STALE
                    bot_instance.logger.warning(f"⚠️ {Y}CACHE STALE{W} - {domain} cache privacy_checkbox tidak valid lagi")
            except:
                # ⚠️ CACHE STALE (selector error)
                bot_instance.logger.warning(f"⚠️ {Y}CACHE STALE{W} - {domain} cache privacy_checkbox tidak valid lagi")
        
        # ✅ AMBIL SELECTORS DARI TEMPLATE CONFIG
        try:
            # Load template config
            current_dir = os.path.dirname(__file__)
            config_path = os.path.join(current_dir, 'config.yaml')
            
            with open(config_path, 'r', encoding='utf-8') as f:
                import yaml
                template_config = yaml.safe_load(f)
            
            privacy_selectors = template_config.get('privacy_checkbox', {}).get('selectors', [])
            
        except Exception as e:
            privacy_selectors = []
        
        # ✅ FALLBACK JIKA CONFIG KOSONG
        if not privacy_selectors:
            privacy_selectors = [
                'input[type="checkbox"][id*="privacy"]',
                'input[type="checkbox"][name*="privacy"]',
                'input[type="checkbox"][id*="gdpr"]',
                'input[type="checkbox"][name*="gdpr"]',
                'input[type="checkbox"][id*="consent"]',
                'input[type="checkbox"][name*="consent"]'
            ]
        
        # ✅ SEARCH NEW CHECKBOX (langsung tanpa log CACHE MISS)
        for selector in privacy_selectors:
            try:
                checkbox = form_element.find_element(By.CSS_SELECTOR, selector)
                if checkbox.is_displayed():
                    # ✅ CACHE SELECTOR YANG BERHASIL (TANPA LOG)
                    bot_instance.cache_selector(domain, 'privacy_checkbox', selector)
                    
                    if not checkbox.is_selected():
                        checkbox.click()
                        bot_instance.logger.info(f"✅ Privacy checkbox checked")
                        # time.sleep(random.uniform(0.5, 1.0))
                        time.sleep(random.uniform(0.1, 0.3))
                    else:
                        bot_instance.logger.info(f"ℹ️ Privacy checkbox already checked")
                    return True
            except:
                continue
        
        bot_instance.logger.info("ℹ️ No privacy checkbox found")
        return False
        
    except Exception as e:
        bot_instance.logger.warning(f"⚠️ Error handling privacy checkbox: {e}")
        return False
# end checkbox


# untuk memunculkan from komentar
def handle_show_comment_button(driver, bot_instance):
    """Handle show comment form button dengan output minimal"""
    try:
        domain = urlparse(driver.current_url).netloc.lower()
        
        # ✅ CEK CACHE DULU (SILENT)
        cached_selector = bot_instance.get_cached_selector(domain, 'show_comment_button')
        if cached_selector:
            try:
                show_button = driver.find_element(By.CSS_SELECTOR, cached_selector)
                if show_button.is_displayed() and show_button.is_enabled():
                    driver.execute_script("arguments[0].click();", show_button)
                    bot_instance.logger.info(f"🔘 Show comment button clicked")
                    # time.sleep(random.uniform(1.0, 2.0))
                    time.sleep(random.uniform(0.2, 0.5)) 
                    return True
            except:
                pass
        
        # ✅ AMBIL SELECTORS DARI TEMPLATE CONFIG
        try:
            current_dir = os.path.dirname(__file__)
            config_path = os.path.join(current_dir, 'config.yaml')
            
            with open(config_path, 'r', encoding='utf-8') as f:
                import yaml
                template_config = yaml.safe_load(f)
            
            show_button_selectors = template_config.get('show_comment_button', {}).get('selectors', [])
            
        except Exception as e:
            show_button_selectors = []
        
        # ✅ FALLBACK SELECTORS
        if not show_button_selectors:
            show_button_selectors = [
                ".write-comment-btn",
                ".write-comment-btn-under",
                "#write-comment-btn",
                ".show-comment-form",
                ".comment-reply-link",
                ".add-comment-btn",
                
            ]
        
        # ✅ SEARCH NEW BUTTON (SILENT CACHE)
        for selector in show_button_selectors:
            try:
                show_button = driver.find_element(By.CSS_SELECTOR, selector)
                if show_button.is_displayed() and show_button.is_enabled():
                    # ✅ CACHE TANPA LOG
                    bot_instance.cache_selector(domain, 'show_comment_button', selector)
                    
                    driver.execute_script("arguments[0].click();", show_button)
                    bot_instance.logger.info(f"🔘 Show comment button clicked")
                    # time.sleep(random.uniform(1.0, 2.0))
                    time.sleep(random.uniform(0.2, 0.5))
                    return True
            except:
                continue
        
        return False
        
    except Exception as e:
        return False



def fill_comment_form(driver, form_element, comment_data, comment_template, signature_data, bot_instance):
    """Fill dan submit comment form dengan smart detection dan typing 1 per 1 huruf"""
    try:
        original_url = driver.current_url
        
        # ✅ SMART DETECTION SETUP
        use_smart_detection = True
        smart_detector = None
        before_state = None
        
        try:
            import sys
            import os
            current_dir = os.path.dirname(__file__)
            sys.path.append(current_dir)
            
            from smart_detection import SmartSuccessDetector
            smart_detector = SmartSuccessDetector(bot_instance)
            before_state = smart_detector.capture_page_state(driver)
            bot_instance.logger.info("🤖 Smart detection initialized")
        except Exception as e:
            bot_instance.logger.warning(f"⚠️ Smart detection unavailable: {e}")
            use_smart_detection = False
        
        # ✅ CARI FIELDS DENGAN CACHE
        name_field = find_form_field_with_cache(
            form_element, ['name', 'author'], bot_instance, 'name_field'
        )
        
        email_field = find_form_field_with_cache(
            form_element, ['email'], bot_instance, 'email_field'
        )
        
        website_field = find_form_field_with_cache(
            form_element, ['website', 'url'], bot_instance, 'website_field'
        )
        
        # ✅ HANDLE HONEYPOT UNTUK COMMENT FIELD
        comment_field = handle_honeypot_comment_field(form_element, bot_instance)
        
        # ✅ VALIDASI REQUIRED FIELDS
        if not name_field or not email_field or not comment_field:
            bot_instance.logger.error("❌ Required fields tidak ditemukan")
            return False, original_url
        
        # ✅ ISI FORM DENGAN TYPING 1 PER 1 HURUF
        try:
            # bot_instance.logger.info("📝 Mengisi form dengan human-like typing...")
            
            # Name field
            type_human_like(name_field, comment_data['name'], bot_instance)
            time.sleep(random.uniform(0.3, 0.7))
            
            # Email field
            type_human_like(email_field, comment_data['email'], bot_instance)
            time.sleep(random.uniform(0.3, 0.7))
            
            # Website field (optional)
            if website_field:
                try:
                    type_human_like(website_field, comment_data.get('website', ''), bot_instance)
                    time.sleep(random.uniform(0.3, 0.7))
                except Exception as e:
                    bot_instance.logger.warning(f"⚠️ Error filling website field: {e}")
            
            # Comment field
            type_human_like(comment_field, comment_data['comment'], bot_instance)
            time.sleep(random.uniform(0.5, 1.0))
            
            # bot_instance.logger.info("✅ Form berhasil diisi dengan human-like typing")
            
        except Exception as e:
            bot_instance.logger.error(f"❌ Error mengisi form: {e}")
            return False, original_url
        
        # ✅ HANDLE PRIVACY CHECKBOX
        try:
            handle_privacy_checkbox(form_element, bot_instance)
        except Exception as e:
            bot_instance.logger.warning(f"⚠️ Error handling privacy checkbox: {e}")
        
        # ✅ BERSIHKAN POPUP SEBELUM SUBMIT
        bot_instance.logger.info("🧹 Membersihkan popup sebelum submit...")
        popup_count = close_popups_once(driver, bot_instance)
        if popup_count > 0:
            time.sleep(random.uniform(0.5, 1.0))
        # ✅ TAMBAHAN: CEK DAN HANDLE CAPTCHA
        try:
            captcha_result = check_captcha(form_element, bot_instance)
            if captcha_result is True:  # CAPTCHA ada tapi gagal solve
                bot_instance.logger.error("❌ CAPTCHA gagal diselesaikan - skip URL")
                return False, original_url
            elif captcha_result is False:  # CAPTCHA ada dan berhasil solve
                # bot_instance.logger.info("✅ CAPTCHA berhasil diselesaikan")
                time.sleep(random.uniform(1.0, 2.0))  # Delay setelah solve CAPTCHA
            # Jika captcha_result is None, artinya tidak ada CAPTCHA, lanjut normal
        except Exception as e:
            bot_instance.logger.warning(f"⚠️ Error checking CAPTCHA: {e}")


        
        # ✅ CARI DAN KLIK SUBMIT BUTTON
        submit_success = False
        
        # Cari submit button dengan cache
        submit_button, submit_selector = find_submit_button_with_cache(form_element, bot_instance)
        
        if submit_button:
            try:
                # Scroll ke submit button
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
                time.sleep(random.uniform(0.5, 1.0))
                
                # Final popup cleanup sebelum submit
                close_popups_once(driver, bot_instance)
                
                # Click submit button
                driver.execute_script("arguments[0].click();", submit_button)
                submit_success = True
                bot_instance.logger.info("✅ Submit button clicked")
                
                # Wait setelah submit
                time.sleep(random.uniform(2.0, 4.0))
                
                # Handle popup setelah submit
                close_popups_once(driver, bot_instance)
                
            except Exception as e:
                bot_instance.logger.error(f"❌ Error clicking submit: {e}")
                
                # Fallback: submit form langsung
                try:
                    driver.execute_script("arguments[0].submit();", form_element)
                    submit_success = True
                    bot_instance.logger.info("✅ Form submitted via fallback method")
                    time.sleep(random.uniform(2.0, 4.0))
                except Exception as e2:
                    bot_instance.logger.error(f"❌ Fallback submit failed: {e2}")
                    return False, original_url
        else:
            bot_instance.logger.error("❌ Submit button tidak ditemukan")
            
            # Last resort: try form submit
            try:
                driver.execute_script("arguments[0].submit();", form_element)
                submit_success = True
                bot_instance.logger.info("✅ Form submitted via last resort method")
                time.sleep(random.uniform(2.0, 4.0))
            except Exception as e:
                bot_instance.logger.error(f"❌ Last resort submit failed: {e}")
                return False, original_url
        
        # ✅ HANDLE HASIL SUBMIT DENGAN SMART DETECTION
        if submit_success:
            if use_smart_detection and smart_detector:
                try:
                    # Smart detection untuk hasil submit
                    is_success, detection_data = smart_detector.detect_success(
                        driver, before_state, wait_time=8
                    )
                    final_url = driver.current_url
                    
                    # Return hasil smart detection
                    return is_success, final_url
                    
                except Exception as e:
                    bot_instance.logger.error(f"❌ Smart detection error: {e}")
                    # Fallback ke basic detection
                    final_url = wait_and_capture_final_url(driver, original_url, bot_instance)
                    basic_success = check_comment_success_indicators(driver, bot_instance)
                    return basic_success, final_url
            else:
                # Basic detection jika smart detection tidak tersedia
                bot_instance.logger.info("🔍 Using basic success detection...")
                final_url = wait_and_capture_final_url(driver, original_url, bot_instance)
                basic_success = check_comment_success_indicators(driver, bot_instance)
                
                if basic_success:
                    bot_instance.logger.info("✅ Comment success detected (basic)")
                else:
                    bot_instance.logger.warning("⚠️ Comment success uncertain (basic)")
                
                return basic_success, final_url
        else:
            bot_instance.logger.error("❌ Submit gagal")
            return False, original_url
    
    except Exception as e:
        bot_instance.logger.error(f"❌ Error dalam fill_comment_form: {e}")
        return False, driver.current_url




def wait_and_capture_final_url(driver, original_url, bot_instance, max_wait=15):
    """Tunggu redirect dan capture URL final"""
    try:
        bot_instance.logger.info("⏳ Menunggu redirect/reload...")
        
        start_time = time.time()
        last_url = original_url
        stable_count = 0
        
        while time.time() - start_time < max_wait:
            current_url = driver.current_url
            
            # Cek apakah URL berubah
            if current_url != last_url:
                bot_instance.logger.info(f"🔄 URL berubah: {current_url}")
                last_url = current_url
                stable_count = 0
            else:
                stable_count += 1
            
            # Jika URL stabil selama 3 detik, anggap selesai
            if stable_count >= 3:
                bot_instance.logger.info(f"✅ URL stabil: {current_url}")
                break
                
            # Cek indikator success
            if check_comment_success_indicators(driver, bot_instance):
                bot_instance.logger.info("✅ Success indicator ditemukan")
                break
                
            time.sleep(1)
        
        final_url = driver.current_url
        
        # Log perubahan URL
        if final_url != original_url:
            bot_instance.logger.info(f"🎯 URL BERUBAH: {original_url} → {final_url}")
        else:
            bot_instance.logger.info(f"📍 URL TETAP: {final_url}")
            
        return final_url
        
    except Exception as e:
        bot_instance.logger.warning(f"⚠️ Error capturing final URL: {e}")
        return driver.current_url

def check_comment_success_indicators(driver, bot_instance):
    """Cek indikator bahwa komentar berhasil dipost"""
    try:
        # Success indicators
        success_selectors = [
            ".comment-success",
            ".success-message", 
            ".comment-submitted",
            ".awaiting-moderation",
            ".comment-pending",
            ".thank-you",
            "[class*='success']",
            "[class*='submitted']",
            "[class*='pending']"
        ]
        
        for selector in success_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        bot_instance.logger.info(f"✅ Success indicator: {selector}")
                        return True
            except:
                continue
        
        # Cek text indicators
        page_source = driver.page_source.lower()
        success_texts = [
            "comment submitted",
            "awaiting moderation", 
            "comment pending",
            "thank you",
            "successfully posted",
            "comment received"
        ]
        
        for text in success_texts:
            if text in page_source:
                bot_instance.logger.info(f"✅ Success text: {text}")
                return True
                
        return False
        
    except Exception as e:
        bot_instance.logger.warning(f"⚠️ Error checking success indicators: {e}")
        return False

def get_submit_selectors(bot_instance):
    """Get submit button selectors"""
    try:
        return [
            'input[type="submit"]',
            'button[type="submit"]', 
            'button[name="submit"]',
            'input[name="submit"]',
            'button[id*="submit"]',
            'input[id*="submit"]',
            '.submit-button',
            '#submit'
        ]
    except Exception as e:
        bot_instance.logger.warning(f"⚠️ Error getting submit selectors: {e}")
        return ['input[type="submit"]']



def find_submit_button_with_cache(form_element, bot_instance):
    """Cari submit button dengan caching - no miss message"""
    from colorama import Fore as F
    W, G, Y, R = F.WHITE, F.GREEN, F.YELLOW, F.RED
    
    try:
        domain = urlparse(bot_instance.driver.current_url).netloc.lower()
        
        # ✅ CEK CACHE DULU
        cached_selector = bot_instance.get_cached_selector(domain, 'submit_button')
        if cached_selector:
            try:
                submit_button = form_element.find_element(By.CSS_SELECTOR, cached_selector)
                if submit_button.is_displayed() and submit_button.is_enabled():
                    # ⚡ CACHE HIT dengan detail
                    bot_instance.logger.info(f"⚡ {G}CACHE HIT{W} - {domain} cache submit_button")
                    return submit_button, cached_selector
                else:
                    # ⚠️ CACHE STALE dengan detail
                    bot_instance.logger.warning(f"⚠️ {Y}CACHE STALE{W} - {domain} cache submit_button tidak valid lagi")
            except:
                # ⚠️ CACHE STALE (selector error) dengan detail
                bot_instance.logger.warning(f"⚠️ {Y}CACHE STALE{W} - {domain} cache submit_button tidak valid lagi")
        
        # ✅ SEARCH NEW SUBMIT BUTTON (langsung tanpa log CACHE MISS)
        submit_selectors = [
            'input[type="submit"]',
            'button[type="submit"]',
            'button[name="submit"]',
            'input[name="submit"]',
            'button[id*="submit"]',
            'input[id*="submit"]',
            '.submit-button',
            '#submit',
            'button[class*="submit"]',
            'input[class*="submit"]',
            'button[value*="submit" i]',
            'input[value*="submit" i]',
            'button[value*="post" i]',
            'input[value*="post" i]',
            'button[value*="send" i]',
            'input[value*="send" i]'
        ]
        
        for selector in submit_selectors:
            try:
                submit_button = form_element.find_element(By.CSS_SELECTOR, selector)
                if submit_button.is_displayed() and submit_button.is_enabled():
                    # ✅ CACHE SELECTOR YANG BERHASIL (TANPA LOG)
                    bot_instance.cache_selector(domain, 'submit_button', selector)
                    return submit_button, selector
            except:
                continue
        
        return None, None
        
    except Exception as e:
        return None, None



def try_submit_with_cache(driver, form_element, bot_instance):
    """Submit form dengan caching - no miss message"""
    from colorama import Fore as F
    W, G, Y, R = F.WHITE, F.GREEN, F.YELLOW, F.RED
    
    try:
        # Get domain untuk caching
        domain = urlparse(driver.current_url).netloc.lower()
        
        # ✅ POPUP CLEANUP SEBELUM SUBMIT
        close_popups_once(driver, bot_instance)
        
        # ✅ CEK CACHE DULU
        cached_selector = bot_instance.get_cached_selector(domain, 'submit_button')
        if cached_selector:
            try:
                submit_btn = form_element.find_element(By.CSS_SELECTOR, cached_selector)
                if submit_btn.is_displayed() and submit_btn.is_enabled():
                    # ⚡ CACHE HIT dengan detail
                    bot_instance.logger.info(f"⚡ {G}CACHE HIT{W} - {domain} cache submit_button")
                    
                    # ✅ FINAL POPUP CHECK sebelum click
                    close_popups_once(driver, bot_instance)
                    
                    driver.execute_script("arguments[0].click();", submit_btn)
                    
                    # ✅ HANDLE POPUP SETELAH SUBMIT
                    time.sleep(2)
                    close_popups_once(driver, bot_instance)
                    
                    return True
                else:
                    # ⚠️ CACHE STALE dengan detail
                    bot_instance.logger.warning(f"⚠️ {Y}CACHE STALE{W} - {domain} cache submit_button tidak valid lagi")
            except:
                # ⚠️ CACHE STALE (selector error) dengan detail
                bot_instance.logger.warning(f"⚠️ {Y}CACHE STALE{W} - {domain} cache submit_button tidak valid lagi")
        
        # ✅ SEARCH NEW SUBMIT BUTTON (langsung tanpa log CACHE MISS)
        submit_selectors = [
            'input[type="submit"]',
            'button[type="submit"]',
            'input[value*="submit" i]',
            'input[value*="post" i]',
            'input[value*="send" i]',
            'button[name*="submit"]',
            'button[id*="submit"]',
            '.submit-button',
            '#submit',
            '[class*="submit"]'
        ]
        
        for selector in submit_selectors:
            try:
                submit_btn = form_element.find_element(By.CSS_SELECTOR, selector)
                if submit_btn.is_displayed() and submit_btn.is_enabled():
                    # ✅ CACHE SELECTOR YANG BERHASIL (TANPA LOG)
                    bot_instance.cache_selector(domain, 'submit_button', selector)
                    
                    # ✅ FINAL POPUP CHECK sebelum click
                    close_popups_once(driver, bot_instance)
                    
                    # Submit dengan JavaScript
                    driver.execute_script("arguments[0].click();", submit_btn)
                    
                    # ✅ HANDLE POPUP SETELAH SUBMIT
                    # time.sleep(2)
                    time.sleep(0.5)
                    close_popups_once(driver, bot_instance)
                    
                    return True
            except:
                continue
        
        # ✅ FALLBACK: SUBMIT FORM LANGSUNG
        try:
            # ✅ POPUP CHECK sebelum fallback submit
            close_popups_once(driver, bot_instance)
            
            driver.execute_script("arguments[0].submit();", form_element)
            
            # ✅ HANDLE POPUP SETELAH FALLBACK SUBMIT
            time.sleep(2)
            close_popups_once(driver, bot_instance)
            
            return True
        except:
            pass
        
        return False
        
    except Exception as e:
        return False


# def type_human_like(element, text):
#     """Fast typing - cepat tapi masih terlihat"""
#     element.clear()
    
#     for char in text:
#         element.send_keys(char)
#         time.sleep(0.08)  # ✅ 0.03 detik per karakter - cepat tapi terlihat


def type_human_like(element, text, bot_instance):
    """Ketik 1 per 1 huruf dengan config dari bot_instance"""
    import time
    import random
    import yaml
    import os
    
    try:
        # ✅ DEFAULT VALUES
        speed_min = 0.05
        speed_max = 0.15
        human_like = True
        
        # ✅ 1. CEK CONFIG UTAMA (main config.yaml)
        main_typing_config = bot_instance.config.get('typing', {})
        if main_typing_config:
            speed_min = main_typing_config.get('speed_min', speed_min)
            speed_max = main_typing_config.get('speed_max', speed_max)
            human_like = main_typing_config.get('human_like', human_like)
        
        # ✅ 2. CEK CONFIG TEMPLATE WORDPRESS (override main config)
        try:
            template_config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
            if os.path.exists(template_config_path):
                with open(template_config_path, 'r', encoding='utf-8') as file:
                    template_config = yaml.safe_load(file)
                    template_typing = template_config.get('settings', {}).get('typing', {})
                    
                    if template_typing:
                        speed_min = template_typing.get('speed_min', speed_min)
                        speed_max = template_typing.get('speed_max', speed_max)
                        human_like = template_typing.get('human_like', human_like)
        except:
            pass
        
        # ✅ CLEAR FIELD
        element.clear()
        
        # ✅ CEK MODE INSTANT
        if not human_like or (speed_min == 0.0 and speed_max == 0.0):
            element.send_keys(text)
            return
        
        # ✅ TYPING 1 PER 1 HURUF
        for char in text:
            element.send_keys(char)  # Kirim 1 karakter
            
            # Delay random antar karakter
            delay = random.uniform(speed_min, speed_max)
            time.sleep(delay)
        
    except Exception as e:
        # ✅ FALLBACK - instant typing
        try:
            element.clear()
            element.send_keys(text)
        except:
            pass