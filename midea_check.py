import os
import time
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ── Config ────────────────────────────────────────────────────
NTFY_TOPIC   = "midea-portasplit-stock"
NTFY_SERVER  = "https://ntfy.sh"
CHROMIUM_PATH = "/data/data/com.termux/files/usr/bin/chromium-browser"

# ── Boutiques ─────────────────────────────────────────────────
STORES = [
    # ── France ────────────────────────────────────────────────
    {
        "name": "ManoMano FR", "flag": "FR",
        "url": "https://www.manomano.fr/p/midea-climatiseur-split-mobile-reversible-froid-chaud-3500w12000btu-wifi-deshumidificateur-ventilateur-jusqua-40m2-kit-fenetre-inclus-83810402",
        "in_stock":  ["en stock", "ajouter au panier", "add to cart"],
        "out_stock": ["rupture", "indisponible", "epuise", "out of stock"],
        "btn_selectors": ["button[data-testid*='add']", "button[data-testid*='cart']", ".add-to-cart"],
    },
    {
        "name": "Fnac", "flag": "FR",
        "url": "https://www.fnac.com/MIDEA-Climatiseur-Split-Mobile-Reversible-Froid-Chaud-3500W-12000BTU-WiFi-deshumidificateur-ventilateur-jusqu-a-40m2-kit-fenetre-inclus/a21457105/w-4",
        "in_stock":  ["ajouter au panier", "livraison", "disponible"],
        "out_stock": ["rupture", "indisponible", "epuise", "temporairement"],
        "btn_selectors": [".f-buyBox-addToCart", "button[data-automation*='add']", ".addToCart"],
    },
    {
        "name": "Boulanger", "flag": "FR",
        "url": "https://www.boulanger.com/ref/1216685",
        "in_stock":  ["ajouter au panier", "retrait 1h", "disponible", "livraison"],
        "out_stock": ["rupture", "indisponible", "epuise", "non disponible"],
        "btn_selectors": ["button[data-ref='add-to-cart']", ".product-add-to-cart", "button[class*='addToCart']"],
    },
    {
        "name": "Amazon FR", "flag": "FR",
        "url": "https://www.amazon.fr/dp/B0CY2YW8BT",
        "in_stock":  ["en stock", "ajouter au panier", "expedie par amazon"],
        "out_stock": ["actuellement indisponible", "rupture de stock"],
        "btn_selectors": ["#add-to-cart-button", "#buy-now-button"],
    },
    {
        "name": "Darty", "flag": "FR",
        "url": "https://www.darty.com/nav/extra/list?text=MIDEA+PortaSplit+MMCS-12HRN8",
        "in_stock":  ["ajouter au panier", "en stock", "disponible"],
        "out_stock": ["rupture", "indisponible", "epuise"],
        "btn_selectors": [".add-to-cart", "button[data-ref*='cart']", "button[class*='addToCart']"],
    },
    {
        "name": "Cdiscount", "flag": "FR",
        "url": "https://www.cdiscount.com/search/10/MIDEA+PortaSplit.html",
        "in_stock":  ["ajouter au panier", "en stock", "disponible"],
        "out_stock": ["rupture", "indisponible", "epuise"],
        "btn_selectors": [".addToCart", "#addToCart", "button[class*='cart']"],
    },
    {
        "name": "Optimea (neuf)", "flag": "FR",
        "url": "https://www.optimea.fr/product/climatiseur-split-mobile-midea/",
        "in_stock":  ["ajouter au panier", "add to cart"],
        "out_stock": ["out of stock", "rupture", "epuise", "indisponible"],
        "btn_selectors": [".single_add_to_cart_button", "button[name='add-to-cart']", ".add_to_cart_button"],
    },
    {
        "name": "Optimea (destockage)", "flag": "FR",
        "url": "https://www.optimea.fr/product/destockage-climatiseur-split-mobile-midea-silencieux-reversible-sans-installation/",
        "in_stock":  ["ajouter au panier", "add to cart"],
        "out_stock": ["out of stock", "rupture", "epuise", "indisponible"],
        "btn_selectors": [".single_add_to_cart_button", "button[name='add-to-cart']", ".add_to_cart_button"],
    },
    {
        "name": "Optimea (seconde vie)", "flag": "FR",
        "url": "https://www.optimea.fr/product/seconde-vie-climatiseur-split-mobile-midea-silencieux-reversible-sans-installation/",
        "in_stock":  ["ajouter au panier", "add to cart"],
        "out_stock": ["out of stock", "rupture", "epuise", "indisponible"],
        "btn_selectors": [".single_add_to_cart_button", "button[name='add-to-cart']", ".add_to_cart_button"],
    },
    {
        "name": "PAC Store FR", "flag": "FR",
        "url": "https://www.pac-store.fr/boutique/MIDEA-Climatiseur-mobile-PortaSplit-3-5-kW-R32-p671790674",
        "in_stock":  ["ajouter au panier", "en stock", "commander"],
        "out_stock": ["rupture", "indisponible", "epuise", "out of stock"],
        "btn_selectors": [".add-to-cart", "#addToCart", "button[class*='cart']"],
    },
    {
        "name": "JBS Electromenager", "flag": "FR",
        "url": "https://jbs-electromenager.com/products/climatiseur-mobile-midea-mmcs-12hrn8-qrd0",
        "in_stock":  ["add to cart", "ajouter au panier"],
        "out_stock": ["sold out", "rupture", "out of stock", "indisponible"],
        "btn_selectors": ["button[name='add']", ".product-form__cart-submit", "button[class*='add-to-cart']"],
    },
    {
        "name": "Hemmera FR", "flag": "FR",
        "url": "https://www.hemmera.fr/climatiseur-portable-midea-mmcs-12hrn8-qrd0-blanc/",
        "in_stock":  ["ajouter au panier", "add to cart", "en stock", "commander"],
        "out_stock": ["rupture", "indisponible", "epuise", "out of stock"],
        "btn_selectors": [".add-to-cart", ".btn-cart", "button[class*='add']"],
    },
    {
        "name": "Bruneau FR", "flag": "FR",
        "url": "https://www.bruneau.fr/product/climatiseur-mobile-midea-mmcs-12hrn8-qrd0/8497277",
        "in_stock":  ["ajouter au panier", "commander", "en stock", "disponible"],
        "out_stock": ["rupture", "indisponible", "epuise"],
        "btn_selectors": [".add-to-cart", "button[class*='cart']", "#addToCart"],
    },
    # ── Belgique / Pays-Bas ────────────────────────────────────
    {
        "name": "Coolblue BE", "flag": "BE",
        "url": "https://www.coolblue.be/fr/recherche?query=Midea+PortaSplit",
        "in_stock":  ["dans le panier", "livraison demain", "disponible", "op voorraad"],
        "out_stock": ["indisponible", "niet op voorraad", "rupture"],
        "btn_selectors": [".add-to-cart-button", "button[class*='add-to-cart']", "[data-testid='add-to-cart']"],
    },
    {
        "name": "Coolblue NL", "flag": "NL",
        "url": "https://www.coolblue.nl/zoeken?query=Midea+PortaSplit",
        "in_stock":  ["in winkelwagen", "morgen in huis", "op voorraad"],
        "out_stock": ["niet op voorraad", "uitverkocht"],
        "btn_selectors": [".add-to-cart-button", "button[class*='add-to-cart']"],
    },
    {
        "name": "MediaMarkt BE", "flag": "BE",
        "url": "https://www.mediamarkt.be/fr/search.html?query=Midea+PortaSplit",
        "in_stock":  ["ajouter au panier", "en stock", "disponible"],
        "out_stock": ["indisponible", "niet op voorraad", "rupture"],
        "btn_selectors": ["button[data-test*='add']", "[class*='add-to-cart']"],
    },
    # ── Allemagne ──────────────────────────────────────────────
    {
        "name": "MediaMarkt DE", "flag": "DE",
        "url": "https://www.mediamarkt.de/de/product/_midea-portasplit-cool-split-klimaanlage-weissgrau-max-raumgrosse-70-m-3035466.html",
        "in_stock":  ["in den einkaufswagen", "auf lager", "jetzt kaufen", "lieferbar"],
        "out_stock": ["nicht verfugbar", "ausverkauft", "nicht lieferbar"],
        "btn_selectors": ["button[data-test*='add']", "[class*='add-to-cart']", "button[class*='AddToCart']"],
    },
    {
        "name": "Conrad DE", "flag": "DE",
        "url": "https://www.conrad.de/de/search.html?search=Midea+PortaSplit",
        "in_stock":  ["in den warenkorb", "auf lager", "sofort lieferbar"],
        "out_stock": ["nicht verfugbar", "ausverkauft"],
        "btn_selectors": ["button[class*='add-to-cart']", ".add-to-cart", "[data-testid*='cart']"],
    },
    {
        "name": "Amazon DE", "flag": "DE",
        "url": "https://www.amazon.de/s?k=Midea+PortaSplit+MMCS-12HRN8",
        "in_stock":  ["in den einkaufswagen", "auf lager"],
        "out_stock": ["derzeit nicht verfugbar", "nicht auf lager"],
        "btn_selectors": ["#add-to-cart-button", ".a-button-input"],
    },
    # ── Espagne ────────────────────────────────────────────────
    {
        "name": "Amazon ES", "flag": "ES",
        "url": "https://www.amazon.es/s?k=Midea+PortaSplit+MMCS-12HRN8",
        "in_stock":  ["anadir al carrito", "en stock", "disponible"],
        "out_stock": ["actualmente no disponible", "agotado"],
        "btn_selectors": ["#add-to-cart-button"],
    },
    {
        "name": "PcComponentes ES", "flag": "ES",
        "url": "https://www.pccomponentes.com/buscar/?query=Midea+PortaSplit",
        "in_stock":  ["anadir al carrito", "en stock", "disponible"],
        "out_stock": ["agotado", "no disponible", "sin stock"],
        "btn_selectors": ["button[class*='add-to-cart']", ".add-to-cart"],
    },
    # ── Italie ─────────────────────────────────────────────────
    {
        "name": "Amazon IT", "flag": "IT",
        "url": "https://www.amazon.it/s?k=Midea+PortaSplit+MMCS-12HRN8",
        "in_stock":  ["aggiungi al carrello", "disponibile"],
        "out_stock": ["momentaneamente non disponibile", "esaurito"],
        "btn_selectors": ["#add-to-cart-button"],
    },
]

