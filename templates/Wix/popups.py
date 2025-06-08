import time
import random
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
import importlib.util


re="\033[1;31m"
gr="\033[1;32m"
cy="\033[1;36m"
hijau   =   "\033[1;92m"
putih   =   "\033[1;97m"
abu     =   "\033[1;90m"
kuning  =   "\033[1;93m"
ungu    =   "\033[1;95m"
merah   =   "\033[1;91m"
biru    =   "\033[1;96m"
kuning2 =   "\33[1;33m"
biru2   =   "\33[0;36m"


try:
    from colorama import Fore
    R = Fore.RED
    G = Fore.GREEN
    W = Fore.WHITE
    Y = Fore.YELLOW
    B = Fore.BLUE
except ImportError:
    R = G = W = Y = B =""

# def handle_popup_dengan_retry(driver, logger=None, max_retries=3):
#     """
#     Handle popup dengan retry jika server 500
#     """
#     for attempt in range(max_retries):
#         try:
#             if logger:
#                 logger.info(f"🔄 {W}[Popup] Attempt {G}{attempt + 1}{W}/{G}{max_retries}")
            
#             # DELAY ANTAR ATTEMPT
#             if attempt > 0:
#                 delay = random.uniform(5, 10) * attempt  # Increasing delay
#                 if logger:
#                     logger.info(f"⏳ [Popup] Waiting {delay:.1f} seconds before retry...")
#                 time.sleep(delay)
            
#             success = handle_google_popup(driver, logger)
#             if success:
#                 return True
                
#         except Exception as e:
#             if logger:
#                 logger.warning(f"⚠️ {R}[Popup] Attempt {attempt + 1} failed: {e}")
            
#             if "500" in str(e) or "server" in str(e).lower():
#                 if logger:
#                     logger.warning("⚠️ [Popup] Server error detected, will retry...")
#                 continue
#             else:
#                 break
    
#     if logger:
#         logger.error(f"❌ [Popup] All {max_retries} attempts failed")
#     return True


def handle_popup_dengan_retry(driver, logger=None, max_retries=3):
    """
    Handle popup dengan retry jika server 500
    """
    for attempt in range(max_retries):
        try:
            if logger:
                logger.info(f"🔄 [Popup] Attempt {attempt + 1}/{max_retries}")
            
            # DELAY ANTAR ATTEMPT (tanpa log)
            if attempt > 0:
                delay = random.uniform(5, 10) * attempt  # Increasing delay
                time.sleep(delay)
            
            success = handle_google_popup(driver, logger)
            if success:
                return True
                
        except Exception as e:
            if "500" in str(e) or "server" in str(e).lower():
                continue
            else:
                break
    
    if logger:
        logger.error(f"❌ [Popup] All {max_retries} attempts failed")
    return True


# def handle_google_popup(driver, logger=None):
#     """
#     Handle Google popup window dan login process
#     """
#     try:
#         if logger:
#             logger.info(f"🔍 {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] Checking for Google popup window...")
        
#         # Tunggu sebentar untuk popup muncul
#         # time.sleep(random.uniform(2, 4))
        
#         try:
#             # Cek apakah ada window baru (popup)
#             WebDriverWait(driver, 2).until(lambda d: len(d.window_handles) > 1)
            
#             window_handles = driver.window_handles

            
#             if len(window_handles) > 1:
#                 if logger:
#                     logger.info(F"🪟 {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] Google popup window terdeteksi")
#                 # Switch ke popup window
#                 main_window = window_handles[0]
#                 popup_window = window_handles[1]
#                 driver.switch_to.window(popup_window)

#                 driver.set_window_size(500, 600)
#                 driver.set_window_position(0, 0)
                

#                 # Handle Google login process
#                 if logger:
#                     logger.info(F"🔄 {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] Switched to popup window")
                
#                 # Handle Google login process
#                 google_login_success = handle_google_login_process(driver, logger)
                
#                 # ✅ IMPROVED: Silent window switching (no unnecessary error logs)
#                 try:
#                     if logger:
#                         logger.info(F"🔄 {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] Memastikan kembali ke main window...")
                    
#                     # Tunggu sebentar untuk popup process selesai
#                     time.sleep(random.uniform(3, 5))
                    
#                     # ✅ SILENT: Get window info tanpa log error yang tidak perlu
#                     current_windows = []
#                     current_window = None
                    
#                     try:
#                         current_windows = driver.window_handles
#                         if logger:
#                             logger.info(f"📊 {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] Available windows: {len(current_windows)}")
#                     except Exception:
#                         # Silent fail - ini normal jika popup sudah tertutup
#                         current_windows = []
                    
#                     try:
#                         current_window = driver.current_window_handle
#                         # Hanya log jika berhasil
#                         if logger:
#                             logger.info(f"📍 {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] Current window active")
#                     except Exception:
#                         # ✅ SILENT: Ini normal behavior ketika popup tertutup otomatis
#                         # Tidak perlu log error karena ini expected
#                         current_window = None
                    
#                     # ✅ SMART: Window switching logic
#                     if current_windows and len(current_windows) >= 1:
#                         # Ada window tersedia
#                         target_window = None
                        
#                         # Prioritas 1: Gunakan main_window jika masih ada
#                         if main_window in current_windows:
#                             target_window = main_window
#                             if logger:
#                                 logger.info(F"🎯 {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] Using original main window")
#                         else:
#                             # Prioritas 2: Gunakan window pertama yang tersedia
#                             target_window = current_windows[0]
#                             if logger:
#                                 logger.info(F"🎯 {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] Using first available window")
                        
