import time
import re
from collections import Counter
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select as select
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

# driver.find_element uvijek ruši test ukoliko ne možemo naći element u zadanome roku


user_input = ""
lista_proizvoda_na_sajtu = []
lista_odabranih_proizvoda = []

# Dobivamo listu proizvoda sa sajta (headless Chrome) - radi novi update svaki put kada se test pokrene u slučaju da se dodaju novi proizvodi, promjene vrijednosti, itd


def product_name_list():
    try:
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--headless")
        options.add_experimental_option(
            "excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(15)
        driver.get("https://rahulshettyacademy.com/seleniumPractise/#/")
        _lista_proizvoda_na_sajtu = driver.find_elements(
            By.CLASS_NAME, value="product-name")
        for proizvod in _lista_proizvoda_na_sajtu:
            lista_proizvoda_na_sajtu.append(proizvod.text)
            print(proizvod.text)
    except Exception() as e:
        print("Greška u dohvaćanju podataka", e)
    finally:
        driver.close()


# Definiramo korisnički input


def user_input_check(user_input):
    global broj_odabranih_proizvoda
    try:
        print("Test se pokreće, molim pričekajte...")
        max_input_num = 3
        # Pozivamo funkciju product_name_list() gdje screjpamo sve proizvode sa sajta u listu da prikažemo korisniku
        product_name_list()
        while max_input_num > 0:
            # Korisnik unosi svoje podatke ovdje
            user_input = str(
                input(f"Izaberite svoj proizvod sa gore navedene liste, možete odabrati još {max_input_num} proizvod(a): ")).title()
            # Provjera korisničkih podataka
            if user_input.isnumeric():
                print(
                    "Krivi unos, naziv proizvoda ne može biti samo broj, molimo unesite točan naziv proizvoda sa ponuđene liste")
            elif user_input not in lista_proizvoda_na_sajtu:
                print(
                    "Odabrani proizvod se trenutno ne nalazi u našoj ponudi, pokušate ponovo (unesite puni naziv proizvoda)")
            elif len(user_input) < 1:
                pass
            else:
                max_input_num -= 1
                lista_odabranih_proizvoda.append(user_input)
        # Možemo ovdje dodati logiku da ograničimo broj progrešnih unosa, za svrhe ovoga testa nije potrebno
        print(f"Odabrali ste proizvode:")
        # Lista odabranih proizvoda i logika za više istih odabranih proizvoda
        broj_odabranih_proizvoda = Counter(lista_odabranih_proizvoda)
        for naziv in broj_odabranih_proizvoda:
            print(str(broj_odabranih_proizvoda[naziv]) + "x ", str(naziv))
        print("User input test JE prošao")
    except Exception() as e:
        print("User input test NIJE prošao", e)


def browser_automation():
    try:
        # Navigacija i dobivanje elemenata u listu
        options2 = Options()
        options2.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=options2)
        driver.maximize_window()
        driver.get("https://rahulshettyacademy.com/seleniumPractise/#/")
        _web_proizvodi_elements_list = driver.find_elements(
            By.XPATH, value=r"""//*[@id="root"]/div/div[1]/div/div[*]""")
        # Logika za odabir jednog ili više proizvoda te dodavanje u košaricu
        cijena_proizvoda_pocetna = int(0)
        for naziv in broj_odabranih_proizvoda:
            broj_klikova = broj_odabranih_proizvoda[naziv]
            naziv_proizvoda_klik = naziv
            index_proizvoda = lista_proizvoda_na_sajtu.index(naziv) + 1
            if broj_klikova == 1:
                driver.execute_script(
                    "window.scrollTo({ top: 0 });")
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                    (By.XPATH, f"""//*[@id="root"]/div/div[1]/div/div[{index_proizvoda}]/div[3]/button"""))).click()
                time.sleep(1)
                # Dobivanje cijene sa početne strane
                cijena_proizvoda = driver.find_element(
                    By.XPATH, value=f"""//*[@id="root"]/div/div[1]/div/div[{index_proizvoda}]/p""").text
                cijena_proizvoda_pocetna += int(cijena_proizvoda)

            elif broj_klikova > 1:
                broj_potrebnih_klikova = 1
                # Radi optimizacije, ovdje dohvaćamo cijenu samo 1 put za računanje totalne cijene
                cijena_proizvoda = driver.find_element(
                    By.XPATH, value=f"""//*[@id="root"]/div/div[1]/div/div[{index_proizvoda}]/p""").text
                # Dobivanje cijene sa početne strane za više istih artikala
                cijena_proizvoda_pocetna = int(
                    cijena_proizvoda_pocetna) + int(cijena_proizvoda) * int(broj_klikova)
                while broj_klikova > broj_potrebnih_klikova:
                    driver.execute_script(
                        "window.scrollTo({ top: 0 });")
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                        (By.XPATH, f"""//*[@id="root"]/div/div[1]/div/div[{index_proizvoda}]/div[2]/a[2]"""))).click()
                    broj_potrebnih_klikova += 1
                driver.find_element(
                    By.XPATH, value=f"""//*[@id="root"]/div/div[1]/div/div[{index_proizvoda}]/div[3]/button""").click()

        # Klik na košaricu
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, f"""//*[@id="root"]/div/header/div/div[3]/a[4]/img"""))).click()
        # Klik na checkout
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, f"""//*[@id="root"]/div/header/div/div[3]/div[2]/div[2]/button"""))).click()
        # Uspoređivanje cijena sa početne strane i processa checkout-a
        checkout_cijena = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, """//*[@id="root"]/div/div/div/div/span[1]"""))).text
        print("Checkout cijena", checkout_cijena)
        print("Početna cijena", cijena_proizvoda_pocetna)

        if int(checkout_cijena) != int(cijena_proizvoda_pocetna):
            print(
                "Cijena sa početne stranice ne odgovara cijeni na checkout-u, test NIJE prošao")
            return
        else:
            print(
                "Cijena sa početne stranice odgovara cijeni na checkout-u, test JE prošao")

        # Upisivanje i potvrđivanje kupona
        driver.find_element(
            By.XPATH, value="""//*[@id="root"]/div/div/div/div/div/input""").send_keys("rahulshettyacademy")
        driver.find_element(
            By.XPATH, value="""//*[@id="root"]/div/div/div/div/div/button""").click()
        # Čekamo 30 sek da se polje koda pojavi, ukoliko ne, rušimo test
        Code_applied_polje = WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
            (By.XPATH, """//*[@id="root"]/div/div/div/div/div/span"""))).text

        # Ako se polje pojavi i test prođe, testiramo da li popust uredno uračunat u cijenu
        cijena_bez_popusta = int(cijena_proizvoda_pocetna)
        # Ovdje računamo popust i dinamički dohvaćamo trenutni popust u slučaju da se u budućnosti promjeni
        popust = driver.find_element(
            By.XPATH, value="""//*[@id="root"]/div/div/div/div/span[2]""").text
        popust = int(popust.removesuffix("%"))
        cijena_sa_popustom = cijena_bez_popusta - cijena_bez_popusta * popust / 100
        print("Cijena bez popusta", cijena_bez_popusta)
        print("Popust: ", popust)
        print("Cijena sa popustom", cijena_sa_popustom)
        web_cijena_sa_popustom = driver.find_element(
            By.XPATH, value="""//*[@id="root"]/div/div/div/div/span[3]""").text
        print("Cijena sa popustom na sajtu: ", web_cijena_sa_popustom)
        # Testiramo ako su obje cijene iste, ako nisu rušimo test (funkciju)
        if float(cijena_sa_popustom) != float(web_cijena_sa_popustom):
            print("Popust nije dodan, test NIJE prošao")
            return
        else:
            print("Popust je dodan, test JE prošao")
        # Nastavljamo sa narudžbom, biramo Srbiju kao zemlju i završavamo kupnju
        # Klikamo kupi button
        driver.find_element(
            By.XPATH, value="""//*[@id="root"]/div/div/div/div/button""").click()
        select_button = select(WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, """//*[@id="root"]/div/div/div/div/div/select"""))))
        # Selektiramo Srbiju kao mjesto kupovine
        select_button.select_by_value('Serbia')
        # Klikamo agree to terms checkbox
        driver.find_element(
            By.XPATH, """//*[@id="root"]/div/div/div/div/input""").click()
        # Klikamo PROCEED button
        driver.find_element(
            By.XPATH, """//*[@id="root"]/div/div/div/div/button""").click()
        # Provjeravamo da li smo dobili text da je uspješna kupovina, te koristimo to kao uvjet prolaska testa
        success_text = driver.find_element(
            By.XPATH, """//*[@id="root"]/div/div/div/div/span""").text

        if "successfully" in success_text:
            print("*** Cijeli test JE prošao uspješno!! ***")
        else:
            print(
                "*** Test NIJE prošao uspješno!!, Pozovite Hrvoje Matošević na 097/7120-800 da popravi ***")
    except Exception() as e:
        print("Browser automation funkcija nije prošla, došlo je do greške", e)
    finally:
        driver.close()


user_input_check(user_input.title())

browser_automation()

