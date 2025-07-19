from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import json
import os
import csv

# Global variable to store the fastest selector for Auto button
fastest_auto_selector = None
found_schoolnames = set()
found_emails = set()
entries = set()

def load_dutch_places():
    """Load Dutch place names from the JSON file."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, "examen_plaatsen.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("plaatsnamen", [])
    except FileNotFoundError:
        print("Error: examen_plaatsen.json not found!")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in examen_plaatsen.json!")
        return []


def process_place(driver, place_name):
    """Process a single place name by searching for 'gym + place_name'."""
    print(f"Processing place: {place_name}")
    driver.get("https://www.cbr.nl/nl/rijschoolzoeker")

    time.sleep(2)
    
    # Wait for page to load
    wait = WebDriverWait(driver, 10)
    
    try:
        # Try multiple selectors to find the search input field
        search_box = None
        
        # First try by aria-label (most specific)
        try:
            search_box = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Zoek een plaatsnaam"]'))
            )
        except:
            pass

        
        if search_box:
            # Clear the input field first
            search_box.clear()
            
            # Type the place name
            search_box.send_keys(place_name)
            print(f"Typed '{place_name}' into search field")
            
            # Wait a moment for any autocomplete suggestions
            time.sleep(2.5)
            
            # Press Enter to search
            search_box.send_keys(Keys.ENTER)
            # print(f"Pressed Enter to search for '{place_name}'")
            
            # Wait for search results to load
            time.sleep(2.5)
            
            # Now click on the "Auto" button to select car as vehicle type
            try:
                global fastest_auto_selector
                auto_button = None
                start_time = time.time()
                
                # Define all possible selectors (ordered by likely speed)
                all_selectors = [
                    # The selector that actually worked in testing
                    "//a[contains(@class, 'vehicle')]//span[text()='Auto']",
                    # Alternative XPath selectors
                    # "//span[text()='Auto']",
                    # "//span[contains(text(), 'Auto')]",
                    # CSS selectors (might not work on this site)
                    # "ul.vehicles li.vehicle_wrapper a.vehicle span.vehicle_name",
                    # "span.vehicle_name",
                    # ".vehicle_name"
                ]
                
                # If we have a known fastest selector, try it first
                if fastest_auto_selector:
                    selectors = [fastest_auto_selector] + [s for s in all_selectors if s != fastest_auto_selector]
                    # print(f"  Using cached fastest selector first: {fastest_auto_selector}")
                else:
                    selectors = all_selectors
                    # print(f"  No cached selector, trying all {len(selectors)} selectors")
                
                for i, selector in enumerate(selectors):
                    selector_start_time = time.time()
                    # print(f"  Trying selector {i+1}/{len(selectors)}: {selector}")
                    
                    try:
                        # Use shorter timeout for faster selector testing
                        short_wait = WebDriverWait(driver, 2)  # 2 seconds instead of 10
                        
                        if selector.startswith("//"):
                            # XPath selector
                            auto_button = short_wait.until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            # CSS selector
                            auto_button = short_wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        
                        if auto_button:
                            selector_time = time.time() - selector_start_time
                            total_time = time.time() - start_time
                            print(f"  ✓ Found 'Auto' button using selector: {selector}")
                            # print(f"  ✓ Selector took {selector_time:.2f}s, total time: {total_time:.2f}s")
                            
                            # Cache the fastest selector for future use
                            if not fastest_auto_selector or selector_time < 1.0:  # If it's fast, cache it
                                fastest_auto_selector = selector
                                # print(f"  💾 Cached this selector as fastest: {selector}")
                            
                            break
                        else:
                            selector_time = time.time() - selector_start_time
                            print(f"  ✗ Selector failed after {selector_time:.2f}s")
                    except Exception as e:
                        selector_time = time.time() - selector_start_time
                        print(f"  ✗ Selector failed after {selector_time:.2f}s: {str(e)}")
                        continue
                
                if auto_button:
                    # Click on the parent <a> tag if we found the span
                    if auto_button.tag_name == 'span':
                        auto_button = auto_button.find_element(By.XPATH, "./parent::a")
                    
                    auto_button.click()
                    print(f"Clicked on 'Auto' button for {place_name}")
                    
                    # Wait for the results to load after selecting vehicle type
                    time.sleep(1)
                    
                    # Now try to find and select the sorting dropdown
                    select_sorting_option(driver, place_name)
                    
                    # Now click on ALL search results one by one
                    click_all_search_results(driver, place_name)
                else:
                    print(f"Could not find 'Auto' button for {place_name} with any selector")
                
            except Exception as e:
                print(f"Could not find or click 'Auto' button for {place_name}: {str(e)}")
            
        else:
            print(f"Could not find search input field for place: {place_name}")
            
    except Exception as e:
        print(f"Error processing place '{place_name}': {str(e)}")


def select_sorting_option(driver, place_name):
    """Find and select the 'Alfabetisch A-Z' sorting option from the dropdown."""
    # print(f"  🔍 Looking for sorting dropdown for {place_name}")
    
    try:
        wait = WebDriverWait(driver, 5)
        start_time = time.time()
        
        # Try multiple selectors to find the sorting dropdown
        dropdown_selectors = [
            # Common dropdown selectors
            # "select",
            "[class*='sort']",
            # "[class*='dropdown']",
            # "[class*='filter']",
            # "[class*='sorteren']",
            # More specific selectors
            # "button[aria-haspopup='true']",
            # "button[aria-expanded]",
            # ".sort-button",
            # ".dropdown-button",
            # ".filter-button"
        ]
        
        dropdown_element = None
        for i, selector in enumerate(dropdown_selectors):
            selector_start_time = time.time()
            # print(f"    Trying dropdown selector {i+1}/{len(dropdown_selectors)}: {selector}")
            
            try:
                if selector.startswith("//"):
                    # XPath selector
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    # CSS selector
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    # print(f"    ✓ Found {len(elements)} potential dropdown elements with selector: {selector}")
                    
                    # Check each element to see if it's the sorting dropdown
                    for j, element in enumerate(elements):
                        try:
                            element_text = element.text.strip()
                            element_html = element.get_attribute('outerHTML')
                            # print(f"      Element {j+1}: Text='{element_text[:50]}...' HTML='{element_html[:100]}...'")
                            
                            # Look for sorting-related text
                            if any(keyword in element_text.lower() for keyword in ['sorteren', 'sort', 'filter', 'dropdown']):
                                dropdown_element = element
                                # print(f"      ✓ Found sorting dropdown: {element_text}")
                                break
                        except Exception as e:
                            # print(f"      ✗ Error checking element {j+1}: {str(e)}")
                            continue
                    
                    if dropdown_element:
                        break
                else:
                    selector_time = time.time() - selector_start_time
                    # print(f"    ✗ No elements found with selector: {selector} (took {selector_time:.2f}s)")
                    
            except Exception as e:
                selector_time = time.time() - selector_start_time
                print(f"    ✗ Selector failed after {selector_time:.2f}s: {str(e)}")
                continue
        
        if dropdown_element:
            # print(f"  ✓ Found sorting dropdown, attempting to click it")
            
            # Click the dropdown to open it
            # dropdown_element.click()
            # print(f"  ✓ Clicked dropdown, waiting for options to appear")
            time.sleep(0.01)
            
            # Now look for the "Alfabetisch A-Z" option
            sort_option_selectors = [
                "//*[contains(text(), 'Alfabetisch A - Z')]",
                # "//*[contains(text(), 'Alfabetisch A-Z')]",
                # "//*[contains(text(), 'Alfabetisch')]",
                # "//option[contains(text(), 'Alfabetisch')]",
                # "//li[contains(text(), 'Alfabetisch')]",
                # "//div[contains(text(), 'Alfabetisch')]"
            ]
            
            sort_option = None
            for i, selector in enumerate(sort_option_selectors):
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        # print(f"    ✓ Found {len(elements)} potential 'Alfabetisch A-Z' options with selector: {selector}")
                        for j, element in enumerate(elements):
                            element_text = element.text.strip()
                            # print(f"      Option {j+1}: '{element_text}'")
                            if 'alfabetisch' in element_text.lower() and 'a' in element_text.lower():
                                sort_option = element
                                # print(f"      ✓ Found 'Alfabetisch A-Z' option: '{element_text}'")
                                break
                        if sort_option:
                            break
                except Exception as e:
                    # print(f"    ✗ Error with sort option selector {selector}: {str(e)}")
                    continue
            
            if sort_option:
                sort_option.click()
                print(f"  ✓ Successfully selected 'Alfabetisch A-Z' sorting option")
                time.sleep(1)  # Wait for sorting to apply
            else:
                print(f"  ✗ Could not find 'Alfabetisch A-Z' option in dropdown")
        else:
            print(f"  ✗ Could not find sorting dropdown for {place_name}")
            
    except Exception as e:
        print(f"  ✗ Error selecting sorting option for {place_name}: {str(e)}")


def click_all_search_results(driver, place_name):
    """Find and click on ALL search results in the list, one by one."""
    # print(f"  🔍 Looking for ALL search results for {place_name}")
    
    try:
        wait = WebDriverWait(driver, 5)
        start_time = time.time()
        
        # Try multiple selectors to find search results
        result_selectors = [
            # Based on the HTML structure shown (table-row with data-rid)
            # "div.table-row",
            # "[data-rid]",
            # ".table-row",
            # Alternative selectors for search results
            # "[class*='result']",
            # "[class*='item']",
            "[class*='row']",
            # "article",
            # ".result-item",
            # ".search-result",
            # ".list-item"
        ]
        
        all_results = []
        working_selector = None

        time.sleep(1)
        
        for i, selector in enumerate(result_selectors):
            selector_start_time = time.time()
            # print(f"    Trying result selector {i+1}/{len(result_selectors)}: {selector}")
            
            try:
                if selector.startswith("//"):
                    # XPath selector
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    # CSS selector
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    print(f"    ✓ Found {len(elements)} potential result elements with selector: {selector}")
                    
                    # Check each element to see if it's a search result
                    valid_results = []
                    for j, element in enumerate(elements):
                        try:
                            element_text = element.text.strip()
                            element_rid = element.get_attribute('data-rid')
                            
                            # Look for elements that look like search results
                            # Check if it has data-rid (like in the HTML structure shown)
                            if element_rid and element_rid != 'None':
                                valid_results.append(element)
                                # print(f"      ✓ Valid result {len(valid_results)}: data-rid='{element_rid}', text='{element_text[:50]}...'")
                        except Exception as e:
                            print(f"      ✗ Error checking element {j+1}: {str(e)}")
                            continue
                    
                    if valid_results:
                        all_results = valid_results
                        working_selector = selector
                        print(f"    ✓ Found {len(all_results)} valid search results with selector: {selector}")
                        break
                else:
                    selector_time = time.time() - selector_start_time
                    print(f"    ✗ No elements found with selector: {selector} (took {selector_time:.2f}s)")
                    
            except Exception as e:
                selector_time = time.time() - selector_start_time
                print(f"    ✗ Selector failed after {selector_time:.2f}s: {str(e)}")
                continue
        
        if all_results:
            print(f"  ✓ Found {len(all_results)} search results, clicking each one...")
            
            # Click on each result one by one (limit to first 10 for testing)
            max_results = min(1000, len(all_results))  # Limit to first 10 results for now
            # print(f"    ⚠️ Limiting to first {max_results} results for testing")
            
            for i, result in enumerate(all_results[:max_results]):
                try:
                    # print(f"    📍 Processing result {i+1}/{max_results}")
                    
                    # Store the current URL to return to results page
                    current_url = driver.current_url
                    
                    # Scroll the result into view first
                    driver.execute_script("arguments[0].scrollIntoView(true);", result)
                    time.sleep(0.01)  # Wait for scroll to complete
                    
                    # Try to find a clickable element within the result
                    clickable_selectors = [
                        "button",
                        "a",
                        "[class*='name']",
                        ".cell--name",
                        ".result-name",
                        ".item-name"
                    ]
                    
                    clickable_element = None
                    for selector in clickable_selectors:
                        try:
                            clickable_elements = result.find_elements(By.CSS_SELECTOR, selector)
                            if clickable_elements:
                                clickable_element = clickable_elements[0]  # Take the first clickable element
                                # print(f"      ✓ Found clickable element with selector: {selector}")
                                break
                        except:
                            continue
                    
                    # If no specific clickable element found, try clicking the result itself
                    if not clickable_element:
                        clickable_element = result
                        print(f"      ✓ Using the result element itself as clickable")
                    
                    # Scroll the clickable element into view
                    driver.execute_script("arguments[0].scrollIntoView(true);", clickable_element)
                    time.sleep(0.01)

                    # Check if current tab URL contains cbr.nl
                    while("cbr.nl" not in driver.current_url.lower()):
                        print("closing tab")
                        # close current tab
                        driver.close()  
                    
                    # Try to click using JavaScript if regular click fails
                    try:
                        clickable_element.click()
                        # print(f"      ✓ Successfully clicked on result {i+1}")
                    except Exception as click_error:
                        # print(f"      ⚠️ Regular click failed, trying JavaScript click: {str(click_error)}")
                        try:
                            driver.execute_script("arguments[0].click();", clickable_element)
                            print(f"      ✓ Successfully clicked on result {i+1} using JavaScript")
                        except Exception as js_error:
                            print(f"      ✗ JavaScript click also failed: {str(js_error)}")
                            continue
                    
                    # Wait a bit for the result to load/expand
                    time.sleep(0.01)
                    
                    # Extract data from this specific result
                    entry = extract_driving_school_data_from_result(driver, place_name, i+1)

                    # Wait a bit before next result

                    # Click the element again so that this result is deselected
                    clickable_element.click()
                    time.sleep(0.01)
                    
                except Exception as e:
                    print(f"      ✗ Error processing result {i+1}: {str(e)}")
                    # Try to return to results page even if there was an error
                    # try:
                    #     driver.back()
                    #     time.sleep(2)
                    # except:
                    #     pass
                    continue
            
            print(f"  ✓ Finished processing all {len(all_results)} search results for {place_name}")
            
        else:
            print(f"  ✗ Could not find any search results for {place_name}")
            
    except Exception as e:
        print(f"  ✗ Error processing search results for {place_name}: {str(e)}")


def extract_driving_school_data_from_result(driver, place_name, result_number) -> str:
    entry = ""
    """Extract driving school information from a specific clicked result."""
    print(f"      📊 Extracting data from result {result_number} for {place_name}")
    
    try:        
        time.sleep(0.01)
        try:
            school_name = extract_school_name(driver)
            print(f"Rijschool naam: {school_name}")
        except Exception as e:
            school_name = None
        
        try:
            email_address = extract_email_address(driver)
            print(f"Email: {email_address}")
        except Exception as e:
            email_address = None
        
        try:
            phone_number = extract_phone_number(driver)
            print(f"Telefoon: {phone_number}")
        except Exception as e:
            phone_number = None
        
        try:
            website = extract_website(driver)
            print(f"Website: {website}")
        except Exception as e:
            website = None
        
        entry = f"{school_name},{phone_number},{email_address},{website}"
        if(entry not in entries):
            print(f"Entry: {entry}")
            # add row to rijscholen_leads.csv
            if(email_address is None):
                with open('leads_no_email.csv', 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([entry])
            else:
                with open('rijscholen_leads.csv', 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([entry])
        else:
            print(f"Entry already exists: {entry}")
        return entry
            
    except Exception as e:
        print(f"        ✗ Fout bij extractie van data uit result {result_number}: {str(e)}")
        print(f"        🔍 Stack trace: {e.__class__.__name__}")
        return True  # Continue to next result even if there was an error


def extract_school_name(driver):
    """Extract the school name from the current page."""
    try:
        # Set a timeout for this operation
        start_time = time.time()
        timeout = 10  # 10 seconds timeout
        
        # Look for school name in various locations
        name_selectors = [
            'h1',
            'h2', 
            'h3',
            '.school-name',
            '.driving-school-name',
            '[class*="name"]',
            '[class*="title"]',
            # More general selectors
            '[class*="school"]',
            '[class*="rijschool"]',
            '.cell--name',
            '.result-name',
            '.item-name',
            'strong',
            'b'
        ]
        
        for selector in name_selectors:
            # Check timeout
            if time.time() - start_time > timeout:
                print(f"        ⏰ Timeout bij zoeken naar school naam")
                break
                
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        name_text = element.text.strip()
                        # Filter out unwanted text
                        if (name_text and 
                            name_text != "Rijschoolzoeker" and 
                            name_text != "Examenlocaties" and
                            name_text != "Resultaten voor Auto" and
                            name_text != "Geef ons je feedback!" and
                            name_text != "Auto" and
                            name_text != "Motor" and
                            name_text != "Bromfiets" and
                            len(name_text) > 3 and
                            not name_text.startswith("Resultaten") and
                            not name_text.startswith("Geen") and
                            not name_text.startswith("Niet") and
                            not name_text.lower().startswith("klik") and
                            not name_text.lower().startswith("selecteer") and
                            not name_text.lower() in found_schoolnames):
                            found_schoolnames.add(name_text.lower().replace(',', ''))
                            return name_text
                    except Exception as element_error:
                        continue
            except Exception as selector_error:
                continue
        
        # If no name found with selectors, try to find it in the page title or URL
        try:
            page_title = driver.title
            if page_title and "rijschool" in page_title.lower():
                # Extract school name from title
                title_parts = page_title.split('-')
                if len(title_parts) > 1:
                    potential_name = title_parts[0].strip()
                    if len(potential_name) > 3:
                        return potential_name
        except Exception as title_error:
            pass
        
        return None
    except Exception as e:
        print(f"        ✗ Fout bij extractie van rijschool naam: {str(e)}")
        return None


def extract_email_address(driver):
    """Extract email address from the current page."""
    try:
        # Set a timeout for this operation
        start_time = time.time()
        timeout = 1  # 10 seconds timeout
        
        # Comprehensive check for emails - try multiple selectors
        email_selectors = [
            # Most specific selectors first
            'a[href^="mailto:"]',
            # 'a.details_contact.details_contact_email',
            # 'a[class*="email"]',
            # # More general selectors
            # 'a[href*="@"]',
            # '[class*="email"]',
            # '[class*="mail"]',
            # # Text-based search
            # 'a',
            # 'span',
            # 'div'
        ]
        
        for email_selector in email_selectors:
            # Check timeout
            if time.time() - start_time > timeout:
                print(f"        ⏰ Timeout bij zoeken naar email")
                break
                
            try:
                email_elements = driver.find_elements(By.CSS_SELECTOR, email_selector)
                if email_elements:
                    for email_element in email_elements:
                        try:
                            email_href = email_element.get_attribute('href') or ''
                            email_text = email_element.text.strip()
                            
                            # Extract email from href (remove mailto: prefix)
                            if email_href.startswith('mailto:'):
                                email_address = email_href[7:]  # Remove 'mailto:' prefix
                                if '@' in email_address and '.' in email_address:
                                    # Basic email validation
                                    if len(email_address) > 5 and '@' in email_address.split('.')[0] and email_address not in found_emails:
                                        found_emails.add(email_address.replace(',', ''))
                                        print(email_selector)
                                        return email_address
                            elif '@' in email_href and '.' in email_href:
                                # Basic email validation
                                if len(email_href) > 5 and '@' in email_href.split('.')[0] and email_href not in found_emails:
                                    found_emails.add(email_href.replace(',', ''))
                                    print(email_selector)
                                    return email_href
                            elif '@' in email_text and '.' in email_text:
                                # Basic email validation
                                if len(email_text) > 5 and '@' in email_text.split('.')[0] and email_text not in found_emails:
                                    found_emails.add(email_text.replace(',', ''))
                                    print(email_selector)
                                    return email_text
                                
                        except Exception as element_error:
                            continue
                        
            except Exception as selector_error:
                continue
        
        # If no email found with selectors, try a broader text search
        # try:
        #     page_text = driver.find_element(By.TAG_NAME, "body").text
        #     # Simple regex to find email patterns
        #     import re
        #     email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        #     emails = re.findall(email_pattern, page_text)
        #     if emails:
        #         return emails[0]  # Return the first email found
        # except Exception as text_error:
        #     pass
        
        return None
    except Exception as e:
        print(f"        ✗ Fout bij extractie van emailadres: {str(e)}")
        return None


def extract_phone_number(driver):
    """Extract phone number from the current page."""
    try:
        # Set a timeout for this operation
        start_time = time.time()
        timeout = 1  # 10 seconds timeout
        
        # Look for phone numbers in various locations
        phone_selectors = [
            'a[href^="tel:"]',
            'a.details_contact.details_contact_phone',
            'a[class*="phone"]',
            'a[class*="tel"]',
            '.phone',
            '.telefoon',
            '[class*="phone"]',
            '[class*="tel"]',
            # More general selectors
            'a[href*="tel"]',
            '[class*="contact"]',
            'span',
            'div'
        ]
        
        for selector in phone_selectors:
            # Check timeout
            if time.time() - start_time > timeout:
                print(f"        ⏰ Timeout bij zoeken naar telefoon")
                break
                
            try:
                phone_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for phone_element in phone_elements:
                    try:
                        phone_href = phone_element.get_attribute('href') or ''
                        phone_text = phone_element.text.strip()
                        
                        # Extract phone from href (remove tel: prefix)
                        if phone_href.startswith('tel:'):
                            phone_number = phone_href[4:]  # Remove 'tel:' prefix
                            if phone_number and len(phone_number) > 5:
                                # Basic validation - should contain digits
                                if any(char.isdigit() for char in phone_number):
                                    return phone_number
                        elif phone_text and len(phone_text) > 5:
                            # Check if it looks like a phone number
                            if any(char.isdigit() for char in phone_text):
                                # Remove common prefixes and clean up
                                cleaned_text = phone_text.replace('+31', '').replace('0031', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                                if len(cleaned_text) >= 8 and cleaned_text.isdigit():
                                    return phone_text  # Return original text for display
                    except Exception as element_error:
                        continue
            except Exception as selector_error:
                continue
        
        # If no phone found with selectors, try a broader text search
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            # Simple regex to find phone patterns (Dutch format)
            import re
            phone_patterns = [
                r'\b0[1-9][0-9]{7,8}\b',  # Dutch landline: 0xx xxxxxxx
                r'\b06[0-9]{8}\b',        # Dutch mobile: 06 xxxxxxxx
                r'\b\+31[0-9]{9}\b',      # International Dutch: +31 xxxxxxxx
                r'\b0031[0-9]{9}\b'       # International Dutch: 0031 xxxxxxxx
            ]
            
            for pattern in phone_patterns:
                phones = re.findall(pattern, page_text.replace(' ', ''))
                if phones:
                    return phones[0]  # Return the first phone found
        except Exception as text_error:
            pass
        
        return None
    except Exception as e:
        print(f"        ✗ Fout bij extractie van telefoonnummer: {str(e)}")
        return None


def extract_website(driver):
    """Extract website URL from the current page."""
    try:
        # Set a timeout for this operation
        start_time = time.time()
        timeout = 1  # 1 second timeout
        
        # Look for website URLs in various locations
        website_selectors = [
            'a.details_contact.details_contact_website',
            'a[href*="http"]',
            'a[href*="www"]',
            'a[class*="website"]',
            'a[class*="site"]',
            'a[class*="web"]',
            '[class*="website"]',
            '[class*="site"]',
            '[class*="web"]',
            # More general selectors
            'a[target="_blank"]',
            'a[rel*="noreferrer"]',
            'a[rel*="noopener"]',
            'a'
        ]
        
        for selector in website_selectors:
            # Check timeout
            if time.time() - start_time > timeout:
                print(f"        ⏰ Timeout bij zoeken naar website")
                break
                
            try:
                website_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for website_element in website_elements:
                    try:
                        website_href = website_element.get_attribute('href') or ''
                        website_text = website_element.text.strip()
                        
                        # Check if href contains a valid website URL
                        if website_href and ('http://' in website_href or 'https://' in website_href or 'www.' in website_href):
                            # Basic validation - should be a website URL
                            if len(website_href) > 10 and '.' in website_href:
                                # Filter out common non-website URLs
                                if not any(exclude in website_href.lower() for exclude in ['mailto:', 'tel:', 'javascript:', '#']):
                                    return website_href
                        elif website_text and ('http://' in website_text or 'https://' in website_text or 'www.' in website_text):
                            # Check if text looks like a website URL
                            if len(website_text) > 10 and '.' in website_text:
                                # Filter out common non-website URLs
                                if not any(exclude in website_text.lower() for exclude in ['mailto:', 'tel:', 'javascript:', '#']):
                                    return website_text
                    except Exception as element_error:
                        continue
            except Exception as selector_error:
                continue
        
        # If no website found with selectors, try a broader text search
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            # Simple regex to find website patterns
            import re
            website_patterns = [
                r'https?://[^\s<>"]+',
                r'www\.[^\s<>"]+',
                r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            ]
            
            for pattern in website_patterns:
                websites = re.findall(pattern, page_text)
                for website in websites:
                    # Basic validation
                    if len(website) > 10 and '.' in website:
                        # Filter out common non-website URLs
                        if not any(exclude in website.lower() for exclude in ['mailto:', 'tel:', 'javascript:', '#', '@']):
                            # Add http:// if no protocol specified
                            if not website.startswith(('http://', 'https://')):
                                website = 'http://' + website
                            return website
        except Exception as text_error:
            pass
        
        return None
    except Exception as e:
        print(f"        ✗ Fout bij extractie van website: {str(e)}")
        return None

def extract_driving_schools(driver, place_name):
    """Extract driving school information from the current page."""
    try:
        # Wait a bit more for results to load
        time.sleep(0.01)
        
        # Look for driving school results on the CBR website
        # The results might appear in different formats
        wait = WebDriverWait(driver, 10)
        
        # Try multiple selectors to find driving school listings
        selectors = [
            '.driving-school',
            '.rijschool', 
            '[class*="school"]',
            '[class*="result"]',
            '.result-item',
            '.school-item',
            'article',
            '.content-item'
        ]
        
        driving_schools = []
        for selector in selectors:
            try:
                schools = driver.find_elements(By.CSS_SELECTOR, selector)
                if schools:
                    driving_schools = schools
                    # print(f"Found {len(driving_schools)} potential driving schools using selector '{selector}' for {place_name}")
                    break
            except:
                continue
        
        if driving_schools:
            print(f"Processing {len(driving_schools)} driving schools for {place_name}")
            
            for i, school in enumerate(driving_schools[:]):  # Limit to first 10
                try:
                    # Try to extract school name using multiple approaches
                    name_selectors = ['h1', 'h2', 'h3', '.name', '.title', '[class*="name"]', '[class*="title"]']
                    school_name = "Unknown"
                    
                    for name_selector in name_selectors:
                        try:
                            name_element = school.find_element(By.CSS_SELECTOR, name_selector)
                            if name_element.text.strip():
                                school_name = name_element.text.strip()
                                break
                        except:
                            continue
                    
                    print(f"  {i+1}. {school_name}")
                    
                    # Try to extract contact information
                    contact_selectors = [
                        'a[href*="mailto"]',
                        '.email', 
                        '[class*="email"]',
                        'a[href*="tel:"]',
                        '.phone',
                        '[class*="phone"]'
                    ]
                    
                    for contact_selector in contact_selectors:
                        try:
                            contact_elements = school.find_elements(By.CSS_SELECTOR, contact_selector)
                            for contact in contact_elements:
                                contact_text = contact.text.strip()
                                contact_href = contact.get_attribute('href') or ''
                                
                                if '@' in contact_text or 'mailto:' in contact_href or contact_text.replace(' ', '').isdigit():
                                    print(f"     Contact: {contact_text}")
                        except:
                            continue
                    
                except Exception as e:
                    print(f"    Error extracting school {i+1}: {str(e)}")
        else:
            print(f"No driving schools found for {place_name}")
            
            # Let's also check if there's a "no results" message
            try:
                no_results = driver.find_elements(By.XPATH, "//*[contains(text(), 'geen resultaten') or contains(text(), 'no results') or contains(text(), 'niet gevonden')]")
                if no_results:
                    print(f"  No results message found for {place_name}")
            except:
                pass
            
    except Exception as e:
        print(f"Error extracting driving schools for {place_name}: {str(e)}")


if __name__ == "__main__":
    with open('leads_no_email.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) # Skip header row
        for row in reader:
            entries.add(row[0])

    with open('rijscholen_leads.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) # Skip header row
        for row in reader:
            entries.add(row[0])
    print(entries)

    # Load Dutch place names
    places = load_dutch_places()
    if not places:
        print("No places loaded. Exiting.")
        exit(1)
    
    print(f"Loaded {len(places)} Dutch places from JSON file.")
    
    edge_options = Options()
    edge_options.add_argument("--headless=false")
    edge_options.add_argument("--start-maximized")
    driver = webdriver.Edge(options=edge_options)
    
    # Process each place (you can limit the number by changing the range)
    for i, place in enumerate(places[1:]):  # Process first 50 places as an example
        print(f"\n--- Processing place {i+1}/{len(places)}: {place} ---")
        process_place(driver, place)
        driver.quit()
        driver = webdriver.Edge(options=edge_options)