#                         # Switch ke target window jika berbeda dari current
#                         if target_window and target_window != current_window:
#                             try:
#                                 driver.switch_to.window(target_window)
#                                 if logger:
#                                     logger.info(F"✅ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] Successfully switched to target window")
#                                     logger.info(f"{Y}{"─" *60}")
#                             except Exception:
#                                 # Silent fail - akan ditangani di fallback
#                                 pass
#                         elif target_window == current_window:
#                             if logger:
#                                 logger.info(F"ℹ️ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] Already in correct window")
                    
#                     # ✅ ALWAYS: Jalankan cleanup (dengan validation internal)
#                     safe_cleanup_with_validation(driver, logger)
                    
#                 except Exception as switch_error:
#                     # ✅ REDUCED LOGGING: Hanya log jika benar-benar unexpected error
#                     if "target window already closed" not in str(switch_error):
#                         if logger:
#                             logger.warning(f"⚠️ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] Unexpected error: {switch_error}")
                    
#                     # ✅ SILENT: Fallback tanpa noise
#                     ultra_safe_fallback(driver, logger)
                
#                 return google_login_success
#             else:
#                 if logger:
#                     logger.info(F"ℹ️ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] Tidak ada popup window terdeteksi")
#                 return True
                
#         except TimeoutException:
#             if logger:
#                 logger.info(F"ℹ️ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] Timeout waiting for popup - mungkin tidak ada popup")
#             return True
        
#     except Exception as e:
#         if logger:
#             logger.error(f"❌ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Popup{putih}] {R}Error dalam handle_google_popup: {e}")
#         return False

def handle_google_popup(driver, logger=None):
    """
    Handle Google popup window dan login process
    """
    try:
        # Tunggu sebentar untuk popup muncul (tanpa log)
        
        try:
            # Cek apakah ada window baru (popup)
            WebDriverWait(driver, 2).until(lambda d: len(d.window_handles) > 1)
            
            window_handles = driver.window_handles
            
            if len(window_handles) > 1:
                # Switch ke popup window (tanpa log)
                main_window = window_handles[0]
                popup_window = window_handles[1]
                driver.switch_to.window(popup_window)

                driver.set_window_size(500, 600)
                driver.set_window_position(0, 0)
                
                # Handle Google login process (tanpa log)
                google_login_success = handle_google_login_process(driver, logger)
                
                # Window switching (tanpa log detail)
                try:
                    # Tunggu sebentar untuk popup process selesai
                    time.sleep(random.uniform(3, 5))
                    
                    # Get window info (tanpa log)
                    current_windows = []
                    current_window = None
                    
                    try:
                        current_windows = driver.window_handles
                    except Exception:
                        current_windows = []
                    
                    try:
                        current_window = driver.current_window_handle
                    except Exception:
                        current_window = None
                    
                    # Window switching logic
                    if current_windows and len(current_windows) >= 1:
                        target_window = None
                        
                        # Prioritas 1: Gunakan main_window jika masih ada
                        if main_window in current_windows:
                            target_window = main_window
                        else:
                            # Prioritas 2: Gunakan window pertama yang tersedia
                            target_window = current_windows[0]
                        
                        # Switch ke target window jika berbeda dari current
                        if target_window and target_window != current_window:
                            try:
                                driver.switch_to.window(target_window)
                                if logger:
                                    logger.info(f"✅ [Google Popup] Successfully switched to target window")
                                    logger.info(f"{Y}{'─' *60}")
                            except Exception:
                                pass
                    
                    # Jalankan cleanup (tanpa log)
                    safe_cleanup_with_validation(driver, None)
                    
                except Exception as switch_error:
                    # Silent fallback
                    ultra_safe_fallback(driver, None)
                
                return google_login_success
            else:
                return True
                
        except TimeoutException:
            return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Google Popup] Error dalam handle_google_popup: {e}")
        return False




def ultra_safe_fallback(driver, logger=None):
    """
    Ultra-safe fallback untuk window switching - SILENT MODE
    """
    try:
        if logger:
            logger.info("🛡️ [Ultra Safe] Memulai ultra-safe fallback...")
        
        # Attempt 1: Get any available window
        available_windows = []
        try:
            available_windows = driver.window_handles
            if logger:
                logger.info(f"🔍 [Ultra Safe] Found {len(available_windows)} windows")
        except Exception:
            # Silent fail
            return False
        
        if not available_windows:
            if logger:
                logger.warning("⚠️ [Ultra Safe] No windows available")
            return False
        
        # Attempt 2: Switch to first available window
        for i, window in enumerate(available_windows):
            try:
                driver.switch_to.window(window)
                
                # Test if window is responsive
                try:
                    _ = driver.current_url
                    if logger:
                        logger.info(f"✅ [Ultra Safe] Successfully switched to responsive window")
                    
                    # Attempt cleanup if window is responsive
                    safe_cleanup_with_validation(driver, logger)
                    return True
                    
                except Exception:
                    # Silent continue to next window
                    continue
                    
            except Exception:
                # Silent continue to next window
                continue
        
        if logger:
            logger.warning("⚠️ [Ultra Safe] All fallback attempts failed")
        return False
        
    except Exception:
        # Silent fail
        return False

