import pandas as pd

data_hdf = pd.HDFStore('../data/data.h5')

if 'bikes' in data_hdf:
    bikes_df = data_hdf['bikes']
    bikes_hdf.sort_index(axis=0)
    bikes_hdf.sort_index(axis=1)
    data_hdf.put('bikes', bikes_df)
if 'stands' in data_hdf:
    stands_df = data_hdf['stands']
    stands_df.sort_index(axis=0)
    stands_df.sort_index(axis=1)
    data_hdf.put('stands', stands_df)

