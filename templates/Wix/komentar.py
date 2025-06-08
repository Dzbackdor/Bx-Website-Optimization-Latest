import time
import random
import os
import re
import yaml
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# Tambahkan import untuk BeautifulSoup
try:
    from bs4 import BeautifulSoup
except ImportError:
    print(f"⚠️ BeautifulSoup4 tidak terinstall. Install dengan: pip install beautifulsoup4")
    BeautifulSoup = None

# Import colors jika tersedia
try:
    from colorama import Fore
    R = Fore.RED
    G = Fore.GREEN
    W = Fore.WHITE
    Y = Fore.YELLOW
except ImportError:
    R = G = W = Y = ""

# ✅ BARU: Config Loader
def load_wix_config():
    """Load configuration dari config.yaml"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return {}

# ✅ BARU: Selector Helper
def get_selectors(config, selector_type, fallback_list=None):
    """Get selectors dari config dengan fallback"""
    try:
        selectors_config = config.get('selectors', {})
        selector_group = selectors_config.get(selector_type, {})
        
        # Gabungkan primary dan alternative
        all_selectors = []
        all_selectors.extend(selector_group.get('primary', []))
        all_selectors.extend(selector_group.get('alternative', []))
        all_selectors.extend(selector_group.get('fallback', []))
        
        return all_selectors if all_selectors else (fallback_list or [])
    except Exception as e:
        print(f"❌ Error getting selectors for {selector_type}: {e}")
        return fallback_list or []

def cari_kotak_komentar_beautifulsoup(driver, logger=None):
    """
    Mencari kotak komentar dengan BeautifulSoup - MENGGUNAKAN CONFIG
    """
    try:
        if logger:
            logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Mencari kotak komentar dengan BeautifulSoup...")
        
        if not BeautifulSoup:
            if logger:
                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} BeautifulSoup tidak tersedia, skip pencarian")
            return False
        
        # ✅ Load config
        config = load_wix_config()
        bs_config = config.get('selectors', {}).get('beautifulsoup', {})
        
        # Ambil HTML halaman
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # ✅ Cari dengan primary class dari config
        primary_class = bs_config.get('primary_class', 'tAaif jkMRy is-editor-empty')
        kotak_komentar = soup.find('p', class_=primary_class)
        
        if kotak_komentar:
            if logger:
                logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Kotak komentar ditemukan dengan BeautifulSoup!")
                logger.info(f"🎯 [Komentar] {Y}[{W}Info{Y}]{W} Element: {kotak_komentar}")
            
            # Coba lakukan selector dengan Selenium
            selector_success = coba_selector_kotak_komentar(driver, logger)
            
            if selector_success:
                if logger:
                    logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Selector kotak komentar berhasil!")
                return True
            else:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} BeautifulSoup menemukan element tapi selector gagal")
                return False
        else:
            if logger:
                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Kotak komentar tidak ditemukan dengan BeautifulSoup")
            
            # ✅ Coba cari dengan alternative classes dari config
            alternative_classes = bs_config.get('alternative_classes', [])
            
            for class_name in alternative_classes:
                try:
                    if logger:
                        logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba class alternatif: '{class_name}'")
                    
                    element_alt = soup.find('p', class_=class_name)
                    if element_alt:
                        if logger:
                            logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Ditemukan dengan class: '{class_name}'")
                        
                        # Coba selector
                        selector_success = coba_selector_kotak_komentar(driver, logger, class_name)
                        if selector_success:
                            return True
                except Exception as e:
                    if logger:
                        logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error dengan class '{class_name}': {e}")
                    continue
            
            # ✅ Coba cari dengan keywords dari config
            try:
                if logger:
                    logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Mencari p tag dengan kata kunci...")
                
                keywords = bs_config.get('search_keywords', ['editor', 'comment', 'input', 'text', 'empty'])
                
                all_p_tags = soup.find_all('p')
                for p_tag in all_p_tags:
                    class_attr = p_tag.get('class', [])
                    if class_attr:
                        class_string = ' '.join(class_attr).lower()
                        
                        if any(keyword in class_string for keyword in keywords):
                            if logger:
                                logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Ditemukan p tag dengan class: '{' '.join(class_attr)}'")
                            
                            # Coba selector dengan class ini
                            selector_success = coba_selector_kotak_komentar(driver, logger, ' '.join(class_attr))
                            if selector_success:
                                return True
                
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error scanning p tags: {e}")
            
            return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Error dalam cari_kotak_komentar_beautifulsoup: {e}")
        return False

def coba_selector_kotak_komentar(driver, logger=None, class_name='tAaif jkMRy is-editor-empty'):
    """
    Coba lakukan selector pada kotak komentar - MENGGUNAKAN CONFIG
    """
    try:
        if logger:
            logger.info(f"🎯 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba selector dengan class: '{class_name}'")
        
        # ✅ Load config
        config = load_wix_config()
        comment_box_selectors = get_selectors(config, 'comment_box')
        
        # Buat selector CSS dari class name
        css_selector = f"p.{class_name.replace(' ', '.')}"
        
        # ✅ Gabungkan dengan selectors dari config
        selectors_to_try = [css_selector]
        selectors_to_try.extend(comment_box_selectors)
        
        # Tambahan selector alternatif
        selectors_to_try.extend([
            f"p[class='{class_name}']",
            f"p[class*='{class_name.split()[0]}']",  # Class pertama saja
        ])
        
        for selector in selectors_to_try:
            try:
                # if logger:
                #     logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba selector: {selector}")
                
                element = driver.find_element(By.CSS_SELECTOR, selector)
                
                if element and element.is_displayed():
                    if logger:
                        logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Element ditemukan dengan selector: {selector}")
                    
                    # Scroll ke element
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(2)
                    
                    # Get element info
                    element_text = element.text or "No text"
                    element_tag = element.tag_name
                    element_class = element.get_attribute("class") or "No class"
                    
                    if logger:
                        logger.info(f"🎯 [Komentar] {Y}[{W}Info{Y}]{W} Element info - Tag: {element_tag}, Class: '{element_class}', Text: '{element_text}'")
                    
                    # Coba klik element
                    click_success = coba_klik_kotak_komentar(driver, element, logger)
                    
                    if click_success:
                        if logger:
                            logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Kotak komentar berhasil diklik!")
                        return True
                    else:
                        if logger:
                            logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Element ditemukan tapi tidak bisa diklik")
                        continue
                    
            except NoSuchElementException:
                continue
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error dengan selector {selector}: {e}")
                continue
        
        if logger:
            logger.error("❌ [Komentar] {Y}[{W}Info{Y}]{R} Semua selector gagal")
        return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Error dalam coba_selector_kotak_komentar: {e}")
        return False

def coba_klik_kotak_komentar(driver, element, logger=None):
    """
    Coba klik kotak komentar dengan berbagai metode - MENGGUNAKAN CONFIG
    """
    try:
        if logger:
            logger.info(f"🖱️ [Komentar] {Y}[{W}Info{Y}]{W} Mencoba klik kotak komentar...")
        
        # ✅ Load config
        config = load_wix_config()
        
        # Method 1: Direct click
        try:
            element.click()
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(input_wait)
            
            if logger:
                logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Direct click berhasil!")
            return True
            
        except ElementClickInterceptedException:
            if logger:
                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Direct click terhalang, mencoba scroll...")
            
            # Method 2: Scroll then click
            try:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(1)
                element.click()
                
                input_wait = config.get('timeouts', {}).get('input_wait', 1)
                time.sleep(input_wait)
                
                if logger:
                    logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Scroll + click berhasil!")
                return True
                
            except Exception as scroll_error:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Scroll + click gagal: {scroll_error}")
        
        # Method 3: JavaScript click
        try:
            if logger:
                logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba JavaScript click...")
            
            driver.execute_script("arguments[0].click();", element)
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(input_wait)
            
            if logger:
                logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} JavaScript click berhasil!")
            return True
            
        except Exception as js_error:
            if logger:
                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} JavaScript click gagal: {js_error}")
        
        # Method 4: ActionChains click
        try:
            if logger:
                logger.infof(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba ActionChains click...")
            
            actions = ActionChains(driver)
            actions.move_to_element(element).click().perform()
            
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(input_wait)
            
            if logger:
                logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} ActionChains click berhasil!")
            return True
            
        except Exception as action_error:
            if logger:
                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} ActionChains click gagal: {action_error}")
        
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Semua metode click gagal!")
        return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Error dalam coba_klik_kotak_komentar: {e}")
        return False



def process_links_in_element(driver, element, links_info, logger=None):
    """
    Proses links dalam komentar (select text dan buat link) - DENGAN FALLBACK DIRECT LINK + CONFIG
    """
    try:
        # if logger:
        #     logger.info(f"🔗 [Komentar] {Y}[{W}Info{Y}]{W} Memulai proses links...")
        
        # ✅ Load config
        config = load_wix_config()
        
        success_count = 0
        
        for link_data in links_info:
            text_to_link = link_data['text']
            url_to_link = link_data['url']
            
            # if logger:
            #     logger.info(f"🔗 [Komentar] {Y}[{W}Info{Y}]{W} Memproses link: {G}{text_to_link} {Y}-> {G}{url_to_link}")
            
            # Klik element untuk fokus
            try:
                element.click()
                click_wait = config.get('timeouts', {}).get('click_wait', 1)
                time.sleep(click_wait)
            except:
                pass
            
            # Select text yang akan diberi link
            if select_text_in_element(driver, element, text_to_link, logger):
                # Klik tombol link
                if click_link_button(driver, logger):
                    # Input URL
                    if input_link_url(driver, url_to_link, logger):
                        # Klik toggle switch jika ada
                        click_toggle_switch(driver, logger)
                        
                        # Save link
                        if save_link(driver, logger):
                            # Tambahan: Klik underline setelah save
                            # if logger:
                            #     logger.info(f"🔗 [Komentar] {Y}[{W}Info{Y}]{W} Menambahkan underline untuk {G}{text_to_link}")
                            
                            underline_success = klik_tombol_underline(driver, logger)
                            if underline_success:
                                if logger:
                                    logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Link + underline berhasil untuk {G}{text_to_link}")
                            else:
                                if logger:
                                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Link berhasil tapi underline gagal untuk '{text_to_link}'")
                            
                            success_count += 1
                        else:
                            if logger:
                                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Gagal save link '{text_to_link}'")
                    else:
                        if logger:
                            logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Gagal input URL untuk '{text_to_link}'")
                else:
                    # ✅ FALLBACK: Jika tombol link tidak ditemukan, masukkan link langsung
                    if logger:
                        logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Tombol link tidak ditemukan untuk {R}{text_to_link}")
                        logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Memasukkan link langsung ke komentar...")
                    
                    fallback_success = insert_direct_link_fallback(driver, element, text_to_link, url_to_link, logger)
                    if fallback_success:
                        success_count += 1
                    else:
                        if logger:
                            logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Fallback direct link juga gagal untuk {R}{text_to_link}")
            else:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Gagal select text '{text_to_link}'")
                
                # ✅ FALLBACK: Jika select text gagal, coba masukkan link langsung
                if logger:
                    logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} FALLBACK: Text selection gagal, coba direct link...")
                
                fallback_success = insert_direct_link_fallback(driver, element, text_to_link, url_to_link, logger)
                if fallback_success:
                    success_count += 1
            
            # Delay antar link dengan config
            link_process_wait = config.get('timeouts', {}).get('link_process_wait', 2)
            time.sleep(random.uniform(link_process_wait * 0.5, link_process_wait))
        
        # if logger:
        #     logger.info(f"🔗 [Komentar] {Y}[{W}Info{Y}]{W} Berhasil memproses {G}{success_count}{W}/{G}{len(links_info)} {W}links")
        
        return success_count > 0
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Error dalam process_links_in_element: {e}")
        return False



def select_text_in_element(driver, element, text_to_select, logger=None):
    """
    Select text tertentu dalam element untuk dijadikan link - MENGGUNAKAN CONFIG
    """
    try:
        # if logger:
        #     logger.info(f"🎯 [Komentar] {Y}[{W}Info{Y}]{W} Selecting text: {G}{text_to_select}")
        
        # ✅ Load config
        config = load_wix_config()
        
        # Method 1: JavaScript selection
        try:
            select_script = """
            var element = arguments[0];
            var textToSelect = arguments[1];
            
            // Find text node containing the text
            function findTextNode(node, text) {
                if (node.nodeType === Node.TEXT_NODE) {
                    if (node.textContent.includes(text)) {
                        return node;
                    }
                } else {
                    for (var i = 0; i < node.childNodes.length; i++) {
                        var result = findTextNode(node.childNodes[i], text);
                        if (result) return result;
                    }
                }
                return null;
            }
            
            var textNode = findTextNode(element, textToSelect);
            if (textNode) {
                var range = document.createRange();
                var startIndex = textNode.textContent.indexOf(textToSelect);
                if (startIndex !== -1) {
                    range.setStart(textNode, startIndex);
                    range.setEnd(textNode, startIndex + textToSelect.length);
                    
                    var selection = window.getSelection();
                    selection.removeAllRanges();
                    selection.addRange(range);
                    
                    return true;
                }
            }
            return false;
            """
            
            selection_success = driver.execute_script(select_script, element, text_to_select)
            
            if selection_success:
                # if logger:
                #     logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Text berhasil diselect dengan JavaScript")
                
                input_wait = config.get('timeouts', {}).get('input_wait', 1)
                time.sleep(input_wait * 0.5)
                return True
            
        except Exception as js_error:
            if logger:
                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} JavaScript selection gagal: {js_error}")
        
        # Method 2: ActionChains double click (fallback)
        try:
            if logger:
                logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba ActionChains double click...")
            
            actions = ActionChains(driver)
            actions.move_to_element(element).double_click().perform()
            
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(input_wait * 0.5)
            
            if logger:
                logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Double click selection berhasil")
            return True
            
        except Exception as action_error:
            if logger:
                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} ActionChains selection gagal: {action_error}")
        
        # Method 3: Ctrl+A (select all as last resort)
        try:
            if logger:
                logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba Ctrl+A selection...")
            
            element.click()
            time.sleep(0.2)
            element.send_keys(Keys.CONTROL + "a")
            
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(input_wait * 0.5)
            
            if logger:
                logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Ctrl+A selection berhasil")
            return True
            
        except Exception as ctrl_error:
            if logger:
                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Ctrl+A selection gagal: {ctrl_error}")
        
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Semua metode selection gagal untuk: '{text_to_select}'")
        return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Error dalam select_text_in_element: {e}")
        return False


def input_fallback_text_with_links(driver, element, fallback_text, logger=None):
    """
    Input fallback text yang sudah mengandung direct links - MENGGUNAKAN CONFIG
    """
    try:
        if logger:
            logger.info(f"🔄 [Fallback] {Y}[{W}Info{Y}]{W} Input fallback text dengan direct links...")
        
        # ✅ Load config
        config = load_wix_config()
        
        # Method 1: Clear dan Send Keys
        try:

            
            element.clear()
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(input_wait * 0.5)
            element.send_keys(fallback_text)
            time.sleep(random.uniform(input_wait, input_wait * 2))
            
            # Verifikasi input
            current_text = element.text or element.get_attribute('value') or ""
            if fallback_text[:20].lower() in current_text.lower():
                if logger:
                    logger.info(f"✅ [Fallback] {Y}[{W}Info{Y}]{W} Clear + Send Keys berhasil!")
                return True
            
        except Exception as e:
            if logger:
                logger.warning(f"⚠️ [Fallback] {Y}[{W}Info{Y}]{W} Clear + Send Keys gagal: {e}")
        
        # Method 2: JavaScript innerHTML
        try:
            if logger:
                logger.info(f"⌨️ [Fallback] {Y}[{W}Info{Y}]{W} Mencoba JavaScript innerHTML...")
            
            driver.execute_script("arguments[0].innerHTML = arguments[1];", element, fallback_text)
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(random.uniform(input_wait, input_wait * 2))
            
            # Trigger events
            driver.execute_script("""
                var element = arguments[0];
                var inputEvent = new Event('input', { bubbles: true });
                var changeEvent = new Event('change', { bubbles: true });
                element.dispatchEvent(inputEvent);
                element.dispatchEvent(changeEvent);
            """, element)
            
            if logger:
                logger.info(f"✅ [Fallback] {Y}[{W}Info{Y}]{W} JavaScript innerHTML berhasil!")
            return True
            
        except Exception as e:
            if logger:
                logger.warning(f"⚠️ [Fallback] {Y}[{W}Info{Y}]{W} JavaScript innerHTML gagal: {e}")
        
        # Method 3: JavaScript textContent
        try:
            if logger:
                logger.info(f"⌨️ [Fallback] {Y}[{W}Info{Y}]{W} Mencoba JavaScript textContent...")
            
            driver.execute_script("arguments[0].textContent = arguments[1];", element, fallback_text)
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(random.uniform(input_wait, input_wait * 2))
            
            # Trigger events
            driver.execute_script("""
                var element = arguments[0];
                var inputEvent = new Event('input', { bubbles: true });
                var changeEvent = new Event('change', { bubbles: true });
                element.dispatchEvent(inputEvent);
                element.dispatchEvent(changeEvent);
            """, element)
            
            if logger:
                logger.info(f"✅ [Fallback] {Y}[{W}Info{Y}]{W} JavaScript textContent berhasil!")
            return True
            
        except Exception as e:
            if logger:
                logger.warning(f"⚠️ [Fallback] {Y}[{W}Info{Y}]{W} JavaScript textContent gagal: {e}")
        
        # Method 4: ActionChains type
        try:
            if logger:
                logger.info(f"⌨️ [Fallback] {Y}[{W}Info{Y}]{W} Mencoba ActionChains type...")
            
            # Clear first
            element.click()
            time.sleep(0.5)
            element.send_keys(Keys.CONTROL + "a")
            time.sleep(0.5)
            element.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            # Type with ActionChains
            actions = ActionChains(driver)
            actions.move_to_element(element).click().send_keys(fallback_text).perform()
            
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(random.uniform(input_wait, input_wait * 2))
            
            if logger:
                logger.info(f"✅ [Fallback] {Y}[{W}Info{Y}]{W} ActionChains type berhasil!")
            return True
            
        except Exception as e:
            if logger:
                logger.warning(f"⚠️ [Fallback] {Y}[{W}Info{Y}]{W} ActionChains type gagal: {e}")
        
        # Method 5: Character by character input (last resort)
        try:
            if logger:
                logger.info(f"⌨️ [Fallback] {Y}[{W}Info{Y}]{W} Mencoba character by character input...")
            
            element.click()
            time.sleep(0.5)
            element.send_keys(Keys.CONTROL + "a")
            time.sleep(0.5)
            element.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            # Type character by character with small delays
            for char in fallback_text:
                element.send_keys(char)
                time.sleep(0.01)  # Very small delay between characters
            
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(input_wait)
            
            if logger:
                logger.info(f"✅ [Fallback] {Y}[{W}Info{Y}]{W} Character by character berhasil!")
            return True
            
        except Exception as e:
            if logger:
                logger.warning(f"⚠️ [Fallback] {Y}[{W}Info{Y}]{W} Character by character gagal: {e}")
        
        if logger:
            logger.error(f"❌ [Fallback] {Y}[{W}Info{Y}]{R} Semua method fallback gagal!")
        return False
        
    except Exception as e:
         if logger:
            logger.error(f"❌ [Fallback] {Y}[{W}Info{Y}]{R} Error dalam input_fallback_text_with_links: {e}")
            return False

# def load_wix_config():
#     """
#     ✅ TAMBAHAN: Load Wix config dengan safe handling
#     """
#     try:
#         import yaml
#         import os
        