def safe_cleanup_with_validation(driver, logger=None):
    """
    Cleanup dengan validation yang sangat ketat - TANPA final backup cleanup
    """
    try:
        if logger:
            logger.info("🧹 [Safe Cleanup] Memulai cleanup dengan validation...")
        
        # ✅ SILENT: Multi-level window validation
        validation_passed = False
        
        try:
            # Test 1: Window handles
            windows = driver.window_handles
            if not windows:
                return False
            
            # Test 2: Current window
            current = driver.current_window_handle
            if current not in windows:
                return False
            
            # Test 3: Page access
            url = driver.current_url
            if logger:
                logger.info(f"✅ [Safe Cleanup] Window validation passed, URL: {url[:50]}...")
            
            validation_passed = True
            
        except Exception:
            # Silent validation fail
            return False
        
        # ✅ STEP 2: PANGGIL cleanup_popups DAN click_safe_area DARI actions.py
        if validation_passed:
            try:
                # ✅ IMPORT ACTIONS MODULE
                import importlib.util
                current_dir = os.path.dirname(os.path.abspath(__file__))
                actions_path = os.path.join(current_dir, "actions.py")
                
                if os.path.exists(actions_path):
                    spec = importlib.util.spec_from_file_location("actions", actions_path)
                    actions_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(actions_module)
                    
                    # ✅ STEP 2A: PANGGIL cleanup_popups() YANG SUDAH TERBUKTI BERHASIL
                    if hasattr(actions_module, 'cleanup_popups'):
                        if logger:
                            logger.info("🧹 [Safe Cleanup] Memanggil cleanup_popups() yang terbukti berhasil...")
                        
                        try:
                            cleanup_result = actions_module.cleanup_popups(driver, logger)
                            
                            if cleanup_result:
                                if logger:
                                    logger.info("✅ [Safe Cleanup] cleanup_popups() berhasil tutup popup!")
                            else:
                                if logger:
                                    logger.info("ℹ️ [Safe Cleanup] cleanup_popups() selesai (no popups)")
                            
                            # ✅ TUNGGU SEBENTAR SETELAH cleanup_popups
                            time.sleep(random.uniform(0.5, 1))
                            
                        except Exception as e:
                            if logger:
                                logger.warning(f"⚠️ [Safe Cleanup] Error cleanup_popups(): {e}")
                    
                    # ✅ STEP 2B: PANGGIL click_safe_area() YANG SUDAH TERBUKTI BERHASIL
                    if hasattr(actions_module, 'click_safe_area'):
                        if logger:
                            logger.info("🎯 [Safe Cleanup] Memanggil click_safe_area() yang terbukti berhasil...")
                        
                        try:
                            actions_module.click_safe_area(driver, logger)
                            
                            if logger:
                                logger.info("✅ [Safe Cleanup] click_safe_area() berhasil!")
                            
                            # ✅ TUNGGU SEBENTAR SETELAH click_safe_area
                            time.sleep(random.uniform(0.5, 1))
                            
                        except Exception as e:
                            if logger:
                                logger.warning(f"⚠️ [Safe Cleanup] Error click_safe_area(): {e}")
                    
                    # ✅ STEP 2C: CLEANUP POPUP SPESIFIK SETELAH LOGIN GOOGLE
                    if logger:
                        logger.info("🧹 [Safe Cleanup] Running cleanup untuk popup setelah login...")
                    
                    popup_setelah_login = cleanup_popup_setelah_login_google(driver, logger)
                    
                    if popup_setelah_login:
                        if logger:
                            logger.info("✅ [Safe Cleanup] Popup setelah login berhasil ditutup")
                    else:
                        if logger:
                            logger.info("ℹ️ [Safe Cleanup] Tidak ada popup setelah login")
                    
                    # ✅ REMOVED: STEP 2D dan 2E sudah dihapus
                    
                    if logger:
                        logger.info("🎉 [Safe Cleanup] Semua tahap cleanup selesai!")
                    
                    return True
                    
                else:
                    if logger:
                        logger.error("❌ [Safe Cleanup] actions.py tidak ditemukan")
                    return False
                    
            except Exception as e:
                if logger:
                    logger.error(f"❌ [Safe Cleanup] Error import actions: {e}")
                return False
        
        return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Safe Cleanup] Error: {e}")
        return False

def auto_cleanup_after_switch(driver, logger=None):
    """
    Auto cleanup setelah switch ke main window - TANPA cleanup_popups_once
    """
    try:
        # ✅ STEP 1: IMPORT ACTIONS MODULE SECARA DINAMIS
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            actions_path = os.path.join(current_dir, "actions.py")
            
            if os.path.exists(actions_path):
                spec = importlib.util.spec_from_file_location("actions", actions_path)
                actions_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(actions_module)
                
                if logger:
                    logger.info(f"✅ {putih}[{biru}Auto Cleanup{putih}] Actions module berhasil diimport")
                
                # ✅ STEP 2: CLEANUP POPUPS
                if hasattr(actions_module, 'cleanup_popups'):
                    try:
                        cleanup_result = actions_module.cleanup_popups(driver, logger)
                        if logger:
                            if cleanup_result:
                                logger.info(f"✅ {putih}[{biru}Auto Cleanup{putih}] cleanup_popups() berhasil")
                            else:
                                logger.info(f"ℹ️ {putih}[{biru}Auto Cleanup{putih}] cleanup_popups() selesai (no popups)")
                        time.sleep(random.uniform(0.5, 1))
                    except Exception as e:
                        if logger:
                            logger.warning(f"⚠️ {putih}[{biru}Auto Cleanup{putih}] Error cleanup_popups(): {e}")
                
                # ✅ STEP 3: CLICK SAFE AREA
                if hasattr(actions_module, 'click_safe_area'):
                    try:
                        actions_module.click_safe_area(driver, logger)
                        if logger:
                            logger.info(f"✅ {putih}[{biru}Auto Cleanup{putih}] click_safe_area() berhasil")
                        time.sleep(random.uniform(0.5, 1))
                    except Exception as e:
                        if logger:
                            logger.warning(f"⚠️ {putih}[{biru}Auto Cleanup{putih}] Error click_safe_area(): {e}")
                
                # ✅ REMOVED: STEP 4 dan 5 (cleanup_popups_once dan final click_safe_area) sudah dihapus
                
                if logger:
                    logger.info(f"🎉 {putih}[{biru}Auto Cleanup{putih}] Auto cleanup selesai!")
                
                return True
                
            else:
                if logger:
                    logger.error(f"❌ {putih}[{biru}Auto Cleanup{putih}] actions.py tidak ditemukan")
                return False
                
        except Exception as e:
            if logger:
                logger.error(f"❌ {putih}[{biru}Auto Cleanup{putih}] Error import actions: {e}")
            return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ {putih}[{biru}Auto Cleanup{putih}] Error: {e}")
        return False

