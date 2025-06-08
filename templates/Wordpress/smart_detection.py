import time
import json
import os
import re
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.common.by import By
from datetime import datetime
from colorama import Fore, init


# Initialize Colorama
init(autoreset=True)

# Colors for terminal text
B = Fore.BLUE
W = Fore.WHITE
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW


class SmartSuccessDetector:
    """Smart auto-detection untuk success indicators"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.learning_data_file = "cache/success_learning_data.json"
        self.domain_patterns_file = "cache/domain_success_patterns.json"
        self.load_learning_data()
    

    def load_learning_data(self):
        """Load learning data tanpa log"""
        try:
            if os.path.exists(self.learning_file):
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    self.learning_data = json.load(f)
                    # ✅ HAPUS LOG "Loaded learning data"
            
            if os.path.exists(self.domain_patterns_file):
                with open(self.domain_patterns_file, 'r', encoding='utf-8') as f:
                    self.domain_patterns = json.load(f)
                    # ✅ HAPUS LOG "Loaded domain patterns"
                    
        except Exception as e:
            # ✅ HAPUS LOG ERROR - tidak perlu
            pass

    def save_learning_data(self):
        """Save learning data tanpa log"""
        try:
            # Save learning data
            os.makedirs(os.path.dirname(self.learning_file), exist_ok=True)
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, indent=2, ensure_ascii=False)
            
            # Save domain patterns  
            with open(self.domain_patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.domain_patterns, f, indent=2, ensure_ascii=False)
            
            # ✅ HAPUS SEMUA LOG SAVING
            
        except Exception as e:
            # ✅ HAPUS LOG ERROR - tidak perlu
            pass

    
    def capture_page_state(self, driver):
        """Capture comprehensive page state"""
        try:
            state = {
                'timestamp': time.time(),
                'url': driver.current_url,
                'title': driver.title,
                'page_source_length': len(driver.page_source),
                'visible_text': self.get_visible_text(driver),
                'form_count': len(driver.find_elements(By.TAG_NAME, "form")),
                'input_count': len(driver.find_elements(By.TAG_NAME, "input")),
                'button_count': len(driver.find_elements(By.TAG_NAME, "button")),
                'alert_elements': self.get_alert_elements(driver),
                'message_elements': self.get_message_elements(driver),
                'url_hash': driver.current_url.split('#')[-1] if '#' in driver.current_url else '',
                'url_params': self.extract_url_params(driver.current_url)
            }
            
            return state
            
        except Exception as e:
            self.bot.logger.warning(f"⚠️ Error capturing page state: {e}")
            return {
                'timestamp': time.time(),
                'url': driver.current_url,
                'error': str(e)
            }
    
    def get_visible_text(self, driver):
        """Get visible text dari halaman"""
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            return body.text.lower()
        except:
            return ""
    
    def get_alert_elements(self, driver):
        """Get alert/notification elements"""
        alert_selectors = [
            '.alert', '.notification', '.message', '.notice',
            '.success', '.error', '.warning', '.info',
            '[class*="alert"]', '[class*="message"]', '[class*="notification"]',
            '[class*="success"]', '[class*="error"]', '[class*="warning"]'
        ]
        
        alerts = []
        for selector in alert_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        alerts.append({
                            'selector': selector,
                            'text': element.text.lower(),
                            'class': element.get_attribute('class'),
                            'id': element.get_attribute('id')
                        })
            except:
                continue
        
        return alerts
    
    def get_message_elements(self, driver):
        """Get potential message elements"""
        message_selectors = [
            '.comment-status', '.comment-message', '.form-message',
            '.submit-message', '.post-message', '.feedback',
            '[id*="message"]', '[id*="status"]', '[id*="feedback"]'
        ]
        
        messages = []
        for selector in message_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.text.strip():
                        messages.append({
                            'selector': selector,
                            'text': element.text.lower(),
                            'class': element.get_attribute('class')
                        })
            except:
                continue
        
        return messages
    
    def extract_url_params(self, url):
        """Extract URL parameters"""
        try:
            parsed = urlparse(url)
            return parse_qs(parsed.query)
        except:
            return {}
    

    def analyze_changes(self, before_state, after_state):
        """Analisis perubahan tanpa log detail"""
        try:
            changes = {
                'url_changed': before_state['url'] != after_state['url'],
                'new_alerts': [],
                'new_messages': [],
                'success_score': 0,
                'confidence': 0,
                'text_changes': {}
            }
            
            # ✅ HAPUS SEMUA LOG URL CHANGES
            
            # URL Analysis (tanpa log)
            if changes['url_changed']:
                new_url = after_state['url']
                url_indicators = ['comment', 'success', 'thank', 'posted', 'submitted']
                
                for indicator in url_indicators:
                    if indicator in new_url.lower():
                        changes['success_score'] += 25
                        # ✅ HAPUS LOG URL INDICATOR
                        break
            
            # Alert Analysis (tanpa log)
            before_alerts = set(before_state.get('alerts', []))
            after_alerts = set(after_state.get('alerts', []))
            new_alerts = after_alerts - before_alerts
            
            for alert in new_alerts:
                # ✅ HAPUS LOG NEW ALERT
                changes['new_alerts'].append({
                    'text': alert,
                    'score': self.calculate_alert_score(alert)
                })
            
            # ✅ HAPUS SEMUA LOG LAINNYA
            
            # Calculate final confidence
            changes['confidence'] = min(changes['success_score'], 100)
            
            return changes
            
        except Exception as e:
            self.bot.logger.error(f"❌ Error analyzing changes: {e}")
            return {'success_score': 50, 'confidence': 50}

    
    def analyze_url_success_indicators(self, before_url, after_url):
        """Analisis URL untuk success indicators"""
        score = 0
        
        # Success indicators dalam URL
        success_indicators = {
            'comment': 25,      # #comment-123, ?comment=submitted
            'success': 20,      # ?success=1, ?status=success
            'submitted': 20,    # ?submitted=true
            'thank': 15,        # ?thank=you
            'moderation': 15,   # ?moderation=pending
            'pending': 15,      # ?pending=approval
            'approved': 20,     # ?approved=1
            'confirm': 15,      # ?confirm=1
            'msg': 10,          # ?msg=success
            'status': 10        # ?status=ok
        }
        
        after_url_lower = after_url.lower()
        for indicator, points in success_indicators.items():
            if indicator in after_url_lower and indicator not in before_url.lower():
                score += points
                self.bot.logger.info(f"✅ URL indicator '{indicator}': +{points} points")
        
        return score
    
    def score_alert_element(self, alert):
        """Score alert element berdasarkan content"""
        text = alert['text'].lower()
        class_name = (alert.get('class') or '').lower()
        
        score = 0
        
        # Positive indicators
        positive_keywords = {
            'success': 30, 'submitted': 25, 'thank': 20, 'received': 20,
            'posted': 20, 'approved': 25, 'moderation': 15, 'pending': 15,
            'confirm': 15, 'complete': 20
        }
        
        for keyword, points in positive_keywords.items():
            if keyword in text:
                score += points
        
        # Class-based scoring
        if 'success' in class_name:
            score += 20
        elif 'error' in class_name:
            score -= 30
        elif 'warning' in class_name:
            score -= 10
        
        # Negative indicators
        negative_keywords = ['error', 'failed', 'invalid', 'required', 'missing']
        for keyword in negative_keywords:
            if keyword in text:
                score -= 25
        
        return max(0, score)
    
    def score_message_element(self, message):
        """Score message element"""
        text = message['text'].lower()
        
        score = 0
        
        # Success phrases
        success_phrases = {
            'comment submitted': 30,
            'awaiting moderation': 25,
            'thank you': 20,
            'successfully posted': 30,
            'comment received': 25,
            'under review': 15,
            'will be published': 20
        }
        
        for phrase, points in success_phrases.items():
            if phrase in text:
                score += points
        
        return score
    
    def analyze_text_changes(self, before_text, after_text):
        """Analisis perubahan text content"""
        before_words = set(before_text.split())
        after_words = set(after_text.split())
        
        new_words = after_words - before_words
        
        # Score new words
        score = 0
        relevant_words = []
        
        success_keywords = {
            'submitted': 20, 'success': 20, 'thank': 15, 'moderation': 15,
            'pending': 15, 'approved': 20, 'received': 15, 'posted': 15,
            'review': 10, 'confirm': 15
        }
        
        for word in new_words:
            for keyword, points in success_keywords.items():
                if keyword in word.lower():
                    score += points
                    relevant_words.append(word)
        
        return {
            'score': score,
            'new_words_count': len(new_words),
            'relevant_words': relevant_words
        }
    
    def make_final_decision(self, changes):
        """Make final decision tanpa log detail"""
        score = changes['success_score']
        confidence = changes['confidence']
        
        # ✅ HAPUS SEMUA LOG DECISION PROCESS
        
        # Decision thresholds (tanpa log)
        if score >= 50:
            return True
        elif score >= 30:
            return True
        elif score >= 15:
            return True
        else:
            return False


    def save_detection_result(self, domain, changes, is_success):
        """Save detection result tanpa log"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Save to learning data (tanpa log)
            if domain not in self.learning_data:
                self.learning_data[domain] = []
            
            detection_entry = {
                'timestamp': timestamp,
                'success_score': changes['success_score'],
                'confidence': changes['confidence'],
                'is_success': is_success,
                'url_changed': changes['url_changed'],
                'new_alerts_count': len(changes['new_alerts']),
                'new_messages_count': len(changes['new_messages']),
                'new_url_hash': changes.get('new_url_hash', ''),
                'new_url_params': changes.get('new_url_params', {}),
                'text_changes_score': changes.get('text_changes', {}).get('score', 0)
            }
            
            self.learning_data[domain].append(detection_entry)
            
            # Keep only last 50 entries per domain
            if len(self.learning_data[domain]) > 50:
                self.learning_data[domain] = self.learning_data[domain][-50:]
            
            # Update domain patterns (tanpa log)
            self.update_domain_patterns(domain, changes, is_success)
            
            # Save to file (tanpa log)
            self.save_learning_data()
            
            # ✅ HAPUS SEMUA LOG
            
        except Exception as e:
            # ✅ HAPUS LOG ERROR
            pass

    
    def update_domain_patterns(self, domain, changes, is_success):
        """✅ TAMBAH METHOD INI - Update domain-specific patterns"""
        try:
            if domain not in self.domain_patterns:
                self.domain_patterns[domain] = {
                    'url_patterns': [],
                    'text_patterns': [],
                    'alert_patterns': [],
                    'success_count': 0,
                    'total_count': 0
                }
            
            patterns = self.domain_patterns[domain]
            patterns['total_count'] += 1
            
            if is_success:
                patterns['success_count'] += 1
                
                # Learn URL hash patterns
                new_hash = changes.get('new_url_hash', '')
                if new_hash and new_hash not in patterns['url_patterns']:
                    patterns['url_patterns'].append(new_hash)
                    self.bot.logger.info(f"📚 Learned URL pattern: {new_hash}")
                
                # Learn text patterns
                relevant_words = changes.get('text_changes', {}).get('relevant_words', [])
                for word in relevant_words:
                    if word.lower() not in patterns['text_patterns']:
                        patterns['text_patterns'].append(word.lower())
                        self.bot.logger.info(f"📚 Learned text pattern: {word}")
                
                # Learn alert patterns
                for alert in changes.get('new_alerts', []):
                    alert_text = alert['text'][:30]  # First 30 chars
                    if alert_text not in patterns['alert_patterns']:
                        patterns['alert_patterns'].append(alert_text)
                        self.bot.logger.info(f"📚 Learned alert pattern: {alert_text}")
            
            # Calculate success rate
            success_rate = patterns['success_count'] / patterns['total_count'] * 100
            self.bot.logger.info(f"📊 Domain {domain} success rate: {success_rate:.1f}% ({patterns['success_count']}/{patterns['total_count']})")
            
        except Exception as e:
            self.bot.logger.error(f"❌ Error updating domain patterns: {e}")
    

    def detect_success(self, driver, before_state, wait_time=5):
        """Deteksi success dengan output minimal"""
        try:
            # ✅ TUNGGU STABILISASI
            time.sleep(wait_time)
            
            # ✅ AMBIL CURRENT URL DENGAN ERROR HANDLING
            try:
                current_url = driver.current_url.lower()
                final_url = driver.current_url  # Original case untuk return
            except Exception as e:
                self.bot.logger.warning(f"⚠️ Error getting URL: {e}")
                # Fallback: lanjut detection normal
                current_url = ""
                final_url = ""
            
            # ❌ CEK FAILED URL PATTERNS (hanya jika URL berhasil diambil)
            if current_url:
                failed_patterns = [
                    'wp-comments-post.php',
                    'comment-error', 
                    'error=',
                    'failed=1'
                ]
                
                for pattern in failed_patterns:
                    if pattern in current_url:
                        self.bot.logger.error(f"❌ URL mengandung '{pattern}' - FAILED")
                        # self.bot.logger.error(f"❌  Decision: FAILED")
                        # self.bot.logger.error(f"🎯 Smart detection: FAILED") 
                        self.bot.logger.error(f"❌ Komentar gagal")
                        return False, {
                            'reason': f'Failed URL pattern: {pattern}',
                            'final_url': final_url,
                            'success_score': 0,
                            'confidence': 100
                        }
            # Capture state setelah submit
            after_state = self.capture_page_state(driver)
            
            # Analisis perubahan
            changes = self.analyze_changes(before_state, after_state)
            
            # ✅ HAPUS SEMUA LOG DETAIL ANALYSIS
            
            # Make decision
            is_success = self.make_final_decision(changes)
            
            # ✅ HANYA LOG KEPUTUSAN AKHIR
            if is_success:
                self.bot.logger.info("✅ Decision: SUCCESS")
            else:
                self.bot.logger.info("❌ Decision: FAILED")
            
            # Save untuk learning (tanpa log)
            domain = urlparse(driver.current_url).netloc.lower()
            self.save_detection_result(domain, changes, is_success)
            
            return is_success, changes
            
        except Exception as e:
            self.bot.logger.error(f"❌ Error in smart detection: {e}")
            return True, {}  # Default success jika error

    
    def get_domain_stats(self, domain):
        """✅ TAMBAH METHOD INI - Get statistics untuk domain"""
        try:
            if domain not in self.domain_patterns:
                return {
                    'success_rate': 0,
                    'total_attempts': 0,
                    'learned_patterns': 0
                }
            
            patterns = self.domain_patterns[domain]
            total_patterns = (
                len(patterns.get('url_patterns', [])) +
                len(patterns.get('text_patterns', [])) +
                len(patterns.get('alert_patterns', []))
            )
            
            success_rate = 0
            if patterns.get('total_count', 0) > 0:
                success_rate = patterns['success_count'] / patterns['total_count'] * 100
            
            return {
                'success_rate': success_rate,
                'total_attempts': patterns.get('total_count', 0),
                'successful_attempts': patterns.get('success_count', 0),
                'learned_patterns': total_patterns,
                'url_patterns': len(patterns.get('url_patterns', [])),
                'text_patterns': len(patterns.get('text_patterns', [])),
                'alert_patterns': len(patterns.get('alert_patterns', []))
            }
            
        except Exception as e:
            self.bot.logger.error(f"❌ Error getting domain stats: {e}")
            return {'error': str(e)}
    

    def print_domain_stats(self, domain):
        """Print statistics tanpa log detail"""
        try:
            stats = self.get_domain_stats(domain)
            
            if 'error' in stats:
                return
            
            # ✅ HAPUS SEMUA LOG STATS
            
        except Exception as e:
            pass

    
    def reset_domain_learning(self, domain):
        """✅ TAMBAH METHOD INI - Reset learning data untuk domain"""
        try:
            if domain in self.learning_data:
                del self.learning_data[domain]
                self.bot.logger.info(f"🗑️ Cleared learning data for {domain}")
            
            if domain in self.domain_patterns:
                del self.domain_patterns[domain]
                self.bot.logger.info(f"🗑️ Cleared domain patterns for {domain}")
            
            self.save_learning_data()
            self.bot.logger.info(f"✅ Reset complete for {domain}")
            
        except Exception as e:
            self.bot.logger.error(f"❌ Error resetting domain learning: {e}")
    
    def export_learning_data(self, output_file="learning_data_export.json"):
        """✅ TAMBAH METHOD INI - Export learning data untuk backup"""
        try:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'learning_data': self.learning_data,
                'domain_patterns': self.domain_patterns,
                'total_domains': len(self.domain_patterns),
                'total_entries': sum(len(entries) for entries in self.learning_data.values())
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.bot.logger.info(f"📤 Learning data exported to {output_file}")
            self.bot.logger.info(f"   Total domains: {export_data['total_domains']}")
            self.bot.logger.info(f"   Total entries: {export_data['total_entries']}")
            
        except Exception as e:
            self.bot.logger.error(f"❌ Error exporting learning data: {e}")
    
    def apply_domain_patterns(self, domain, changes):
        """Apply learned patterns untuk domain"""
        try:
            if domain not in self.domain_patterns:
                self.bot.logger.info(f"🔍 {W}No learned patterns for {G}{domain} {W}yet")
                return 0
            
            patterns = self.domain_patterns[domain]
            bonus = 0
            
            self.bot.logger.info(f"🎯 Applying learned patterns for {domain}")
            
            # Apply learned URL patterns
            if 'url_patterns' in patterns and patterns['url_patterns']:
                new_hash = changes.get('new_url_hash', '').lower()
                new_url = changes.get('after_url', '').lower()
                
                for pattern in patterns['url_patterns']:
                    if pattern.lower() in new_hash or pattern.lower() in new_url:
                        bonus += 10
                        self.bot.logger.info(f"✅ URL pattern match: {pattern} (+10 points)")
            
            # Apply learned text patterns
            if 'text_patterns' in patterns and patterns['text_patterns']:
                relevant_words = changes.get('text_changes', {}).get('relevant_words', [])
                page_text = changes.get('new_text', '').lower()
                
                for pattern in patterns['text_patterns']:
                    # Check in relevant words
                    for word in relevant_words:
                        if pattern.lower() in word.lower():
                            bonus += 5
                            self.bot.logger.info(f"✅ Text pattern match: {pattern} (+5 points)")
                            break
                    
                    # Check in page text
                    if pattern.lower() in page_text:
                        bonus += 3
                        self.bot.logger.info(f"✅ Page text pattern match: {pattern} (+3 points)")
            
            # Apply learned alert patterns
            if 'alert_patterns' in patterns and patterns['alert_patterns']:
                new_alerts = changes.get('new_alerts', [])
                
                for alert in new_alerts:
                    alert_text = alert.get('text', '').lower()
                    for pattern in patterns['alert_patterns']:
                        if pattern.lower() in alert_text:
                            bonus += 15
                            self.bot.logger.info(f"✅ Alert pattern match: {pattern} (+15 points)")
            
            if bonus > 0:
                self.bot.logger.info(f"🎯 Total domain pattern bonus: +{bonus} points")
            else:
                self.bot.logger.info(f"🔍 No pattern matches found for {domain}")
            
            return bonus
            
        except Exception as e:
            self.bot.logger.error(f"❌ Error applying domain patterns: {e}")
            return 0