#         config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
#         with open(config_path, 'r', encoding='utf-8') as f:
#             return yaml.safe_load(f)
#     except Exception:
#         return {}



def click_link_button(driver, logger=None):
    """
    ✅ FIXED: Klik tombol link untuk membuat hyperlink - DENGAN CONFIG
    """
    try:
        # if logger:
        #     logger.info(f"🔗 [Komentar] {Y}[{W}Info{Y}]{W} Mencari tombol link...")
        
        # ✅ Load config
        config = load_wix_config()
        
        # Ambil selectors dari config
        link_selectors = config.get('selectors', {}).get('link_button', {}).get('primary', [])
        
        # Fallback jika config tidak ada
        if not link_selectors:
            link_selectors = [
                '[data-hook="text-button-link"]'
            ]
        
        # Ambil timeout dari config
        element_wait = config.get('timeouts', {}).get('element_wait', 5)
        
        for selector in link_selectors:
            try:
                # if logger:
                #     logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba selector: {Y}{selector}")
                
                link_button = WebDriverWait(driver, element_wait).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                if link_button.is_displayed():
                    link_button.click()
                    # if logger:
                    #     logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Tombol link berhasil diklik: {Y}{selector}")
                    
                    click_wait = config.get('timeouts', {}).get('click_wait', 2)
                    time.sleep(click_wait)
                    return True
                    
            except TimeoutException:
                if logger:
                    logger.warning(f"⏰ [Komentar] {Y}[{W}Info{Y}]{W} Timeout untuk selector: {selector}")
                continue
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error dengan selector {selector}: {e}")
                continue
        
        # Coba dengan JavaScript sebagai fallback
        if logger:
            logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba JavaScript untuk tombol link...")
        
        js_script = """
        var linkSelectors = [
            '[data-hook="text-button-link"]'
        ];
        
        for (var i = 0; i < linkSelectors.length; i++) {
            var button = document.querySelector(linkSelectors[i]);
            if (button && button.offsetParent !== null) {
                button.click();
                return "Berhasil klik tombol link dengan JavaScript: " + linkSelectors[i];
            }
        }
        return "Tombol link tidak ditemukan dengan JavaScript";
        """
        
        result = driver.execute_script(js_script)
        
        if logger:
            logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Hasil JavaScript: {result}")
        
        if "Berhasil" in result:
            click_wait = config.get('timeouts', {}).get('click_wait', 2)
            time.sleep(click_wait)
            return True
        
        if logger:
            logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Tombol link tidak ditemukan")
        return False
        
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error clicking link button: {e}")
        return False

