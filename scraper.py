from playwright.sync_api import sync_playwright
import re

class GSTScraper:
    def __init__(self, headless=True):
        self.headless = headless

    def validate_gst_number(self, gst_number):
        gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
        return re.match(gst_pattern, gst_number.upper()) is not None

    def scrape_gst_data(self, gst_number):
        if not self.validate_gst_number(gst_number):
            return {'success': False, 'error': 'Invalid GST number format'}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                page.goto("https://www.knowyourgst.com/gst-number-search/", timeout=60000)

                page.fill("input[type='text']", gst_number.upper())
                page.click("button, input[type='submit']")
                page.wait_for_selector("table", timeout=15000)

                rows = page.query_selector_all("table tr")
                data = {}

                for row in rows:
                    cols = row.query_selector_all("td")
                    if len(cols) >= 2:
                        key = cols[0].inner_text().strip()
                        value = cols[1].inner_text().strip()

                        # Map relevant fields
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
                        else:
                            data[key.lower().replace(" ", "_")] = value

                browser.close()

                return {
                    'success': True,
                    'data': data,
                    'gst_number': gst_number.upper()
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Playwright error: {str(e)}'
            }

    def close(self):
        pass  # No persistent browser session to close in Playwright
