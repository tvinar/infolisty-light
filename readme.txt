wget https://ais2.uniba.sk/repo2/repository/default/ais/informacnelisty/2025-2026/FMFI/SK/mAIN.xml
python3 process-study-program.py mAIN.xml
python3 infolist-xml2html.py infolisty/2-AIN-181.xml 2-AIN-181.html