def input_link_url(driver, url, logger=None):
    """
    ✅ FIXED: Input URL ke dalam dialog link - DENGAN CONFIG
    """
    try:
        # if logger:
        #     logger.info(f"🔗 [Komentar] {Y}[{W}Info{Y}]{W} Memasukkan URL: {G}{url}")
        
        # ✅ Load config
        config = load_wix_config()
        
        # Tunggu dialog muncul
        click_wait = config.get('timeouts', {}).get('click_wait', 2)
        time.sleep(click_wait)
        
        # Ambil selectors dari config
        url_selectors = config.get('selectors', {}).get('url_input', {}).get('primary', [])
        
        # Fallback jika config tidak ada
        if not url_selectors:
            url_selectors = [
                'div[data-hook="link-modal-url-input"] input[data-hook="wsr-input"]',
                'input[data-hook="wsr-input"]',
                'input[placeholder*="url" i]',
                'input[type="url"]'
            ]
        
        element_wait = config.get('timeouts', {}).get('element_wait', 5)
        
        for selector in url_selectors:
            try:
                url_input = WebDriverWait(driver, element_wait).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                url_input.click()
                time.sleep(0.5)
                url_input.clear()
                url_input.send_keys(url)
                
                # if logger:
                #     logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} URL berhasil dimasukkan: {Y}{selector}")
                
                input_wait = config.get('timeouts', {}).get('input_wait', 1)
                time.sleep(input_wait)
                return True
                
            except:
                continue
        
        if logger:
            logger.warning("⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Input URL tidak ditemukan")
        return False
        
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error input URL: {e}")
        return False


def click_toggle_switch(driver, logger=None):
    """
    ✅ FIXED: Klik toggle switch jika ada (untuk open in new tab, dll) - DENGAN CONFIG
    """
    try:
        # if logger:
        #     logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Mencari toggle switch...")
        
        # ✅ Load config
        config = load_wix_config()
        
        # Ambil selectors dari config
        toggle_selectors = config.get('selectors', {}).get('toggle_switch', {}).get('primary', [])
        
        # Fallback jika config tidak ada
        if not toggle_selectors:
            toggle_selectors = [
                '[data-hook="toggle-switch-input"]',
                '.toggle-switch',
                'input[type="checkbox"]'
            ]
        
        for selector in toggle_selectors:
            try:
                toggles = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if len(toggles) >= 2:
                    # Klik toggle kedua (biasanya untuk "open in new tab")
                    toggles[1].click()
                    # if logger:
                    #     logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Toggle switch kedua berhasil diklik")
                    
                    click_wait = config.get('timeouts', {}).get('click_wait', 1)
                    time.sleep(click_wait)
                    return True
                elif len(toggles) == 1:
                    toggles[0].click()
                    if logger:
                        logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Toggle switch tunggal berhasil diklik")
                    
                    click_wait = config.get('timeouts', {}).get('click_wait', 1)
                    time.sleep(click_wait)
                    return True
                
            except:
                continue
        
        if logger:
            logger.info(f"ℹ️ [Komentar] {Y}[{W}Info{Y}]{W} Toggle switch tidak ditemukan (optional)")
        return True  # Return True karena toggle switch optional
        
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error toggle switch: {e}")
        return True  # Return True karena toggle switch optional



def insert_direct_link_fallback(driver, element, text_to_link, url_to_link, logger=None):
    """
    Fallback: Masukkan link langsung ke komentar dalam format "text url" - MENGGUNAKAN CONFIG
    """
    try:
        if logger:
            logger.info(f"🔄 [Fallback] {Y}[{W}Info{Y}]{W} Memasukkan direct link: {G}{text_to_link} {Y}-> {G}{url_to_link}")
        
        # ✅ Load config
        config = load_wix_config()
        
        # Klik element untuk fokus
        try:
            element.click()
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(input_wait * 0.5)
        except:
            pass
        
        # Ambil text yang sudah ada di element
        current_text = ""
        try:
            current_text = element.text or element.get_attribute('value') or element.get_attribute('textContent') or ""
        except:
            current_text = ""
        
        if logger:
            logger.info(f"📝 [Fallback] {Y}[{W}Info{Y}]{W} Current text: {Y}{current_text}")
        
        # Buat format link langsung
        direct_link_format = f"{text_to_link} {url_to_link}"
        
        # Cek apakah text_to_link sudah ada di current_text
        if text_to_link in current_text:
            # Replace text yang sudah ada dengan format link
            new_text = current_text.replace(text_to_link, direct_link_format)
            if logger:
                logger.info(f"🔄 [Fallback] {Y}[{W}Info{Y}]{W} Replace mode: {G}{current_text} {Y}-> {G}{new_text}'")
        else:
            # Append link ke text yang sudah ada
            if current_text.strip():
                new_text = f"{current_text} {direct_link_format}"
            else:
                new_text = direct_link_format
            if logger:
                logger.info(f"🔄 [Fallback] {Y}[{W}Info{Y}]{W} Append mode: '{current_text}' -> '{new_text}'")
        
        # Method 1: Clear dan input ulang
        input_success = False
        try:
            if logger:
                logger.info(f"⌨️ [Fallback] {Y}[{W}Info{Y}]{W} Method 1: Clear + Send Keys...")
            
            element.clear()
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(input_wait * 0.5)
            element.send_keys(new_text)
            time.sleep(random.uniform(input_wait, input_wait * 2))
            
            # Verifikasi
            verify_text = element.text or element.get_attribute('value') or ""
            if url_to_link in verify_text:
                if logger:
                    logger.info(f"✅ [Fallback] {Y}[{W}Info{Y}]{W} Clear + Send Keys berhasil!")
                input_success = True
            
        except Exception as e:
            if logger:
                logger.warning(f"⚠️ [Fallback] {Y}[{W}Info{Y}]{W} Clear + Send Keys gagal: {e}")
        
        # Method 2: JavaScript innerHTML
        if not input_success:
            try:
                if logger:
                    logger.info(f"⌨️ [Fallback] {Y}[{W}Info{Y}]{W} Method 2: JavaScript innerHTML...")
                
                driver.execute_script("arguments[0].innerHTML = arguments[1];", element, new_text)
                input_wait = config.get('timeouts', {}).get('input_wait', 1)
                time.sleep(random.uniform(input_wait, input_wait * 2))
                
                # Trigger events
                driver.execute_script("""
                    var element = arguments[0];
                    var inputEvent = new Event('input', { bubbles: true });
                    var changeEvent = new Event('change', { bubbles: true });
                    element.dispatchEvent(inputEvent);
                    element.dispatchEvent(changeEvent);
                """, element)
                
                if logger:
                    logger.info(f"✅ [Fallback] {Y}[{W}Info{Y}]{W} JavaScript innerHTML berhasil!")
                input_success = True
                
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Fallback] {Y}[{W}Info{Y}]{W} JavaScript innerHTML gagal: {e}")
        
        # Method 3: JavaScript textContent
        if not input_success:
            try:
                if logger:
                    logger.info(f"⌨️ [Fallback] {Y}[{W}Info{Y}]{W} Method 3: JavaScript textContent...")
                
                driver.execute_script("arguments[0].textContent = arguments[1];", element, new_text)
                input_wait = config.get('timeouts', {}).get('input_wait', 1)
                time.sleep(random.uniform(input_wait, input_wait * 2))
                
                # Trigger events
                driver.execute_script("""
                    var element = arguments[0];
                    var inputEvent = new Event('input', { bubbles: true });
                    var changeEvent = new Event('change', { bubbles: true });
                    element.dispatchEvent(inputEvent);
                    element.dispatchEvent(changeEvent);
                """, element)
                
                if logger:
                    logger.info(f"✅ [Fallback] {Y}[{W}Info{Y}]{W} JavaScript textContent berhasil!")
                input_success = True
                
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Fallback] {Y}[{W}Info{Y}]{W} JavaScript textContent gagal: {e}")
        
        # Method 4: ActionChains append
        if not input_success:
            try:
                if logger:
                    logger.info(f"⌨️ [Fallback] {Y}[{W}Info{Y}]{W} Method 4: ActionChains append...")
                
                # Posisikan cursor di akhir text
                element.click()
                time.sleep(0.5)
                
                # Pindah ke akhir text
                element.send_keys(Keys.CONTROL + Keys.END)
                time.sleep(0.5)
                
                # Tambahkan space dan link
                element.send_keys(f" {url_to_link}")
                input_wait = config.get('timeouts', {}).get('input_wait', 1)
                time.sleep(input_wait)
                
                if logger:
                    logger.info(f"✅ [Fallback] {Y}[{W}Info{Y}]{W} ActionChains append berhasil!")
                input_success = True
                
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Fallback] {Y}[{W}Info{Y}]{W} ActionChains append gagal: {e}")
        
        if input_success:
            if logger:
                logger.info(f"✅ [Fallback] {Y}[{W}Info{Y}]{W} Direct link berhasil dimasukkan: '{text_to_link}' + {url_to_link}")
            return True
        else:
            if logger:
                logger.error(f"❌ [Fallback] {Y}[{W}Info{Y}]{R} Semua method direct link gagal untuk '{text_to_link}'")
            return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Fallback] {Y}[{W}Info{Y}]{R} Error dalam insert_direct_link_fallback: {e}")
        return False


def debug_config_selectors(driver, logger=None):
    """Debug function untuk test semua selectors dari config"""
    try:
        if logger:
            logger.info("🔍 [Debug] Testing config selectors...")
        
        config = load_wix_config()
        
        selector_groups = ['comment_box', 'link_button', 'url_input', 'save_button', 'post_button', 'toggle_switch']
        
        for group in selector_groups:
            selectors = get_selectors(config, group)
            if logger:
                logger.info(f"🎯 [Debug] Testing {group} selectors ({len(selectors)}):")
            
            found_count = 0
            for i, selector in enumerate(selectors):
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [el for el in elements if el.is_displayed()]
                    
                    if visible_elements:
                        found_count += 1
                        if logger:
                            logger.info(f"  ✅ {i+1}. {selector} - Found {len(visible_elements)} visible elements")
                    else:
                        if logger:
                            logger.info(f"  ❌ {i+1}. {selector} - No visible elements")
                            
                except Exception as e:
                    if logger:
                        logger.info(f"  ⚠️ {i+1}. {selector} - Error: {e}")
            
            if logger:
                logger.info(f"📊 [Debug] {group}: {found_count}/{len(selectors)} selectors found elements")
        
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Debug] Error dalam debug_config_selectors: {e}")
        return False



def save_link(driver, logger=None):
    """
    ✅ FIXED: Save/apply link yang sudah dibuat - DENGAN CONFIG
    """
    try:
        # if logger:
        #     logger.info(f"💾 [Komentar] {Y}[{W}Info{Y}]{W} Menyimpan link...")
        
        # ✅ Load config
        config = load_wix_config()
        
        # Ambil selectors dari config
        save_selectors = config.get('selectors', {}).get('save_button', {}).get('primary', [])
        
        # Fallback jika config tidak ada
        if not save_selectors:
            save_selectors = [
                '[data-hook="link-modal-save-button"]',
                'button[data-testid="save"]',
                'button[data-testid="apply"]',
                '.save-button',
                '.apply-button',
                'button:contains("Save")',
                'button:contains("Apply")',
                'button:contains("OK")'
            ]
        
        element_wait = config.get('timeouts', {}).get('element_wait', 5)
        
        for selector in save_selectors:
            try:
                save_button = WebDriverWait(driver, element_wait).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                save_button.click()
                # if logger:
                #     logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Link berhasil disimpan: {Y}{selector}")
                
                click_wait = config.get('timeouts', {}).get('click_wait', 2)
                time.sleep(click_wait)
                return True
                
            except:
                continue
        
        # Coba dengan JavaScript jika selector tidak berhasil
        try:
            if logger:
                logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba save dengan JavaScript...")
            
            save_script = """
            var saveButton = document.querySelector('[data-hook="link-modal-save-button"]') ||
                           document.querySelector('button[data-testid="save"]') ||
                           document.querySelector('.save-button');
            if (saveButton) {
                saveButton.click();
                return true;
            }
            return false;
            """
            
            result = driver.execute_script(save_script)
            if result:
                if logger:
                    logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Link berhasil disimpan dengan JavaScript")
                
                click_wait = config.get('timeouts', {}).get('click_wait', 2)
                time.sleep(click_wait)
                return True
        except:
            pass
        
        if logger:
            logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Tombol save link tidak ditemukan")
        return False
        
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error save link: {e}")
        return False




