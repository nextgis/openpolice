# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# get_police_stations-v1.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# About: Grab 112.ru data on участковые, creates two tables linked with unique id, policemen and locations they are responsible for.
# Created: 13:26 07.05.2013
# Usage example: python get_police_stations-v1.py 45000000000
# ---------------------------------------------------------------------------

import urllib2,urllib
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import ucsv as csv
import re
import sys
import os
import zipfile,zlib

def process(filt):
    filt = int(filt)
    f_okato = open("res/okato_codes.csv",'rb')
    csvreader = csv.DictReader(f_okato)
    for row in csvreader:
        if filt == row['OKATO1'] or filt == row['OKATO2'] or filt == row['OKATO3'] or filt == 0:
            
            if str(row['OKATO3']) != '':
                final = "http://112.ru/publish/00/00/nearOrg/mvd/" + str(row['OKATO1']) + "/f" + str(row['OKATO2']) + "/" + str(row['OKATO3']) 
            else:
                final = "http://112.ru/publish/00/00/nearOrg/mvd/" + str(row['OKATO1']) + "/f" + str(row['OKATO2'])
            try:
                res = urllib2.urlopen(final + ".shtml")
                parse_org(final,str(row['OKATO2']))
            except urllib2.URLError, e:
                #import pdb;pdb.set_trace()
                get_photo_status = False
                if hasattr(e, 'reason'):
                    print 'We failed to reach a server.'
                    print 'Reason: ', e.reason
                elif hasattr(e, 'code'):
                    print 'The server couldn\'t fulfill the request.'
                    print 'Error code: ' + str(e.code)  + " Page: " + final + ".shtml"
        
def parse_org(url,okato):
    print(url + ".shtml")
    res = urllib2.urlopen(url + ".shtml")
    soup = BeautifulSoup(''.join(res.read()))
        
    trs = soup.findAll('tr')
    i = 0
    for tr in trs:
        i = i + 1
        org_id = okato + "_" + str(i)
        tds = tr.findAll('td')
        for td in tds:
            pod = tds[0].text
            phone = tds[1].text
            addr = tds[2].text
            if str(tds[3]) != "<td class=\"oddTd\"></td>" and str(tds[3]) != "<td class=\"evenTd\"></td>":
                latlon = tds[3].find('a')['href'].split('?')[1].split('&')
                lat = latlon[0].split("=")[1]
                lon = latlon[1].split("=")[1]
            else:
                lat,lon = str(-9999),str(-9999)
            hours = tds[4].text
    
        #write to results file
        csvwriter_mvd.writerow(dict(ID=org_id,
                                POD=' '.join(pod.split()),
                                PHONE=' '.join(phone.split()),
                                ADDR=addr.strip(),
                                LAT=lat.strip(),
                                LON=lon.strip(),
                                HOURS=' '.join(hours.split()),
                                URL=url + ".shtml"))

if __name__ == '__main__':
    args = sys.argv[ 1: ]
    
    if len(args) == 1:
        filt = args[0] #use 45000000000 for RU-MOW
    else:
        filt = 0    # get everything
    
    mvd_name = "mvd.csv"
    mvdz_name = "mvd.zip"
    
    f_mvd = open("res/" + mvd_name,"wb")
    fieldnames_mvd = ("ID","POD","PHONE","ADDR","LAT","LON","HOURS","URL")
    csvwriter_mvd = csv.DictWriter(f_mvd, fieldnames=fieldnames_mvd)
    
    process(filt)
    
    f_mvd.close()
    
    #zip results
    os.chdir("res")
    fMvdz = zipfile.ZipFile(mvdz_name,'w')
    fMvdz.write(mvd_name, compress_type=zipfile.ZIP_DEFLATED)
    fMvdz.close()