def run_safe_cleanup(driver, logger=None):
    """
    Jalankan cleanup dengan safety checks - SIMPLIFIED
    """
    try:
        if logger:
            logger.info("🧹 [Safe Cleanup] Memulai safe cleanup...")
        
        # Import module actions secara dinamis
        import importlib.util
        current_dir = os.path.dirname(os.path.abspath(__file__))
        actions_path = os.path.join(current_dir, "actions.py")
        
        if os.path.exists(actions_path):
            spec = importlib.util.spec_from_file_location("actions", actions_path)
            actions_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(actions_module)
            
            if logger:
                logger.info("✅ [Safe Cleanup] Actions module berhasil diimport")
            
            # ✅ GUNAKAN cleanup_popups BIASA
            if hasattr(actions_module, 'cleanup_popups'):
                if logger:
                    logger.info("🧹 [Safe Cleanup] Menjalankan cleanup_popups...")
                
                try:
                    cleanup_result = actions_module.cleanup_popups(driver, logger)
                    
                    if cleanup_result:
                        if logger:
                            logger.info("✅ [Safe Cleanup] cleanup_popups berhasil dijalankan")
                    else:
                        if logger:
                            logger.info("ℹ️ [Safe Cleanup] cleanup_popups selesai (tidak ada popup)")
                    
                    return True
                    
                except Exception as cleanup_error:
                    if logger:
                        logger.warning(f"⚠️ [Safe Cleanup] Error cleanup_popups: {cleanup_error}")
                    return False
            else:
                if logger:
                    logger.warning("⚠️ [Safe Cleanup] Fungsi cleanup_popups tidak ditemukan")
                return False
        else:
            if logger:
                logger.warning("⚠️ [Safe Cleanup] File actions.py tidak ditemukan")
            return False
            
    except Exception as cleanup_error:
        if logger:
            logger.warning(f"⚠️ [Safe Cleanup] Error: {cleanup_error}")
        return False

# def handle_google_login_process(driver, logger=None):
#     """
#     Handle proses login Google di popup window - Minimal logging
#     """
#     try:
#         if logger:
#             logger.info(f"🔐 {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Login{putih}] Memulai proses login Google...")
        
#         # Tunggu halaman Google login load
#         time.sleep(random.uniform(3, 5))
        
#         # Load akun dari file
#         email, password = load_google_account()
        
#         if not email or not password:
#             if logger:
#                 logger.error(f"❌ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Login{putih}] {R}Akun Google tidak ditemukan di akun.txt")
#             return False
        
#         # Proses login LANGSUNG TANPA CEK URL
#         login_success = perform_google_login(driver, email, password, logger)
        
#         if login_success:
#             if logger:
#                 logger.info(f"✅ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Login{putih}] {G}Login Google selesai")
#             return True
#         else:
#             if logger:
#                 logger.error(f"❌ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Login{putih}] {R}Login Google gagal")
#             return False
        
#     except Exception as e:
#         if logger:
#             logger.error(f"❌ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Login{putih}] {R}Error dalam handle_google_login_process: {e}")
#         return False


def handle_google_login_process(driver, logger=None):
    """
    Handle proses login Google di popup window - Minimal logging
    """
    try:
        # Tunggu halaman Google login load (tanpa log)
        time.sleep(random.uniform(3, 5))
        
        # Load akun dari file (tanpa log)
        email, password = load_google_account()
        
        if not email or not password:
            if logger:
                logger.error(f"❌ [Google Login] Akun Google tidak ditemukan di akun.txt")
            return False
        
        # Proses login LANGSUNG TANPA CEK URL (tanpa log)
        login_success = perform_google_login(driver, email, password, logger)
        
        return login_success
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Google Login] Error dalam handle_google_login_process: {e}")
        return False



