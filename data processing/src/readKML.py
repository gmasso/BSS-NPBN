import xml.etree.ElementTree as ET
import pandas as pd

tree = ET.parse("../../data/velib.kml")
root = tree.getroot();
print("coucou")

#for child in root.findall