def klik_tombol_underline(driver, logger=None):
    """
    ✅ FIXED: Fungsi untuk mengklik tombol underline setelah membuat link - DENGAN CONFIG
    """
    try:
        # if logger:
        #     logger.info(f"🔗 [Komentar] {Y}[{W}Info{Y}]{W} Mencari tombol underline...")
        
        # ✅ Load config
        config = load_wix_config()
        # Tunggu sebentar setelah save link
        click_wait = config.get('timeouts', {}).get('click_wait', 2)
        time.sleep(click_wait)
        
        # Ambil selectors dari config
        underline_selectors = config.get('selectors', {}).get('underline_button', {}).get('primary', [])
        
        # Fallback jika config tidak ada
        if not underline_selectors:
            underline_selectors = [
                '[data-hook="text-button-underline active"]',
                '[data-hook="text-button-underline"]',
                '[data-hook*="text-button-underline"]',
                'button[data-hook*="underline"]',
                '.text-button-underline',
                '[aria-label*="underline" i]',
                '[title*="underline" i]'
            ]
        
        element_wait = config.get('timeouts', {}).get('element_wait', 5)
        
        for selector in underline_selectors:
            try:
                # if logger:
                #     logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba selector underline: {Y}{selector}")
                
                underline_button = WebDriverWait(driver, element_wait).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                if underline_button.is_displayed():
                    # Scroll ke tombol
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", underline_button)
                    time.sleep(1)
                    
                    # Klik tombol underline
                    underline_button.click()
                    
                    # if logger:
                    #     logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Tombol underline berhasil diklik: {Y}{selector}")
                    
                    time.sleep(1)
                    return True
                    
            except TimeoutException:
                continue
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error dengan selector {selector}: {e}")
                continue
        
        # Coba pendekatan JavaScript jika selector gagal
        if logger:
            logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba JavaScript untuk tombol underline...")
        
        underline_script = """
        // Cari tombol underline dengan berbagai selector
        var selectors = [
            '[data-hook="text-button-underline active"]',
            '[data-hook="text-button-underline"]',
            '[data-hook*="text-button-underline"]',
            'button[data-hook*="underline"]'
        ];
        
        for (var i = 0; i < selectors.length; i++) {
            var button = document.querySelector(selectors[i]);
            if (button && button.offsetParent !== null) {
                button.click();
                return "Berhasil mengklik tombol underline dengan JavaScript: " + selectors[i];
            }
        }
        
        // Coba cari semua tombol yang mengandung "underline"
        var allButtons = document.querySelectorAll('[data-hook*="text-button-underline"]');
        if (allButtons.length > 0) {
            for (var j = 0; j < allButtons.length; j++) {
                if (allButtons[j].offsetParent !== null) {
                    allButtons[j].click();
                    return "Berhasil mengklik tombol underline alternatif dengan JavaScript";
                }
            }
        }
        
        return "Tombol underline tidak ditemukan dengan JavaScript";
        """
        
        result = driver.execute_script(underline_script)
        
        if logger:
            logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Hasil JavaScript underline: {result}")
        
        if "Berhasil" in result:
            time.sleep(1)
            return True
        
        if logger:
            logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Tombol underline tidak ditemukan, lanjut tanpa underline")
        
        return False
        
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error dalam klik_tombol_underline: {e}")
        return False



def klik_tombol_post(driver, logger=None):
    """
    ✅ FIXED: Fungsi untuk mengklik tombol post komentar - DENGAN CONFIG
    """
    try:
        # if logger:
        #     logger.info(f"🚀 [Komentar] {Y}[{W}Info{Y}]{W} Mencari tombol post...")
        
        # ✅ Load config
        config = load_wix_config()
        
        # Tunggu sebentar
        click_wait = config.get('timeouts', {}).get('click_wait', 2)
        time.sleep(click_wait)
        
        # Ambil selectors dari config
        post_selectors = config.get('selectors', {}).get('post_button', {}).get('primary', [])
        
        # Fallback jika config tidak ada
        if not post_selectors:
            post_selectors = [
                '[data-hook="primary-btn"]',
                'button[data-hook="primary-btn"]',
                'button[type="submit"]',
                '.primary-btn',
                '.submit-button',
                'button:contains("Post")',
                'button:contains("Submit")',
                'button:contains("Send")'
            ]
        
        element_wait = config.get('timeouts', {}).get('submit_wait', 10)
        
        for selector in post_selectors:
            try:
                post_button = WebDriverWait(driver, element_wait).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                if post_button.is_displayed():
                    # Scroll ke tombol
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", post_button)
                    time.sleep(1)
                    
                    # Klik tombol post
                    post_button.click()
                    
                    # if logger:
                    #     logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Tombol post berhasil diklik: {Y}{selector}")
                    
                    # Tunggu untuk memastikan komentar terkirim
                    submit_wait = config.get('timeouts', {}).get('submit_wait', 5)
                    time.sleep(submit_wait)
                    return True
                    
            except TimeoutException:
                continue
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error dengan selector {selector}: {e}")
                continue
        
        # Coba dengan JavaScript jika selector gagal
        if logger:
            logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba JavaScript untuk tombol post...")
        
        post_script = """
        var postButton = document.querySelector('[data-hook="primary-btn"]') ||
                        document.querySelector('button[data-hook="primary-btn"]') ||
                        document.querySelector('button[type="submit"]') ||
                        document.querySelector('.primary-btn');
        if (postButton && postButton.offsetParent !== null) {
            postButton.click();
            return "Berhasil mengklik tombol post dengan JavaScript";
        }
        return "Tombol post tidak ditemukan dengan JavaScript";
        """
        
        result = driver.execute_script(post_script)
        
        if logger:
            logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Hasil JavaScript post: {result}")
        
        if "Berhasil" in result:
            submit_wait = config.get('timeouts', {}).get('submit_wait', 5)
            time.sleep(submit_wait)
            return True
        
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Tombol post tidak ditemukan")
        return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Error dalam klik_tombol_post: {e}")
        return False


def cari_kotak_komentar_aktif(driver, logger=None):
    """
    ✅ FIXED: Cari kotak komentar yang sudah aktif/diklik sebelumnya
    """
    try:
        # if logger:
        #     logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Mencari kotak komentar aktif...")
        
        # ✅ Load config untuk selectors
        config = load_wix_config()
        
        # Ambil selectors dari config
        active_selectors = config.get('selectors', {}).get('active_comment_box', {}).get('primary', [])
        
        # Fallback jika config tidak ada
        if not active_selectors:
            active_selectors = [
                "p.tAaif.jkMRy.is-editor-empty",
                "p.tAaif.jkMRy",
                "p[class*='tAaif'][class*='jkMRy']",
                "p[class*='is-editor-empty']",
                "div[contenteditable='true']",
                "p[contenteditable='true']",
                "[data-hook*='comment']",
                "[class*='comment'][class*='editor']"
            ]
        
        for selector in active_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        # if logger:
                        #     logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Kotak komentar aktif ditemukan: {Y}{selector}")
                        return element
                        
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error dengan selector {selector}: {e}")
                continue
        
        if logger:
            logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Kotak komentar aktif tidak ditemukan")
        return None
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Error dalam cari_kotak_komentar_aktif: {e}")
        return None


def cari_kotak_komentar_dengan_fallback(driver, logger=None):
    """
    Fungsi utama untuk mencari kotak komentar dengan berbagai metode fallback - MENGGUNAKAN CONFIG
    """
    try:
        if logger:
            logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Memulai pencarian kotak komentar dengan fallback...")
        
        # ✅ Load config
        config = load_wix_config()
        
        # Method 1: BeautifulSoup detection
        if logger:
            logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Method 1: BeautifulSoup detection...")
        
        bs_success = cari_kotak_komentar_beautifulsoup(driver, logger)
        if bs_success:
            if logger:
                logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} BeautifulSoup method berhasil!")
            return True
        
        # Method 2: Direct selector attempts dengan config
        if logger:
            logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Method 2: Direct selector attempts...")
        
        # ✅ Get selectors dari config
        comment_box_selectors = get_selectors(config, 'comment_box')
        
        # Fallback selectors jika config kosong
        if not comment_box_selectors:
            comment_box_selectors = [
                "p.tAaif.jkMRy.is-editor-empty",
                "p.tAaif.jkMRy",
                "p[class*='tAaif']",
                "p[class*='jkMRy']",
                "p[class*='is-editor-empty']",
                "[contenteditable='true']",
                "[data-hook*='comment']",
                ".comment-editor",
                ".comment-input"
            ]
        
        for selector in comment_box_selectors:
            try:
                if logger:
                    logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba selector: {selector}")
                
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed():
                        if logger:
                            logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Element ditemukan: {selector}")
                        
                        # Scroll dan klik
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                        
                        click_wait = config.get('timeouts', {}).get('click_wait', 2)
                        time.sleep(click_wait)
                        
                        try:
                            element.click()
                            input_wait = config.get('timeouts', {}).get('input_wait', 1)
                            time.sleep(random.uniform(input_wait, input_wait * 2))
                            
                            if logger:
                                logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Element berhasil diklik: {selector}")
                            return True
                            
                        except Exception as click_error:
                            if logger:
                                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Gagal klik element: {click_error}")
                            continue
                            
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error dengan selector {selector}: {e}")
                continue
        
        # Method 3: JavaScript search
        if logger:
            logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Method 3: JavaScript search...")
        
        try:
            # ✅ Gunakan keywords dari config
            keywords = config.get('text_search', {}).get('relevant_keywords', ['tAaif', 'jkMRy', 'is-editor-empty', 'comment', 'editor'])
            
            js_keywords = ', '.join([f'"{keyword}"' for keyword in keywords])
            js_search_script = f"""
            // Cari semua element yang mungkin kotak komentar
            var candidates = [];
            var keywords = [{js_keywords}];
            
            // Cari berdasarkan class
            keywords.forEach(function(cls) {{
                var elements = document.querySelectorAll('[class*="' + cls + '"]');
                elements.forEach(function(el) {{
                    if (el.offsetParent !== null) {{ // visible
                        candidates.push(el);
                    }}
                }});
            }});
            
            // Cari berdasarkan contenteditable
            var editableElements = document.querySelectorAll('[contenteditable="true"]');
            editableElements.forEach(function(el) {{
                if (el.offsetParent !== null) {{
                    candidates.push(el);
                }}
            }});
            
            // Return info tentang candidates
            return candidates.map(function(el) {{
                return {{
                    tagName: el.tagName,
                    className: el.className,
                    id: el.id,
                    text: el.textContent.substring(0, 50)
                }};
            }});
            """
            
            candidates = driver.execute_script(js_search_script)
            
            if candidates:
                if logger:
                    logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} JavaScript menemukan {len(candidates)} kandidat:")
                    for i, candidate in enumerate(candidates):
                        logger.info(f"  {i+1}. {candidate['tagName']}.{candidate['className']} - '{candidate['text']}'")
                
                # Coba klik kandidat pertama
                try:
                    click_script = """
                    var candidates = arguments[0];
                    if (candidates.length > 0) {
                        var firstCandidate = document.querySelector(candidates[0].tagName + '[class*="' + candidates[0].className.split(' ')[0] + '"]');
                        if (firstCandidate) {
                            firstCandidate.scrollIntoView({behavior: 'smooth', block: 'center'});
                            setTimeout(function() {
                                firstCandidate.click();
                            }, 1000);
                            return true;
                        }
                    }
                    return false;
                    """
                    
                    js_click_success = driver.execute_script(click_script, candidates)
                    
                    if js_click_success:
                        if logger:
                            logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} JavaScript click berhasil!")
                        
                        click_wait = config.get('timeouts', {}).get('click_wait', 2)
                        time.sleep(click_wait)
                        return True
                        
                except Exception as js_error:
                    if logger:
                        logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} JavaScript click gagal: {js_error}")
            
        except Exception as js_error:
            if logger:
                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} JavaScript search gagal: {js_error}")
        
        # Method 4: Brute force click pada semua p tags
        if logger:
            logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Method 4: Brute force p tags...")
        
        try:
            all_p_tags = driver.find_elements(By.TAG_NAME, "p")
            
            if logger:
                logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Ditemukan {len(all_p_tags)} p tags")
            
            # ✅ Gunakan keywords dari config
            keywords = config.get('text_search', {}).get('relevant_keywords', ['editor', 'comment', 'input', 'text', 'empty'])
            
            for i, p_tag in enumerate(all_p_tags):
                try:
                    if p_tag.is_displayed():
                        class_attr = p_tag.get_attribute("class") or ""
                        
                        # Cek apakah class mengandung kata kunci yang relevan
                        if any(keyword in class_attr.lower() for keyword in keywords):
                            if logger:
                                logger.info(f"🎯 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba p tag {i+1} dengan class: '{class_attr}'")
                            
                            # Scroll dan klik
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", p_tag)
                            time.sleep(1)
                            
                            p_tag.click()
                            input_wait = config.get('timeouts', {}).get('input_wait', 1)
                            time.sleep(random.uniform(input_wait, input_wait * 2))
                            
                            if logger:
                                logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} P tag berhasil diklik: {class_attr}")
                            return True
                            
                except Exception as p_error:
                    continue
                    
        except Exception as brute_error:
            if logger:
                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Brute force method gagal: {brute_error}")
        
        # Method 5: Last resort - cari berdasarkan posisi atau text dengan config
        if logger:
            logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Method 5: Last resort search...")
        
        try:
            # ✅ Gunakan placeholder texts dari config
            placeholder_texts = config.get('text_search', {}).get('placeholder_texts', [
                "write a comment",
                "add a comment", 
                "your comment",
                "leave a comment",
                "comment here",
                "tulis komentar",
                "tambah komentar"
            ])
            
            for placeholder in placeholder_texts:
                try:
                    xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{placeholder}')]"
                    elements = driver.find_elements(By.XPATH, xpath)
                    
                    for element in elements:
                        if element.is_displayed():
                            if logger:
                                logger.info(f"🎯 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba element dengan text: '{placeholder}'")
                            
                            # Scroll dan klik
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                            time.sleep(1)
                            
                            element.click()
                            input_wait = config.get('timeouts', {}).get('input_wait', 1)
                            time.sleep(random.uniform(input_wait, input_wait * 2))
                            
                            if logger:
                                logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Element berhasil diklik: {placeholder}")
                            return True
                            
                except Exception as placeholder_error:
                    continue
                    
        except Exception as last_resort_error:
            if logger:
                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Last resort method gagal: {last_resort_error}")
        
        # Jika semua method gagal
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Semua method pencarian kotak komentar gagal!")
        
        return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Error dalam cari_kotak_komentar_dengan_fallback: {e}")
        return False



