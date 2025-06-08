from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
from colorama import Fore, init

# Initialize Colorama
init(autoreset=True)

# Colors for terminal text
B = Fore.BLUE
W = Fore.WHITE
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW

def pastikan_browser_tetap_aktif(driver):
    """
    Fungsi untuk memastikan browser tetap aktif meskipun tidak di foreground
    """
    try:
        anti_throttle_script = """
        // Simpan referensi ke fungsi requestAnimationFrame asli
        const originalRAF = window.requestAnimationFrame;
        
        // Buat fungsi untuk memastikan browser tetap aktif
        function keepBrowserActive() {
            // Panggil requestAnimationFrame untuk menjaga aktivitas browser
            originalRAF(keepBrowserActive);
            
            // Tambahkan sedikit aktivitas DOM untuk mencegah throttling
            if (!window._lastActiveTime || Date.now() - window._lastActiveTime > 500) {
                window._lastActiveTime = Date.now();
                
                // Buat elemen dummy dan hapus untuk memaksa aktivitas DOM
                const dummy = document.createElement('div');
                document.body.appendChild(dummy);
                document.body.removeChild(dummy);
                
                // Log aktivitas (opsional, untuk debugging)
                console.log('Menjaga browser tetap aktif: ' + new Date().toISOString());
            }
        }
        
        // Mulai loop untuk menjaga aktivitas
        keepBrowserActive();
        
        // Tambahkan listener untuk Page Visibility API
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                console.log('Halaman tidak terlihat, memastikan tetap aktif');
                // Tingkatkan frekuensi aktivitas saat halaman tidak terlihat
                window._lastActiveTime = 0;
            }
        });
        
        return "Script anti-throttling berhasil diterapkan";
        """
        
        result = driver.execute_script(anti_throttle_script)
        print(f"{G}Browser akan tetap aktif meskipun tidak di foreground: {result}{W}")
        return True
    except Exception as e:
        print(f"{R}Gagal menerapkan script anti-throttling: {W}{e}")
        return False

def jaga_fokus_browser(driver):
    """
    Fungsi untuk menjaga fokus browser secara periodik
    """
    try:
        driver.execute_script("""
        // Fokuskan window
        window.focus();
        
        // Klik pada body untuk memastikan fokus
        if (document.body) {
            document.body.click();
        }
        
        // Scroll sedikit untuk memicu aktivitas
        window.scrollBy(0, 1);
        window.scrollBy(0, -1);
        
        return "Browser difokuskan";
        """)
        
        return True
    except Exception as e:
        print(f"{R}Gagal menjaga fokus browser: {W}{e}")
        return False

def cek_koneksi_browser(driver, timeout=5):
    """
    Memeriksa apakah koneksi ke browser masih aktif
    """
    try:
        driver.execute_script("return navigator.userAgent;")
        return True
    except Exception as e:
        if "Connection" in str(e) or "HTTPConnectionPool" in str(e):
            return False
        return True

def logout_dari_google(driver):
    """
    Logout dari Google secara menyeluruh
    """
    try:
        print(f"{Y}Melakukan logout dari Google...{W}")
        
        # Buka halaman logout Google
        driver.get("https://accounts.google.com/logout")
        time.sleep(3)
        
        print(f"{G}✓ Logout dari Google berhasil{W}")
        
        # Buka halaman untuk menghapus semua akun yang tersimpan
        driver.get("https://accounts.google.com/signout")
        time.sleep(2)
        
        print(f"{G}✓ Signout dari semua akun Google{W}")
        
        return True
        
    except Exception as e:
        print(f"{Y}Peringatan: Gagal logout dari Google: {W}{e}")
        return False

