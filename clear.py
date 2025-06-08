from colorama import Fore, init
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Initialize Colorama
init(autoreset=True)

# Colors for terminal text
B = Fore.BLUE
W = Fore.WHITE
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW

def logout_dari_google(driver, logger=None):
    """
    Logout dari Google secara menyeluruh
    """
    def log_message(message):
        if logger:
            logger.info(message)
        else:
            print(message)
    
    try:
        log_message(f"{Y}Melakukan logout dari Google...{W}")
        
        # Buka halaman logout Google dengan timeout
        driver.set_page_load_timeout(30)
        driver.get("https://accounts.google.com/logout")
        time.sleep(3)
        
        log_message(f"{G}✓ Logout dari Google berhasil{W}")
        
        # Buka halaman untuk menghapus semua akun yang tersimpan
        driver.get("https://accounts.google.com/signout")
        time.sleep(2)
        
        log_message(f"{G}✓ Signout dari semua akun Google{W}")
        
        return True
        
    except TimeoutException:
        log_message(f"{Y}⚠️ Timeout saat logout dari Google{W}")
        return False
    except WebDriverException as e:
        log_message(f"{Y}⚠️ WebDriver error saat logout: {W}{e}")
        return False
    except Exception as e:
        log_message(f"{Y}⚠️ Gagal logout dari Google: {W}{e}")
        return False
    
def hapus_cookies_menyeluruh(driver, logger=None):
    """
    Menghapus semua cookies termasuk cookies Google
    """
    def log_message(message):
        if logger:
            logger.info(message)
        else:
            print(message)
    
    try:
        log_message(f"{Y}Menghapus semua cookies...{W}")
        
        # Hapus semua cookies dari domain saat ini
        driver.delete_all_cookies()
        log_message(f"{G}✓ Cookies domain saat ini dihapus{W}")
        
        # Kunjungi domain Google dan hapus cookies
        google_domains = [
            "https://google.com",
            "https://accounts.google.com", 
            "https://myaccount.google.com",
            "https://gmail.com",
            "https://youtube.com"
        ]
        
        # Set timeout untuk safety
        original_timeout = driver.timeouts.page_load
        driver.set_page_load_timeout(15)
        
        for domain in google_domains:
            try:
                driver.get(domain)
                time.sleep(1)
                driver.delete_all_cookies()
                log_message(f"{G}✓ Cookies {domain} dihapus{W}")
            except TimeoutException:
                log_message(f"{Y}⚠️ Timeout accessing {domain}{W}")
                continue
            except WebDriverException as e:
                log_message(f"{Y}⚠️ Error accessing {domain}: {W}{e}")
                continue
            except Exception as e:
                log_message(f"{Y}⚠️ Gagal hapus cookies {domain}: {W}{e}")
                continue
        
        # Restore original timeout
        driver.set_page_load_timeout(original_timeout)
        return True
        
    except Exception as e:
        log_message(f"{R}❌ Gagal menghapus cookies: {W}{e}")
        return False

def hapus_semua_data_browser(driver, logger=None):
    """
    Menghapus semua data browser secara menyeluruh
    """
    def log_message(message):
        if logger:
            logger.info(message)
        else:
            print(message)
    
    try:
        log_message(f"{Y}Menghapus semua data browser...{W}")
        
        # Script JavaScript untuk menghapus semua data
        cleanup_script = """
        // 1. Clear semua storage
        try {
            var results = [];
            
            // Clear localStorage
            if (window.localStorage) {
                window.localStorage.clear();
                results.push('localStorage cleared');
            }
            
            // Clear sessionStorage
            if (window.sessionStorage) {
                window.sessionStorage.clear();
                results.push('sessionStorage cleared');
            }
            
            // Clear IndexedDB
            if (window.indexedDB) {
                indexedDB.databases().then(databases => {
                    databases.forEach(db => {
                        indexedDB.deleteDatabase(db.name);
                    });
                }).catch(e => console.log('IndexedDB clear error:', e));
                results.push('IndexedDB cleanup initiated');
            }
            
            // Clear Cache API
            if ('caches' in window) {
                caches.keys().then(names => {
                    names.forEach(name => {
                        caches.delete(name);
                    });
                }).catch(e => console.log('Cache clear error:', e));
                results.push('Cache cleanup initiated');
            }
            
            // Clear Service Workers
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.getRegistrations().then(registrations => {
                    registrations.forEach(registration => {
                        registration.unregister();
                    });
                }).catch(e => console.log('Service Worker clear error:', e));
                results.push('Service Worker cleanup initiated');
            }
            
            return "Browser data cleanup: " + results.join(', ');
            
        } catch(e) {
            return "Error saat menghapus data: " + e.message;
        }
        """
        
        try:
            result = driver.execute_script(cleanup_script)
            if result:
                log_message(f"{G}✓ {result}{W}")
            else:
                log_message(f"{Y}⚠️ JavaScript cleanup returned empty result{W}")
        except WebDriverException as e:
            log_message(f"{Y}⚠️ JavaScript execution error: {W}{e}")
            return False
        
        return True
        
    except Exception as e:
        log_message(f"{R}❌ Gagal menghapus data browser: {W}{e}")
        return False

def reset_browser_state(driver, logger=None):
    """
    Reset state browser ke kondisi awal
    """
    def log_message(message):
        if logger:
            logger.info(message)
        else:
            print(message)
    
    try:
        log_message(f"{Y}Reset state browser...{W}")
        
        # Tutup semua tab kecuali tab utama
        try:
            window_handles = driver.window_handles
            if len(window_handles) > 1:
                main_window = window_handles[0]
                for handle in window_handles[1:]:
                    try:
                        driver.switch_to.window(handle)
                        driver.close()
                    except WebDriverException:
                        continue  # Tab mungkin sudah tertutup
                driver.switch_to.window(main_window)
                log_message(f"{G}✓ Tab tambahan ditutup{W}")
        except Exception as e:
            log_message(f"{Y}⚠️ Gagal menutup tab tambahan: {W}{e}")
        
        # Reset zoom level
        try:
            driver.execute_script("document.body.style.zoom = '100%';")
            log_message(f"{G}✓ Zoom level direset{W}")
        except Exception as e:
            log_message(f"{Y}⚠️ Gagal reset zoom: {W}{e}")
        
        # Clear browser history (jika memungkinkan)
        try:
            driver.execute_script("""
            if (window.history && window.history.clear) {
                window.history.clear();
            }
            """)
            log_message(f"{G}✓ History browser dibersihkan{W}")
        except Exception as e:
            log_message(f"{Y}⚠️ Gagal clear history: {W}{e}")
        
        return True
        
    except Exception as e:
        log_message(f"{R}❌ Gagal reset browser state: {W}{e}")
        return False