def load_google_account():
    """
    Load akun Google dari file akun.txt
    """
    try:
        # Cari file akun.txt di berbagai lokasi
        possible_paths = [
            "akun.txt",
            "templates/website2/akun.txt",
            os.path.join(os.path.dirname(__file__), "akun.txt"),
            os.path.join(os.path.dirname(__file__), "..", "..", "akun.txt")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as file:
                    lines = [line.strip() for line in file.readlines() if line.strip() and not line.startswith('#')]
                    
                    if len(lines) >= 2:
                        email = lines[0]
                        password = lines[1]
                        return email, password
        
        print("❌ File akun.txt tidak ditemukan")
        return None, None
        
    except Exception as e:
        print(f"❌ Error loading Google account: {e}")
        return None, None

def click_continue_button_if_exists(driver, logger=None, timeout=10):
    """
    Cari dan klik tombol Continue jika ada - Minimal logging
    """
    try:
        # Berbagai selector untuk tombol Continue
        continue_selectors = [
            # Selector spesifik dari contoh
            "span[jsname='V67aGc'].VfPpkd-vQzf8d",
            "span[jsname='V67aGc']",
            ".VfPpkd-vQzf8d",
            
            # Selector umum Continue
            "button:contains('Continue')",
            "span:contains('Continue')",
            "div:contains('Continue')",
            "[role='button']:contains('Continue')",
            
            # Selector berdasarkan atribut
            "button[data-testid*='continue']",
            "button[aria-label*='continue' i]",
            "[data-hook*='continue']",
            
            # Selector CSS class umum
            ".continue-button",
            ".btn-continue",
            "#continue",
            "#continueButton",
            
            # Selector berdasarkan text content
            "*[role='button'][aria-label*='Continue']",
            "button[type='submit']",
            "input[type='submit'][value*='Continue']"
        ]
        
        # Tunggu sebentar untuk elemen muncul
        time.sleep(random.uniform(2, 4))
        
        for selector in continue_selectors:
            try:
                # Handle selector dengan :contains()
                if ':contains(' in selector:
                    text = selector.split(':contains(')[1].split(')')[0].strip("'\"")
                    xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
                    
                    elements = driver.find_elements(By.XPATH, xpath)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element_text = element.text.strip().lower()
                            if 'continue' in element_text:
                                if logger:
                                    logger.info("✅ [Continue] Continue button diklik")
                                
                                # Klik dengan berbagai metode
                                click_success = click_continue_element(driver, element, logger)
                                if click_success:
                                    return True
                else:
                    # CSS Selector biasa
                    try:
                        element = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        
                        if element and element.is_displayed():
                            element_text = element.text.strip()
                            if 'continue' in element_text.lower() or not element_text:
                                if logger:
                                    logger.info("✅ [Continue] Continue button diklik")
                                
                                # Klik dengan berbagai metode
                                click_success = click_continue_element(driver, element, logger)
                                if click_success:
                                    return True
                                    
                    except TimeoutException:
                        continue
                    except Exception:
                        continue
                        
            except Exception:
                continue
        
        # Tidak ada logging jika tidak ditemukan
        return False
        
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ [Continue] Error: {e}")
        return False

def click_continue_element(driver, element, logger=None):
    """
    Klik element Continue - Minimal logging
    """
    try:
        # Scroll ke element
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(1)
        
        # Method 1: Direct Click
        try:
            element.click()
            time.sleep(random.uniform(2, 4))
            return True
        except ElementClickInterceptedException:
            pass
        except Exception:
            pass
        
        # Method 2: JavaScript Click
        try:
            driver.execute_script("arguments[0].click();", element)
            time.sleep(random.uniform(2, 4))
            return True
        except Exception:
            pass
        
        # Method 3: ActionChains
        try:
            actions = ActionChains(driver)
            actions.move_to_element(element).click().perform()
            time.sleep(random.uniform(2, 4))
            return True
        except Exception:
            pass
        
        # Method 4: Enter key
        try:
            from selenium.webdriver.common.keys import Keys
            element.send_keys(Keys.ENTER)
            time.sleep(random.uniform(2, 4))
            return True
        except Exception:
            pass
        
        return False
        
    except Exception:
        return False

# def perform_google_login(driver, email, password, logger=None):
#     """
#     Perform actual Google login - Minimal logging
#     """
#     try:
#         if logger:
#             logger.info(f"📧 {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Login{putih}] Mengisi email...")
        
#         # Tunggu dan isi email
#         email_success = fill_google_email(driver, email, logger)
#         if not email_success:
#             if logger:
#                 logger.error(f"❌ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Login{putih}] {R}Gagal mengisi email")
#             return False
        
#         if logger:
#             logger.info(f"🔑 {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Login{putih}] Mengisi password...")
        
#         # Tunggu dan isi password
#         password_success = fill_google_password(driver, password, logger)
#         if not password_success:
#             if logger:
#                 logger.error(f"❌ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Login{putih}] {R}Gagal mengisi password")
#             return False
        
#         # Cari dan klik tombol Continue jika ada
#         continue_success = click_continue_button_if_exists(driver, logger)
        
#         # Tunggu proses login selesai
#         time.sleep(random.uniform(5, 8))
        
#         if logger:
#             logger.info(f"✅ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Login{putih}] {G}Proses login selesai")
        
#         return True
        
#     except Exception as e:
#         if logger:
#             logger.error(f"❌ {putih}[{biru2}G{merah}o{kuning2}o{biru2}g{hijau}l{merah}e {kuning2}Login{putih}] {R}Error dalam perform_google_login: {e}")
#         return False


def perform_google_login(driver, email, password, logger=None):
    """
    Perform actual Google login - Minimal logging
    """
    try:
        # Tunggu dan isi email (tanpa log)
        email_success = fill_google_email(driver, email, logger)
        if not email_success:
            if logger:
                logger.error(f"❌ [Google Login] Gagal mengisi email")
            return False
        
        # Tunggu dan isi password (tanpa log)
        password_success = fill_google_password(driver, password, logger)
        if not password_success:
            if logger:
                logger.error(f"❌ [Google Login] Gagal mengisi password")
            return False
        
        # Cari dan klik tombol Continue jika ada (tanpa log)
        continue_success = click_continue_button_if_exists(driver, None)
        
        # Tunggu proses login selesai (tanpa log)
        time.sleep(random.uniform(5, 8))
        
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Google Login] Error dalam perform_google_login: {e}")
        return False