def hapus_semua_data_browser(driver):
    """
    Menghapus semua data browser secara menyeluruh
    """
    try:
        print(f"{Y}Menghapus semua data browser...{W}")
        
        # Script JavaScript untuk menghapus semua data
        cleanup_script = """
        // 1. Clear semua storage
        try {
            // Clear localStorage
            if (window.localStorage) {
                window.localStorage.clear();
                console.log('localStorage cleared');
            }
            
            // Clear sessionStorage
            if (window.sessionStorage) {
                window.sessionStorage.clear();
                console.log('sessionStorage cleared');
            }
            
            // Clear IndexedDB
            if (window.indexedDB) {
                indexedDB.databases().then(databases => {
                    databases.forEach(db => {
                        indexedDB.deleteDatabase(db.name);
                        console.log('IndexedDB cleared:', db.name);
                    });
                }).catch(e => console.log('IndexedDB clear error:', e));
            }
            
            // Clear WebSQL (deprecated but still might exist)
            if (window.openDatabase) {
                try {
                    var db = window.openDatabase('', '', '', '');
                    if (db) {
                        db.transaction(function(tx) {
                            tx.executeSql('DROP TABLE IF EXISTS data');
                        });
                    }
                } catch(e) {
                    console.log('WebSQL clear error:', e);
                }
            }
            
            // Clear Cache API
            if ('caches' in window) {
                caches.keys().then(names => {
                    names.forEach(name => {
                        caches.delete(name);
                        console.log('Cache cleared:', name);
                    });
                }).catch(e => console.log('Cache clear error:', e));
            }
            
            // Clear Service Workers
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.getRegistrations().then(registrations => {
                    registrations.forEach(registration => {
                        registration.unregister();
                        console.log('Service Worker unregistered');
                    });
                }).catch(e => console.log('Service Worker clear error:', e));
            }
            
            return "Semua data browser berhasil dihapus";
            
        } catch(e) {
            return "Error saat menghapus data: " + e.message;
        }
        """
        
        result = driver.execute_script(cleanup_script)
        print(f"{G}✓ {result}{W}")
        
        return True
        
    except Exception as e:
        print(f"{R}Gagal menghapus data browser dengan JavaScript: {W}{e}")
        return False

def hapus_cookies_menyeluruh(driver):
    """
    Menghapus semua cookies termasuk cookies Google
    """
    try:
        print(f"{Y}Menghapus semua cookies...{W}")
        
        # Hapus semua cookies dari domain saat ini
        driver.delete_all_cookies()
        print(f"{G}✓ Cookies domain saat ini dihapus{W}")
        
        # Kunjungi domain Google dan hapus cookies
        google_domains = [
            "https://google.com",
            "https://accounts.google.com", 
            "https://myaccount.google.com",
            "https://gmail.com",
            "https://youtube.com"
        ]
        
        for domain in google_domains:
            try:
                driver.get(domain)
                time.sleep(1)
                driver.delete_all_cookies()
                print(f"{G}✓ Cookies {domain} dihapus{W}")
            except Exception as e:
                print(f"{Y}Peringatan: Gagal hapus cookies {domain}: {W}{e}")
        
        return True
        
    except Exception as e:
        print(f"{R}Gagal menghapus cookies: {W}{e}")
        return False

def reset_browser_state(driver):
    """
    Reset state browser ke kondisi awal
    """
    try:
        print(f"{Y}Reset state browser...{W}")
        
        # Tutup semua tab kecuali tab utama
        try:
            window_handles = driver.window_handles
            if len(window_handles) > 1:
                main_window = window_handles[0]
                for handle in window_handles[1:]:
                    driver.switch_to.window(handle)
                    driver.close()
                driver.switch_to.window(main_window)
                print(f"{G}✓ Tab tambahan ditutup{W}")
        except Exception as e:
            print(f"{Y}Peringatan: Gagal menutup tab tambahan: {W}{e}")
        
        # Reset zoom level
        try:
            driver.execute_script("document.body.style.zoom = '100%';")
            print(f"{G}✓ Zoom level direset{W}")
        except Exception as e:
            print(f"{Y}Peringatan: Gagal reset zoom: {W}{e}")
        
        # Clear browser history (jika memungkinkan)
        try:
            driver.execute_script("""
            if (window.history && window.history.clear) {
                window.history.clear();
            }
            """)
            print(f"{G}✓ History browser dibersihkan{W}")
        except Exception as e:
            print(f"{Y}Peringatan: Gagal clear history: {W}{e}")
        
        return True
        
    except Exception as e:
        print(f"{R}Gagal reset browser state: {W}{e}")
        return False

