#!/opt/local/bin/python
import pandas as pd

import sys
from datetime_converter import convert_datestring_to_datetime

fileName = sys.argv[1];

if int(fileName[6:-4]) < 201309:
    exit(0)

#try:
if True:
    with open(fileName, 'r') as f:
        trips_df = pd.read_csv(f, sep=';')

    # Transform the dates into datetimes
    trips_df.loc[:,'out_dt'] = trips_df.loc[:,'out_date'].map(lambda x: convert_datestring_to_datetime(x))
    trips_df.loc[:,'in_dt'] = trips_df.loc[:,'in_date'].map(lambda x: convert_datestring_to_datetime(x))

    # Select the info about trips arriving in stations
    in_df = trips_df.loc[:, ['in_dt', 'in_station', 'reason']]
    in_df.loc[:, 'bkmove'] = 1
    # Group the trips by destination station
    in_grouped = in_df.groupby('in_station')
    for station_id, arr_df in in_grouped:
        arr_df.set_index('in_dt', inplace=True)
        arr_df.index.names = ['dt']
        try:
            with pd.HDFStore('../data/station_data/trips.h5') as trips_hdf:
                trips_hdf.put('station_'+str(station_id), arr_df[['bkmove', 'reason']], format='t', append=True)
        except ValueError as err:
            print(err)

    # Select the info about trips leaving stations
    out_df = trips_df.loc[:, ['out_dt', 'out_station', 'reason']]
    out_df.loc[:, 'bkmove'] = -1
    # Group the trips by departure station
    out_grouped = out_df.groupby('out_station')
    for station_id, dep_df in out_grouped:
        dep_df.set_index('out_dt', inplace=True)
        dep_df.index.names = ['dt']
        try:
            with pd.HDFStore('../data/station_data/trips.h5') as trips_hdf:
                trips_hdf.put('station_'+str(station_id), dep_df[['bkmove', 'reason']], format='t', append=True)
        except ValueError as err:
            print(err)