def cari_dan_klik_submit(driver, logger=None):
    """
    ✅ FIXED: Cari dan klik tombol submit komentar - UPDATED dengan fallback ke klik_tombol_post + CONFIG
    """
    try:
        if logger:
            logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Mencari tombol submit...")
        
        # ✅ Load config
        config = load_wix_config()
        
        # Tunggu sebentar
        click_wait = config.get('timeouts', {}).get('click_wait', 2)
        time.sleep(random.uniform(click_wait * 0.5, click_wait))
        
        # Daftar selector untuk tombol submit
        submit_selectors = [
            'button[data-hook="primary-btn"]',
            '[data-hook="primary-btn"]',
            'button[type="submit"]',
            '.primary-btn',
            'button:contains("Post")',
            'button:contains("Submit")',
            'button:contains("Send")',
            'button:contains("Publish")',
            '.submit-button',
            '.post-button'
        ]
        
        element_wait = config.get('timeouts', {}).get('element_wait', 5)
        
        for selector in submit_selectors:
            try:
                if logger:
                    logger.info(f"🔍 [Komentar] {Y}[{W}Info{Y}]{W} Mencoba selector: {selector}")
                
                submit_button = WebDriverWait(driver, element_wait).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                if submit_button.is_displayed():
                    # Scroll ke tombol
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
                    time.sleep(1)
                    
                    # Klik tombol
                    submit_button.click()
                    
                    if logger:
                        logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Tombol submit berhasil diklik: {selector}")
                    
                    # Tunggu untuk memastikan submit berhasil
                    submit_wait = config.get('timeouts', {}).get('submit_wait', 5)
                    time.sleep(random.uniform(submit_wait * 0.6, submit_wait))
                    return True
                    
            except TimeoutException:
                continue
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Error dengan selector {selector}: {e}")
                continue
        
        # ✅ FALLBACK: Gunakan klik_tombol_post jika selector gagal
        if logger:
            logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Fallback ke klik_tombol_post...")
        
        return klik_tombol_post(driver, logger)
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Error dalam cari_dan_klik_submit: {e}")
        
        # ✅ FINAL FALLBACK: Tetap coba klik_tombol_post
        if logger:
            logger.info(f"🔄 [Komentar] {Y}[{W}Info{Y}]{W} Final fallback ke klik_tombol_post...")
        
        return klik_tombol_post(driver, logger)