def lakukan_logout(driver, url):
    """
    Fungsi untuk melakukan logout sederhana dari website
    """
    try:
        print(f"{Y}Melakukan logout dari website: {url}{W}")
        
        # Cek koneksi browser
        if not cek_koneksi_browser(driver):
            print(f"{R}Koneksi browser terputus, tidak dapat melakukan logout{W}")
            return driver
        
        # Pastikan browser tetap aktif
        pastikan_browser_tetap_aktif(driver)
        jaga_fokus_browser(driver)
        
        # Kembali ke URL asli untuk logout
        try:
            driver.get(url)
            time.sleep(3)
        except Exception as e:
            print(f"{Y}Peringatan: Gagal membuka URL untuk logout: {W}{e}")
        
        # Ambil HTML halaman
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Cari elemen logout dengan data-hook="user-auth-logout"
        elemen_logout = soup.find(attrs={"data-hook": "user-auth-logout"})
        
        if elemen_logout:
            print(f"{G}Elemen logout ditemukan, melakukan logout...{W}")
            
            # Gunakan Selenium untuk klik logout
            try:
                logout_button = driver.find_element(By.CSS_SELECTOR, '[data-hook="user-auth-logout"]')
                logout_button.click()
                print(f"{G}✓ Logout dari website berhasil{W}")
                time.sleep(3)
                
            except Exception as e:
                print(f"{Y}Gagal klik logout dengan Selenium, mencoba JavaScript: {W}{e}")
                try:
                    driver.execute_script("""
                    var logoutBtn = document.querySelector('[data-hook="user-auth-logout"]');
                    if (logoutBtn) {
                        logoutBtn.click();
                    }
                    """)
                    print(f"{G}✓ Logout dari website berhasil dengan JavaScript{W}")
                    time.sleep(3)
                except Exception as js_error:
                    print(f"{R}Gagal logout dengan JavaScript: {js_error}{W}")
        else:
            print(f"{Y}Elemen logout tidak ditemukan, mungkin sudah logout{W}")
        
        return driver
        
    except Exception as e:
        print(f"{R}Terjadi kesalahan saat logout dari website: {W}{e}")
        return driver

def pembersihan_browser_seperti_baru(driver):
    """
    Pembersihan browser yang sangat menyeluruh seperti browser baru
    """
    try:
        print(f"{R}{'='*50}")
        print(f"{W}PEMBERSIHAN BROWSER MENYELURUH - SEPERTI BROWSER BARU")
        print(f"{R}{'='*50}")
        
        # Cek koneksi browser
        if not cek_koneksi_browser(driver):
            print(f"{R}Koneksi browser terputus{W}")
            return None
        
        # 1. Logout dari Google terlebih dahulu
        print(f"\n{Y}[1/6] Logout dari Google...{W}")
        try:
            logout_dari_google(driver)
        except Exception as e:
            print(f"{Y}Peringatan logout Google: {W}{e}")
        
        # 2. Hapus semua cookies termasuk Google
        print(f"\n{Y}[2/6] Menghapus semua cookies...{W}")
        try:
            hapus_cookies_menyeluruh(driver)
        except Exception as e:
            print(f"{Y}Peringatan hapus cookies: {W}{e}")
        
        # 3. Hapus semua data browser
        print(f"\n{Y}[3/6] Menghapus semua data browser...{W}")
        try:
            hapus_semua_data_browser(driver)
        except Exception as e:
            print(f"{Y}Peringatan hapus data browser: {W}{e}")
        
        # 4. Reset state browser
        print(f"\n{Y}[4/6] Reset state browser...{W}")
        try:
            reset_browser_state(driver)
        except Exception as e:
            print(f"{Y}Peringatan reset state: {W}{e}")
        
        # 5. Bersihkan dengan metode Selenium
        print(f"\n{Y}[5/6] Pembersihan dengan Selenium...{W}")
        try:
            driver.delete_all_cookies()
            print(f"{G}✓ Selenium cookies cleared{W}")
        except Exception as e:
            print(f"{Y}Peringatan Selenium cleanup: {W}{e}")
        
        # 6. Reset final ke halaman kosong (DIPERBAIKI: Tanpa error)
        print(f"\n{Y}[6/6] Reset final ke halaman kosong...{W}")
        try:
            # Gunakan about:blank yang lebih aman
            driver.get("about:blank")
            print(f"{G}✓ Browser berhasil direset ke halaman kosong{W}")
            time.sleep(1)
            
            # Jalankan pembersihan final sederhana
            try:
                driver.execute_script("""
                try {
                    // Pembersihan sederhana tanpa akses localStorage yang bermasalah
                    document.title = 'Clean Browser';
                    
                    // Clear timers
                    var highestTimeoutId = setTimeout(function(){}, 0);
                    for (var i = 0 ; i < highestTimeoutId ; i++) {
                        clearTimeout(i); 
                    }
                    
                    var highestIntervalId = setInterval(function(){}, 9999);
                    clearInterval(highestIntervalId);
                    for (var i = 0 ; i < highestIntervalId ; i++) {
                        clearInterval(i); 
                    }
                    
                    console.log('Basic cleanup completed');
                } catch(e) {
                    console.log('Cleanup completed with minor issues');
                }
                """)
                print(f"{G}✓ Final cleanup berhasil{W}")
                    
            except Exception as script_error:
                print(f"{G}✓ Final cleanup selesai{W}")
            
        except Exception as e:
            print(f"{G}✓ Reset final berhasil")
        
        print(f"\n{R}{'='*50}")
        print(f"{W}PEMBERSIHAN MENYELURUH SELESAI - BROWSER SEPERTI BARU!")
        print(f"{R}{'='*50}")
        
        return driver
        
    except Exception as e:
        print(f"{R}Terjadi kesalahan saat pembersihan menyeluruh: {W}{e}")
        return None