# def fill_google_email(driver, email, logger=None):
#     """
#     Isi field email Google
#     """
#     try:
#         email_selectors = [
#             "input[type='email']",
#             "input[name='identifier']",
#             "input[id='identifierId']",
#             "#Email",
#             "[data-testid='email']"
#         ]
        
#         for selector in email_selectors:
#             try:
#                 if logger:
#                     logger.info(f"🔍 {putih}[{biru}Email{putih}] Mencoba selector: {Y}{selector}")
                
#                 email_field = WebDriverWait(driver, 10).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
#                 )
                
#                 if email_field:
#                     # Clear dan isi email
#                     email_field.clear()
#                     time.sleep(0.5)
                    
#                     # Type email dengan delay natural
#                     for char in email:
#                         email_field.send_keys(char)
#                         time.sleep(random.uniform(0.05, 0.15))
                    
#                     time.sleep(1)
                    
#                     # Tekan Enter atau cari tombol Next
#                     try:
#                         email_field.send_keys(Keys.ENTER)
#                         if logger:
#                             logger.info(f"✅ {putih}[{biru}Email{putih}] {G}Email diisi dan Enter ditekan")
#                     except:
#                         # Cari tombol Next
#                         next_button = driver.find_element(By.CSS_SELECTOR, "#identifierNext, [data-testid='next'], button:contains('Next')")
#                         if next_button:
#                             next_button.click()
#                             if logger:
#                                 logger.info(f"✅ {putih}[{biru}Email{putih}] {G}Email diisi dan Next diklik")
                    
#                     time.sleep(random.uniform(2, 4))
#                     return True
                    
#             except TimeoutException:
#                 continue
#             except Exception as e:
#                 if logger:
#                     logger.warning(f"⚠️ {putih}[{biru}Email{putih}] {R}Error dengan selector {selector}: {e}")
#                 continue
        
#         if logger:
#             logger.error(f"❌ {putih}[{biru}Email{putih}] {R}Email field tidak ditemukan")
#         return False
        
#     except Exception as e:
#         if logger:
#             logger.error(f"❌ {putih}[{biru}Email{putih}] {R}Error dalam fill_google_email: {e}")
#         return False


def fill_google_email(driver, email, logger=None):
    """
    Isi field email Google
    """
    try:
        email_selectors = [
            "input[type='email']",
            "input[name='identifier']",
            "input[id='identifierId']",
            "#Email",
            "[data-testid='email']"
        ]
        
        for selector in email_selectors:
            try:
                email_field = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                if email_field:
                    # Clear dan isi email
                    email_field.clear()
                    time.sleep(0.5)
                    
                    # Type email dengan delay natural
                    for char in email:
                        email_field.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.15))
                    
                    time.sleep(1)
                    
                    # Tekan Enter atau cari tombol Next
                    try:
                        email_field.send_keys(Keys.ENTER)
                        if logger:
                            logger.info(f"✅ [Email] Email diisi dan Enter ditekan")
                    except:
                        # Cari tombol Next
                        next_button = driver.find_element(By.CSS_SELECTOR, "#identifierNext, [data-testid='next'], button:contains('Next')")
                        if next_button:
                            next_button.click()
                            if logger:
                                logger.info(f"✅ [Email] Email diisi dan Next diklik")
                    
                    time.sleep(random.uniform(2, 4))
                    return True
                    
            except TimeoutException:
                continue
            except Exception as e:
                continue
        
        if logger:
            logger.error(f"❌ [Email] Email field tidak ditemukan")
        return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Email] Error dalam fill_google_email: {e}")
        return False




# def fill_google_password(driver, password, logger=None):
#     """
#     Isi field password Google - TANPA cleanup_popups_once (sudah dipindah ke handle_google_popup)
#     """
#     try:
#         password_selectors = [
#             "input[type='password']",
#             "input[name='password']",
#             "#password",
#             "[data-testid='password']"
#         ]
        
#         for selector in password_selectors:
#             try:
#                 if logger:
#                     logger.info(f"🔍 {putih}[{biru}Password{putih}] Mencoba selector: {Y}{selector}")
                
#                 password_field = WebDriverWait(driver, 10).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
#                 )
                
#                 if password_field:
#                     # Clear dan isi password
#                     password_field.clear()
#                     time.sleep(0.5)
                    
#                     # Type password dengan delay natural
#                     for char in password:
#                         password_field.send_keys(char)
#                         time.sleep(random.uniform(0.05, 0.15))
                    
#                     time.sleep(1)
                    
#                     # Tekan Enter atau cari tombol Next/Sign in
#                     try:
#                         password_field.send_keys(Keys.ENTER)
#                         if logger:
#                             logger.info(f"✅ {putih}[{biru}Password{putih}] {G}Password diisi dan Enter ditekan")
                        
#                     except:
#                         # Cari tombol Sign in/Next
#                         signin_selectors = [
#                             "#passwordNext",
#                             "[data-testid='signin']",
#                             "button:contains('Sign in')",
#                             "button:contains('Next')"
#                         ]
                        
