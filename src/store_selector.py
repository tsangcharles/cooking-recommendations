from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class FlippStoreSelector:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Initialize Chrome driver with options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def select_store(self, postal_code="L6E1T8"):
        """Navigate to Flipp and set postal code"""
        try:
            print(f"Navigating to Flipp.com...")
            self.driver.get("https://flipp.com/")
            
            # Wait for page to load
            time.sleep(3)
            
            # Find the postal code input field
            print(f"Entering postal code: {postal_code}")
            postal_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    'input[data-cy="postalCodeInput"]'
                ))
            )
            
            # Clear and enter postal code
            postal_input.clear()
            postal_input.send_keys(postal_code)
            time.sleep(1)
            
            # Click "Start Saving" button
            print("Clicking Start Saving button...")
            start_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    'a[data-cy="startSaving"]'
                ))
            )
            start_button.click()
            time.sleep(3)
            
            print("Postal code set successfully!")
            return True
            
        except Exception as e:
            print(f"Error setting postal code: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