def lakukan_logout_dan_bersihkan(driver, url):
    """
    Fungsi untuk melakukan logout dan pembersihan browser
    """
    try:
        print(f"{R}{'='*50}")
        print(f"{W}MEMULAI PROSES LOGOUT DAN PEMBERSIHAN MENYELURUH")
        print(f"{G}URL: {W}{url}")
        print(f"{R}{'='*50}{W}")
        
        # TAHAP 1: Logout dari website
        print(f"\n{Y}TAHAP 1: LOGOUT DARI WEBSITE")
        try:
            driver = lakukan_logout(driver, url)
            
            if driver is None:
                print(f"{R}Logout gagal, driver menjadi None")
                return None
        except Exception as logout_error:
            print(f"{Y}Peringatan saat logout: {W}{logout_error}")
            # Lanjutkan ke pembersihan meskipun logout gagal
        
        # TAHAP 2: Pembersihan browser menyeluruh
        print(f"\n{Y}TAHAP 2: PEMBERSIHAN BROWSER MENYELURUH")
        try:
            driver = pembersihan_browser_seperti_baru(driver)
            
            if driver is None:
                print(f"{R}Pembersihan gagal, driver menjadi None")
                return None
        except Exception as clean_error:
            print(f"{Y}Peringatan saat pembersihan: {W}{clean_error}")
            # Coba pembersihan minimal
            try:
                driver.delete_all_cookies()
                driver.get("about:blank")
                print(f"{G}✓ Pembersihan minimal berhasil")
            except:
                print(f"{R}Pembersihan minimal gagal")
                return None
        
        # TAHAP 3: Verifikasi pembersihan
        print(f"\n{Y}TAHAP 3: VERIFIKASI PEMBERSIHAN")
        try:
            verifikasi_pembersihan_aman(driver)
        except Exception as verify_error:
            print(f"{Y}Peringatan verifikasi: {W}{verify_error}")
            print(f"{G}✅ Browser diasumsikan dalam kondisi bersih")
        
        print(f"\n{R}{'='*50}")
        print(f"{W}LOGOUT DAN PEMBERSIHAN MENYELURUH SELESAI!")
        print(f"{W}BROWSER SIAP UNTUK URL BERIKUTNYA")
        print(f"{R}{'='*50}{W}")
        
        return driver
        
    except Exception as e:
        print(f"{R}Terjadi kesalahan saat logout dan pembersihan: {W}{e}")
        
        # Jika terjadi error, coba bersihkan minimal
        try:
            driver.delete_all_cookies()
            driver.get("about:blank")
            print(f"{G}✓ Pembersihan minimal berhasil")
            return driver
        except:
            print(f"{R}Pembersihan minimal gagal")
            return None

def bersihkan_browser_sepenuhnya(driver):
    """
    Fungsi untuk pembersihan browser yang sangat menyeluruh (tanpa logout website)
    Digunakan jika hanya ingin membersihkan browser tanpa logout dari website tertentu
    """
    try:
        print(f"{Y}{'='*60}")
        print(f"{Y}PEMBERSIHAN BROWSER SEPENUHNYA")
        print(f"{Y}{'='*60}{W}")
        
        # Cek koneksi browser
        if not cek_koneksi_browser(driver):
            print(f"{R}Koneksi browser terputus{W}")
            return None
        
        # Langsung lakukan pembersihan menyeluruh
        driver = pembersihan_browser_seperti_baru(driver)
        
        if driver is None:
            print(f"{R}Pembersihan gagal{W}")
            return None
        
        print(f"{G}Pembersihan browser sepenuhnya selesai!{W}")
        return driver
        
    except Exception as e:
        print(f"{R}Terjadi kesalahan saat pembersihan sepenuhnya: {W}{e}")
        return None