# ── Selenium setup ─────────────────────────────────────────────
def make_driver():
    opts = Options()
    is_github_actions = "GITHUB_ACTIONS" in os.environ

    if is_github_actions:
        print("🔧 Environnement : GitHub Actions")
        opts.add_argument("--headless=new")
    else:
        print("📱 Environnement : Local (Termux)")
        opts.binary_location = CHROMIUM_PATH
        opts.add_argument("--headless")

    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--lang=fr-FR")
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    if is_github_actions:
        driver = webdriver.Chrome(options=opts)
    else:
        service = Service(executable_path=CHROMIUM_PATH)
        driver = webdriver.Chrome(service=service, options=opts)
        
    driver.set_page_load_timeout(30)
    return driver

# ── Checker ────────────────────────────────────────────────────
def check_store(driver, store):
    try:
        driver.get(store["url"])
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)

        # 1. Bouton panier spécifique
        for sel in store.get("btn_selectors", []):
            try:
                btn = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
                if btn.is_displayed():
                    btn_text = btn.text.lower()
                    if any(out_word in btn_text for out_word in store["out_stock"]):
                        continue
                    return True, f"bouton panier actif ({sel})"
            except Exception:
                pass

        # 2. Fallback Analyse textuelle
        text = driver.find_element(By.TAG_NAME, "body").text.lower()
        for signal in store["out_stock"]:
            if signal in text:
                return False, f"rupture: '{signal}'"

        for signal in store["in_stock"]:
            if signal in text:
                return True, f"stock détecté: '{signal}'"

        return False, "aucun signal clair"

    except Exception as e:
        return False, "erreur: " + str(e)[:50]

