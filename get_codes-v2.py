#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# police-mvd.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# About: Grab 112.ru data on ó÷àñòêîâûå, creates two tables linked with unique id, policemen and locations they are responsible for.
# Created: 13:26 07.05.2013
# Usage example: python police-mvd.py 45000000000
# ---------------------------------------------------------------------------

from bs4 import BeautifulSoup
import urllib2
import csv
import requests

def get_subj_list(link):
    u = urllib2.urlopen(link)
    r = u.read()
    f = open("codes/subjects.html","wb")
    f.write(r)
    f.close()

def proc_subj_list():
    f = open("codes/subjects.html")
    soup = BeautifulSoup(''.join(f.read()),"lxml")
    subj_select = soup.find("select", { "class" : "subject select" })
    subjs = subj_select.findAll("option", { "class" : "data" })
    for subj in subjs:
        name = subj.text.encode("utf-8")
        code = subj['value']
        csvwriter.writerow(dict(NAME1=name,
                            CODE1=code))

def get_mun_list(code1):
    link = "http://mvd.ru/kladr/subzone_option/" + code1
    r = requests.get(link)

    f_subj_subzone = open("codes/subj_subzone_" + code1 + ".txt","wb")
    f_subj_subzone.write(r.text)
    f_subj_subzone.close()


def proc_mun_list(code1,name1):
    f_subj_subzone = open("codes/subj_subzone_" + code1 + ".txt")
    soup = BeautifulSoup(''.join(f_subj_subzone.read()),"lxml")
    options = soup.findAll("option")

    #empty line for cases when next level is empty (Москва (г))
    csvwriter_subzone.writerow(dict(NAME1=name1,
                            CODE1=code1,
                            NAME2="",
                            CODE2=""))

    for option in options:
        name2 = option.text
        code2 = option['value'].replace('\\"','')
        csvwriter_subzone.writerow(dict(NAME1=name1,
                            CODE1=code1,
                            NAME2=name2.decode('unicode_escape').encode("utf-8"),
                            CODE2=code2))

def get_city_list(code2):
    link = "http://mvd.ru/kladr/city_zone_option/" + code2
    r = requests.get(link)

    f_subj_subzone = open("codes/subj_cityzone_" + code2 + ".txt","wb")
    f_subj_subzone.write(r.text)
    f_subj_subzone.close()

def proc_city_list(code1,name1,code2,name2):
    f_cityzone = open("codes/subj_cityzone_" + code2 + ".txt")
    soup = BeautifulSoup(''.join(f_cityzone.read()),"lxml")
    options = soup.findAll("option")

    #empty line for cases when next level is empty
    csvwriter_cityzone.writerow(dict(NAME1=name1,
                            CODE1=code1,
                            NAME2=name2,
                            CODE2=code2,
                            NAME3="",
                            CODE3=""))

    for option in options:
        name3 = option.text
        code3 = option['value'].replace('\\"','')
        csvwriter_cityzone.writerow(dict(NAME1=name1,
                            CODE1=code1,
                            NAME2=name2,
                            CODE2=code2,
                            NAME3=name3.decode('unicode_escape').encode("utf-8"),
                            CODE3=code3))

if __name__ == '__main__':
    subj_page_link = "http://mvd.ru/help/district"
    
    #subject level
    fieldnames_data = ("NAME1","CODE1")
    f_subj = open("codes/codes_subj.csv","wb")
    csvwriter = csv.DictWriter(f_subj, fieldnames=fieldnames_data)
    get_subj_list(subj_page_link)
    proc_subj_list()
    f_subj.close()
    
    #rayon+city district level
    f_subj = open("codes/codes_subj.csv")
    csvreader = csv.DictReader(f_subj, fieldnames=fieldnames_data)
    f_subzone = open("codes/codes_subzone.csv","wb")
    fieldnames_data = ("NAME1","CODE1","NAME2","CODE2")
    csvwriter_subzone = csv.DictWriter(f_subzone, fieldnames=fieldnames_data)
    for row in csvreader:
        print(row['NAME1'])
        get_mun_list(row['CODE1'])
        proc_mun_list(row['CODE1'],row['NAME1'])
    f_subj.close()
    f_subzone.close()

    #settlement level
    f_subzone = open("codes/codes_subzone.csv")
    csvreader = csv.DictReader(f_subzone, fieldnames=fieldnames_data)
    f_cityzone = open("codes/codes_cityzone.csv","wb")
    fieldnames_data = ("NAME1","CODE1","NAME2","CODE2","NAME3","CODE3")
    csvwriter_cityzone = csv.DictWriter(f_cityzone, fieldnames=fieldnames_data)
    for row in csvreader:
        print(row['NAME2'])
        get_city_list(row['CODE2'])
        proc_city_list(row['CODE1'],row['NAME1'],row['CODE2'],row['NAME2'])
    f_subzone.close()
    f_cityzone.close()