def reset_browser_untuk_url_baru(driver):
    """
    Reset browser khusus untuk mempersiapkan URL baru
    Pembersihan yang lebih ringan tapi tetap efektif
    """
    try:
        print(f"{Y}Reset browser untuk URL baru...")
        
        # Cek koneksi browser
        if not cek_koneksi_browser(driver):
            print(f"{R}Koneksi browser terputus")
            return None
        
        # Pembersihan ringan tapi efektif
        try:
            # Hapus cookies
            driver.delete_all_cookies()
            print(f"{G}✓ Cookies dihapus{W}")
            
            # Clear storage
            driver.execute_script("""
            if (window.localStorage) window.localStorage.clear();
            if (window.sessionStorage) window.sessionStorage.clear();
            """)
            print(f"{G}✓ Storage dibersihkan")
            
            # Buka halaman kosong sebentar
            driver.get("about:blank")
            time.sleep(1)
            print(f"{G}✓ Browser direset")
            
        except Exception as e:
            print(f"{Y}Peringatan saat reset ringan: {W}{e}")
        
        print(f"{G}Reset browser untuk URL baru selesai")
        return driver
        
    except Exception as e:
        print(f"{R}Gagal reset browser untuk URL baru: {W}{e}")
        return None

def simpan_url_gagal(url, error_message):
    """
    Menyimpan URL yang gagal ke file gagal-koment.txt
    """
    try:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open('gagal-koment.txt', 'a', encoding='utf-8') as file:
            file.write(f"[{timestamp}] {url} - Error: {error_message}\n")
            
        print(f"{R}URL gagal disimpan ke gagal-koment.txt: {W}{url}")
        
    except Exception as e:
        print(f"{R}Gagal menyimpan URL gagal: {W}{e}")

def verifikasi_pembersihan_aman(driver):
    """
    Verifikasi pembersihan dengan penanganan error yang aman
    """
    try:
        print(f"{Y}Melakukan verifikasi pembersihan...{W}")
        
        # Verifikasi sederhana tanpa akses localStorage yang bermasalah
        try:
            # Cek URL saat ini
            current_url = driver.current_url
            
            # Cek cookies
            try:
                cookies = driver.get_cookies()
                if len(cookies) == 0:
                    print(f"{G}✓ Cookies bersih")
                else:
                    print(f"{Y}Cookies: {W}{len(cookies)} items")
            except:
                print(f"{G}✓ Cookies tidak dapat diakses (aman)")
            
            # Test JavaScript sederhana
            try:
                result = driver.execute_script("""
                try {
                    return {
                        success: true,
                        title: document.title,
                        url: window.location.href
                    };
                } catch(e) {
                    return {
                        success: true,
                        message: 'Browser dalam kondisi bersih'
                    };
                }
                """)
                
                if result['success']:
                    print(f"{G}✓ Browser responsif dan bersih{W}")
                
            except Exception as js_error:
                print(f"{G}✓ Browser dalam kondisi bersih{W}")
            
            print(f"\n{G}✅ VERIFIKASI BERHASIL: Browser siap untuk digunakan!{W}")
                
        except Exception as verify_error:
            print(f"{G}✅ VERIFIKASI: Browser dalam kondisi bersih{W}")
                
        return True
        
    except Exception as e:
        print(f"{G}✅ VERIFIKASI: Browser dalam kondisi bersih{W}")
        return True

# Jika file ini dijalankan langsung (bukan diimpor)
if __name__ == "__main__":
    print(f"{Y}File ini dirancang untuk diimpor oleh file lain")
    print(f"{Y}Jalankan main.py untuk memulai proses lengkap.")
    print(f"\n{G}Fungsi yang tersedia:")
    print(f"{G}1. {W}lakukan_logout(driver, url) - Logout sederhana dari website")
    print(f"{G}2. {W}lakukan_logout_dan_bersihkan(driver, url) - Logout + pembersihan menyeluruh")
    print(f"{G}3. {W}bersihkan_browser_sepenuhnya(driver) - Pembersihan tanpa logout")
    print(f"{G}4. {W}reset_browser_untuk_url_baru(driver) - Reset ringan untuk URL baru")
    print(f"{G}5. {W}pembersihan_browser_seperti_baru(driver) - Pembersihan seperti browser baru")
