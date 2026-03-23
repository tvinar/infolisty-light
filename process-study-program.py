import xml.etree.ElementTree as ET
import os
import argparse
import sys




def rozdel_xml(vstupny_subor,vystupny_dir):
    # Vytvorenie adresára, ak neexistuje
    if not os.path.exists(vystupny_dir):
        os.makedirs(vystupny_dir)
        print(f"Vytvorený adresár: {vystupny_dir}")

    try:
        # Načítanie a spracovanie vstupného XML
        tree = ET.parse(vstupny_subor)
        root = tree.getroot()

        # Vyhľadanie kontajnera informacneListy
        informacne_listy = root.find('informacneListy')
        
        if informacne_listy is None:
            print("Chyba: Element <informacneListy> nebol nájdený.")
            return

        pocet_spracovanych = 0

        # Prechádzanie jednotlivých informačných listov
        for info_list in informacne_listy.findall('informacnyList'):
            skratka_elem = info_list.find('skratka')
            
            if skratka_elem is not None and skratka_elem.text:
                skratka = skratka_elem.text.strip()
                
                # Vyčistenie názvu súboru od nepovolených znakov (napr. lomky)
                bezpecny_nazov = "".join([c for c in skratka if c.isalnum() or c in ('-', '_', '.')]).strip()
                subor_cesta = os.path.join(vystupny_dir, f"{bezpecny_nazov}.xml")

                # Vytvorenie nového XML stromu pre jeden informačný list
                # Každý súbor bude mať vlastnú XML deklaráciu
                with open(subor_cesta, 'wb') as f:
                    f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
                    # Zapísanie elementu informacnyList
                    ET.ElementTree(info_list).write(f, encoding='utf-8', xml_declaration=False)
                
                pocet_spracovanych += 1
                print(f"Uložené: {subor_cesta}")

        print(f"\nHovoto! Celkovo spracovaných listov: {pocet_spracovanych}")

    except FileNotFoundError:
        print(f"Chyba: Súbor '{vstupny_subor}' nebol nájdený.")
    except ET.ParseError:
        print(f"Chyba: Súbor '{vstupny_subor}' nie je platný XML súbor.")

# Spustenie skriptu
if __name__ == "__main__":
    # Nastavenie parsera argumentov
    parser = argparse.ArgumentParser(description="Rozdelí XML súbor študijného programu na jednotlivé informačné listy.")
    
    # Pridanie argumentov
    parser.add_argument("vstup", help="Cesta k vstupnému XML súboru (napr. AIN.xml)")
    parser.add_argument("-o", "--output", default="infolisty", 
                        help="Názov výstupného adresára (predvolené: 'infolisty')")

    # Spracovanie argumentov
    args = parser.parse_args()

    # Spustenie hlavnej funkcie
    rozdel_xml(args.vstup, args.output)
