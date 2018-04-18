import xml.etree.ElementTree as ET
import csv
import pandas as pd

tree = ET.parse("../../data/Resident_data.xml")
root = tree.getroot();

# open a file for writing

#print("coucou")

#Test_data = open('../../data/Test.csv', 'w')

# create the csv writer object
#
#csvwriter = csv.writer(Test_data)
#Test_head = []

#count = 0
#print(root.findall('b'))
#for child in root.findall('description'):
#    Test = []
print(root.findall('Name'))
#    coordinates = child.find('b').tag
    
#    if count == 0:
#    coordinates = child.find('b').tag
#        Test_head.append(coordinates)
#		Address = member[3].tag
#		resident_head.append(Address)
#        csvwriter.writerow(Test_head)
#        count = count + 1
#
#        coordinates = child.find('coordinates').text
#        Test.append(coordinates)
#
#	EmailAddress = member.find('EmailAddress').text
#	resident.append(EmailAddress)
#	Address = member[3][0].text
#	address_list.append(Address)
#	City = member[3][1].text
#	address_list.append(City)
#	StateCode = member[3][2].text
#	address_list.append(StateCode)
#	PostalCode = member[3][3].text
#	address_list.append(PostalCode)
#	resident.append(address_list)
#        csvwriter.writerow(Test)
#Test_data.close()