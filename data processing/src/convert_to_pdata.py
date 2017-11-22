# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 14:06:31 2015

@author: gmas
"""
#####  PACKAGES #####
import pandas as pd
import json

from glob import glob
##### END PACKAGES #####

##### Collect the whole dataset to store all the data in a HDF5 file #####
velibHDF_path = '../data/velibData.h5'
velibHDF = pd.HDFStore(velibHDF_path)

#Extract trips data
print("***** EXTRACTION AND CONVERSION OF TRIPS DATA *****")
#isEmpty = True
#emptyDF = pd.DataFrame()   
dfList=[]
for fileName in glob('../data/trips/paris-*.csv.gz'):
    #Extract the period over which the data was collected
    dataPeriod = fileName.replace('../data/trips/paris-','')
    dataPeriod = dataPeriod.replace('.csv.gz','')
    print('treating period',dataPeriod,end='...')
    dfList.append(pd.read_csv(fileName, compression='gzip', sep=';'))
    #if isEmpty:
    #    globalDF = emptyDF.append(pd.read_csv(fileName, compression='gzip', sep=';'))
    #    isEmpty = False
    #else:
    #    globalDF = pd.concat([globalDF, pd.read_csv(fileName, compression='gzip', sep=';')])
    
    print('done')
globalDF = pd.concat(dfList)
velibHDF.put('trips/global', globalDF)
#
print("Now splitting the data between stations...")
#stationList = np.unique(globaDF['instation','outstation'].values.ravel())
#for st_id in stationList:
#    
#    globalDF
# = avail_df[avail_df.index.map(is_workingday)]
print("done.")
print("***** TRIPS DATA CONVERTED *****")
        

print("***** CONVERSION OF AVAILABILITY DATA *****")
#Extract availability data
#for fileName in glob('../data/availability/station_data/*'):
#    #Extract the period over which the data was collected
#    stationID = fileName.replace('../data/availability/station_data/stationAvail_','')
#    print('converting availability data from station',stationID,end=' to HDF5 format...')
#    with open(fileName, 'r') as availFile:
#        availDF = pd.read_table(availFile, sep=' ', index_col=0, names=['state', 'freebk', 'freebs'], lineterminator='\n')
#        HDF_path = 'availability/station_'+stationID
#        velibHDF.put(HDF_path, availDF)
#        print('done');
        
print("***** AVAILABILITY DATA CONVERTED *****")

print(" All velib data available have been stored to",  velibHDF_path)


fileName = '../data/availability/station_data/stationAvail_14037'
stationID = fileName.replace('../data/availability/station_data/stationAvail_','')
with open(fileName, 'rb') as availFile:
    print('the file is opened')
    availDF = pd.read_table(fileName, sep = ' ', index_col=0, names=['state', 'freebk', 'freebs'], lineterminator='\n')
    print('df created')
    print(availDF)
#text=";".join([str(1),str(2), str(3),str(4)])+"a\n";
#print(text)


