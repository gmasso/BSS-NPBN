import xml.etree.ElementTree as ET
import pandas as pd

tree = ET.parse("../data/velib.kml")
root = tree.getroot();
