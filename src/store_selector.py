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
                # Wait for page to load
                time.sleep(2)
            # Try to handle cookie/consent banners if present. Many sites render consent via JS;
            # try a mix of CSS selectors and XPath text-matching to click common accept buttons.
            try:
                accept_selectors = [
                    'button[data-cy="consent-accept"]',
                    'button[aria-label="Accept"]',
                    'button.cky-btn-accept',
                    'button[data-cky-tag="accept-button"]',
                    'button[data-cky-tag="detail-accept-button"]',
                ]

                clicked_accept = False
                for sel in accept_selectors:
                    try:
                        elems = self.driver.find_elements(By.CSS_SELECTOR, sel)
                        for btn in elems:
                            if btn and btn.is_displayed():
                                print(f"Clicking consent button (css): {sel}")
                                try:
                                    btn.click()
                                    time.sleep(1)
                                    clicked_accept = True
                                    break
                                except Exception:
                                    continue
                        if clicked_accept:
                            break
                    except Exception:
                        continue

                # If not found by CSS, try XPath text search for common phrases (case-insensitive)
                if not clicked_accept:
                    xpath_variants = [
                        "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
                        "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'i agree')]",
                        "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree')]",
                    ]
                    for xp in xpath_variants:
                        try:
                            elems = self.driver.find_elements(By.XPATH, xp)
                            for btn in elems:
                                try:
                                    if btn.is_displayed():
                                        print(f"Clicking consent button (xpath): {xp}")
                                        btn.click()
                                        time.sleep(1)
                                        clicked_accept = True
                                        break
                                except Exception:
                                    continue
                            if clicked_accept:
                                break
                        except Exception:
                            continue

            except Exception as e:
                print(f"Consent handling encountered an error: {e}")

            # Find the postal code input field (fast single wait) and set value via JS
            print(f"Entering postal code: {postal_code}")
            selectors = [
                'input[data-cy="postalCodeInput"]',
                'input[name="postalCode"]',
                'input[placeholder*="Postal"]',
                'input[type="text"]'
            ]

            # Use a WebDriverWait that looks for any of the selectors and allow a longer timeout
            def find_any_input(driver):
                for s in selectors:
                    elems = driver.find_elements(By.CSS_SELECTOR, s)
                    if elems:
                        return elems[0]
                return False

            postal_input = WebDriverWait(self.driver, 12, poll_frequency=0.3).until(find_any_input)
            if not postal_input:
                raise Exception("Postal input element not found with any selector")

            # Set input value using JS to be faster than send_keys, and dispatch input events
            try:
                self.driver.execute_script(
                    "arguments[0].focus(); arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
                    postal_input,
                    postal_code,
                )
            except Exception:
                # Fallback to send_keys if JS approach fails
                postal_input.clear()
                postal_input.send_keys(postal_code)

            # Try to click the start button quickly using one wait for any selector
            print("Clicking Start Saving button...")
            start_selectors = [
                'a[data-cy="startSaving"]',
                'button[data-cy="startSaving"]',
                'a[href*="start"]',
                'button[type="submit"]'
            ]

            def find_and_click_start(driver):
                for s in start_selectors:
                    elems = driver.find_elements(By.CSS_SELECTOR, s)
                    for el in elems:
                        try:
                            if el.is_displayed() and el.is_enabled():
                                el.click()
                                return True
                        except Exception:
                            continue
                return False

            try:
                clicked = WebDriverWait(self.driver, 8, poll_frequency=0.25).until(find_and_click_start)
            except TimeoutException:
                print("Start button not found or not clickable within timeout. Trying fallback.")
                clicked = False

            if not clicked:
                # As a last resort, press Enter on the input
                try:
                    print("Fallback: Pressing Enter on postal code input.")
                    postal_input.send_keys('\n')
                    clicked = True
                    # Add a small wait for page to process the submission
                    time.sleep(3)
                except Exception as e:
                    print(f"Fallback with Enter key failed: {e}")
                    clicked = False

            if not clicked:
                raise Exception("Start button not found / could not be clicked")

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
