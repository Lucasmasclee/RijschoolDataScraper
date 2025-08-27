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

def open_edge_browser_simple():
    """
    Eenvoudige methode om Edge te openen - probeert direct zonder webdriver-manager
    """
    try:
        print("🔍 Probeer Edge direct te openen...")
        
        # Edge opties instellen
        edge_options = Options()
        edge_options.add_argument("--start-maximized")
        edge_options.add_argument("--disable-blink-features=AutomationControlled")
        edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        edge_options.add_experimental_option('useAutomationExtension', False)
        
        # Probeer Edge te openen zonder expliciete driver
        driver = webdriver.Edge(options=edge_options)
        
        # JavaScript uitvoeren om webdriver eigenschap te verbergen
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Microsoft Edge browser succesvol geopend!")
        print("🔍 Browser is zichtbaar (headless = false)")
        
        return driver
        
    except Exception as e:
        print(f"❌ Eenvoudige methode mislukt: {e}")
        return None

def open_edge_browser():
    """
    Opent een Microsoft Edge browser instance met headless = false
    zodat je kunt zien wat er gebeurt
    """
    # Probeer eerst de eenvoudige methode
    driver = open_edge_browser_simple()
    if driver:
        return driver
    
    # Als dat niet lukt, probeer de geavanceerde methode
    try:
        # Edge opties instellen
        edge_options = Options()
        edge_options.add_argument("--start-maximized")  # Browser maximaliseren
        edge_options.add_argument("--disable-blink-features=AutomationControlled")  # Detectie vermijden
        edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        edge_options.add_experimental_option('useAutomationExtension', False)
        
        # Probeer eerst de geïnstalleerde Edge driver te gebruiken
        try:
            print("🔍 Zoeken naar geïnstalleerde Edge driver...")
            # Controleer of msedgedriver.exe al bestaat in de huidige directory
            if os.path.exists("msedgedriver.exe"):
                print("✅ Gevonden: msedgedriver.exe in huidige directory")
                service = Service("msedgedriver.exe")
            else:
                print("📥 Downloaden van Edge driver via webdriver-manager...")
                service = Service(EdgeChromiumDriverManager().install())
        except Exception as download_error:
            print(f"⚠️ Download mislukt: {download_error}")
            print("🔄 Probeer handmatige installatie...")
            
            # Probeer Edge te openen zonder expliciete driver (Windows kan dit vaak zelf vinden)
            try:
                print("🔍 Probeer Edge te openen zonder expliciete driver...")
                driver = webdriver.Edge(options=edge_options)
                print("✅ Edge geopend zonder expliciete driver!")
                return driver
            except Exception as fallback_error:
                print(f"❌ Fallback mislukt: {fallback_error}")
                raise Exception("Kan Edge driver niet vinden of installeren")
        
        # Browser openen met gevonden driver
        driver = webdriver.Edge(service=service, options=edge_options)
        
        # JavaScript uitvoeren om webdriver eigenschap te verbergen
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Microsoft Edge browser succesvol geopend!")
        print("🔍 Browser is zichtbaar (headless = false)")
        
        return driver
        
    except Exception as e:
        print(f"❌ Fout bij het openen van Edge browser: {e}")
        print("\n💡 Mogelijke oplossingen:")
        print("1. Controleer je internetverbinding")
        print("2. Download handmatig msedgedriver.exe van:")
        print("   https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
        print("3. Plaats msedgedriver.exe in dezelfde map als dit script")
        print("4. Zorg ervoor dat Microsoft Edge geïnstalleerd is")
        return None

def accept_cookies(driver):
    """
    Accepteert automatisch alle cookies door op de "Alles accepteren" knop te klikken
    """
    try:
        print("🍪 Zoeken naar cookie acceptatie knop...")
        
        # Wacht tot de cookie banner verschijnt (maximaal 10 seconden)
        wait = WebDriverWait(driver, 10)
        
        # Probeer verschillende selectors voor de "Alles accepteren" knop
        cookie_selectors = [
            "button[id='L2AGLb']",  # Google's standaard cookie acceptatie knop
            "button:contains('Alles accepteren')",  # Nederlandse tekst
            "button:contains('Accept all')",  # Engelse tekst
            "button[aria-label*='Accept']",  # Aria-label met accept
            "button[data-ved*='accept']",  # Data-ved attribuut
            ".QS5gu.sy4vM",  # Class combinatie uit de HTML
            "button.tHlp8d"  # Class van de button
        ]
        
        cookie_button = None
        
        for selector in cookie_selectors:
            try:
                if selector.startswith("button:contains"):
                    # Voor contains selectors, zoek naar tekst
                    text = selector.split("'")[1]
                    cookie_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{text}')]"))
                    )
                else:
                    cookie_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                
                if cookie_button:
                    print(f"✅ Cookie knop gevonden met selector: {selector}")
                    break
                    
            except Exception:
                continue
        
        if cookie_button:
            # Scroll naar de knop om ervoor te zorgen dat deze zichtbaar is
            driver.execute_script("arguments[0].scrollIntoView(true);", cookie_button)
            time.sleep(1)
            
            # Klik op de knop
            cookie_button.click()
            print("✅ Cookies succesvol geaccepteerd!")
            
            # Wacht even zodat de cookie banner verdwijnt
            time.sleep(2)
            return True
            
        else:
            print("⚠️ Geen cookie acceptatie knop gevonden - mogelijk zijn cookies al geaccepteerd")
            return False
            
    except Exception as e:
        print(f"⚠️ Fout bij het accepteren van cookies: {e}")
        print("💡 Mogelijk zijn cookies al geaccepteerd of is er geen cookie banner")
        return False

