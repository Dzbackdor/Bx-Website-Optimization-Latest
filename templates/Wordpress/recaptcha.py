import time
import random
import os
import json  
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from colorama import Fore, init
from selenium.webdriver.common.action_chains import ActionChains


# Initialize Colorama
init(autoreset=True)

# Colors for terminal text
B = Fore.BLUE
W = Fore.WHITE
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW

# ✅ IMPORT API CONFIG
try:
    from api_config import WIT_API_TOKEN, ASSEMBLYAI_API_KEY, AUDIO_DOWNLOAD_TIMEOUT, TRANSCRIPTION_TIMEOUT
    # print(f"{G}✅ API config loaded successfully{W}")
except ImportError:
    print(f"{Y}⚠️ api_config.py not found, using default values{W}")
    WIT_API_TOKEN = "YOUR_WIT_AI_TOKEN_HERE"
    ASSEMBLYAI_API_KEY = "YOUR_ASSEMBLYAI_KEY_HERE"
    AUDIO_DOWNLOAD_TIMEOUT = 30
    TRANSCRIPTION_TIMEOUT = 60


def transcribe_audio_with_wit(audio_file_path):
    """
    Transkripsi audio menggunakan Wit.ai API (Silent version)
    """
    try:
        if not WIT_API_TOKEN or WIT_API_TOKEN == "YOUR_WIT_AI_TOKEN_HERE":
            return None
        
        # ✅ HAPUS SEMUA LOG VERBOSE
        if not os.path.exists(audio_file_path):
            return None
        
        file_size = os.path.getsize(audio_file_path)
        if file_size == 0:
            return None
        
        headers = {
            'Authorization': f'Bearer {WIT_API_TOKEN}',
            'Content-Type': 'audio/mpeg3'
        }
        
        try:
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                
                if not audio_data:
                    return None
                
                response = requests.post(
                    'https://api.wit.ai/speech',
                    headers=headers,
                    data=audio_data,
                    timeout=30
                )
                
                # ✅ HAPUS LOG RESPONSE DETAIL
                if response.status_code != 200:
                    return None

                # Parse response (SILENT)
                json_objects = []
                current_object = []

                for line in response.text.splitlines():
                    line = line.strip()
                    if line.startswith("{"):
                        current_object = [line]
                    elif line.endswith("}"):
                        current_object.append(line)
                        json_string = "\n".join(current_object)
                        try:
                            json_objects.append(json.loads(json_string))
                        except json.JSONDecodeError:
                            continue
                    elif current_object:
                        current_object.append(line)

                # Find final text (SILENT)
                final_text = None
                for obj in json_objects:
                    if obj.get("type") == "FINAL_UNDERSTANDING":
                        final_text = obj.get("text")
                        break

                if not final_text:
                    try:
                        if json_objects and "text" in json_objects[0]:
                            final_text = json_objects[0]["text"]
                        elif response.text and "{" in response.text:
                            json_response = json.loads(response.text)
                            if "text" in json_response:
                                final_text = json_response["text"]
                    except:
                        pass
                    
                    if not final_text:
                        return None

                if final_text and final_text.strip():
                    # ✅ HAPUS LOG SUCCESS - akan di-handle di solve_recaptcha_v2
                    return final_text.strip()
                else:
                    return None
                    
        except Exception as e:
            return None
            
    except Exception as e:
        return None

