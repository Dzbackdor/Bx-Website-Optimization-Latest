import requests
import time
import os
import tempfile
import random
from selenium.webdriver.common.by import By

# ✅ SINGLE API KEY
OCR_API_KEY = "xxxxx"

def ensure_temp_audio_dir():
    """Ensure temp_audio directory exists"""
    try:
        current_dir = os.getcwd()
        temp_audio_dir = os.path.join(current_dir, "temp_audio")
        
        if not os.path.exists(temp_audio_dir):
            os.makedirs(temp_audio_dir)
        
        return temp_audio_dir
        
    except Exception as e:
        # Fallback to system temp if failed
        return tempfile.gettempdir()

def solve_secureimg_captcha(driver, logger):
    """Solve #secureimg CAPTCHA dengan enhanced OCR - Clean output"""
    try:
        logger.info("🖼️ Solving #secureimg CAPTCHA...")
        
        # 1. Capture image (SILENT)
        image_path = capture_secureimg(driver, logger)
        if not image_path:
            return False
        
        # 2. Enhanced OCR (SILENT PROCESSING)
        captcha_text = enhanced_ocr_with_preprocessing(image_path, logger)
        if not captcha_text:
            cleanup_file(image_path)
            return False
        
        # 3. Input ke securitycode field (SILENT)
        success = input_to_securitycode(driver, captcha_text, logger)
        
        # 4. Cleanup (SILENT)
        cleanup_file(image_path)
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Error solving #secureimg: {e}")
        return False

def capture_secureimg(driver, logger):
    """Capture #secureimg element ke temp_audio folder - Silent"""
    try:
        # Find #secureimg
        secureimg = driver.find_element(By.CSS_SELECTOR, "#secureimg")
        if not secureimg.is_displayed():
            logger.error("❌ #secureimg not visible")
            return None
        
        # ✅ SAVE TO temp_audio DIRECTORY (SILENT)
        temp_audio_dir = ensure_temp_audio_dir()
        filename = f"secureimg_{int(time.time())}.png"
        filepath = os.path.join(temp_audio_dir, filename)
        
        secureimg.screenshot(filepath)
        
        if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
            # ✅ HAPUS LOG CAPTURE - tidak perlu
            return filepath
        else:
            logger.error("❌ Screenshot failed")
            return None
        
    except Exception as e:
        logger.error(f"❌ Error capturing #secureimg: {e}")
        return None

def ocr_single_attempt(image_path, logger, attempt_type="default"):
    """Single OCR attempt dengan Engine 2 only - Silent"""
    try:
        with open(image_path, 'rb') as f:
            files = {'file': ('captcha.png', f, 'image/png')}
            data = {
                'apikey': OCR_API_KEY,
                'language': 'eng',
                'OCREngine': 2,  # ✅ FIXED ENGINE 2
                'scale': True
            }
            
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code != 200:
            # ✅ HAPUS LOG WARNING - silent processing
            return None
        
        result = response.json()
        if result.get('IsErroredOnProcessing', True):
            # ✅ HAPUS LOG ERROR - silent processing
            return None
        
        parsed_results = result.get('ParsedResults', [])
        if not parsed_results:
            # ✅ HAPUS LOG WARNING - silent processing
            return None
        
        raw_text = parsed_results[0].get('ParsedText', '').strip()
        clean_text = clean_captcha_text(raw_text)
        
        # ✅ HAPUS LOG OCR DETAIL - silent processing
        return clean_text
        
    except Exception as e:
        # ✅ HAPUS LOG ERROR - silent processing
        return None

def clean_captcha_text(text):
    """Clean OCR text dengan fix common mistakes"""
    if not text:
        return None
    
    # Remove whitespace and special chars
    import re
    clean = re.sub(r'[^a-zA-Z0-9]', '', text)
    
    # Analyze if text looks more like letters or numbers
    letter_count = sum(1 for c in clean if c.isalpha())
    number_count = sum(1 for c in clean if c.isdigit())
    
    # If mostly letters, prefer letter corrections
    if letter_count >= number_count:
        clean = clean.replace('0', 'o')  # 0 -> o
        clean = clean.replace('1', 'l')  # 1 -> l
        clean = clean.replace('5', 's')  # 5 -> s
        clean = clean.replace('6', 'g')  # 6 -> g
        clean = clean.replace('8', 'b')  # 8 -> b
    
    # Specific pattern fixes
    pattern_fixes = {
        'cobp1ums': 'cobplums',
        'c0bp1ums': 'cobplums',
        'cobplums': 'cobplums',
        'rigornil': 'rigornil',
        'rigor': 'rigor',
    }
    
    clean_lower = clean.lower()
    for wrong, correct in pattern_fixes.items():
        if clean_lower == wrong.lower():
            return correct
    
    return clean if len(clean) >= 3 else None

