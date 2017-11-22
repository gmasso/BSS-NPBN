import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sys import argv
import os.path

from datetime_converter import *
import datetime

##################################################################################
###                       compute_optimal_timeshift                            ###
##################################################################################
def compute_optimal_timeshift(trips_series, avail_series, initial_shift):
    """ Return the optimal time shift to align the trips data with the bikes availability data."""

    time_shift = initial_shift

    time_inter = datetime.timedelta(seconds=256)

    try:
        middle_measures = avail_series
        slack_middle = (trips_series.asof(avail_series.index).reindex(avail_series.index) - middle_measures.loc[:,'freebk']).dropna()
        middle_err = compute_error(trips_df, avail_df.loc[:,'bikes')

        right_measures = avail_series
        right_measures.index += time_inter
        right_err = compute_error(trips_df, right_df)

        left_measures = avail_series
        left_measures.index -= time_inter
        left_err = compute_error(trips_df, left_df)

        if left_err == -1 or right_err == -1:
            return time_shift

        limit_td = datetime.timedelta(seconds=1)

        while time_inter > limit_td and middle_err > 0:
            if right_err < middle_err:
                time_shift += time_inter

                left_df.loc[:,:] = middle_df.loc[:,:]
                left_err = middle_err

                middle_df = right_df
                middle_err = right_err

                right_df = trips_df
                right_df.index += time_inter
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
                left_df.index -= time_inter
                left_err = compute_error(avail_df, left_df)
                if left_err == -1:
                    left_err = middle_err
            
            else:
                time_inter = time_inter/2.0

                right_df = trips_df
                right_df.index += time_inter
                right_err = compute_error(avail_df, right_df)

                left_df = trips_df
                left_df.index -= time_inter
                left_err = compute_error(avail_df, left_df)

        return time_shift

    except IndexError as ind_err:
        print(ind_err)
        return datetime.timedelta(0)


##################################################################################
###                          compute_patch_error                               ###
##################################################################################
def patch_error(slack_series, patch_dt, patch_move):
    """ Returns the difference in the error when adding the patch_move at datetime patch_dt.""" 
#error between the set of measures contained in avail_df and the trajectory based on trips_df."""

    slack_series.loc[patch_dt:] += patch_move
    return ((slack_series.dropna())**2).sum()

##################################################################################
###                             add_single_trip                                ###
##################################################################################
def get_patch_dt(slack_series, bike_move):
    """ Return the best time to insert a trip of type 'bike_move' into the trajectory."""    

    best_error = ((slack_series.dropna())**2).sum()
    
    # If no bike_move is given, try both and select the one that improves the matching the most.
    if bike_move == 0:
        
        # Get the best datetime to insert a departure and an arrival to the trajectory
        dep_dt, dep_error = get_patch_dt(slack_series, -1)
        arr_dt, arr_error = get_patch_dt(slack_series, 1)

        if dep_error < arr_error:
            bike_move = -1
            patch_dt = dep_dt
            patch_error = dep_error
        else:
            bike_move = 1
            patch_dt = arr_dt
            patch_error = arr_error

    else:
        patch_dt = slack_series.iloc[int(slack_series.len()/2)].index

    if patch_error < best_error:
        

##################################################################################
###                              compute_error                                 ###
##################################################################################
def compute_patch_trips(trajectory_df, measures_df):
    """ Returns a set of trips to add to the trajectory in trajectory_df to match the control measures in measures_df."""

    patch_trips = pd.DataFrame(columns=trajectory_df.columns)
    measures_df = measures_df.dropna()

    if trajectory_df.empty:
        print("Error: No trajectory to compare with the measures")
        return -1

    slack_series = (trajectory_df['freebk'].asof(measures_df.index).reindex(measures_df.index) - measures_df['freebk'])
    best_error = ((slack_series.dropna())**2).sum()
    bike_move = np.sign(slack_series.sum())

    
    # Compute the best insertion for the trip and the error associated with the corrected trajectory 
    best_dt = get_patch_dt(slack_series, bike_move)

    start_inter = trajectory_df.index[0]
    end_inter = trajectory_df.index[-1]
    time_candidates = end_inter - start_inter

    while time_candidates > datetime.timedelta(seconds=1):
        patch_time = trajectory_df.index[0] + time_candidates/2
        
    return 0

##################################################################################
###                            correct_trajectory                              ###
##################################################################################
def correct_trajectory(trajectory_df, measures_df):
    """ Returns the error between the set of measures contained in avail_df and the trajectory based on trips_df."""

    if measures_df.empty:
        return correct_out_of_bounds(trajectory_df)
    best_error = compute_error(trajectory_df, measures_df)

    slack_series = (trajectory_df['freebk'].asof(measures_df.index).reindex(measures_df.index) - measures_df['freebk']).dropna()
    return (slack_series**2).sum()










def build_trajectory(trips_df, control_df):
    """Build a trajectory for the station based on the trips data, corrected with the occupancy measures at this station."""

    # Build a tentative trajectory from the first measure, using only trips information to compute the evolution of the number of bikes in the station
    trajectory_series = avail_df.ix[0,'freebk'] + trips_df.loc[:,'bkmove'].cumsum()
    
    corrective_trips = pd.Series()

    # Spot the trajectory points when there is a negative number a bikes in the station
    zero_violations = trajectory_series
    zero_violations[zero_violations >= 0] = 0
    zero_error = 100 * (zero_violations**2).sum()

    # Spot the trajectory points when there are more bikes than the station capacity
    capacity_violations = trajectory_series - (control_df['freebk'] + control_df['freebs']).asof(trajectory_series)
    capacity_violations[capacity_violations < 0] = 0
    capacity_error = 100 * (capacity_violations**2).sum()

    # Get the gaps between the built trajectory points and the control points 
    gap_series = (trajectory_df['freebk'].asof(control_df.index).reindex(control_df.index) - control_df['freebk']).dropna()
    gap_error = (gap_series**2).sum()

    
    trajectory_df = pd.DataFrame(columns=['freebk', 'freebs', 'bkmove', 'reason', 'blockedbk'])
    trajectory_df[['bkmove', 'reason']] = trips_df.loc[:,['bkmove', 'reason']]
    trajectory_df['blockedbk'] = avail_df['blockedbk'].asof(trajectory_df.index)
    trajectory_df['freebk'] = avail_df.ix[0,'freebk'] + trips_df.loc[:,'bkmove'].cumsum()
    trajectory_df['freebs'] = avail_df.ix[0,'freebs'] - trips_df.loc[:,'bkmove'].cumsum()


    return trajectory_df




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
# Make sure the indices are unique
avail_df = avail_df.groupby(avail_df.index).first()
avail_df.rename(columns={'occubs': 'blockedbk'}, inplace=True)

trips_df = data_hdf['trips']
# Remove Nan value and duplicates and sort the dataframe
trips_df.dropna()
trips_df.sort_index(axis=0, inplace=True)

# Restrict the availability data to the ones that are synchronized with the trips data
avail_df = avail_df.loc[avail_df.index.asof(trips_df.index[0]):, :]

# Set the start of control measures when there are at least 100 measures during a day
while avail_df.loc[:avail_df.index[0]+datetime.timedelta(days=1), 'freebk'].count() < 100:
    avail_df = avail_df.loc[avail_df.index[0]+datetime.timedelta(days=1):]

# Select only the trips that happen after the first availability measure
trips_df = trips_df.loc[avail_df.index[0]:,:]

#############################################################################
###          PHASE 2: CORRECT INCONSISTENCIES IN THE TRAJECTORY           ###
#############################################################################
if trips_df.empty:
    exit(0)

# Create a trajectory dataframe grouping all the information about the evolution through time
trajectory_df = build_trajectory(trips_df, avail_df)

#######################################################################
### PHASE 2: SHIFT THE TRIPS DATETIME TO MATCH THE STATION MEASURES ###
#######################################################################

# Compare slices of 6 hours of the trajectory with the availability control measures to determine possible time shifts between the two datasets
slice_hours = 6
slice_duration = datetime.timedelta(hours=slice_hours)
# Define the first slice as the 
slice_dt = trajectory_df.index[0].replace(hour = slice_hours * int(trajectory_df.index[0].hour/slice_hours), minute = 0, second=0)

# Initialize the time shift to zero
shift = datetime.timedelta(0)

while slice_dt < last_trips_df:
    # Compute the optimal timeshift between the control measures and the trips data
    #shift = compute_optimal_timeshift(trajectory_df.loc[slice_dt:slice_dt+slice_duration, 'freebk'], avail_df.loc[avail_df.index.asof(slice_dt+shift):slice_dt+slice_duration+shift, 'freebk'])
    shift = compute_optimal_timeshift(trajectory_df.loc[slice_dt:slice_dt+slice_duration, 'freebk'], avail_df.loc[avail_df.index.asof(slice_dt+shift):, 'freebk'], shift)

    # Apply the shift to the the control measures during the corresponding time interval
    avail_df.loc[slice_dt:slice_dt+slice_duration].index += shift
    
    print("Done. Plotting...")
    trajectory_df.loc[slice_dt:slice_dt+slice_duration,'freebk'].plot(color='b')
    avail_df.loc[slice_dt:slice_dt+slice_duration,'freebk'].plot(color='g')
    plt.show()

    # Iterate to the next slice
    slice_dt = slice_dt + slice_duration


#############################################################################
### PHASE 3: ADD MISSING TRIPS TO THE TRAJECTORY TO AVOID INCONSISTENCIES ###
#############################################################################

dt_corrected = trajectory_df.index[0]
problematic_records = trajectory_df[trajectory_df['freebk'] < 0 or trajectory_df['freebs'] < 0]
# If there are problematic records, add some trips to the trajectory until that date and time
while not problematic_records.empty:
    dt_prob = problematic_records.index[0]
    # Select all data before problematic record and correct the trajectory over this time interval
    missing_trips_df = compute_patch_trips(trajectory_df[dt_corrected:dt_prob], avail_data[dt_corrected:dt_prob])
    trajectory_df.append(missing_trips_df)
    dt_corrected = dt_prob
    
    

trajectory_control = trajectory_df['freebk'].asof(avail_df.index)
slack_series = (trajectory_control.reindex(avail_df.index) - avail_df['freebk']).dropna()

#
## Adjust the trajectory by comparing its evolution with the station measures
#remaining_measures = avail_df
#while not remaining_measures.empty:
#    
#
traj_occubs = avail_df.loc[:,'blockedbk'].asof(trajectory_df.index)
trajectory_df.loc[:,'freebk'] -= traj_occubs.loc[:]
#
#
##corrected_slck = slack_series - avail_df.loc[trajectory_df.index[0]:,'occubs']
#
#slack_lz = slack_series[slack_series<0]
#slack_gz = slack_series[slack_series>0]
#
#diff_series = slack_series.diff().dropna()
#

# Select the shift that impacts the most the remainder of the planning horizon
#index, missing_trips = locate_missing_trips(slack_series, trajectory_df['freebs'])
#modify_trajectory(trajectory_df, trajectory_control.iloc[index].index, missing_trips)
#use nb_trips_to_add = fabs(missing_trips)

#print(trajectory_df['freebk'])
#print(traj_occubs)
#print(trajectory_control)
#print(slack_series)
#best_gap = (slack_series**2).sum()
#print(slack_series.min())
#print(slack_series.max())
#
#print(diff_series.min())
#print(diff_series.cumsum())#.drop_duplicates(keep='first'))
#print(slack_lz)
#print(slack_gz)

print("Done. Plotting...")
trajectory_df.loc[:,'freebk'].plot(color='b')
avail_df.loc[trajectory_df.index[0]:,'freebk'].plot(color='g')
#traj_occubs.plot(color='m')
#
avail_df.loc[trajectory_df.index[0]:,'blockedbk'].plot(color='r')
###(trajectory_df['freebk'].asof(avail_df.index).reindex(avail_df.index)+avail_df.loc[trajectory_df.index[0]:,'occubs']).plot(color='r')

#diff_series.plot(color='m')
#corrected_slck.plot(color='m')
slack_series.plot(color='y')
plt.savefig('../figures/test_correction.pdf')
plt.show()