def update_config_with_delays():
    """
    ✅ TAMBAHAN: Update config.yaml dengan delays jika belum ada
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        
        if os.path.exists(config_path) and yaml:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            # Tambahkan delays jika belum ada
            if 'delays' not in config:
                config['delays'] = {
                    'initial_wait': 2.5,
                    'between_steps': 2.5,
                    'final_wait': 4,
                    'retry_delay': 1.5
                }
            
            # Tambahkan logging config jika belum ada
            if 'logging' not in config:
                config['logging'] = {
                    'max_comment_length': 100,
                    'show_element_info': True,
                    'show_verification': True
                }
            
            # Simpan kembali
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                
    except Exception:
        pass  # Silent fail jika tidak bisa update


def test_all_functions(driver, logger=None):
    """
    ✅ TAMBAHAN: Test semua fungsi komentar untuk debugging
    """
    try:
        if logger:
            logger.info(f"🧪 [Test] {Y}[{W}Info{Y}]{W} Memulai test semua fungsi komentar...")
        
        # Test 1: Load config
        if logger:
            logger.info(f"🧪 [Test] {Y}[{W}Info{Y}]{W} 1. Test load config...")
        config = load_wix_config()
        if logger:
            logger.info(f"✅ [Test] {Y}[{W}Info{Y}]{W} Config loaded: {len(config)} keys")
        
        # Test 2: Format comment
        if logger:
            logger.info(f"🧪 [Test] {Y}[{W}Info{Y}]{W} 2. Test format comment...")
        test_comment = "This is a test comment with {link text|https://example.com} inside."
        formatted = format_comment_for_log(test_comment, config, logger)
        if logger:
            logger.info(f"✅ [Test] {Y}[{W}Info{Y}]{W} Formatted: {formatted}")
        
        # Test 3: Process links
        if logger:
            logger.info(f"🧪 [Test] {Y}[{W}Info{Y}]{W} 3. Test process links...")
        processed_text, links_info = process_comment_with_links(test_comment, logger)
        if logger:
            logger.info(f"✅ [Test] {Y}[{W}Info{Y}]{W} Processed: {processed_text}")
            logger.info(f"✅ [Test] {Y}[{W}Info{Y}]{W} Links found: {len(links_info)}")
        
        # Test 4: Cari kotak komentar
        if logger:
            logger.info(f"🧪 [Test] {Y}[{W}Info{Y}]{W} 4. Test cari kotak komentar...")
        kotak_found = cari_kotak_komentar_dengan_fallback(driver, logger)
        if logger:
            if kotak_found:
                logger.info(f"✅ [Test] {Y}[{W}Info{Y}]{W} Kotak komentar ditemukan!")
            else:
                logger.warning(f"⚠️ [Test] {Y}[{W}Info{Y}]{W} Kotak komentar tidak ditemukan")
        
        # ❌ COMMENT OUT: Test 5 yang bermasalah
        # # Test 5: Debug page elements
        # if logger:
        #     logger.info("🧪 [Test] {Y}[{W}Info{Y}]{W} 5. Test debug page elements...")
        # debug_page_elements(driver, logger)
        
        if logger:
            logger.info(f"🎉 [Test] {Y}[{W}Info{Y}]{W} Semua test selesai!")
        
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Test] {Y}[{W}Info{Y}]{R} Error dalam test: {e}")
        return False



def validate_comment_format(comment_text, logger=None):
    """
    ✅ TAMBAHAN: Validasi format komentar sebelum diproses
    """
    try:
        if logger:
            logger.info(f"🔍 [Validate] {Y}[{W}Info{Y}]{W} Memvalidasi format komentar...")
        
        issues = []
        
        # Cek panjang komentar
        if len(comment_text) < 10:
            issues.append("Komentar terlalu pendek (< 10 karakter)")
        elif len(comment_text) > 1000:
            issues.append("Komentar terlalu panjang (> 1000 karakter)")
        
        # Cek format link
        link_pattern = r'\{([^|]+)\|([^}]+)\}'
        link_matches = re.findall(link_pattern, comment_text)
        
        for i, (text, url) in enumerate(link_matches):
            if not text.strip():
                issues.append(f"Link {i+1}: Text kosong")
            if not url.strip():
                issues.append(f"Link {i+1}: URL kosong")
            if not url.startswith(('http://', 'https://')):
                issues.append(f"Link {i+1}: URL tidak valid (harus dimulai dengan http/https)")
        
        # Cek karakter khusus yang mungkin bermasalah
        problematic_chars = ['<', '>', '"', "'"]
        for char in problematic_chars:
            if char in comment_text:
                issues.append(f"Mengandung karakter bermasalah: {char}")
        
        if issues:
            if logger:
                logger.warning(f"⚠️ [Validate] {Y}[{W}Info{Y}]{W} Ditemukan {len(issues)} masalah:")
                for issue in issues:
                    logger.warning(f"   - {issue}")
            return False, issues
        else:
            if logger:
                logger.info(f"✅ [Validate] {Y}[{W}Info{Y}]{W} Format komentar valid!")
            return True, []
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Validate] {Y}[{W}Info{Y}]{R} Error validasi: {e}")
        return False, [f"Error validasi: {e}"]
    

def cleanup_after_comment(driver, logger=None):
    """
    ✅ TAMBAHAN: Cleanup setelah komentar (tutup modal, dll)
    """
    try:
        if logger:
            logger.info(f"🧹 [Cleanup] {Y}[{W}Info{Y}]{W} Melakukan cleanup setelah komentar...")
        
        # Coba tutup modal atau dialog yang mungkin masih terbuka
        close_selectors = [
            '[data-hook="modal-close-button"]',
            '.modal-close',
            '.close-button',
            '[aria-label="Close"]',
            '.popup-close',
            '[data-testid="close"]'
        ]
        
        for selector in close_selectors:
            try:
                close_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                for button in close_buttons:
                    if button.is_displayed():
                        button.click()
                        if logger:
                            logger.info(f"✅ [Cleanup] {Y}[{W}Info{Y}]{W} Modal ditutup: {selector}")
                        time.sleep(1)
                        break
            except:
                continue
        
        # Klik di area kosong untuk memastikan tidak ada element yang terfokus
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            body.click()
            time.sleep(0.5)
        except:
            pass
        
        # Scroll ke atas halaman
        try:
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
        except:
            pass
        
        if logger:
            logger.info(f"✅ [Cleanup] {Y}[{W}Info{Y}]{W} Cleanup selesai!")
        
        return True
        
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ [Cleanup] {Y}[{W}Info{Y}]{W} Error cleanup: {e}")
        return False



def get_comment_status(driver, logger=None):
    """
    ✅ TAMBAHAN: Cek status komentar setelah submit (berhasil/gagal)
    """
    try:
        if logger:
            logger.info(f"🔍 [Status] {Y}[{W}Info{Y}]{W} Mengecek status komentar...")
        
        # Tunggu sebentar untuk response
        time.sleep(3)
        
        # Indikator sukses
        success_indicators = [
            "comment posted",
            "comment added", 
            "thank you",
            "success",
            "published",
            "komentar berhasil",
            "terima kasih"
        ]
        
        # Indikator error
        error_indicators = [
            "error",
            "failed",
            "try again",
            "invalid",
            "required",
            "gagal",
            "kesalahan"
        ]
        
        # Cek text di halaman
        page_text = driver.page_source.lower()
        
        # Cek success
        for indicator in success_indicators:
            if indicator in page_text:
                if logger:
                    logger.info(f"✅ [Status] {Y}[{W}Info{Y}]{W} Indikator sukses ditemukan: '{indicator}'")
                return "success"
        
        # Cek error
        for indicator in error_indicators:
            if indicator in page_text:
                if logger:
                    logger.warning(f"⚠️ [Status] {Y}[{W}Info{Y}]{W} Indikator error ditemukan: '{indicator}'")
                return "error"
        
        # Cek apakah ada alert atau notification
        try:
            alerts = driver.find_elements(By.CSS_SELECTOR, ".alert, .notification, .message, [role='alert']")
            for alert in alerts:
                if alert.is_displayed():
                    alert_text = alert.text.lower()
                    if any(indicator in alert_text for indicator in success_indicators):
                        if logger:
                            logger.info(f"✅ [Status] {Y}[{W}Info{Y}]{W} Alert sukses: '{alert.text}'")
                        return "success"
                    elif any(indicator in alert_text for indicator in error_indicators):
                        if logger:
                            logger.warning(f"⚠️ [Status] {Y}[{W}Info{Y}]{W} Alert error: '{alert.text}'")
                        return "error"
        except:
            pass
        
        if logger:
            logger.info(f"ℹ️ [Status] {Y}[{W}Info{Y}]{W} Status tidak dapat ditentukan")
        return "unknown"
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Status] {Y}[{W}Info{Y}]{R} Error cek status: {e}")
        return "error"




# ✅ BARU: Helper function untuk debug config
def debug_config_selectors(logger=None):
    """Debug function untuk melihat semua selectors dari config"""
    try:
        config = load_wix_config()
        selectors_config = config.get('selectors', {})
        
        if logger:
            logger.info("🔧 [Debug] Config selectors loaded:")
            for selector_type, selector_data in selectors_config.items():
                if isinstance(selector_data, dict):
                    logger.info(f"  {selector_type}:")
                    for sub_type, sub_selectors in selector_data.items():
                        if isinstance(sub_selectors, list):
                            logger.info(f"    {sub_type}: {len(sub_selectors)} selectors")
                        else:
                            logger.info(f"    {sub_type}: {sub_selectors}")
                else:
                    logger.info(f"  {selector_type}: {selector_data}")
        
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Debug] Error debugging config: {e}")
        return False

# ✅ BARU: Test function untuk config
def test_config_loading(logger=None):
    """Test function untuk memastikan config loading berfungsi"""
    try:
        if logger:
            logger.info("🧪 [Test] Testing config loading...")
        
        # Test 1: Load config
        config = load_wix_config()
        if not config:
            if logger:
                logger.error(f"❌ [Test] Config loading failed")
            return False
        
        if logger:
            logger.info(f"✅ [Test] Config loaded successfully")
        
        # Test 2: Validate config structure
        validation_result = validate_config(config, logger)
        if not validation_result:
            if logger:
                logger.warning("⚠️ [Test] Config validation failed")
        
        # Test 3: Test selector extraction
        test_selectors = get_selectors(config, 'comment_box')
        if logger:
            logger.info(f"✅ [Test] Comment box selectors: {len(test_selectors)} found")
        
        # Test 4: Test timeout values
        timeouts = config.get('timeouts', {})
        if logger:
            logger.info(f"✅ [Test] Timeouts configured: {list(timeouts.keys())}")
        
        # Test 5: Export config for verification
        export_success = export_current_config("test_config_export.yaml", logger)
        if export_success and logger:
            logger.info(f"✅ [Test] Config export successful")
        
        if logger:
            logger.info(f"🎉 [Test] All config tests passed!")
        
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Test] Error dalam test_config_loading: {e}")
        return False

def get_config_summary(logger=None):
    """Get summary of current config untuk debugging"""
    try:
        config = load_wix_config()
        
        summary = {
            'selectors_count': {},
            'timeouts': config.get('timeouts', {}),
            'total_selectors': 0
        }
        
        selector_groups = ['comment_box', 'link_button', 'url_input', 'save_button', 'post_button', 'toggle_switch']
        
        for group in selector_groups:
            selectors = get_selectors(config, group)
            summary['selectors_count'][group] = len(selectors)
            summary['total_selectors'] += len(selectors)
        
        if logger:
            logger.info(f"📋 [Config Summary]:")
            logger.info(f"  Total selectors: {summary['total_selectors']}")
            logger.info(f"  Selector groups: {summary['selectors_count']}")
            logger.info(f"  Timeouts: {summary['timeouts']}")
        
        return summary
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Error getting config summary: {e}")
        return {}

def reset_element_to_default_state(driver, element, logger=None):
    """Reset element ke state default sebelum input"""
    try:
        if logger:
            logger.info(f"🔄 [Reset] Resetting element to default state...")
        
        # ✅ Load config
        config = load_wix_config()
        
        # Method 1: Clear content
        try:
            element.clear()
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(input_wait * 0.5)
            
            if logger:
                logger.info(f"✅ [Reset] Element cleared successfully")
            
        except Exception as clear_error:
            if logger:
                logger.warning(f"⚠️ [Reset] Clear failed: {clear_error}")
            
            # Fallback: Select all and delete
            try:
                element.click()
                time.sleep(0.2)
                element.send_keys(Keys.CONTROL + "a")
                time.sleep(0.2)
                element.send_keys(Keys.DELETE)
                
                if logger:
                    logger.info(f"✅ [Reset] Element cleared with Ctrl+A+Delete")
                
            except Exception as fallback_error:
                if logger:
                    logger.warning(f"⚠️ [Reset] Fallback clear failed: {fallback_error}")
        
        # Method 2: Remove any existing formatting
        try:
            # JavaScript to remove formatting
            driver.execute_script("""
                var element = arguments[0];
                element.innerHTML = '';
                element.textContent = '';
                
                // Remove any inline styles
                element.removeAttribute('style');
                
                // Trigger events to notify the page
                var events = ['input', 'change', 'focus'];
                events.forEach(function(eventType) {
                    var event = new Event(eventType, { bubbles: true });
                    element.dispatchEvent(event);
                });
            """, element)
            
            if logger:
                logger.info(f"✅ [Reset] Formatting removed with JavaScript")
            
        except Exception as js_error:
            if logger:
                logger.warning(f"⚠️ [Reset] JavaScript formatting removal failed: {js_error}")
        
        # Method 3: Focus element
        try:
            element.click()
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(input_wait * 0.3)
            
            if logger:
                logger.info(f"✅ [Reset] Element focused")
            
        except Exception as focus_error:
            if logger:
                logger.warning(f"⚠️ [Reset] Focus failed: {focus_error}")
        
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Reset] Error dalam reset_element_to_default_state: {e}")
        return False
    

def verify_element_state(driver, element, expected_text="", logger=None):
    """Verify state element setelah input"""
    try:
        if logger:
            logger.info(f"🔍 [Verify] Checking element state...")
        
        # Get current text from various sources
        current_text = ""
        text_sources = []
        
        try:
            text_content = element.text or ""
            if text_content:
                text_sources.append(f"text: '{text_content}'")
                current_text = text_content
        except:
            pass
        
        try:
            value_content = element.get_attribute('value') or ""
            if value_content:
                text_sources.append(f"value: '{value_content}'")
                if not current_text:
                    current_text = value_content
        except:
            pass
        
        try:
            inner_html = element.get_attribute('innerHTML') or ""
            if inner_html:
                text_sources.append(f"innerHTML: '{inner_html[:50]}...'")
        except:
            pass
        
        try:
            text_content_attr = element.get_attribute('textContent') or ""
            if text_content_attr:
                text_sources.append(f"textContent: '{text_content_attr}'")
        except:
            pass
        
        if logger:
            logger.info(f"📝 [Verify] Current text sources: {text_sources}")
            logger.info(f"📝 [Verify] Primary text: '{current_text}'")
        
        # Check if expected text is present
        if expected_text:
            if expected_text.lower() in current_text.lower():
                if logger:
                    logger.info(f"✅ [Verify] Expected text found: '{expected_text}'")
                return True
            else:
                if logger:
                    logger.warning(f"⚠️ [Verify] Expected text not found: '{expected_text}'")
                return False
        else:
            # Just check if element has any content
            has_content = bool(current_text.strip())
            if logger:
                logger.info(f"📊 [Verify] Element has content: {has_content}")
            return has_content
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Verify] Error dalam verify_element_state: {e}")
        return False

def wait_for_element_ready(driver, element, logger=None):
    """Wait until element is ready for interaction"""
    try:
        if logger:
            logger.info(f"⏳ [Wait] Waiting for element to be ready...")
        
        # ✅ Load config
        config = load_wix_config()
        element_wait = config.get('timeouts', {}).get('element_wait', 5)
        
        # Wait for element to be clickable
        try:
            # Get element selector for WebDriverWait
            element_tag = element.tag_name
            element_class = element.get_attribute('class') or ""
            element_id = element.get_attribute('id') or ""
            
            # Create a selector
            if element_id:
                selector = f"#{element_id}"
            elif element_class:
                clean_class = element_class.strip().replace(' ', '.')
                selector = f"{element_tag}.{clean_class}"
            else:
                selector = element_tag
            
            # Wait for element to be clickable
            WebDriverWait(driver, element_wait).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            if logger:
                logger.info(f"✅ [Wait] Element is ready for interaction")
            return True
            
        except TimeoutException:
            if logger:
                logger.warning(f"⚠️ [Wait] Timeout waiting for element to be ready")
            return False
        except Exception as wait_error:
            if logger:
                logger.warning(f"⚠️ [Wait] Error waiting for element: {wait_error}")
            
            # Fallback: just check if element is displayed and enabled
            try:
                if element.is_displayed() and element.is_enabled():
                    if logger:
                        logger.info(f"✅ [Wait] Element ready (fallback check)")
                    return True
                else:
                    if logger:
                        logger.warning(f"⚠️ [Wait] Element not ready (fallback check)")
                    return False
            except:
                return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Wait] Error dalam wait_for_element_ready: {e}")
        return False



def process_comment_with_links(comment_text, logger=None):
    """
    ✅ FIXED: Proses komentar yang mengandung pola {text|url} dan simpan informasi link
    """
    try:
        # if logger:
        #     logger.info(f"🔗 [Komentar] {Y}[{W}Info{Y}]{W} Memproses komentar dengan links...")
        
        # Pattern untuk mendeteksi {text|url}
        link_pattern = r'\{([^|]+)\|([^}]+)\}'
        
        # Cari semua matches
        link_matches = re.findall(link_pattern, comment_text)
        
        # Simpan informasi link
        links_info = []
        
        if link_matches:
            # if logger:
            #     logger.info(f"🔗 [Komentar] {Y}[{W}Info{Y}]{W} Ditemukan {G}{len(link_matches)} {W}link dalam komentar")
            
            for i, (text, url) in enumerate(link_matches):
                text = text.strip()
                url = url.strip()
                
                links_info.append({
                    'text': text,
                    'url': url,
                    'index': i
                })
                
                if logger:
                    logger.info(f"🔗 [Komentar] {Y}[{W}Info{Y}]{W} Link {G}{i+1}{W}: {Y}{text} {W}-> {Y}{url}")
            
            # Hapus format {text|url} dan ganti dengan text saja
            processed_comment = re.sub(link_pattern, r'\1', comment_text)
            
            # if logger:
            #     logger.info(f"📝 [Komentar] {Y}[{W}Info{Y}]{W} Original: {Y}{comment_text}")
            #     logger.info(f"📝 [Komentar] {Y}[{W}Info{Y}]{W} Processed: {Y}{processed_comment}")
            
            return processed_comment, links_info
        else:
            if logger:
                logger.info(f"📝 [Komentar] {Y}[{W}Info{Y}]{W} Tidak ada link khusus dalam komentar")
            return comment_text, []
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Error processing comment links: {e}")
        return comment_text, []


def input_komentar_text(driver, element, text, logger=None):
    """
    ✅ UPDATED: Input text ke kotak komentar - DELEGATE TO PROCESSED VERSION
    """
    try:
        if logger:
            logger.info(f"⌨️ [Komentar] {Y}[{W}Info{Y}]{W} Memulai input text...")
        
        # Process comment links once
        processed_text, links_info = process_comment_with_links(text, logger)
        
        # Delegate to processed version
        return input_komentar_text_processed(driver, element, processed_text, links_info, logger)
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Error dalam input_komentar_text: {e}")
        return False


def format_comment_for_log(comment_text, config=None, logger=None):
    """
    ✅ FIXED: Format comment untuk logging (hide sensitive info jika perlu)
    """
    try:
        # Jika comment terlalu panjang, potong untuk log
        max_log_length = 100
        if config and isinstance(config, dict):
            max_log_length = config.get('logging', {}).get('max_comment_length', 100)
        
        if len(comment_text) > max_log_length:
            return f"{comment_text[:max_log_length]}..."
        
        return comment_text
        
    except Exception:
        return "Comment text unavailable"


def verify_comment_input(driver, element, expected_text, logger=None):
    """
    ✅ FIXED: Verifikasi bahwa text sudah masuk dengan benar - REMOVE DUPLICATE PROCESSING
    """
    try:
        # if logger:
        #     logger.info(f"🔍 [Verify] {Y}[{W}Info{Y}]{W} Memverifikasi input komentar...")
        
        # ❌ REMOVE: Duplicate comment processing
        # processed_text, _ = process_comment_with_links(expected_text, logger)
        
        # ✅ USE: Expected text directly (sudah diproses sebelumnya)
        text_to_verify = expected_text
        
        # Ambil text dari berbagai sumber
        verification_methods = [
            ('textContent', lambda: element.get_attribute('textContent')),
            ('innerText', lambda: element.get_attribute('innerText')),
            ('innerHTML', lambda: element.get_attribute('innerHTML')),
            ('value', lambda: element.get_attribute('value')),
            ('text', lambda: element.text)
        ]
        
        for method_name, method_func in verification_methods:
            try:
                current_text = method_func() or ""
                
                if current_text.strip():
                    # Cek apakah expected text ada dalam current text
                    if text_to_verify.lower() in current_text.lower():
                        if logger:
                            # logger.info(f"✅ [Verify] {Y}[{W}Info{Y}]{W} Verifikasi berhasil dengan {method_name}")
                            # logger.info(f"📝 [Verify] {Y}[{W}Info{Y}]{W} Current text: '{current_text[:50]}...'")
                            return True
                    
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Verify] {Y}[{W}Info{Y}]{W} Method {method_name} gagal: {e}")
                continue
        
        if logger:
            logger.warning(f"⚠️ [Verify] {Y}[{W}Info{Y}]{W} Verifikasi gagal - text tidak ditemukan")
        
        return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Verify] {Y}[{W}Info{Y}]{R} Error dalam verify_comment_input: {e}")
        return False


def load_wix_config():
    """
    ✅ FIXED: Load Wix config dengan safe handling dan proper imports
    """
    try:
        import yaml
        import os
        
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config if config else {}
        else:
            # Return default config jika file tidak ada
            return {
                'timeouts': {
                    'element_wait': 5,
                    'click_wait': 2,
                    'input_wait': 1,
                    'submit_wait': 5,
                    'link_process_wait': 2
                },
                'delays': {
                    'initial_wait': 2.5,
                    'between_steps': 2.5,
                    'final_wait': 4,
                    'retry_delay': 1.5
                },
                'logging': {
                    'max_comment_length': 100,
                    'show_element_info': True,
                    'show_verification': True
                }
            }
            
    except Exception as e:
        # Return minimal config jika ada error
        return {
            'timeouts': {'input_wait': 1, 'click_wait': 2},
            'delays': {'initial_wait': 2.5, 'between_steps': 2.5, 'final_wait': 4}
        }




def get_comment_element_info(driver, element, logger=None):
    """
    ✅ FIXED: Debug info untuk comment element
    """
    try:
        # if logger:
            # logger.info(f"🔍 [Debug] {Y}[{W}Info{Y}]{W} Getting comment element info...")
        
        info = {
            'tag_name': element.tag_name,
            'class': element.get_attribute('class') or 'No class',
            'id': element.get_attribute('id') or 'No ID',
            'contenteditable': element.get_attribute('contenteditable'),
            'placeholder': element.get_attribute('placeholder'),
            'data_hook': element.get_attribute('data-hook'),
            'is_displayed': element.is_displayed(),
            'is_enabled': element.is_enabled(),
            'text_length': len(element.text or ''),
            'innerHTML_length': len(element.get_attribute('innerHTML') or ''),
            'location': element.location,
            'size': element.size
        }
        
        if logger:
            # logger.info(f"📊 [Debug] {Y}[{W}Info{Y}]{W} Element info:")
            for key, value in info.items():
                # logger.info(f"   {key}: {value}")
        
                return info
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Debug] {Y}[{W}Info{Y}]{R} Error getting element info: {e}")
        return {}


def smart_retry_input(driver, element, text, max_retries=3, logger=None):
    """
    ✅ FIXED: Smart retry untuk input dengan berbagai strategi - OPTIMIZE PROCESSING
    """
    try:
        # if logger:
        #     logger.info(f"🔄 [SmartRetry] {Y}[{W}Info{Y}]{W} Memulai smart retry input (max: {G}{max_retries})")
        
        config = load_wix_config()
        
        # ✅ PROCESS ONCE: Process comment links only once at the beginning
        processed_text, links_info = process_comment_with_links(text, logger)
        
        for attempt in range(max_retries):
            if logger:
                logger.info(f"🔄 [SmartRetry] {Y}[{W}Info{Y}]{W} Percobaan {G}{attempt + 1}{W}/{G}{max_retries}")
            
            # Strategi berbeda untuk setiap percobaan
            if attempt == 0:
                # Percobaan 1: Method normal dengan processed data
                success = input_komentar_text_processed(driver, element, processed_text, links_info, logger)
            elif attempt == 1:
                # Percobaan 2: Refresh element dan coba lagi
                if logger:
                    logger.info(f"🔄 [SmartRetry] {Y}[{W}Info{Y}]{W} Refreshing element...")
                
                # Coba cari element lagi
                refreshed_element = cari_kotak_komentar_aktif(driver, logger)
                if refreshed_element:
                    success = input_komentar_text_processed(driver, refreshed_element, processed_text, links_info, logger)
                else:
                    success = False
            else:
                # Percobaan 3: Fallback total dengan direct links
                if logger:
                    logger.info(f"🔄 [SmartRetry] {Y}[{W}Info{Y}]{W} Using fallback total...")
                
                # Buat text dengan direct links
                fallback_text = processed_text
                for link_data in links_info:
                    text_to_link = link_data['text']
                    url_to_link = link_data['url']
                    
                    if text_to_link in fallback_text:
                        fallback_text = fallback_text.replace(text_to_link, f"{text_to_link} {url_to_link}")
                    else:
                        fallback_text += f" {text_to_link} {url_to_link}"
                
                success = input_fallback_text_with_links(driver, element, fallback_text, logger)
            
            if success:
                # ✅ VERIFY: Use processed text for verification
                if verify_comment_input(driver, element, processed_text, logger):
                    if logger:
                        # logger.info(f"✅ [SmartRetry] {Y}[{W}Info{Y}]{W} Berhasil pada percobaan {attempt + 1}!")
                        return True
                else:
                    if logger:
                        logger.warning(f"⚠️ [SmartRetry] {Y}[{W}Info{Y}]{W} Input berhasil tapi verifikasi gagal")
            
            # Delay sebelum retry
            if attempt < max_retries - 1:
                retry_delay = config.get('timeouts', {}).get('input_wait', 1) * (attempt + 1)
                if logger:
                    logger.info(f"⏳ [SmartRetry] {Y}[{W}Info{Y}]{W} Menunggu {retry_delay}s sebelum retry...")
                time.sleep(retry_delay)
        
        if logger:
            logger.error(f"❌ [SmartRetry] {Y}[{W}Info{Y}]{R} Semua percobaan gagal!")
        return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [SmartRetry] {Y}[{W}Info{Y}]{R} Error dalam smart_retry_input: {e}")
        return False


def input_komentar_text_processed(driver, element, processed_text, links_info, logger=None):
    """
    ✅ NEW: Input text yang sudah diproses (avoid duplicate processing)
    """
    try:
        # if logger:
        #     logger.info(f"⌨️ [Komentar] {Y}[{W}Info{Y}]{W} Memulai input text (pre-processed)...")
        
        # ✅ Load config
        config = load_wix_config()
        
        # Method 1: Clear dan Send Keys
        input_success = False
        
        try:
            # if logger:
            #     logger.info(f"⌨️ [Komentar] {Y}[{W}Info{Y}]{W} Mencoba Clear + Send Keys...")
            
            element.clear()
            input_wait = config.get('timeouts', {}).get('input_wait', 1)
            time.sleep(input_wait * 0.5)
            element.send_keys(processed_text)
            time.sleep(random.uniform(input_wait, input_wait * 2))
            
            # Verifikasi input
            current_text = element.text or element.get_attribute('value') or ""
            if processed_text.lower() in current_text.lower():
                # if logger:
                #     logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Clear + Send Keys berhasil!")
                input_success = True
            
        except Exception as e:
            if logger:
                logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Clear + Send Keys gagal: {e}")
        
        # Method 2: JavaScript innerHTML (jika method 1 gagal)
        if not input_success:
            try:
                if logger:
                    logger.info(f"⌨️ [Komentar] {Y}[{W}Info{Y}]{W} Mencoba JavaScript innerHTML...")
                
                driver.execute_script("arguments[0].innerHTML = arguments[1];", element, processed_text)
                input_wait = config.get('timeouts', {}).get('input_wait', 1)
                time.sleep(random.uniform(input_wait, input_wait * 2))
                
                # Trigger input event
                driver.execute_script("""
                    var element = arguments[0];
                    var event = new Event('input', { bubbles: true });
                    element.dispatchEvent(event);
                """, element)
                
                if logger:
                    logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} JavaScript innerHTML berhasil!")
                input_success = True
                
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} JavaScript innerHTML gagal: {e}")
        
        # Method 3: JavaScript textContent (jika method 2 gagal)
        if not input_success:
            try:
                if logger:
                    logger.info(f"⌨️ [Komentar] {Y}[{W}Info{Y}]{W} Mencoba JavaScript textContent...")
                
                driver.execute_script("arguments[0].textContent = arguments[1];", element, processed_text)
                input_wait = config.get('timeouts', {}).get('input_wait', 1)
                time.sleep(random.uniform(input_wait, input_wait * 2))
                
                # Trigger events
                driver.execute_script("""
                    var element = arguments[0];
                    var inputEvent = new Event('input', { bubbles: true });
                    var changeEvent = new Event('change', { bubbles: true });
                    element.dispatchEvent(inputEvent);
                    element.dispatchEvent(changeEvent);
                """, element)
                
                if logger:
                    logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} JavaScript textContent berhasil!")
                input_success = True
                
            except Exception as e:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} JavaScript textContent gagal: {e}")
        
        # ✅ PROSES LINKS: Jika input berhasil dan ada links
        if input_success and links_info:
            # if logger:
            #     logger.info(f"🔗 [Komentar] {Y}[{W}Info{Y}]{W} Memproses {G}{len(links_info)} {W}links")
            
            # Gunakan fungsi yang sudah dimodifikasi dengan fallback
            link_success = process_links_in_element(driver, element, links_info, logger)
            
            if link_success:
                # if logger:
                #     logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{G} Semua links berhasil diproses{W}!")
                pass
            else:
                if logger:
                    logger.warning(f"⚠️ [Komentar] {Y}[{W}Info{Y}]{W} Beberapa links gagal diproses")
        
        if input_success:
            if logger:
                # logger.info(f"✅ [Komentar] {Y}[{W}Info{Y}]{W} Input komentar berhasil!")
                return True
        else:
            if logger:
                logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Semua metode input gagal")
            return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Error dalam input_komentar_text_processed: {e}")
        return False

def truncate_text_for_log(text, max_length=50):
    """Helper function untuk truncate text di log"""
    if len(text) <= max_length:
        return text
    
    # Cari posisi spasi terdekat sebelum max_length
    truncate_pos = max_length
    space_pos = text.rfind(' ', 0, max_length)
    
    if space_pos > max_length * 0.7:  # Jika spasi tidak terlalu jauh
        truncate_pos = space_pos
    
    return text[:truncate_pos] + "..."


def lanjutkan_komentar(driver, comment_data, comment_template, signature_data, logger=None):
    """
    ✅ FINAL FIXED: Fungsi untuk melanjutkan proses komentar setelah login berhasil dan kotak komentar ditemukan
    """
    try:
        if logger:
            logger.info(f"📝 [Komentar] {Y}[{W}Info{Y}]{W} Memulai proses input komentar...")
        
        # ✅ Load config dengan error handling
        config = load_wix_config()
        
        # ✅ GUNAKAN CONFIG DELAYS dengan fallback
        delays = config.get('delays', {})
        initial_wait = delays.get('initial_wait', 2.5)
        between_steps = delays.get('between_steps', 2.5)
        final_wait = delays.get('final_wait', 4)
        
        # Tunggu sebentar untuk memastikan kotak komentar siap
        time.sleep(random.uniform(initial_wait * 0.8, initial_wait * 1.2))
        
        # Ambil komentar yang akan diposting
        comment_text = comment_data.get('comment', 'Thanks for sharing this valuable information!')
        
        # if logger:
        #     display_text = format_comment_for_log(comment_text, config, logger)
        #     logger.info(f"💬 [Komentar] {Y}[{W}Info{Y}]{W} Text yang akan diposting: {display_text}")
        
        # Cari kotak komentar yang sudah diklik sebelumnya
        kotak_komentar = cari_kotak_komentar_aktif(driver, logger)
        
        if not kotak_komentar:
            if logger:
                logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Kotak komentar tidak ditemukan atau tidak aktif")
            return False
        
        # ✅ Debug element info (optional)
        logging_config = config.get('logging', {})
        if logging_config.get('show_element_info', True) and logger:
            get_comment_element_info(driver, kotak_komentar, logger)
        
        # ✅ Input komentar dengan smart retry
        input_success = smart_retry_input(driver, kotak_komentar, comment_text, max_retries=3, logger=logger)
        
        if not input_success:
            if logger:
                logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Gagal input komentar setelah semua percobaan")
            return False
        
        # Tunggu sebentar setelah input
        time.sleep(random.uniform(between_steps * 0.8, between_steps * 1.2))
        
        # ✅ Klik tombol post menggunakan fungsi yang sudah ada
        # if logger:
        #     logger.info(f"🚀 [Komentar] {Y}[{W}Info{Y}]{W} Mengklik tombol post komentar...")
        
        post_success = klik_tombol_post(driver, logger)
        
        if post_success:
            # if logger:
            #     logger.info(f"🎉 [Komentar] {Y}[{W}Info{Y}]{W} Komentar berhasil disubmit!")
            
            # Tunggu untuk melihat hasil
            time.sleep(random.uniform(final_wait * 0.8, final_wait * 1.2))
            return True
        else:
            if logger:
                logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Gagal submit komentar")
            return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ [Komentar] {Y}[{W}Info{Y}]{R} Error dalam lanjutkan_komentar: {e}")
        return False


# ✅ TAMBAHAN: Helper function untuk load config yang lebih robust
def load_wix_config():
    """Load Wix config dengan error handling yang lebih baik"""
    try:
        import os
        import yaml
        
        # Path ke config file
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        
        if not os.path.exists(config_path):
            print(f"⚠️ Config file tidak ditemukan: {config_path}")
            return get_default_config()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not config:
            print(f"⚠️ Config file kosong, menggunakan default config")
            return get_default_config()
        
        # Merge dengan default config untuk memastikan semua key ada
        default_config = get_default_config()
        merged_config = merge_configs(default_config, config)
        
        return merged_config
        
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return get_default_config()

def get_default_config():
    """Default config jika file config tidak tersedia"""
    return {
        'selectors': {
            'comment_box_pattern': '[id*=\'root-comment-box-start-\']',
            'comment_box_xpath': '//*[contains(@id, \'root-comment-box-start-\')]',
            'comment_form': 'body',
            'name_field': 'input',
            'email_field': 'input',
            'comment_field': 'textarea, input',
            'safe_click_areas': ['body', 'main', '.content', '#content']
        },
        'timeouts': {
            'element_wait': 5,
            'click_wait': 2,
            'input_wait': 1,
            'submit_wait': 5
        },
        'text_search': {
            'relevant_keywords': ['tAaif', 'jkMRy', 'is-editor-empty', 'comment', 'editor'],
            'placeholder_texts': [
                "write a comment",
                "add a comment", 
                "your comment",
                "leave a comment",
                "comment here",
                "tulis komentar",
                "tambah komentar"
            ]
        }
    }

def merge_configs(default_config, user_config):
    """Merge user config dengan default config"""
    try:
        merged = default_config.copy()
        
        for key, value in user_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key].update(value)
            else:
                merged[key] = value
        
        return merged
        
    except Exception as e:
        print(f"❌ Error merging configs: {e}")
        return default_config

def get_selectors(config, selector_type, fallback_selectors=None):
    """Get selectors dari config dengan fallback"""
    try:
        selectors_config = config.get('selectors', {})
        
        # Coba ambil dari config
        if selector_type in selectors_config:
            selector_data = selectors_config[selector_type]
            
            # Jika berupa string, convert ke list
            if isinstance(selector_data, str):
                return [selector_data]
            
            # Jika berupa list, return langsung
            elif isinstance(selector_data, list):
                return selector_data
            
            # Jika berupa dict, coba ambil 'selectors' key
            elif isinstance(selector_data, dict):
                if 'selectors' in selector_data:
                    return selector_data['selectors']
                else:
                    # Return semua values yang berupa list atau string
                    all_selectors = []
                    for value in selector_data.values():
                        if isinstance(value, list):
                            all_selectors.extend(value)
                        elif isinstance(value, str):
                            all_selectors.append(value)
                    return all_selectors
        
        # Fallback ke selectors yang diberikan
        if fallback_selectors:
            return fallback_selectors
        
        # Last resort fallback
        return []
        
    except Exception as e:
        print(f"❌ Error getting selectors for {selector_type}: {e}")
        return fallback_selectors or []

# ✅ TAMBAHAN: Function untuk validate config
def validate_config(config, logger=None):
    """Validate config structure"""
    try:
        required_sections = ['selectors', 'timeouts']
        missing_sections = []
        
        for section in required_sections:
            if section not in config:
                missing_sections.append(section)
        
        if missing_sections:
            if logger:
                logger.warning(f"⚠️ Missing config sections: {missing_sections}")
            return False
        
        # Validate timeouts are numeric
        timeouts = config.get('timeouts', {})
        for key, value in timeouts.items():
            if not isinstance(value, (int, float)):
                if logger:
                    logger.warning(f"⚠️ Invalid timeout value for {key}: {value}")
                return False
        
        if logger:
            logger.info(f"✅ Config validation passed")
        
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Config validation error: {e}")
        return False

# ✅ TAMBAHAN: Function untuk export current config
def export_current_config(output_file="current_wix_config.yaml", logger=None):
    """Export current config untuk debugging"""
    try:
        import yaml
        
        config = load_wix_config()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        if logger:
            logger.info(f"📤 Current config exported to {output_file}")
        
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Error exporting config: {e}")
        return False
    

# ✅ TAMBAHAN: Auto-update config saat import
try:
    update_config_with_delays()
except:
    pass  # Silent fail

__all__ = [
    # Core functions
    'lanjutkan_komentar',
    'cari_kotak_komentar_dengan_fallback', 
    'cari_kotak_komentar_beautifulsoup',
    'coba_selector_kotak_komentar',
    'coba_klik_kotak_komentar',
    'cari_kotak_komentar_aktif',
    
    # Comment processing
    'process_comment_with_links',
    'input_komentar_text',
    'smart_retry_input',
    'verify_comment_input',
    'validate_comment_format',
    
    # Link processing
    'process_links_in_element',
    'insert_direct_link_fallback',
    'input_fallback_text_with_links',
    'select_text_in_element',
    'click_link_button',
    'input_link_url',
    'click_toggle_switch',
    'save_link',
    'klik_tombol_underline',
    
    # Submit functions
    'klik_tombol_post',
    'cari_dan_klik_submit',
    
    # Utility functions
    'load_wix_config',
    'format_comment_for_log',
    'get_comment_element_info',
    'test_komentar_functionality',
    'test_all_functions',
    'cleanup_after_comment',
    'get_comment_status',
    'update_config_with_delays'
]