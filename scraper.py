from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import re

class GSTScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Use WebDriverManager to automatically download and manage ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def validate_gst_number(self, gst_number):
        """Validate GST number format"""
        gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
        return re.match(gst_pattern, gst_number.upper()) is not None
    
    def scrape_gst_data(self, gst_number):
        """Scrape GST data from knowyourgst.com"""
        try:
            # Validate GST number format
            if not self.validate_gst_number(gst_number):
                return {
                    'success': False,
                    'error': 'Invalid GST number format'
                }
            
            # Navigate to the website
            url = "https://www.knowyourgst.com/gst-number-search/"
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Find and fill the GST number input field
            gst_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
            )
            gst_input.clear()
            gst_input.send_keys(gst_number.upper())
            
            # Find and click the verify button
            verify_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button, input[type='submit']"))
            )
            verify_button.click()
            
            # Wait for results to load
            time.sleep(3)
            
            # Wait for the results table or data to appear
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Extract data from the results
            data = self.extract_gst_data()
            
            return {
                'success': True,
                'data': data,
                'gst_number': gst_number.upper()
            }
            
        except TimeoutException:
            return {
                'success': False,
                'error': 'Timeout: Unable to load GST data or invalid GST number'
            }
        except NoSuchElementException:
            return {
                'success': False,
                'error': 'Unable to find required elements on the page'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }
    
    def extract_gst_data(self):
        """Extract GST data from the results page"""
        try:
            data = {}
            
            # Try to find table rows with data
            table = self.driver.find_element(By.TAG_NAME, "table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 2:
                    key = cells[0].text.strip()
                    value = cells[1].text.strip()
                    
                    # Map the keys to standardized field names
                    if "Business Name" in key or "Trade Name" in key:
                        data['business_name'] = value
                    elif "PAN Number" in key:
                        data['pan_number'] = value
                    elif "Legal Name" in key:
                        data['legal_name'] = value
                    elif "Address" in key:
                        data['address'] = value
                    elif "Entity Type" in key:
                        data['entity_type'] = value
                    elif "Registration Type" in key:
                        data['registration_type'] = value
                    elif "State" in key:
                        data['state'] = value
                    elif "Status" in key:
                        data['status'] = value
                    elif "Department Code" in key or "Department Type" in key:
                        data['department_code_and_type'] = value
                    elif "Nature of Business" in key:
                        data['nature_of_business'] = value
                    elif "Registration Date" in key:
                        data['registration_date'] = value
            
            # Alternative method: Try to find specific elements by class or ID
            try:
                # Look for common class names or IDs that might contain the data
                elements = self.driver.find_elements(By.CSS_SELECTOR, "div, span, p")
                for element in elements:
                    text = element.text.strip()
                    if ":" in text:
                        parts = text.split(":", 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            if key and value:
                                if 'department_code_and_type' not in data and ("Department Code" in key or "Department Type" in key):
                                    data['department_code_and_type'] = value
                            elif 'nature_of_business' not in data and "Nature of Business" in key:
                                data['nature_of_business'] = value
                            elif 'registration_date' not in data and "Registration Date" in key:
                                data['registration_date'] = value
                            else:
                                
                                data[key.lower().replace(" ", "_")] = value
            except:
                pass
            
            return data
            
        except Exception as e:
            print(f"Error extracting data: {e}")
            return {}
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
    
    def __del__(self):
        """Destructor to ensure driver is closed"""
        self.close()