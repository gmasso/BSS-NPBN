import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sys import argv
import os.path

from datetime_converter import *
import datetime
#from merge_data import extract_trips_data_period


##################################################################################
###                              compute_error                                 ###
##################################################################################
def compute_error(avail_df, trips_df):
    """ Returns the error between the set of measures contained in avail_df and the trajectory based on trips_df."""

    if trips_df.empty:
        return -1

    start_dt = trips_df.index[0]
    # The first measure used to define the starting number of bikes in the station happens at the last measure time before the first trip record
    if avail_df.loc[:start_dt, :].empty:
        return -1 

    #paris_tz = timezone('Europe/Paris')
    #print(avail_df.loc[paris_tz.localize(datetime.datetime(2013,10,25,4,40), is_dst=True).astimezone(paris_tz):paris_tz.localize(datetime.datetime(2013,10,25,4,50), is_dst=True).astimezone(paris_tz)])
    first_dt = avail_df.index.asof(start_dt) #loc[:start_dt].index[-1], avail_df.index[0])

    start_avail = avail_df['freebk'].asof(start_dt)
    # Compute the trajectory using
    trajectory = start_avail + trips_df.loc[first_dt:avail_df.index[-1],'bkmove'].cumsum()

    avail_series = avail_df.loc[first_dt:,'freebk']

    error = 0
    #trajectory = trajectory.drop_duplicates()
    for dt_control, avail_control in avail_series.iteritems():
        error += (avail_control - trajectory.asof(dt_control))**2

    # Return the mean error per control points
    return (error/float(len(avail_series)))

##################################################################################
###                       compute_optimal_timeshift                            ###
##################################################################################
def compute_optimal_timeshift(avail_df, trips_df):
    """ Return the optimal time shift to align the trips data with the bikes availability data."""

    time_shift = datetime.timedelta(seconds=0)

    time_inter = datetime.timedelta(seconds=256)

    try:
        middle_df = trips_df
        middle_err = compute_error(avail_df, trips_df)

        right_df = trips_df
        right_df.index = right_df.index.map(lambda x: x + time_inter)
        right_err = compute_error(avail_df, right_df)

        left_df = trips_df
        left_df.index = left_df.index.map(lambda x: x - time_inter)
        left_err = compute_error(avail_df, left_df)

        if left_err == -1 or right_err == -1:
            return time_shift

        limit_td = datetime.timedelta(seconds=1)

        while time_inter > limit_td and middle_err > 0:
            if right_err < middle_err:
                time_shift += time_inter

                left_df = middle_df
                left_err = middle_err

                middle_df = right_df
                middle_err = right_err

                right_df = trips_df
                right_df.index = right_df.index.map(lambda x: x + time_inter)
                right_err = compute_error(avail_df, right_df)
                if right_err == -1:
                    right_err = middle_err

            elif left_err < middle_err:

                time_shift -= time_inter

                right_df = middle_df
                right_err = middle_err

                middle_df = left_df
                middle_err = left_err

                left_df = trips_df
                left_df.index = left_df.index.map(lambda x: x - time_inter)
                left_err = compute_error(avail_df, left_df)
                if left_err == -1:
                    left_err = middle_err
            
            else:
                time_inter = time_inter/2.0

                right_df = trips_df
                right_df.index = right_df.index.map(lambda x: x + time_inter)
                right_err = compute_error(avail_df, right_df)

                left_df = trips_df
                left_df.index = left_df.index.map(lambda x: x - time_inter)
                left_err = compute_error(avail_df, left_df)
        

        return time_shift
    except IndexError as ind_err:
        print(ind_err)
        #print('avail_df : ', avail_df)
        #print(middle_df.index)
        #print(trips_df.index[:10])
        return datetime.timedelta(0)

##################################################################################
###                           add_missing_trips                                ###
##################################################################################
def add_missing_trips(avail_df, trips_df, last_avail, last_stands):
    """Add some trips to the trajectory to improve the consistency with the measures."""
#    print("Procedure to add the missing trips is not implemented yet") 

    trajectory_df = pd.dataframe(columns=['bkmove', 'reason', 'freebk', 'freebs'])
    if trips_df.empty:
        return trajectory_df

    trajectory_df[['bkmove', 'reason']] = trips_df.loc[:,['bkmove', 'reason']]
    trajectory_df['freebk'] = last_avail + trips_df.loc[:,'bkmove'].cumsum()
    trajectory_df['freebs'] = last_stands - trips_df.loc[:,'bkmove'].cumsum()
    #print(trajectory_df.ix[0,['bkmove','freebk']])
    
    start_dt = trips_df.index[0]
    if avail_df.loc[:start_dt, :].empty:
        return trajectory_df

    first_dt = avail_df.index.asof(start_dt) #loc[:start_dt].index[-1], avail_df.index[0])
    return trajectory_df



