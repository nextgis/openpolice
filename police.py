# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# police.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# About: Grab 112.ru data on участковые, creates two tables linked with unique id, policemen and locations they are responsible for.
# Created: 13:26 07.05.2013
# Usage example: 
# ---------------------------------------------------------------------------

import urllib2,urllib
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import ucsv as csv
import re

def process(filt):
    filt = int(filt)
    f_okato = open("okato_codes.csv",'rb')
    csvreader = csv.DictReader(f_okato)
    for row in csvreader:
        if filt == row['OKATO1'] or filt == row['OKATO2'] or filt == row['OKATO3']:
            final = "http://112.ru/publish/00/00/uum/" + str(row['OKATO1']) + "/" + str(row['OKATO2']) + "/" + str(row['OKATO3'])
            parse_man(final,str(row['OKATO3']))
        
def get_photo(photo_url,man_id):
    try:
        u = urllib2.urlopen(photo_url)
    except urllib2.URLError, e:
        #import pdb;pdb.set_trace()
        get_photo_status = False
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    else:
        meta = u.info()
        #meta_len = len(meta.getheaders("Content-Length"))
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading photo: %s Kb: %s" % (man_id, file_size/1024)
        f = open("photos/" + man_id + ".jpg","wb")
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,

        f.close()
        get_photo_status = True
    return get_photo_status
        
def parse_man(url,okato):
    res = urllib2.urlopen(url + "/contents.xml")
    tree = ET.parse(res)
    for doc in tree.findall('doc'):
        val = doc[0].attrib['file']
        if 'file' in val:
            url_file = url + "/" + val
            man_id = okato + "_" + val.replace(".html","")
            print(url_file)
            res = urllib2.urlopen(url_file)
            soup = BeautifulSoup(''.join(res.read()))
            photo_url = "http://112.ru" + soup.find('img')['src']
            get_photo_status = get_photo(photo_url,man_id)
            
            divs = soup.findAll('div')
            name = list(soup.find("div", { "class" : "uchbold" }).strings)[0]
            sign = list(soup.find("div", { "style" : "margin-top: 7px" }).strings)[0]
            type = sign.split(",")[0]
            rank = sign.split(",")[1]
            if len(list(soup.find("div", { "style" : "margin-top: 7px" }).strings)) > 1:
                phone = list(soup.find("div", { "style" : "margin-top: 7px" }).strings)[1]
            else:
                phone = u"не указан"
            
            #write to man file
            csvwriter_man.writerow(dict(ID=man_id,
                                    NAME=name.strip(),
                                    TYPE=type.strip(),
                                    RANK=rank.strip(),
                                    PHONE=phone.strip().replace("  "," ").replace(u"Телефон: ",""),
                                    URL=url_file))
            lis = soup.findAll('li')
            for li in lis:
                str = list(li.strings)[0]
                uldoma = str.split(u", дома: ")
                ul = uldoma[0]
                if len(uldoma) > 1:
                    try:
                        #TODO: handle 44-1 (example: http://112.ru/publish/00/00/uum/45000000000/45277000000/45277595000/file9.html)
                        #TODO: handle 23-25, 1 - 25 (example: http://112.ru/publish/00/00/uum/45000000000/45280000000/45280569000/file1.html)
                        doma = map(unicode, re.findall(r'(\d+\s*(?:\(.*?\))*)', uldoma[1])) #split(",")
                    except:
                        print(uldoma[1])
                else:
                    doma = ("")
                for dom in doma:
                    #write to geo file
                    csvwriter_geo.writerow(dict(ID=man_id,
                                    addr_o=u"Москва, " + ul.strip() + ", " + dom.strip()))


if __name__ == '__main__':
    f_geo = open("RU-MOW.csv","wb")
    f_man = open("RU-MOW-man.csv","wb")
    fieldnames_geo = ("ID","addr_o")
    fieldnames_man = ("ID","NAME","TYPE","RANK","PHONE","URL")
    csvwriter_geo = csv.DictWriter(f_geo, fieldnames=fieldnames_geo)
    csvwriter_man = csv.DictWriter(f_man, fieldnames=fieldnames_man)
    
    filt = "45000000000"
    if filt == None: filt = 0
    process(filt)
    
    f_man.close()
    f_geo.close()