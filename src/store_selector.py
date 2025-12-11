from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

class FlippStoreSelector:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Initialize Chromium driver with options"""
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/chromium"
        if self.headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service('/usr/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def select_store(self, postal_code="L6E1T8"):
        """Navigate to Flipp and set postal code"""
        try:
            # Ensure the driver is initialized. If not, initialize now.
            if not self.driver:
                try:
                    print("Driver not initialized; calling setup_driver() before select_store()")
                    self.setup_driver()
                except Exception as e:
                    print(f"Failed to initialize driver in select_store: {e}")
                    raise
            # Only navigate if we're not already on Flipp to save time
            try:
                current = self.driver.current_url if self.driver else ""
            except Exception:
                current = ""

            if not current or "flipp.com" not in current:
                print(f"Navigating to Flipp.com...")
                self.driver.get("https://flipp.com/")
                time.sleep(0.5)
            
            # Quick consent handling - just check the most common button
            try:
                consent_btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.cky-btn-accept'))
                )
                print("Clicking consent button")
                consent_btn.click()
                time.sleep(0.3)
            except TimeoutException:
                # No consent banner found, continue
                pass
            except Exception as e:
                # Consent handling failed, but continue anyway
                pass

            # Find the postal code input field and set value via JS
            print(f"Entering postal code: {postal_code}")
            postal_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-cy="postalCodeInput"]'))
            )

            # Set input value using JS (faster than send_keys)
            self.driver.execute_script(
                "arguments[0].focus(); arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
                postal_input,
                postal_code,
            )
            time.sleep(0.5)  # Brief wait for UI to update

            # Click the start button
            print("Clicking Start Saving button...")
            start_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-cy="startSaving"]'))
            )
            start_button.click()
            time.sleep(1)  # Brief wait for navigation

            print("Postal code set successfully!")
            return True
            
        except Exception as e:
            print(f"Error setting postal code: {e}")
            import traceback
            traceback.print_exc()

            # Save debug artifacts (screenshot + page source) to output dir
            try:
                out_dir = os.getenv('DEBUG_OUTPUT_DIR', '/app/output')
                os.makedirs(out_dir, exist_ok=True)
                ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
                screenshot_path = os.path.join(out_dir, f'selector_failure_{ts}.png')
                html_path = os.path.join(out_dir, f'selector_failure_{ts}.html')
                try:
                    if self.driver:
                        self.driver.save_screenshot(screenshot_path)
                        with open(html_path, 'w', encoding='utf-8') as f:
                            f.write(self.driver.page_source)
                        print(f"Wrote debug files: {screenshot_path}, {html_path}")
                except Exception as e2:
                    print(f"Failed to write debug artifacts: {e2}")
            except Exception:
                pass

            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
