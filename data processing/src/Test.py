# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 19:17:15 2018

@author: akosgo14
"""

import xml.etree.ElementTree as ET
import csv

tree = ET.parse("../../data/velib.kml")
root = tree.getroot()

# open a file for writing

Resident_data = open('../../data/ResidentData.csv', 'w')

# create the csv writer object

csvwriter = csv.writer(Resident_data)
resident_head = []

count = 0
for member in root.findall('kml'):
	resident = []
	address_list = []
	if count == 0:
		b = member.find('b').tag
		resident_head.append(b)
		p = member.find('p').tag
		resident_head.append(p)
		csvwriter.writerow(resident_head)
		count = count + 1

	b = member.find('b').text
	resident.append(b)
	p = member.find('p').text
	resident.append(p)
	csvwriter.writerow(resident)
Resident_data.close()