# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# get_okato_codes.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# Created: 15:50 11.05.2013
# ---------------------------------------------------------------------------

import urllib2,urllib
import xml.etree.ElementTree as ET
import ucsv as csv

def get_codes():
    urlbase = "http://112.ru/publish/00/00/"
    urlbase_okato = urlbase + "okato/"
    urlbase_data = urlbase + "uum/"
    
    urllist = urlbase_okato + "content.xml" #http://112.ru/publish/00/00/okato/content.xml
    res_fed = urllib2.urlopen(urllist)
    tree_fed = ET.parse(res_fed)
    for item_fed in tree_fed.findall('item'):
        itemcode0 = item_fed.attrib['code0']
        itemname = item_fed.attrib['name']
        urllist = urlbase_okato + itemcode0 + "/content.xml" #http://112.ru/publish/00/00/okato/1/content.xml
        res_lvl1 = urllib2.urlopen(urllist)
        tree_lvl1 = ET.parse(res_lvl1)
        for item_lvl1 in tree_lvl1.findall('item'):
            okato_lvl1 = item_lvl1.attrib['code']
            okato_lvl1nm = item_lvl1.attrib['name']
            urllist = urlbase_okato + itemcode0 + "/" + okato_lvl1 + "/content.xml" #http://112.ru/publish/00/00/okato/1/45000000000/content.xml
            res_lvl2 = urllib.urlopen(urllist)
            if res_lvl2.getcode() != 404:
                print("Checking...." + itemcode0 + "," + okato_lvl1)
                tree_lvl2 = ET.parse(res_lvl2)
                for item_lvl2 in tree_lvl2.findall('item'):
                    okato_lvl2 = item_lvl2.attrib['code']
                    okato_lvl2nm = item_lvl2.attrib['name']
                    urllist = urlbase_okato + itemcode0 + "/" + okato_lvl1 + "/" + okato_lvl2 + "/content.xml" #http://112.ru/publish/00/00/okato/1/45000000000/content.xml
                    res_lvl3 = urllib.urlopen(urllist)
                    if res_lvl3.getcode() != 404:
                        tree_lvl3 = ET.parse(res_lvl3)
                        for item_lvl3 in tree_lvl3.findall('item'):
                            okato_lvl3 = item_lvl3.attrib['code']
                            okato_lvl3nm = item_lvl3.attrib['name']
                            final = urlbase_data + okato_lvl1 + "/" + okato_lvl2 + "/" + okato_lvl3 + "/" + "contents.xml"
                            csvwriter_okato.writerow(dict(FEDCODE=itemcode0,
                                                        FEDNAME=itemname,
                                                        OKATO1=okato_lvl1,
                                                        OKATO1NM=okato_lvl1nm,
                                                        OKATO2=okato_lvl2,
                                                        OKATO2NM=okato_lvl2nm,
                                                        OKATO3=okato_lvl3,
                                                        OKATO3NM=okato_lvl3nm,
                                                        URL=final))
                    else:
                        final = urlbase_data + okato_lvl1 + "/" + okato_lvl2 + "/" + "contents.xml"
                        csvwriter_okato.writerow(dict(FEDCODE=itemcode0,
                                                      FEDNAME=itemname,
                                                      OKATO1=okato_lvl1,
                                                      OKATO1NM=okato_lvl1nm,
                                                      OKATO2=okato_lvl2,
                                                      OKATO2NM=okato_lvl2nm,
                                                      URL=final))
        
            else:
                csvwriter_okato.writerow(dict(FEDCODE=itemcode0,
                                                        FEDNAME=itemname,
                                                        OKATO1=okato_lvl1,
                                                        OKATO1NM=okato_lvl1nm,
                                                        OKATO2=9999999999999,
                                                        OKATO2NM=u"не загружено",
                                                        OKATO3=9999999999999,
                                                        OKATO3NM=u"не загружено",
                                                        URL=urllist))
if __name__ == '__main__':
    f_okato = open("okato_codes.csv","wb")
    fieldnames_okato = ("FEDCODE","FEDNAME","OKATO1","OKATO1NM","OKATO2","OKATO2NM","OKATO3","OKATO3NM","URL")
    csvwriter_okato = csv.DictWriter(f_okato, fieldnames=fieldnames_okato)
    
    get_codes()
    
    f_okato.close()