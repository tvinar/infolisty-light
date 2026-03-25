wget https://ais2.uniba.sk/repo2/repository/default/ais/informacnelisty/2025-2026/FMFI/SK/mAIN.xml
python3 process-study-program.py mAIN.xml
python3 infolist-xml2html.py infolisty/2-AIN-181.xml 2-AIN-181.html

## prehlad datumov VUPCH
python3 datumy-vupch.py FMFI >datumy.csv
python3 datuny-vupch.py PriF >>datumy.csv

## zoznam vsetkych skratiek predmetov studijneho programu
## (ocakavame skratky v 2. stlpci)
## link do google docs je priamo v subore
./zoznam-skratiek.pl
