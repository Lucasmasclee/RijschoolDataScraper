from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
import os
import json
from selenium.webdriver.common.keys import Keys
import re
import csv

list_of_rijscholen = []

def open_edge_browser_fast():
    """
    Geoptimaliseerde methode om Edge te openen voor snelle uitvoering
    """
    try:
        # Edge opties instellen voor snelheid
        edge_options = Options()
        edge_options.add_argument("--start-maximized")
        edge_options.add_argument("--disable-blink-features=AutomationControlled")
        edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        edge_options.add_experimental_option('useAutomationExtension', False)
        # Voeg extra optimalisaties toe voor snelheid
        edge_options.add_argument("--disable-extensions")
        edge_options.add_argument("--disable-plugins")
        edge_options.add_argument("--disable-images")
        edge_options.add_argument("--disable-javascript")  # Alleen indien mogelijk
        
        # Probeer Edge te openen zonder expliciete driver
        try:
            driver = webdriver.Edge(options=edge_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception:
            # Fallback naar webdriver-manager
            service = Service(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=edge_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        
    except Exception as e:
        print(f"❌ Fout bij het openen van Edge browser: {e}")
        return None

def accept_cookies_fast(driver):
    """
    Snelle cookie acceptatie zonder veel logging
    """
    try:
        wait = WebDriverWait(driver, 5)  # Verlaagd van 10 naar 5 seconden
        
        cookie_selectors = [
            "button[id='L2AGLb']",
            "button:contains('Alles accepteren')",
            "button:contains('Accept all')",
            "button[aria-label*='Accept']",
            "button[data-ved*='accept']",
            ".QS5gu.sy4vM",
            "button.tHlp8d"
        ]
        
        for selector in cookie_selectors:
            try:
                if selector.startswith("button:contains"):
                    text = selector.split("'")[1]
                    cookie_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{text}')]"))
                    )
                else:
                    cookie_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                
                if cookie_button:
                    cookie_button.click()
                    time.sleep(0.5)  # Verlaagd van 2 naar 0.5 seconden
                    return True
                    
            except Exception:
                continue
        
        return False
            
    except Exception:
        return False

def extract_contact_info_fast(driver, rijschool_naam):
    """
    Geoptimaliseerde contactgegevens extractie
    """
    try:
        wait = WebDriverWait(driver, 3)  # Verlaagd van 5 naar 3 seconden
        
        contact_selectors = [
            "a.details__contact",
            "a[class*='details__contact']",
            "p a.details__contact",
            "div a.details__contact"
        ]
        
        contact_info = {
            'rijschool_naam': rijschool_naam,
            'telefoonnummers': [],
            'emailadressen': [],
            'websites': []
        }
        
        # Zoek naar alle contact elementen
        contact_elements = []
        for selector in contact_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    contact_elements = elements
                    break
            except Exception:
                continue
        
        if not contact_elements:
            try:
                contact_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='tel'], a[href*='mailto'], a[href*='http']")
            except Exception:
                pass
        
        if contact_elements:
            for element in contact_elements:
                try:
                    href = element.get_attribute('href')
                    text = element.text.strip()
                    classes = element.get_attribute('class')
                    
                    if href and text:
                        # Telefoonnummer
                        if 'details__contact__phone' in classes or 'tel:' in href:
                            phone = href.replace('tel:', '') if 'tel:' in href else text
                            phone = re.sub(r'[^0-9\s]', '', phone)
                            if phone not in contact_info['telefoonnummers']:
                                contact_info['telefoonnummers'].append(phone)
                        
                        # Emailadres
                        elif 'details__contact__email' in classes or 'mailto:' in href:
                            email = href.replace('mailto:', '') if 'mailto:' in href else text
                            if email not in contact_info['emailadressen']:
                                contact_info['emailadressen'].append(email)
                        
                        # Website
                        elif 'details__contact__website' in classes or ('http' in href and 'mailto:' not in href and 'tel:' not in href):
                            website = href if 'http' in href else text
                            if website not in contact_info['websites']:
                                contact_info['websites'].append(website)
                
                except Exception:
                    continue

        # Schrijf direct naar CSV
        with open('rijscholen_leads.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            new_rijschool_naam = contact_info['rijschool_naam'] if contact_info['rijschool_naam'] else "None"
            telefoonnummer = contact_info['telefoonnummers'][0] if contact_info['telefoonnummers'] else "None"
            emailadres = contact_info['emailadressen'][0] if contact_info['emailadressen'] else "None"
            website = contact_info['websites'][0] if contact_info['websites'] else "None"

            # Verwijder dubbele aanhalingstekens
            new_rijschool_naam = new_rijschool_naam.replace("\"", "").replace(",", "")
            telefoonnummer = telefoonnummer.replace("\"", "").replace(",", "")
            emailadres = emailadres.replace("\"", "").replace(",", "")
            website = website.replace("\"", "").replace(",", "")

            writer.writerow([new_rijschool_naam, telefoonnummer, emailadres, website])
            list_of_rijscholen.append(new_rijschool_naam)
        
        return contact_info
        
    except Exception:
        return {
            'rijschool_naam': rijschool_naam,
            'telefoonnummers': [],
            'emailadressen': [],
            'websites': []
        }

def start_datascraper_fast(driver):
    """
    Geoptimaliseerde datascraper voor snelheid
    """
    print("🚀 RijFlow Data Scraper - Snelle versie")
    print("=" * 50)
    
    alle_rijscholen_data = []
    
    try:
        with open('nederlandse_plaatsnamen.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        plaatsnamen = data.get('plaatsnamen', [])
        print(f"📋 {len(plaatsnamen)} examenplaatsen gevonden")
        
        for i, plaats in enumerate(plaatsnamen[100:]):
            print(f"📍 Verwerk plaats {i+1}/{len(plaatsnamen)}: {plaats}")
            
            try:
                # Open nieuw tabblad
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                
                # Ga naar CBR rijschoolzoeker
                driver.get("https://www.cbr.nl/nl/rijschoolzoeker")
                
                wait = WebDriverWait(driver, 8)  # Verlaagd van 10 naar 8 seconden
                
                # Zoek de zoekbalk
                search_selectors = [
                    "input[aria-label='Zoek een plaatsnaam']",
                    "input[placeholder='Plaats']",
                    "input.react-autosuggest_input",
                    "input[type='text']",
                    "input[autocomplete='off']"
                ]
                
                search_input = None
                for selector in search_selectors:
                    try:
                        search_input = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if search_input:
                            break
                    except Exception:
                        continue
                
                if search_input:
                    # Typ de plaatsnaam in de zoekbalk
                    search_input.clear()
                    search_input.send_keys(plaats)
                    time.sleep(0.5)
                    search_input.send_keys(Keys.ENTER)
                    
                    time.sleep(1)  # Verlaagd van 2 naar 1 seconde
                    
                    # Zoek en klik op de "Auto" knop
                    try:
                        # Maak het scherm kleiner voor betere zichtbaarheid
                        driver.execute_script("document.body.style.zoom = '0.8'")
                        
                        auto_button_selectors = [
                            "a.vehicle",
                            "a[class*='vehicle']",
                            "a:has(.vehicle__name:contains('Auto'))",
                            "a:has(.vehicle__name)",
                            "a.vehicle"
                        ]
                        
                        auto_button = None
                        for selector in auto_button_selectors:
                            try:
                                auto_button = wait.until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                )
                                if auto_button:
                                    vehicle_name = auto_button.find_element(By.CSS_SELECTOR, ".vehicle__name")
                                    if "Auto" in vehicle_name.text:
                                        break
                                    else:
                                        auto_button = None
                            except Exception:
                                continue
                        
                        # Als knop niet gevonden, scroll naar beneden
                        if not auto_button:
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(1)  # Verlaagd van 2 naar 1 seconde
                            
                            for selector in auto_button_selectors:
                                try:
                                    auto_button = wait.until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                    )
                                    if auto_button:
                                        vehicle_name = auto_button.find_element(By.CSS_SELECTOR, ".vehicle__name")
                                        if "Auto" in vehicle_name.text:
                                            break
                                        else:
                                            auto_button = None
                                except Exception:
                                    continue
                        
                        if auto_button:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", auto_button)
                            time.sleep(0.3)  # Verlaagd van 1 naar 0.3 seconde
                            
                            auto_button.click()
                            time.sleep(2)  # Verlaagd van 3 naar 2 seconden
                            
                            # Zoek en klik op de "Alfabetisch" knop
                            try:
                                time.sleep(1)  # Verlaagd van 2 naar 1 seconde
                                
                                alfabetisch_button_selectors = [
                                    "button.sorting__link.sorting__link--ASC",
                                    "button.sorting__link",
                                    "ul.sorting button.sorting__link",
                                    "li.sorting__option button.sorting__link",
                                    "button[class*='sorting__link']",
                                    "button[class*='sorting']",
                                    "button"
                                ]
                                
                                alfabetisch_button = None
                                for selector in alfabetisch_button_selectors:
                                    try:
                                        alfabetisch_button = wait.until(
                                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                        )
                                        if alfabetisch_button:
                                            button_text = alfabetisch_button.text.strip()
                                            if "Alfabetisch" in button_text or "Alphabetical" in button_text:
                                                break
                                            else:
                                                alfabetisch_button = None
                                    except Exception:
                                        continue
                                
                                # Als knop niet gevonden, scroll naar de sorting sectie
                                if not alfabetisch_button:
                                    try:
                                        sorting_section = driver.find_element(By.CSS_SELECTOR, "div.selector__section--sorting")
                                        if sorting_section:
                                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sorting_section)
                                            time.sleep(1)  # Verlaagd van 2 naar 1 seconde
                                        else:
                                            sorting_container = driver.find_element(By.CSS_SELECTOR, "ul.sorting")
                                            if sorting_container:
                                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sorting_container)
                                                time.sleep(1)  # Verlaagd van 2 naar 1 seconde
                                    except Exception:
                                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                        time.sleep(1)  # Verlaagd van 2 naar 1 seconde
                                    
                                    # Probeer opnieuw de knoppen te vinden na het scrollen
                                    for selector in alfabetisch_button_selectors:
                                        try:
                                            alfabetisch_button = wait.until(
                                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                            )
                                            if alfabetisch_button:
                                                button_text = alfabetisch_button.text.strip()
                                                if "Alfabetisch" in button_text or "Alphabetical" in button_text:
                                                    break
                                                else:
                                                    alfabetisch_button = None
                                        except Exception:
                                            continue
                                
                                if alfabetisch_button:
                                    button_text = alfabetisch_button.text.strip()
                                    
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", alfabetisch_button)
                                    time.sleep(0.3)  # Verlaagd van 1 naar 0.3 seconde
                                    
                                    if alfabetisch_button.is_enabled() and alfabetisch_button.is_displayed():
                                        alfabetisch_button.click()
                                        time.sleep(2)  # Verlaagd van 3 naar 2 seconden
                                        
                                        # Zoek en klik op alle zoekresultaten
                                        try:
                                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-row")))
                                            time.sleep(1)  # Verlaagd van 2 naar 1 seconde
                                            
                                            search_results = driver.find_elements(By.CSS_SELECTOR, "div.table-row")
                                            print(f"  📍 {len(search_results)} zoekresultaten gevonden")
                                            
                                            if search_results:
                                                plaats_rijscholen = []
                                                
                                                # Klik op elk zoekresultaat één voor één
                                                for j, result in enumerate(search_results):
                                                    # Sluit alle tabbladen die niet "rijschool" bevatten
                                                    while "rijschool" not in driver.current_url:
                                                        driver.close()
                                                        driver.switch_to.window(driver.window_handles[0])

                                                    try:
                                                        clickable_button = result.find_element(By.CSS_SELECTOR, "button.cell.cell--name")
                                                        
                                                        if clickable_button and clickable_button.is_enabled() and clickable_button.is_displayed():
                                                            rijschool_naam = clickable_button.text.strip().replace("\"", "").replace(",", "")
                                                            if rijschool_naam in list_of_rijscholen:
                                                                continue
                                                            
                                                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clickable_button)
                                                            time.sleep(0.2)  # Verlaagd van 0.5 naar 0.2 seconde
                                                            
                                                            # Klik op de linkerkant van de knop om advertenties te vermijden
                                                            driver.execute_script("""
                                                                var rect = arguments[0].getBoundingClientRect();
                                                                var x = rect.left + 10;
                                                                var y = rect.top + rect.height / 2;
                                                                
                                                                var clickEvent = new MouseEvent('click', {
                                                                    view: window,
                                                                    bubbles: true,
                                                                    cancelable: true,
                                                                    clientX: x,
                                                                    clientY: y
                                                                });
                                                                arguments[0].dispatchEvent(clickEvent);
                                                            """, clickable_button)
                                                            
                                                            time.sleep(1)  # Verlaagd van 2 naar 1 seconde
                                                            
                                                            # Scroll naar de contactgegevens sectie
                                                            try:
                                                                contact_container_selectors = [
                                                                    "p:has(a.details__contact)",
                                                                    "div:has(a.details__contact)",
                                                                    "a.details__contact"
                                                                ]
                                                                
                                                                contact_container = None
                                                                for selector in contact_container_selectors:
                                                                    try:
                                                                        contact_container = driver.find_element(By.CSS_SELECTOR, selector)
                                                                        if contact_container:
                                                                            break
                                                                    except Exception:
                                                                        continue
                                                                
                                                                if contact_container:
                                                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", contact_container)
                                                                    time.sleep(0.3)  # Verlaagd van 1 naar 0.3 seconde
                                                                else:
                                                                    driver.execute_script("window.scrollBy(0, 300);")
                                                                    time.sleep(0.3)  # Verlaagd van 1 naar 0.3 seconde
                                                                    
                                                            except Exception:
                                                                driver.execute_script("window.scrollBy(0, 300);")
                                                                time.sleep(0.3)  # Verlaagd van 1 naar 0.3 seconde
                                                            
                                                            time.sleep(0.5)  # Verlaagd van 1 naar 0.5 seconde
                                                            
                                                            # Extraheer contactgegevens
                                                            contact_info = extract_contact_info_fast(driver, rijschool_naam)
                                                            contact_info['plaatsnaam'] = plaats
                                                            plaats_rijscholen.append(contact_info)
                                                            
                                                            time.sleep(1)  # Verlaagd van 2 naar 1 seconde
                                                            
                                                            # Sluit de details weer
                                                            try:
                                                                if clickable_button.is_enabled() and clickable_button.is_displayed():
                                                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clickable_button)
                                                                    time.sleep(0.2)  # Verlaagd van 0.5 naar 0.2 seconde
                                                                    
                                                                    driver.execute_script("""
                                                                        var rect = arguments[0].getBoundingClientRect();
                                                                        var x = rect.left + 10;
                                                                        var y = rect.top + rect.height / 2;
                                                                        
                                                                        var clickEvent = new MouseEvent('click', {
                                                                            view: window,
                                                                            bubbles: true,
                                                                            cancelable: true,
                                                                            clientX: x,
                                                                            clientY: y
                                                                        });
                                                                        arguments[0].dispatchEvent(clickEvent);
                                                                    """, clickable_button)
                                                                else:
                                                                    try:
                                                                        new_button = result.find_element(By.CSS_SELECTOR, "button.cell.cell--name")
                                                                        if new_button.is_enabled() and new_button.is_displayed():
                                                                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", new_button)
                                                                            time.sleep(0.2)  # Verlaagd van 0.5 naar 0.2 seconde
                                                                            driver.execute_script("""
                                                                                var rect = arguments[0].getBoundingClientRect();
                                                                                var x = rect.left + 10;
                                                                                var y = rect.top + rect.height / 2;
                                                                                
                                                                                var clickEvent = new MouseEvent('click', {
                                                                                    view: window,
                                                                                    bubbles: true,
                                                                                    cancelable: true,
                                                                                    clientX: x,
                                                                                    clientY: y
                                                                                });
                                                                                arguments[0].dispatchEvent(clickEvent);
                                                                            """, new_button)
                                                                    except Exception:
                                                                        pass
                                                                
                                                                time.sleep(0.5)  # Verlaagd van 1 naar 0.5 seconde
                                                                
                                                            except Exception:
                                                                time.sleep(0.5)  # Verlaagd van 1 naar 0.5 seconde
                                                            
                                                        else:
                                                            pass
                                                            
                                                    except Exception:
                                                        continue
                                                
                                                alle_rijscholen_data.extend(plaats_rijscholen)
                                                print(f"  ✅ {len(plaats_rijscholen)} rijschoolgegevens verzameld voor {plaats}")
                                            else:
                                                print("  ⚠️ Geen zoekresultaten gevonden")
                                                
                                        except Exception as e:
                                            print(f"  ❌ Fout bij verwerken van zoekresultaten: {e}")
                                    else:
                                        print(f"  ⚠️ Knop '{button_text}' is niet klikbaar")
                                else:
                                    print("  ❌ Kon de 'Alfabetisch' knop niet vinden")
                                    
                            except Exception as e:
                                print(f"  ❌ Fout bij het klikken op de 'Alfabetisch' knop: {e}")
                        else:
                            print("  ❌ Kon de 'Auto' knop niet vinden")
                            
                    except Exception as e:
                        print(f"  ❌ Fout bij het klikken op de 'Auto' knop: {e}")
                
            except Exception as e:
                print(f"  ❌ Fout bij verwerken van plaats '{plaats}': {e}")
                continue

            time.sleep(1)  # Verlaagd van 2 naar 1 seconde
        
        print(f"\n💾 {len(alle_rijscholen_data)} rijschoolgegevens verzameld")
        
    except FileNotFoundError:
        print("❌ examen_plaatsen.json bestand niet gevonden!")
    except json.JSONDecodeError as e:
        print(f"❌ Fout bij het lezen van JSON: {e}")
    except Exception as e:
        print(f"❌ Onverwachte fout: {e}")

def main_fast():
    """
    Geoptimaliseerde hoofdfunctie
    """
    print("🚀 RijFlow Data Scraper - Snelle versie")
    print("=" * 50)
    
    driver = open_edge_browser_fast()
    
    if driver:
        try:
            # Ga naar Google om cookies te accepteren
            driver.get("https://www.google.com")
            accept_cookies_fast(driver)
            time.sleep(1)  # Verlaagd van 2 naar 1 seconde
            
            # Ga naar de CBR rijschoolzoeker
            driver.get("https://www.cbr.nl/nl/rijschoolzoeker")
            start_datascraper_fast(driver)
            
        except Exception as e:
            print(f"❌ Fout tijdens uitvoering: {e}")
        
        finally:
            input("\n👆 Druk op Enter om de browser te sluiten...")
            driver.quit()
    
    print("\n🎯 Klaar!")

if __name__ == "__main__":
    # Laad bestaande rijschoolnamen
    with open('rijscholen_leads.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            list_of_rijscholen.append(row[0])

    print(f"📋 {len(list_of_rijscholen)} bestaande rijscholen geladen")
    main_fast()