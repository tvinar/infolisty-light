import xml.etree.ElementTree as ET
from jinja2 import Template
import argparse
import os
import sys

def parse_course_xml(xml_file):
    """Extrahuje dáta z XML štruktúry podľa vzoru 1-AIN-121.xml."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        print(f"Chyba pri čítaní XML: {e}")
        sys.exit(1)

    def get_text_list(tag_name):
        """Pomocná funkcia na získanie zoznamu textov z elementov ako _SO_ alebo _L_."""
        element = root.find(tag_name)
        if element is not None:
            texty = element.find('texty')
            if texty is not None:
                return [p.text for p in texty.findall('p') if p.text]
        return []

    # Mapovanie dát z XML elementov
    data = {
        "vysoka_skola": "Univerzita Komenského v Bratislave",
        "fakulta": "Fakulta matematiky, fyziky a informatiky",
        "akademicky_rok": "2025-2026",
        "kod": root.findtext('kod'),
        "nazov": root.findtext('nazov'),
        "web": root.find('_URL_/texty/p').text if root.find('_URL_/texty/p') is not None else "",
        "rozsah": root.findtext('rozsahTyzdenny'),
        "kredity": root.findtext('kredit'),
        "semester": f"{root.findtext('.//skratka')} {root.findtext('.//popis')} {root.findtext('.//rokRocnik')}/{root.findtext('.//kodSemester')}",
        "stupen": root.findtext('stupenPredmetu'),
        "podmienky": get_text_list('_PA_'),
        "vaha": root.findtext('_VH_/texty/p') if root.find('_VH_/texty/p') is not None else "50/50",
        "vysledky": get_text_list('_VV_'),
        "osnova": get_text_list('_SO_'),
        "literatura": get_text_list('_L_'),
        "jazyk": root.findtext('_PJ_/texty/p') or "slovenský",
        "hodnotenia": [
            {"kod": h.findtext('kod'), "perc": h.findtext('percentualneVyjadrenieZCelkPoctuHodnoteni')}
            for h in root.findall('.//hodnoteniePredmetu')
        ],
        "celkovy_pocet": root.findtext('.//celkovyPocetHodnotenychStudentov'),
        "vyucujuci": [
            {
                "meno": v.findtext('plneMeno'),
                "typ": "prednášajúci" if v.findtext('typ') == 'P' else "cvičiaci",
                "id": v.findtext('pridelenyEmail').split('@')[0] if v.findtext('pridelenyEmail') else "ludia"
            } for v in root.findall('.//vyucujuci')
        ],
        "datum_zmeny": root.findtext('datumSchvalenia')
    }
    return data

# HTML šablóna kopírujúca štýl z 1-AIN-121_22.html
HTML_TEMPLATE = """
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="sk" lang="sk">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Informačný list: {{ nazov }}</title>
    <style type="text/css">
        body {font-family: serif; max-width: 50em; margin: 2em auto;}
        h1 { font-size: 110%; text-align: center; }
        table {width: 100%; border-collapse: collapse; margin-top: 1em;}
        table td {padding: 0.4em; border: thin solid black; vertical-align: top;}
        #literatura p {text-indent: -1em; padding-left: 1em;}
    </style>
</head>
<body>
    <h1>INFORMAČNÝ LIST PREDMETU</h1>
    <table>
        <tr><td colspan="2"><strong>Vysoká škola:</strong> {{ vysoka_skola }}</td></tr>
        <tr><td colspan="2"><strong>Fakulta:</strong> {{ fakulta }}</td></tr>
        <tr><td colspan="2"><strong>Akademický rok:</strong> {{ akademicky_rok }}</td></tr>
        <tr><td><strong>Kód:</strong> {{ kod }}</td><td><strong>Názov predmetu:</strong> {{ nazov }}</td></tr>
        <tr><td colspan="2"><strong>Web:</strong> <a href="{{ web }}">{{ web }}</a></td></tr>
        <tr><td colspan="2"><strong>Počet kreditov:</strong> {{ kredity }}</td></tr>
        <tr><td colspan="2"><strong>Odporúčaný semester:</strong> {{ semester }}</td></tr>
        <tr><td colspan="2"><strong>Stupeň štúdia:</strong> {{ stupen }}</td></tr>
        <tr>
            <td colspan="2">
                <strong>Podmienky absolvovania:</strong><br/>
                {% for p in podmienky %}<p>{{ p }}</p>{% endfor %}
                <p>Váha priebežného / záverečného hodnotenia: {{ vaha }}</p>
            </td>
        </tr>
        <tr><td colspan="2"><strong>Výsledky vzdelávania:</strong><br/>{% for p in vysledky %}<p>{{ p }}</p>{% endfor %}</td></tr>
        <tr><td colspan="2"><strong>Stručná osnova:</strong><br/>{% for p in osnova %}<p>{{ p }}</p>{% endfor %}</td></tr>
        <tr><td colspan="2" id="literatura"><strong>Literatúra:</strong><br/>{% for p in literatura %}<p>{{ p }}</p>{% endfor %}</td></tr>
        <tr><td colspan="2"><strong>Jazyk:</strong> {{ jazyk }}</td></tr>
        <tr>
            <td colspan="2">
                <strong>Hodnotenia (spolu {{ celkovy_pocet }}):</strong><br/>
                {% for h in hodnotenia %}{{ h.kod }}: {{ h.perc }}%{% if not loop.last %}, {% endif %}{% endfor %}
            </td>
        </tr>
        <tr>
            <td colspan="2">
                <strong>Vyučujúci:</strong><br/>
                {% for v in vyucujuci %}
                <a href="https://sluzby.fmph.uniba.sk/ludia/{{ v.id }}">{{ v.meno }}</a> ({{ v.typ }})<br/>
                {% endfor %}
            </td>
        </tr>
        <tr><td colspan="2"><strong>Dátum poslednej zmeny:</strong> {{ datum_zmeny }}</td></tr>
    </table>
</body>
</html>
"""

def main():
    parser = argparse.ArgumentParser(description='Prevodník informačných listov z XML do HTML.')
    parser.add_argument('vstup', help='Cesta k vstupnému XML súboru (napr. 1-AIN-121.xml)')
    parser.add_argument('vystup', help='Názov výstupného HTML súboru (napr. vystup.html)')
    
    args = parser.parse_args()

    if not os.path.exists(args.vstup):
        print(f"Chyba: Súbor '{args.vstup}' neexistuje.")
        return

    # Spracovanie dát
    data = parse_course_xml(args.vstup)
    
    # Renderovanie cez Jinja2
    template = Template(HTML_TEMPLATE)
    html_content = template.render(data)
    
    # Zápis do súboru
    with open(args.vystup, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Hotovo! HTML bolo uložené do: {args.vystup}")

if __name__ == "__main__":
    main()