# ── Alerte ntfy ───────────────────────────────────────────────
def notify(winners):
    lines = [w["flag"] + " " + w["name"] + "\n" + w["url"] for w in winners]
    body  = "\n\n".join(lines)
    try:
        requests.post(
            NTFY_SERVER + "/" + NTFY_TOPIC,
            data=body.encode("utf-8"),
            headers={
                "Title":  "Midea PortaSplit EN STOCK !",
                "Priority": "urgent",
                "Tags":     "white_check_mark,snowflake",
            },
            timeout=10,
        )
        print("  Notification ntfy envoyee !")
    except Exception as e:
        print("  ntfy echoue: " + str(e))

# ── Main ──────────────────────────────────────────────────────
def main():
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    print(f"\n=== Midea PortaSplit Stock Check v4.1 === {now}")
    print(f"{len(STORES)} boutiques chargées\n")

    driver = make_driver()
    winners = []

    try:
        for store in STORES:
            in_stock, reason = check_store(driver, store)
            icon = "✅" if in_stock else "❌"
            print(f"[{icon}] {store['flag']} {store['name']} ({reason})")
            if in_stock:
                winners.append(store)
            time.sleep(2)
    finally:
        driver.quit()

    print(f"\nResultat: {len(winners)}/{len(STORES)} en stock")

    if winners:
        print("\nTROUVE ! Envoi alerte...")
        notify(winners)
    else:
        print("Toujours en rupture.")
    print()

if __name__ == "__main__":
    main()
