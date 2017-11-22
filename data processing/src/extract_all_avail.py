import pandas as pd

import json
import sys

import time

fileName = sys.argv[1];

with open(fileName, 'r') as f:
    data = f.readlines()

data = map(lambda x: x.rstrip(), data)
data_json_str = "[" + ','.join(data) + "]"

data_df = pd.read_json(data_json_str)
#Create a big dataframe with all data separated by line
split_df = pd.DataFrame()
for index, row in data_df.iterrows():
    #Create the dataframe for this particular tstp
    tstp_df = pd.DataFrame(row['ststates'])
    tstp_df['tstp'] = row['tstp']
    #Append this smaal df to the main one
    split_df = split_df.append(tstp_df)

if split_df.empty:
    exit(0)

#Reshape the final dataframe with a multiindex
split_df.set_index(['tstp', 'nb'], inplace=True)
split_df.sort_index(axis=0)

for station_id, station_df in split_df.groupby(level=1):
    station_df.index = station_df.index.droplevel(1)
    station_df = station_df[station_df['state']=='open']
    try:
        with pd.HDFStore('../data/station_data/station_'+str(station_id)+'.h5') as data_hdf:
            data_hdf.put('availability', station_df[['freebk', 'freebs']], format='t', append=True)
    except ValueError as err:
        print(station_df[station_df['state']!='open'])
        print(err)