def transcribe_audio_with_assemblyai(audio_file_path):
    """
    Transkripsi audio menggunakan AssemblyAI API
    """
    try:
        if not ASSEMBLYAI_API_KEY or ASSEMBLYAI_API_KEY == "YOUR_ASSEMBLYAI_KEY_HERE":
            print(f"{Y}⚠️ AssemblyAI API key tidak dikonfigurasi{W}")
            return None
        
        print(f"{B}🎤 Mencoba transkripsi dengan AssemblyAI...{W}")
        
        # Step 1: Upload file
        headers = {'authorization': ASSEMBLYAI_API_KEY}
        
        with open(audio_file_path, 'rb') as audio_file:
            upload_response = requests.post(
                'https://api.assemblyai.com/v2/upload',
                headers=headers,
                files={'file': audio_file},
                timeout=60
            )
        
        if upload_response.status_code != 200:
            print(f"{R}❌ AssemblyAI upload failed: {upload_response.status_code}{W}")
            return None
        
        audio_url = upload_response.json()['upload_url']
        print(f"{G}✅ File uploaded ke AssemblyAI{W}")
        
        # Step 2: Request transcription
        transcript_request = {
            'audio_url': audio_url,
            'language_code': 'en'
        }
        
        transcript_response = requests.post(
            'https://api.assemblyai.com/v2/transcript',
            headers=headers,
            json=transcript_request,
            timeout=30
        )
        
        if transcript_response.status_code != 200:
            print(f"{R}❌ AssemblyAI transcript request failed{W}")
            return None
        
        transcript_id = transcript_response.json()['id']
        print(f"{B}🔄 Menunggu hasil transkripsi AssemblyAI...{W}")
        
        # Step 3: Poll for result
        max_polls = 30
        for poll in range(max_polls):
            result_response = requests.get(
                f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
                headers=headers,
                timeout=30
            )
            
            if result_response.status_code == 200:
                result = result_response.json()
                status = result['status']
                
                if status == 'completed':
                    transcription = result.get('text', '').strip()
                    if transcription:
                        print(f"{G}✅ Transkripsi AssemblyAI berhasil: {transcription}{W}")
                        return transcription
                    else:
                        print(f"{R}❌ AssemblyAI tidak mengembalikan text{W}")
                        return None
                elif status == 'error':
                    print(f"{R}❌ AssemblyAI transcription error{W}")
                    return None
                else:
                    print(f"{Y}⏳ AssemblyAI status: {status} (poll {poll+1}/{max_polls}){W}")
                    time.sleep(2)
            else:
                print(f"{R}❌ AssemblyAI polling error: {result_response.status_code}{W}")
                return None
        
        print(f"{R}❌ AssemblyAI timeout setelah {max_polls} polls{W}")
        return None
        
    except Exception as e:
        print(f"{R}❌ Error AssemblyAI transcription: {e}{W}")
        return None

