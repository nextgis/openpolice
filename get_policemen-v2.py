#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# grab-policemen-v2.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# About: Grab mvd.ru data on local policemen, creates two tables linked by unique id, policemen and addresses they cover.
# Created: 10.03.2014
# Usage example: python grab-policemen-v2.py 45000000000
# ---------------------------------------------------------------------------

from bs4 import BeautifulSoup
import urllib2
import csv
import requests

def get_pol(link,payload,offset):
    r = requests.post(link, data=payload)
    a = r.text.decode('unicode_escape').replace('\\','')

    soup = BeautifulSoup(''.join(a))
    divs = soup.findAll("div", { "class" : "data" })
    if divs == []:
        res = "not ok"
    else:
        man_id = offset
        for div in divs:
            man_id = man_id + 1
            if div.find("img"):
                img = "http://mvd.ru/" + div.find("img")['src'].replace('\\','')
                get_photo_status = get_photo(img,man_id)
            else:
                img = ""
            
            if div.find("b"):
                name = div.find("b").text.strip()
            else:
                name = ""
            if div.find("div", { "class" : "sl-item-subtitle" }):
                rank = div.find("div", { "class" : "sl-item-subtitle" }).text
            else:
                rank = ""

            variables = []
            t = div.find("div", { "class" : "sl-list font14" })
            tts = str(t).split("<br/>")
            substrs = [u"Телефон",u"Дополнительные телефоны",u"Адрес участкового пункта полиции"]
            for substr in substrs:
                it = "not ok"
                for tt in tts:
                    if substr in tt.decode("utf-8"):
                        variables.append(BeautifulSoup(''.join(tt)).find("b").text)
                        it = "ok"
                        break
                if it != "ok":
                    variables.append("")
                

            phone = variables[0]
            phone_add = variables[1]
            adr = variables[2]
            
            try:
                csvwriter_pol.writerow(dict(MAN_ID=man_id,
                                            IMG=img,
                                            NAME=name.encode("utf-8"),
                                            RANK=rank.encode("utf-8"),
                                            ADR=adr.encode("utf-8"),
                                            PHONE=phone,
                                            PHONE_ADD=phone_add,
                                            OFFSET=offset))
            except:
                print div

            get_addr(div,man_id)

            res = "ok"

    return res

def get_addr(div,man_id):
    lis = div.find("ul").findAll("li")
    for li in lis:

        addrsrc = li.text

        csvwriter_addrsrc.writerow(dict(MAN_ID=man_id,
                        ADDR=addrsrc.encode("utf-8")))

        addrs = addrsrc.split(",")
        city = addrs[0].replace(u" (г)","")
        street = addrs[1].split(" (")[0]
        del addrs[0]
        del addrs[0]

        if len(addrs) > 0:
            for addr in addrs:
                res_addr = city + "," + street + "," + addr
                csvwriter_addr.writerow(dict(MAN_ID=man_id,
                        ADDR=res_addr.encode("utf-8")))
        else:
            res_addr = city + "," + street
            csvwriter_addr.writerow(dict(MAN_ID=man_id,
                        ADDR=res_addr.encode("utf-8")))   

def get_photo(photo_url,man_id):
    try:
        u = urllib2.urlopen(photo_url)
    except urllib2.URLError, e:
        
        get_photo_status = False
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    else:
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading photo: %s Kb: %s" % (man_id, file_size/1024)
        f = open("photos/" + str(man_id) + ".jpg","wb")
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,

        f.close()
        get_photo_status = True
    return get_photo_status

if __name__ == '__main__':
    link = "http://mvd.ru/help/district/search"

    #init csv for address source
    f_addrsrc = open("policemen/addr_source.csv","wb")
    fieldnames_data = ("MAN_ID","ADDR","OFFSET")
    csvwriter_addrsrc = csv.DictWriter(f_addrsrc, fieldnames=fieldnames_data)

    #init csv for processed addresses
    f_addr = open("policemen/addr.csv","wb")
    fieldnames_data = ("MAN_ID","ADDR")
    csvwriter_addr = csv.DictWriter(f_addr, fieldnames=fieldnames_data)

    #init csv for policemen
    f_pol = open("policemen/policemen.csv","wb")
    fieldnames_data = ("MAN_ID","NAME","IMG","ADR","RANK","PHONE","PHONE_ADD","OFFSET")
    csvwriter_pol = csv.DictWriter(f_pol, fieldnames=fieldnames_data)
    offset = 0
    res = "ok"
    while res == "ok":
        payload = {'subject': '7700000000000', 'type': 'district', 'offset': str(offset)}
        res = get_pol(link,payload,offset)
        offset = offset + 20
        print offset

    f_pol.close()
    f_addr.close()
    f_addrsrc.close()