def close_browser(driver):
    """
    Sluit de browser
    """
    if driver:
        driver.quit()
        print("🔒 Browser gesloten")

def start_datascraper(driver):
    """
    Start de datascraper
    """
    print("🚀 RijFlow Data Scraper - Stap 2: Start de datascraper")
    print("=" * 50)
    
    try:
        # Open examen_plaatsen.json
        with open('examen_plaatsen.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Haal de plaatsnamen op uit de JSON structuur
        plaatsnamen = data.get('plaatsnamen', [])
        
        # print(f"📋 Gevonden {len(plaatsnamen)} examenplaatsen:")
        # for plaats in plaatsnamen:
        #     print(f"  - {plaats}")
        
        # Voor elke plaats: open nieuw tabb        print(f"📋 Gevonden {len(plaatsnamen)} examenplaatsen:")
        for plaats in plaatsnamen:
            print(f"  - {plaats}")
        
        # Voor elke plaats: open nieuw tabblad en zoek
        print("\n🔍 Start met data scraping voor elke plaats...")
        
        for i, plaats in enumerate(plaatsnamen):
            print(f"\n📍 Verwerk plaats {i+1}/{len(plaatsnamen)}: {plaats}")
            
            try:
                # Open nieuw tabblad
                print("  📑 Open nieuw tabblad...")
                driver.execute_script("window.open('');")
                
                # Schakel naar het nieuwe tabblad
                driver.switch_to.window(driver.window_handles[-1])
                
                # Ga naar CBR rijschoolzoeker
                print("  🌐 Navigeer naar CBR rijschoolzoeker...")
                driver.get("https://www.cbr.nl/nl/rijschoolzoeker")
                
                # Wacht tot de pagina geladen is
                wait = WebDriverWait(driver, 10)
                
                # Zoek de zoekbalk (zoekbalk voor plaatsnaam)
                print("  🔍 Zoek naar de zoekbalk...")
                
                # Probeer verschillende selectors voor de zoekbalk
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
                            # print(f"    ✅ Zoekbalk gevonden met selector: {selector}")
                            break
                    except Exception:
                        continue
                
                if search_input:
                    # Typ de plaatsnaam in de zoekbalk
                    # print(f"  ✏️ Typ plaatsnaam: {plaats}")
                    search_input.clear()
                    search_input.send_keys(plaats)
                    search_input.send_keys(Keys.ENTER)
                    
                    # Wacht even zodat de suggesties kunnen laden
                    time.sleep(2)
                    
                    print(f"  ✅ Plaatsnaam '{plaats}' succesvol ingetypt in zoekbalk")
                    
                    # Zoek en klik op de "Auto" knop
                    # print("   Zoek naar de 'Auto' knop...")
                    try:
                        # Oplossing 1: Maak het scherm kleiner (Ctrl + -)
                        # print("  🔍 Probeer scherm kleiner te maken...")
                        driver.execute_script("document.body.style.zoom = '0.8'")
                        time.sleep(1)
                        
                        # Probeer verschillende selectors voor de Auto knop
                        auto_button_selectors = [
                            "a.vehicle",
                            "a[class*='vehicle']",
                            "a:has(.vehicle__name:contains('Auto'))",
                            "a:has(.vehicle__name)"
                        ]
                        
                        auto_button = None
                        for selector in auto_button_selectors:
                            try:
                                # Wacht tot de knop zichtbaar is
                                auto_button = wait.until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                )
                                if auto_button:
                                    # Controleer of dit de juiste knop is (bevat "Auto" tekst)
                                    vehicle_name = auto_button.find_element(By.CSS_SELECTOR, ".vehicle__name")
                                    if "Auto" in vehicle_name.text:
                                        print(f"  ✅ Auto knop gevonden met selector: {selector}")
                                        break
                                    else:
                                        auto_button = None
                            except Exception:
                                continue
                        
                        # Oplossing 2: Als knop nog niet gevonden, scroll naar beneden
                        if not auto_button:
                            print("  🔍 Knop niet gevonden, scroll naar beneden...")
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(2)
                            
                            # Probeer opnieuw de knoppen te vinden na het scrollen
                            for selector in auto_button_selectors:
                                try:
                                    auto_button = wait.until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                    )
                                    if auto_button:
                                        # Controleer of dit de juiste knop is (bevat "Auto" tekst)
                                        vehicle_name = auto_button.find_element(By.CSS_SELECTOR, ".vehicle__name")
                                        if "Auto" in vehicle_name.text:
                                            print(f"  ✅ Auto knop gevonden na scrollen met selector: {selector}")
                                            break
                                        else:
                                            auto_button = None
                                except Exception:
                                    continue
                        
                        if auto_button:
                            # Scroll naar de knop om ervoor te zorgen dat deze zichtbaar is
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", auto_button)
                            time.sleep(1)
                            
                            # Klik op de Auto knop
                            # print("  🖱️ Klik op de 'Auto' knop...")
                            auto_button.click()
                            print("  ✅ Auto knop succesvol geklikt!")
                            
                            # Wacht even zodat de pagina kan laden na het klikken
                            time.sleep(3)
                            
                            # Zoek en klik op de "Alfabetisch" knop (gebruik dezelfde logica als Auto knop)
                            print("  🔍 Zoek naar de 'Alfabetisch' knop...")
                            try:
                                # Wacht even zodat de pagina geladen is na het klikken op Auto
                                time.sleep(2)
                                
                                # Gebruik dezelfde logica als voor de Auto knop
                                # Gebaseerd op de HTML structuur: button.sorting__link binnen ul.sorting
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
                                        print(f"  🔍 Probeer selector: {selector}")
                                        alfabetisch_button = wait.until(
                                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                        )
                                        if alfabetisch_button:
                                            # Controleer of dit de juiste knop is (bevat "Alfabetisch" tekst)
                                            button_text = alfabetisch_button.text.strip()
                                            print(f"  📍 Gevonden knop met tekst: '{button_text}'")
                                            if "Alfabetisch" in button_text or "Alphabetical" in button_text:
                                                print(f"  ✅ Alfabetisch knop gevonden met selector: {selector}")
                                                break
                                            else:
                                                print(f"  ⚠️ Verkeerde knop, zoek verder...")
                                                alfabetisch_button = None
                                    except Exception as e:
                                        print(f"  ❌ Selector '{selector}' mislukt: {e}")
                                        continue
                                
                                # Als knop nog niet gevonden, scroll naar de sorting sectie
                                if not alfabetisch_button:
                                    print("  🔍 Knop niet gevonden, scroll naar de sorting sectie...")
                                    try:
                                        # Zoek eerst naar de sorting sectie container
                                        sorting_section = driver.find_element(By.CSS_SELECTOR, "div.selector__section--sorting")
                                        if sorting_section:
                                            # Scroll naar de sorting sectie
                                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sorting_section)
                                            time.sleep(2)
                                            print("  📍 Scrolled naar sorting sectie")
                                        else:
                                            # Fallback: zoek naar ul.sorting
                                            sorting_container = driver.find_element(By.CSS_SELECTOR, "ul.sorting")
                                            if sorting_container:
                                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sorting_container)
                                                time.sleep(2)
                                                print("  📍 Scrolled naar ul.sorting container")
                                    except Exception:
                                        # Fallback: scroll naar beneden
                                        print("  🔍 Fallback: scroll naar beneden...")
                                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                        time.sleep(2)
                                    
                                    # Probeer opnieuw de knoppen te vinden na het scrollen
                                    print("  🔍 Probeer opnieuw na scrollen...")
                                    for selector in alfabetisch_button_selectors:
                                        try:
                                            print(f"  🔍 Probeer selector (na scrollen): {selector}")
                                            alfabetisch_button = wait.until(
                                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                            )
                                            if alfabetisch_button:
                                                # Controleer of dit de juiste knop is (bevat "Alfabetisch" tekst)
                                                button_text = alfabetisch_button.text.strip()
                                                print(f"  📍 Gevonden knop na scrollen met tekst: '{button_text}'")
                                                if "Alfabetisch" in button_text or "Alphabetical" in button_text:
                                                    print(f"  ✅ Alfabetisch knop gevonden na scrollen met selector: {selector}")
                                                    break
                                                else:
                                                    print(f"  ⚠️ Verkeerde knop na scrollen, zoek verder...")
                                                    alfabetisch_button = None
                                        except Exception as e:
                                            print(f"  ❌ Selector '{selector}' mislukt na scrollen: {e}")
                                            continue
                                
                                if alfabetisch_button:
                                    # Extra verificatie: controleer of dit echt de Alfabetisch knop is
                                    button_text = alfabetisch_button.text.strip()
                                    button_classes = alfabetisch_button.get_attribute("class")
                                    
                                    print(f"  🔍 Gevonden knop: '{button_text}' met classes: {button_classes}")
                                    
                                    # Scroll naar de knop om ervoor te zorgen dat deze zichtbaar is
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", alfabetisch_button)
                                    time.sleep(1)
                                    
                                    # Controleer of de knop klikbaar is
                                    if alfabetisch_button.is_enabled() and alfabetisch_button.is_displayed():
                                        # Klik op de Alfabetisch knop
                                        print(f"  🖱️ Klik op de '{button_text}' knop...")
                                        alfabetisch_button.click()
                                        print(f"  ✅ Alfabetisch knop succesvol geklikt!")
                                        
                                        # Wacht even zodat de pagina kan laden na het klikken
                                        time.sleep(3)
                                        
                                        # Zoek en klik op alle zoekresultaten
                                        print("  🔍 Zoek naar alle zoekresultaten...")
                                        try:
                                            # Wacht tot de zoekresultaten geladen zijn
                                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-row")))
                                            time.sleep(2)  # Extra wachttijd voor volledige laad
                                            
                                            # Zoek alle zoekresultaten
                                            search_results = driver.find_elements(By.CSS_SELECTOR, "div.table-row")
                                            print(f"  📍 Gevonden {len(search_results)} zoekresultaten")
                                            
                                            if search_results:
                                                # Klik op elk zoekresultaat één voor één
                                                for i, result in enumerate(search_results):
                                                    try:
                                                        # Zoek de klikbare knop binnen dit resultaat
                                                        clickable_button = result.find_element(By.CSS_SELECTOR, "button.cell.cell--name")
                                                        
                                                        if clickable_button and clickable_button.is_enabled() and clickable_button.is_displayed():
                                                            # Haal de rijschoolnaam op voor logging
                                                            rijschool_naam = clickable_button.text.strip()
                                                            print(f"  🖱️ Klik op resultaat {i+1}/{len(search_results)}: {rijschool_naam[:50]}...")
                                                            
                                                            # Scroll naar de knop om ervoor te zorgen dat deze zichtbaar is
                                                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clickable_button)
                                                            time.sleep(0.5)
                                                            
                                                            # Klik op de knop
                                                            clickable_button.click()
                                                            print(f"  ✅ Resultaat {i+1} succesvol geklikt!")
                                                            
                                                            # Wacht even zodat de details kunnen laden
                                                            time.sleep(2)
                                                            
                                                            # Sluit de details weer (klik opnieuw op dezelfde knop)
                                                            clickable_button.click()
                                                            print(f"  🔒 Details van resultaat {i+1} gesloten")
                                                            time.sleep(1)
                                                            
                                                        else:
                                                            print(f"  ⚠️ Knop voor resultaat {i+1} is niet klikbaar")
                                                            
                                                    except Exception as e:
                                                        print(f"  ❌ Fout bij klikken op resultaat {i+1}: {e}")
                                                        continue
                                                
                                                print(f"  ✅ Alle {len(search_results)} zoekresultaten succesvol verwerkt!")
                                            else:
                                                print("  ⚠️ Geen zoekresultaten gevonden")
                                                
                                        except Exception as e:
                                            print(f"  ❌ Fout bij verwerken van zoekresultaten: {e}")
                                    else:
                                        print(f"  ⚠️ Knop '{button_text}' is niet klikbaar (enabled: {alfabetisch_button.is_enabled()}, displayed: {alfabetisch_button.is_displayed()})")
                                else:
                                    print("  ❌ Kon de 'Alfabetisch' knop niet vinden")
                                    
                            except Exception as e:
                                print(f"  ❌ Fout bij het klikken op de 'Alfabetisch' knop: {e}")
                        else:
                            print("  ❌ Kon de 'Auto' knop niet vinden, zelfs na scrollen")
                            
                    except Exception as e:
                        print(f"  ❌ Fout bij het klikken op de 'Auto' knop: {e}")
                
            except Exception as e:
                print(f"  ❌ Fout bij verwerken van plaats '{plaats}': {e}")
                continue

            time.sleep(2)
        
        print(f"\n🎯 Data scraping voltooid voor alle {len(plaatsnamen)} plaatsen!")
        print("💡 Alle tabbladen zijn geopend en klaar voor verdere verwerking")
        
    except FileNotFoundError:
        print("❌ examen_plaatsen.json bestand niet gevonden!")
    except json.JSONDecodeError as e:
        print(f"❌ Fout bij het lezen van JSON: {e}")
    except Exception as e:
        print(f"❌ Onverwachte fout: {e}")