def solve_recaptcha_v2(driver, logger):
    """
    Solve reCAPTCHA v2 dengan log yang bersih
    """
    try:
        logger.info("🤖 Starting reCAPTCHA v2 solving process...")
        
        # ✅ HAPUS LOG DEBUG IFRAME - fungsi tetap jalan
        # logger.info("🔍 === DEBUGGING IFRAMES ===")
        # logger.info(f"📋 Total iframes: {len(all_iframes)}")
        
        all_iframes = driver.find_elements(By.TAG_NAME, "iframe")
        
        recaptcha_count = 0
        for i, iframe in enumerate(all_iframes):
            try:
                src = iframe.get_attribute("src") or "No src"
                if "recaptcha" in src.lower():
                    recaptcha_count += 1
                    is_displayed = iframe.is_displayed()
                    
                    # ✅ HAPUS LOG VERBOSE
                    # logger.info(f"🎯 reCAPTCHA iframe {recaptcha_count}: displayed={is_displayed}")
                    # logger.info(f"    src: {src[:100]}...")
                    
                    if not is_displayed:
                        # ✅ HAPUS LOG
                        # logger.info("🔧 Showing hidden iframe...")
                        driver.execute_script("""
                            arguments[0].style.display = 'block';
                            arguments[0].style.visibility = 'visible';
                            arguments[0].style.opacity = '1';
                        """, iframe)
                        time.sleep(1)
                        # logger.info(f"    After show: {iframe.is_displayed()}")
            except Exception as e:
                # logger.warning(f"Error processing iframe {i}: {e}")
                pass
        
        # ✅ HAPUS LOG
        # logger.info(f"📋 Found {recaptcha_count} reCAPTCHA iframes")
        
        # Cari main iframe
        main_iframe = None
        main_selectors = [
            'iframe[src*="recaptcha"][src*="anchor"]',
            'iframe[src*="recaptcha/api2/anchor"]',
            'iframe[title*="reCAPTCHA"]'
        ]
        
        for selector in main_selectors:
            try:
                iframes = driver.find_elements(By.CSS_SELECTOR, selector)
                for iframe in iframes:
                    if iframe.is_displayed():
                        main_iframe = iframe
                        # ✅ HAPUS LOG
                        # logger.info(f"✅ Main iframe found: {selector}")
                        break
                if main_iframe:
                    break
            except Exception as e:
                # logger.warning(f"Error with selector {selector}: {e}")
                pass
        
        if not main_iframe:
            logger.error("❌ Main iframe tidak ditemukan")
            return False
        
        # Klik checkbox
        try:
            driver.switch_to.frame(main_iframe)
            # ✅ HAPUS LOG
            # logger.info("🔄 Switched to main iframe")
            
            checkbox_selectors = ['.recaptcha-checkbox-border', '.recaptcha-checkbox', '#recaptcha-anchor']
            checkbox = None
            
            for selector in checkbox_selectors:
                try:
                    checkbox = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if checkbox.is_displayed():
                        # ✅ HAPUS LOG
                        # logger.info(f"✅ Checkbox found: {selector}")
                        break
                except:
                    continue
            
            if not checkbox:
                logger.error("❌ Checkbox tidak ditemukan")
                driver.switch_to.default_content()
                return False
            
            checkbox.click()
            # ✅ HAPUS LOG
            # logger.info("✅ Checkbox clicked")
            time.sleep(3)
            driver.switch_to.default_content()
            
        except Exception as e:
            logger.error(f"❌ Error clicking checkbox: {e}")
            driver.switch_to.default_content()
            return False
        
        # Tunggu challenge iframe
        # ✅ HAPUS LOG
        # logger.info("⏳ Waiting for challenge iframe...")
        challenge_iframe = None
        
        for wait_time in range(10):
            try:
                challenge_iframes = driver.find_elements(By.CSS_SELECTOR, 'iframe[src*="bframe"]')
                for iframe in challenge_iframes:
                    if iframe.is_displayed():
                        challenge_iframe = iframe
                        # ✅ HAPUS LOG
                        # logger.info(f"✅ Challenge iframe found after {wait_time + 1}s")
                        break
                if challenge_iframe:
                    break
                time.sleep(1)
            except:
                time.sleep(1)
        
        if not challenge_iframe:
            # ✅ HAPUS LOG
            # logger.info("✅ No challenge - mungkin sudah solved")
            return True
        
        # Handle audio challenge
        try:
            driver.switch_to.frame(challenge_iframe)
            # ✅ HAPUS LOG
            # logger.info("🔄 Switched to challenge iframe")
            time.sleep(3)
            
            buttons = driver.find_elements(By.TAG_NAME, "button")
            # ✅ HAPUS LOG
            # logger.info(f"📋 Found {len(buttons)} buttons in challenge")
            
            audio_button = None
            try:
                audio_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "recaptcha-audio-button"))
                )
                # ✅ HAPUS LOG
                # logger.info("✅ Audio button found")
            except:
                logger.error("❌ Audio button tidak ditemukan")
                driver.switch_to.default_content()
                return False
            
            audio_button.click()
            # ✅ HAPUS LOG
            # logger.info("✅ Audio button clicked")
            time.sleep(5)
            
            # ✅ HAPUS LOG
            # logger.info("🎵 Processing audio challenge...")
            
            if process_audio_challenge_complete(driver, logger):
                # ✅ HAPUS LOG
                # logger.info("✅ Audio challenge berhasil")
                driver.switch_to.default_content()
                return True
            else:
                logger.error("❌ Audio challenge gagal")
                driver.switch_to.default_content()
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in audio challenge: {e}")
            driver.switch_to.default_content()
            return False
        
    except Exception as e:
        logger.error(f"❌ Error solving reCAPTCHA: {e}")
        try:
            driver.switch_to.default_content()
        except:
            pass
        return False

