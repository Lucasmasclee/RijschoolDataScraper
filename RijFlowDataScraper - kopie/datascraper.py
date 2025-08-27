from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
import os

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

def close_browser(driver):
    """
    Sluit de browser
    """
    if driver:
        driver.quit()
        print("🔒 Browser gesloten")

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
            # Test: ga naar een eenvoudige pagina om te controleren of alles werkt
            print("🌐 Test: ga naar Google...")
            driver.get("https://www.google.com")
            
            # Wacht even zodat je kunt zien wat er gebeurt
            print("⏳ Wacht 5 seconden zodat je kunt zien wat er gebeurt...")
            time.sleep(5)
            
            print("✅ Test succesvol! Browser werkt correct.")
            
        except Exception as e:
            print(f"❌ Fout tijdens test: {e}")
        
        finally:
            # Vraag gebruiker of ze de browser willen sluiten
            input("\n👆 Druk op Enter om de browser te sluiten...")
            close_browser(driver)
    
    print("\n🎯 Klaar voor de volgende stap!")

if __name__ == "__main__":
    print("start")
    main()