#                         for signin_selector in signin_selectors:
#                             try:
#                                 if ':contains(' in signin_selector:
#                                     text = signin_selector.split(':contains(')[1].split(')')[0].strip("'\"")
#                                     xpath = f"//button[contains(text(), '{text}')]"
#                                     signin_button = driver.find_element(By.XPATH, xpath)
#                                 else:
#                                     signin_button = driver.find_element(By.CSS_SELECTOR, signin_selector)
                                    
#                                 if signin_button:
#                                     signin_button.click()
#                                     if logger:
#                                         logger.info(f"✅ {putih}[{biru}Password{putih}] {G}Password diisi dan Sign in diklik")
#                                     break
#                             except:
#                                 continue
                    
#                     time.sleep(random.uniform(3, 5))
#                     return True
                    
#             except TimeoutException:
#                 continue
#             except Exception as e:
#                 if logger:
#                     logger.warning(f"⚠️ {putih}[{biru}Password{putih}] {R}Error dengan selector {selector}: {e}")
#                 continue
        
#         if logger:
#             logger.error(f"❌ {putih}[{biru}Password{putih}] {G}Password field tidak ditemukan")
#         return False
        
#     except Exception as e:
#         if logger:
#             logger.error(f"❌ {putih}[{biru}Password{putih}] Error dalam fill_google_password: {e}")
#         return False


def fill_google_password(driver, password, logger=None):
    """
    Isi field password Google - TANPA cleanup_popups_once (sudah dipindah ke handle_google_popup)
    """
    try:
        password_selectors = [
            "input[type='password']",
            "input[name='password']",
            "#password",
            "[data-testid='password']"
        ]
        
        for selector in password_selectors:
            try:
                password_field = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                if password_field:
                    # Clear dan isi password
                    password_field.clear()
                    time.sleep(0.5)
                    
                    # Type password dengan delay natural
                    for char in password:
                        password_field.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.15))
                    
                    time.sleep(1)
                    
                    # Tekan Enter atau cari tombol Next/Sign in
                    try:
                        password_field.send_keys(Keys.ENTER)
                        if logger:
                            logger.info(f"✅ [Password] Password diisi dan Enter ditekan")
                        
                    except:
                        # Cari tombol Sign in/Next
                        signin_selectors = [
                            "#passwordNext",
                            "[data-testid='signin']",
                            "button:contains('Sign in')",
                            "button:contains('Next')"
                        ]
                        
                        for signin_selector in signin_selectors:
                            try:
                                if ':contains(' in signin_selector:
                                    text = signin_selector.split(':contains(')[1].split(')')[0].strip("'\"")
                                    xpath = f"//button[contains(text(), '{text}')]"
                                    signin_button = driver.find_element(By.XPATH, xpath)
                                else:
                                    signin_button = driver.find_element(By.CSS_SELECTOR, signin_selector)
                                    
                                if signin_button:
                                    signin_button.click()
                                    if logger:
                                        logger.info(f"✅ [Password] Password diisi dan Sign in diklik")
                                    break
                            except:
                                continue
                    
                    time.sleep(random.uniform(3, 5))
                    return True
                    
            except TimeoutException:
                continue
            except Exception as e:
                continue
        
        if logger:
            logger.error(f"❌ [Password] Password field tidak ditemukan")
        return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Password] Error dalam fill_google_password: {e}")
        return False



def comprehensive_popup_cleanup(driver, logger=None):
    """
    Comprehensive popup cleanup
    """
    try:
        if logger:
            logger.info("🧹 [Cleanup] Comprehensive popup cleanup...")
        
        # Berbagai selector untuk popup close buttons
        close_selectors = [
            "button#close.ng-scope",
            "button[id*='close']",
            "button.close",
            ".close",
            "[class*='close']",
            ".dismiss",
            "[class*='dismiss']",
            ".fa-times",
            ".icon-close",
            "[aria-label='Close']",
            "[title='Close']",
            "[id*='close']",
            "[id*='dismiss']",
            ".modal-backdrop",
            ".overlay",
            ".popup-overlay",
            "[data-dismiss='modal']",
            ".modal-close",
            "button[class*='close']"
        ]
        
        popups_closed = 0
        
        for selector in close_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        try:
                            element.click()
                            popups_closed += 1
                            if logger:
                                logger.info(f"🗑️ [Cleanup] Popup closed: {selector}")
                            time.sleep(random.uniform(0.5, 1))
                        except:
                            continue
                        
            except Exception as e:
                continue
        
        # Tekan Escape untuk menutup popup
        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            if logger:
                logger.info("⌨️ [Cleanup] Escape key pressed")
            time.sleep(1)
        except:
            pass
        
        if logger:
            logger.info(f"✅ [Cleanup] Cleanup selesai, {popups_closed} popup ditutup")
        
        return True
        
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ [Cleanup] Error dalam comprehensive_popup_cleanup: {e}")
        return False