def process_audio_challenge_complete(driver, logger):
    """
    Proses lengkap audio challenge - log bersih
    """
    try:
        # ✅ HAPUS LOG
        # logger.info("🎵 Processing audio challenge...")
        
        try:
            audio_source = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "audio-source"))
            )
            # ✅ HAPUS LOG
            # logger.info("✅ Audio source found")
        except TimeoutException:
            logger.error("❌ Audio source tidak muncul dalam 15 detik")
            return False
        
        audio_url = audio_source.get_attribute("src")
        if not audio_url:
            logger.error("❌ Audio URL tidak ditemukan")
            return False
        
        # ✅ HAPUS LOG
        # logger.info(f"✅ Audio URL obtained: {audio_url[:50]}...")
        
        # Download audio
        try:
            temp_dir = "temp_audio"
            os.makedirs(temp_dir, exist_ok=True)
            
            audio_filename = f"recaptcha_audio_{int(time.time())}.mp3"
            audio_filepath = os.path.join(temp_dir, audio_filename)
            
            response = requests.get(audio_url, timeout=30)
            response.raise_for_status()
            
            with open(audio_filepath, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            # ✅ HAPUS LOG
            # logger.info(f"✅ Audio downloaded: {file_size} bytes")
            
        except Exception as e:
            logger.error(f"❌ Error downloading audio: {e}")
            return False
        
        # Transkripsi audio
        transcription = None
        
        # Coba Wit.ai dulu
        if WIT_API_TOKEN and WIT_API_TOKEN != "YOUR_WIT_AI_TOKEN_HERE":
            # ✅ HAPUS LOG
            # logger.info("🎤 Trying Wit.ai transcription...")
            transcription = transcribe_audio_with_wit(audio_filepath)
            if transcription:
                # ✅ HAPUS LOG - akan ditampilkan di level atas
                # logger.info(f"✅ Wit.ai transcription: '{transcription}'")
                pass
        
        # Coba AssemblyAI jika Wit.ai gagal
        if not transcription and ASSEMBLYAI_API_KEY and ASSEMBLYAI_API_KEY != "YOUR_ASSEMBLYAI_KEY_HERE":
            # ✅ HAPUS LOG
            # logger.info("🎤 Trying AssemblyAI transcription...")
            transcription = transcribe_audio_with_assemblyai(audio_filepath)
            if transcription:
                # ✅ HAPUS LOG
                # logger.info(f"✅ AssemblyAI transcription: '{transcription}'")
                pass
        
        # Cleanup file
        try:
            os.remove(audio_filepath)
        except:
            pass
        
        if not transcription:
            logger.error("❌ Semua API transkripsi gagal")
            return False
        
        return submit_audio_answer_complete(driver, transcription, logger)
        
    except Exception as e:
        logger.error(f"❌ Error processing audio challenge: {e}")
        return False



def submit_audio_answer_complete(driver, transcription, logger):
    """Submit jawaban audio - log bersih"""
    try:
        # ✅ HAPUS LOG
        # logger.info("⌨️ Submitting audio answer...")
        
        input_selectors = [
            '#audio-response',
            'input[id="audio-response"]',
            'input[name="audio-response"]',
            'input[type="text"]'
        ]
        
        audio_input = None
        for selector in input_selectors:
            try:
                audio_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if audio_input.is_displayed():
                    # ✅ HAPUS LOG
                    # logger.info(f"✅ Audio input found: {selector}")
                    break
            except:
                continue
        
        if not audio_input:
            logger.error("❌ Audio input field tidak ditemukan")
            return False
        
        # Isi input
        audio_input.clear()
        time.sleep(1)
        
        for char in transcription:
            audio_input.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        
        time.sleep(2)
        # ✅ HAPUS LOG
        # logger.info("✅ Answer typed successfully")
        
        # Cari verify button
        verify_selectors = [
            '#recaptcha-verify-button',
            'button[id="recaptcha-verify-button"]',
            'button[type="submit"]',
            '.rc-button-default'
        ]
        
        verify_button = None
        for selector in verify_selectors:
            try:
                verify_button = driver.find_element(By.CSS_SELECTOR, selector)
                if verify_button.is_displayed() and verify_button.is_enabled():
                    # ✅ HAPUS LOG
                    # logger.info(f"✅ Verify button found: {selector}")
                    break
            except:
                continue
        
        if not verify_button:
            logger.error("❌ Verify button tidak ditemukan")
            return False
        
        verify_button.click()
        # ✅ HAPUS LOG
        # logger.info("✅ Verify button clicked")
        time.sleep(5)
        
        return check_audio_result(driver, logger)
        
    except Exception as e:
        logger.error(f"❌ Error submitting answer: {e}")
        return False


def check_audio_result(driver, logger):
    """Cek hasil - log bersih"""
    try:
        # ✅ HAPUS LOG
        # logger.info("🔍 Checking audio result...")
        
        error_selectors = [
            '.rc-audiochallenge-error-message',
            '[class*="error"]',
            '[class*="incorrect"]'
        ]
        
        for selector in error_selectors:
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for error_element in error_elements:
                    if error_element.is_displayed() and error_element.text.strip():
                        logger.warning(f"⚠️ Error detected: {error_element.text}")
                        return False
            except:
                continue
        
        # ✅ HAPUS LOG
        # logger.info("✅ No error messages found")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking result: {e}")
        return False