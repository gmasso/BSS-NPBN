import pandas as pd
import glob


trips_hdf = pd.HDFStore('../data/station_data/trips.h5')

for station_name in trips_hdf.keys():
    print(station_name)
    trips_df = trips_hdf[station_name]
    trips_df.sort_index(axis=0, inplace=True)
    with pd.HDFStore("../data/station_data/"+station_name+".h5") as station_hdf:
        station_hdf.put('trips', trips_df, format='t')
    
