import requests
import argparse
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import pandas as pd
import sys

# vyparsuj nazov fakulty z command line argumentu
parser = argparse.ArgumentParser(description="Skript na spracovanie XML súborov z webového adresára.")
parser.add_argument("fakulta", type=str, help="Názov fakulty (napr. FMFI)")
args = parser.parse_args()

# 1. URL adresa webového adresára
url = f"https://ais2.uniba.sk/repo2/repository/default/ais/zamestnanec/{args.fakulta}/SK/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "sk,en-US;q=0.7,en;q=0.3",
}

#print(f"Sťahujem zoznam súborov pre fakultu {args.fakulta}...")
response = requests.get(url, headers=headers)
response.raise_for_status()  # Kontrola, či je stránka dostupná

# Parsovanie HTML na získanie zoznamu súborov
soup = BeautifulSoup(response.content, 'html.parser')

xml_files = []
for link in soup.find_all('a'):
    href = link.get('href')
    if href and href.endswith('.xml'):
        xml_files.append(href)

# vypis na stderr
print(f"Nájdených {len(xml_files)} XML súborov. Začínam spracovanie...", file=sys.stderr)

data = []

# 2. Prechádzanie a čítanie každého XML súboru
# urob iba prvych 10 súborov, aby sme nepreťažili server
count = 0
for filename in xml_files:
    count += 1
    if count > 30000:
        break

    file_url = filename
 
    # Z názvu súboru vyparsuj login (napr. priezvisko7) extrahovaním časti pred príponou .xml
    # napr. https://ais2.uniba.sk/repo2/repository/default/ais/zamestnanec/FMFI/SK/priezvisko7.xml -> priezvisko7
    login = (filename.split('/')[-1].replace('.xml', '')).split('.')[0]
    
    try:
        print(file_url, file=sys.stderr)
        file_response = requests.get(file_url, headers=headers)
        # print(file_response.content)
        
        # Parsovanie obsahu XML
        root = ET.fromstring(file_response.content)
        
        datum = "1900-01-01"  # Predvolená hodnota, ak nenájdeme požadovaný blok
        
        # Hľadanie bloku s idTyp = -109
        for popisOsoby in root.findall('.//popisOsoby'):
            idTyp = popisOsoby.find('idTyp')
            if idTyp is not None and idTyp.text == '-109':
                text_element = popisOsoby.find('text')
                if text_element is not None:
                    datum = text_element.text
                break
                
        data.append({'login': login, 'datum': datum})
        
    except requests.exceptions.RequestException as e:
        data.append({'login': login, 'datum': datum, 'chyba': f'Chyba sťahovania'})
    except ET.ParseError:
        data.append({'login': login, 'datum': datum, 'chyba': f'Chyba parsovania XML'})
# 3. Vytvorenie a zobrazenie tabuľky
df = pd.DataFrame(data)

# Zobrazenie výsledku ako tsv
print(df.to_csv(sep='\t', index=False))

# Ak si chcete tabuľku uložiť do Excelu, odkomentujte nasledujúci riadok:
# df.to_excel("zoznam_aktualizacii.xlsx", index=False)