#######################################################################
#######################################################################
###                         MAIN PROGRAM                            ###  
#######################################################################
#######################################################################

#######################################################################
###                   PHASE 1: DATA COLLECTION                      ###
#######################################################################

# Get the data from the availability file and store it into a list
station_id = argv[1]
print("Treating station " + station_id +"...")

data_hdf = pd.HDFStore("../data/station_data/station_"+str(station_id)+".h5")
# Get the dataframe from the hdf5 file of the station data
avail_df = data_hdf['availability']
if avail_df.empty:
    exit(0)
avail_df = avail_df.groupby(avail_df.index).first()

trips_df = data_hdf['trips']
# Remove Nan value and duplicates and sort the dataframe
trips_df.dropna()
trips_df.sort_index(axis=0, inplace=True)
# Select only the trips that happen after the first availability measure
trips_df = trips_df.loc[avail_df.index[0]:]

# Restrict the dataframes to the period they have in common
trips_df = trips_df.loc[starting_dt:, :]
avail_df = avail_df.loc[avail_df.index.asof(trips_df.index[0]):, :]

#######################################################################
###             PHASE 2: MERGE TO BUILD A TRAJECTORY                ###
#######################################################################

# Create a trajectory dataframe grouping all the information about the evolution through time
trajectory_df = pd.DataFrame(columns=['freebk', 'freebs', 'bkmove', 'reason'])

last_dt = max(avail_df.index[-1], trips_df.index[-1])
first_avail = avail_df['freebk'].asof(last_dt+datetime.timedelta(seconds=1))
first_stands = avail_df['freebs'].asof(last_dt+datetime.timedelta(seconds=1))
opt_tshift = datetime.timedelta(0)

while starting_dt < last_dt:
    # Extract the data from both datasets on a daily period
    next_day_dt = starting_dt.replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1)
    avail_period_df = avail_df.loc[starting_dt:next_day_dt, :]
    # Select the trips corresponding to the same period with a maximum time shift of one hour between the two datasets
    trips_period_df = trips_df.loc[starting_dt + opt_tshift:next_day_dt + datetime.timedelta(hours=1), :]
    if trips_period_df.empty or (avail_period_df.empty and trajectory_df.empty):
        # Advance to the following day
        starting_dt = next_day_dt
        continue
    #print(trips_period_df.index[0] + opt_tshift)
    
    # For each day, compute the optimal shift to make the two datasets consistent
    opt_tshift = compute_optimal_timeshift(avail_period_df, trips_period_df)
    if opt_tshift > datetime.timedelta(0):
        print("Shift between the two datasets : ", opt_tshift)
    # Select the trips for the corresponding period, including the ones within the timeshift calculated
    trips_period_df = trips_period_df.loc[:next_day_dt + opt_tshift, :]
    # Apply the timeshift to the datetime indices of the trips dataframe
    trips_period_df.index = trips_period_df.index.map(lambda x: x + opt_tshift)
    
#    # Add some trips to match the availability measures throughout the day and append the obtained trajectory for the day to the trajectory dataframe
#    #trajectory_df = trajectory_df.append(add_missing_trips(avail_period_df, trips_period_df, last_avail, last_stands))
#    if not trajectory_df.empty:
#        last_avail = trajectory_df.ix[-1, 'freebk']
#        last_stands = trajectory_df.ix[-1, 'freebs']
#    
    # Advance to the following day
    starting_dt = next_day_dt


trajectory_df.sort_index(axis=0)

#starting_index = avail_df.index[0]
#if trips_df.index[0] > avail_df.index[0]: 
#    starting_index = avail_df.loc[:trips_df.index[0],:].index[-1]
#    trips_series = trips_df.loc[:,'type']
#else:
#    trips_series = trips_df.loc[avail_df.index[0]:,'type']
#
#print('start index', str(starting_index))
#print('first index', str(avail_df.index[0]))
#print(avail_df.loc[trips_df.index[0]:,:].index)
#print(trips_df.index)
#starting_point = avail_df.loc[starting_index,'freebk'] 
#traj_df = starting_point + trips_series.cumsum()
#
trajectory_df.loc[:,'freebk'].plot()
avail_df.loc[trajectory_df.index[0]:,'freebk'].plot()
plt.show()