def cleanup_popup_setelah_login_google(driver, logger=None):
    """
    Cleanup popup spesifik yang muncul setelah login Google berhasil
    """
    try:
        if logger:
            logger.info("🔍 [Google Cleanup] Mencari popup setelah login Google...")
        
        # ✅ SELECTOR SPESIFIK UNTUK POPUP SETELAH LOGIN GOOGLE
        popup_setelah_login_selectors = [
            # Popup konfirmasi login
            "[aria-label='Close']",
            "[aria-label='close']",
            "[aria-label*='close' i]",
            
            # Welcome/success popup
            "[data-testid='close']",
            "[data-testid='close-button']",
            "[data-hook='close-button']",
            
            # Modal setelah login
            ".modal-close",
            ".close-button",
            ".close",
            "button.close",
            
            # Popup notifikasi
            ".notification-close",
            ".alert-close",
            "[class*='close']",
            
            # Overlay setelah login
            ".overlay-close",
            ".popup-close",
            "[data-dismiss='modal']",
            "[data-dismiss='popup']",
            
            # Generic close buttons
            "button[title*='close' i]",
            "button[aria-label*='close' i]",
            "[role='button'][aria-label*='close' i]",
            
            # Icon-based close
            ".fa-times",
            ".fa-close",
            ".icon-close",
            ".icon-times",
            
            # Specific untuk website ini
            "button#close.ng-scope",
            "button[id='close'][class='ng-scope']",
            "button#close[aria-label='Close']",
            "#close.ng-scope"
        ]
        
        popup_ditutup = False
        popup_count = 0
        
        # ✅ COBA TUTUP POPUP DENGAN 3 METHOD
        for selector in popup_setelah_login_selectors:
            try:
                popup_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for popup in popup_elements:
                    if popup.is_displayed() and popup.is_enabled():
                        if logger:
                            logger.info(f"🚨 [Google Cleanup] Popup setelah login ditemukan: {selector}")
                        
                        # ✅ METHOD 1: DIRECT CLICK
                        try:
                            popup.click()
                            popup_ditutup = True
                            popup_count += 1
                            
                            if logger:
                                logger.info(f"✓ [Google Cleanup] Popup #{popup_count} ditutup dengan klik normal")
                            
                            time.sleep(0.5)
                            return True  # Return langsung setelah tutup 1 popup
                            
                        except ElementClickInterceptedException:
                            try:
                                # ✅ METHOD 2: JAVASCRIPT CLICK
                                driver.execute_script("arguments[0].click();", popup)
                                popup_ditutup = True
                                popup_count += 1
                                
                                if logger:
                                    logger.info(f"✓ [Google Cleanup] Popup #{popup_count} ditutup dengan JavaScript")
                                
                                time.sleep(0.5)
                                return True
                                
                            except Exception:
                                try:
                                    # ✅ METHOD 3: FORCE HIDE
                                    driver.execute_script("""
                                        var element = arguments[0];
                                        element.style.display = 'none';
                                        element.style.visibility = 'hidden';
                                        element.style.opacity = '0';
                                        
                                        // Hide parent containers
                                        var parent = element.parentNode;
                                        if (parent) {
                                            parent.style.display = 'none';
                                        }
                                        
                                        // Hide modal backdrop if exists
                                        var backdrop = document.querySelector('.modal-backdrop, .overlay, .popup-overlay');
                                        if (backdrop) {
                                            backdrop.style.display = 'none';
                                        }
                                    """, popup)
                                    
                                    popup_ditutup = True
                                    popup_count += 1
                                    
                                    if logger:
                                        logger.info(f"✓ [Google Cleanup] Popup #{popup_count} disembunyikan dengan force hide")
                                    
                                    time.sleep(0.5)
                                    return True
                                    
                                except Exception:
                                    continue
                        
                        except Exception:
                            continue
                
                # ✅ BATAS MAKSIMAL 3 POPUP PER CLEANUP
                if popup_count >= 3:
                    if logger:
                        logger.info(f"🛑 [Google Cleanup] Batas maksimal {popup_count} popup tercapai")
                    break
                    
            except Exception:
                continue
        
        # ✅ FALLBACK: ESC KEY
        if not popup_ditutup:
            try:
                if logger:
                    logger.info("🔄 [Google Cleanup] Mencoba ESC key sebagai fallback...")
                
                actions = ActionChains(driver)
                actions.send_keys(Keys.ESCAPE)
                actions.perform()
                time.sleep(0.3)
                
                # ✅ CEK APAKAH ESC BERHASIL
                remaining_popups = driver.find_elements(By.CSS_SELECTOR, ".modal, .popup, .overlay, [class*='modal'], [class*='popup']")
                visible_popups = [el for el in remaining_popups if el.is_displayed()]
                
                if len(visible_popups) == 0:
                    popup_ditutup = True
                    if logger:
                        logger.info("✅ [Google Cleanup] ESC key berhasil tutup popup")
                
            except Exception:
                pass
        
        # ✅ SUMMARY
        if popup_ditutup:
            if logger:
                logger.info(f"✅ [Google Cleanup] Cleanup setelah login selesai: {popup_count} popup ditutup")
        else:
            if logger:
                logger.info("ℹ️ [Google Cleanup] Tidak ada popup setelah login yang ditemukan")
        
        return popup_ditutup
        
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ [Google Cleanup] Error: {e}")
        return False

# pengaturan popup window



# Jika file ini dijalankan langsung (bukan diimpor)
# Jika file ini dijalankan langsung (bukan diimpor)
if __name__ == "__main__":
    print("🤖 File popups.py - Website2 Template")
    print("=" * 40)
    print("📝 Fungsi yang tersedia:")
    print("1. handle_popup_dengan_retry(driver, logger, max_retries)")
    print("2. handle_google_popup(driver, logger)")
    print("3. handle_google_login_process(driver, logger)")
    print("4. load_google_account()")
    print("5. perform_google_login(driver, email, password, logger)")
    print("6. comprehensive_popup_cleanup(driver, logger)")
    print("7. cleanup_popup_setelah_login_google(driver, logger)")  # ← TAMBAHAN
    print("\n⚠️ File ini dirancang untuk diimpor oleh actions.py")
    print("   Pastikan file akun.txt sudah dibuat dengan format:")
    print("   Baris 1: email@gmail.com")
    print("   Baris 2: password")