def main():
    """
    Hoofdfunctie om de browser te openen en te testen
    """
    print("🚀 RijFlow Data Scraper - Stap 1: Edge Browser Openen")
    print("=" * 50)
    
    # Browser openen
    driver = open_edge_browser()
    
    if driver:
        try:
            # Ga naar Google om cookies te accepteren
            print("🌐 Ga naar Google om cookies te accepteren...")
            driver.get("https://www.google.com")
            
            # Probeer automatisch cookies te accepteren
            accept_cookies(driver)
            
            # Wacht even zodat de cookies verwerkt zijn
            print("⏳ Wacht 2 seconden zodat cookies verwerkt zijn...")
            time.sleep(2)
            
            # Ga naar de CBR rijschoolzoeker
            print("🌐 Ga naar CBR rijschoolzoeker...")
            driver.get("https://www.cbr.nl/nl/rijschoolzoeker")

            start_datascraper(driver)
            
            print("✅ CBR rijschoolzoeker succesvol geopend!")
            
        except Exception as e:
            print(f"❌ Fout tijdens uitvoering: {e}")
        
        finally:
            # Vraag gebruiker of ze de browser willen sluiten
            input("\n👆 Druk op Enter om de browser te sluiten...")
            close_browser(driver)
    
    print("\n🎯 Klaar voor de volgende stap!")

if __name__ == "__main__":
    print("start")
    main()
    print("end")