def enhanced_ocr_with_preprocessing(image_path, logger):
    """Enhanced OCR dengan Engine 2 Only - Silent processing"""
    try:
        # ✅ HAPUS LOG "Enhanced OCR processing" - silent
        
        results = []
        
        # ✅ ATTEMPT 1: Original image, Engine 2 (SILENT)
        result1 = ocr_single_attempt(image_path, logger, "original-engine2")
        if result1:
            results.append(result1)
        
        # ✅ ATTEMPT 2: Preprocessed image, Engine 2 (SILENT)
        processed_path = preprocess_image(image_path, logger)
        if processed_path:
            result2 = ocr_single_attempt(processed_path, logger, "processed-engine2")
            if result2:
                results.append(result2)
            
            cleanup_file(processed_path)
        
        if not results:
            logger.error("❌ All OCR attempts failed")
            return None
        
        # Choose best result (SILENT)
        best_result = choose_best_ocr_result(results, logger)
        return best_result
        
    except Exception as e:
        logger.error(f"❌ Enhanced OCR error: {e}")
        return None

def preprocess_image(image_path, logger):
    """Preprocess image untuk OCR yang lebih baik - Silent"""
    try:
        from PIL import Image, ImageEnhance
        
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize 3x larger
        width, height = img.size
        img = img.resize((width * 3, height * 3), Image.LANCZOS)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        # ✅ SAVE PROCESSED TO temp_audio (SILENT)
        temp_audio_dir = ensure_temp_audio_dir()
        filename = f"secureimg_processed_{int(time.time())}.png"
        processed_path = os.path.join(temp_audio_dir, filename)
        
        img.save(processed_path, 'PNG')
        
        # ✅ HAPUS LOG PREPROCESSING - silent
        return processed_path
        
    except Exception as e:
        # ✅ HAPUS LOG WARNING - silent
        return None

def choose_best_ocr_result(results, logger):
    """Choose best OCR result dari 2 Engine 2 attempts - Silent"""
    try:
        if len(results) == 1:
            # ✅ HAPUS LOG - silent
            return results[0]
        
        # Remove duplicates first
        unique_results = list(set(results))
        
        if len(unique_results) == 1:
            # ✅ HAPUS LOG - silent
            return unique_results[0]
        
        # ✅ SIMPLIFIED SCORING UNTUK 2 RESULTS (SILENT)
        scored_results = []
        
        for result in unique_results:
            score = 0
            
            # Length score (4-8 chars typical for CAPTCHA)
            if 4 <= len(result) <= 8:
                score += 10
            elif len(result) < 4:
                score -= 5
            
            # Letter ratio score
            letter_count = sum(1 for c in result if c.isalpha())
            letter_ratio = letter_count / len(result) if result else 0
            if letter_ratio > 0.6:
                score += 15
            
            # Known good patterns
            good_patterns = ['cobplums', 'plums', 'cob', 'rigornil', 'rigor']
            if any(pattern in result.lower() for pattern in good_patterns):
                score += 20
            
            # Avoid obviously wrong patterns
            if result.count('1') > 2 or result.count('0') > 2:
                score -= 10
            
            scored_results.append((result, score))
        
        # Sort by score
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        best_result = scored_results[0][0]
        
        # ✅ HAPUS SEMUA LOG COMPARISON - silent processing
        return best_result
        
    except Exception as e:
        return results[0] if results else None

def input_to_securitycode(driver, captcha_text, logger):
    """Input ke securitycode field - Silent"""
    try:
        # ✅ HAPUS LOG INPUT - silent
        
        securitycode = driver.find_element(By.CSS_SELECTOR, 'input[name="securitycode"]')
        
        if not securitycode.is_displayed():
            logger.error("❌ securitycode field not visible")
            return False
        
        # Clear and input (SILENT)
        securitycode.clear()
        time.sleep(0.2)
        
        # Type character by character (SILENT)
        for char in captcha_text:
            securitycode.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        # Verify (SILENT)
        if securitycode.get_attribute('value') == captcha_text:
            # ✅ HAPUS LOG SUCCESS - akan di-handle di level atas
            return True
        else:
            logger.error("❌ Input verification failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error inputting answer: {e}")
        return False

def cleanup_file(filepath):
    """Delete temp file dan cleanup temp_audio jika kosong - Silent"""
    try:
        if filepath and os.path.exists(filepath):
            filename = os.path.basename(filepath)
            os.remove(filepath)
            # ✅ HAPUS LOG DELETE - silent
            
            # ✅ CLEANUP temp_audio FOLDER JIKA KOSONG (SILENT)
            temp_audio_dir = os.path.dirname(filepath)
            if os.path.basename(temp_audio_dir) == "temp_audio":
                try:
                    # Check if only secureimg files left
                    remaining_files = os.listdir(temp_audio_dir)
                    secureimg_files = [f for f in remaining_files if f.startswith('secureimg_')]
                    
                    # If no secureimg files left, try to remove directory
                    if not secureimg_files:
                        if not remaining_files:  # Completely empty
                            os.rmdir(temp_audio_dir)
                            # ✅ HAPUS LOG REMOVE DIRECTORY - silent
                except:
                    pass  # Directory not empty or has other files
            
    except Exception as e:
        # ✅ HAPUS LOG ERROR - silent
        pass

def detect_and_solve_secureimg(driver, logger):
    """Detect dan solve #secureimg CAPTCHA"""
    try:
        secureimg = driver.find_element(By.CSS_SELECTOR, "#secureimg")
        securitycode = driver.find_element(By.CSS_SELECTOR, 'input[name="securitycode"]')
        
        if secureimg.is_displayed() and securitycode.is_displayed():
            logger.info("🖼️ #secureimg CAPTCHA detected")
            return solve_secureimg_captcha(driver, logger)
        else:
            return False
        
    except:
        return False
