#####  PACKAGES #####
import pandas as pd
import gzip

from os.path import isfile;
from glob import glob
from datetime_converter import convert_tstp_sec_to_datetime, convert_datetime_to_string, delocalize_datetime, is_workingday, convert_datestring_to_datetime, convert_datetime_to_tstp

dataHDF = pd.HDFStore('../data/velibData.h5')

print(dataHDF['availability/station_14037'])

