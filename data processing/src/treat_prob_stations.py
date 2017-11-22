import pandas as pd
#import numpy as np

import json
import sys

import time
#def reform(list_of_dict, ):
#    """ Reforms a nested dictionary into a dictionary with tuples as keys """
fileName = sys.argv[1];

def append_data_to_hdf(split_df):
   for station_id, station_df in split_df.groupby(level=1):
       station_df.index = station_df.index.droplevel(1)
       station_df = station_df[station_df['state']=='open']
       try:
           with pd.HDFStore('../data/station_data/station_'+str(station_id)+'.h5') as data_hdf:
               data_hdf.put('availability', station_df[['freebk', 'freebs']], format='t', append=True)
       except ValueError as err:
           print(err)

def append_to_df(df_to_add, big_df):
    for index, row in df_to_add.iterrows():
        #Create the dataframe for this particular tstp
        tstp_df = pd.DataFrame(row['ststates'])
        tstp_df.loc[:, 'tstp'] = row['tstp']
        #Append this small df to the main one
        big_df = big_df.append(tstp_df)
    
    #Reshape the final dataframe with a multiindex
    big_df.set_index(['tstp', 'nb'], inplace=True)
    big_df.sort_index(axis=0)
    
    return big_df

data = ' '
split_df = pd.DataFrame()
with open(fileName, 'r') as f:
    try:
        data = f.readlines()

        data = map(lambda x: x.rstrip(), data)
        data_json_str = "[" + str(data) + "]"

#ref    = {(outerKey, innerKey): values for outerKey, innerDict in data_dict.iteritems() for innerKey, values in innerDict.iteritems()}
        data_df = pd.read_json(data_json_str)
        append_data_to_df(data_df, split_df)
        append_data_to_hdf(split_df)

    except ValueError as err:
        print("Failed to read the json file, trying line by line...")
        split_df=pd.DataFrame()
        while not data == '':
            try:
                data = f.readline()
                data_json_str = "[" + str(data) + "]"

                data_df = pd.read_json(data_json_str)
                #Create a big dataframe with all data separated by line
                append_to_df(data_df, split_df)
            except ValueError as err:
                print("error, skipping line")
                continue

        append_data_to_hdf(split_df)
