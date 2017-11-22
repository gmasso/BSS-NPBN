import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sys import argv
import os.path

from datetime_converter import *
import datetime

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
###                           compute_patch_trips                              ###
##################################################################################
def compute_patch_trips(gap_series, zero_violations, capacity_violations):
    """ Returns a set of trips to add to the trajectory in trajectory_df to match the control measures in measures_df."""

    zero_error = zero_violations.size * (zero_violations**2).sum()
    capacity_error = capacity_violations.size * (capacity_violations**2).sum()

    patch_trips = pd.Series()

    # Find date candidate to add to the patch trips
    

##################################################################################
###                            shift_patch_trips                               ###
##################################################################################
def shift_patch_trips(trips_df, control_df, capacity_violations):
    """ Shift the corrective trips in time to avoid boundaries violations."""

    trajectory_series = avail_df.ix[0,'freebk'] + all_trips_df.loc[:, 'bkmove'].cumsum()

    # Spot the trajectory points when there is a negative number a bikes in the station
    zero_violations = 0

    # Spot the trajectory points when there are more bikes than the station capacity
    capacity_violations[capacity_violations < 0] = 0

    # Merge the two trips dataframe
    all_trips = trips.df.append(corrective_trips)
    all_trips.sort_index(axis=0, inplace=True)

##################################################################################
###                        compute_best_insertion_dt                           ###
##################################################################################
def compute_best_insertion_dt(gap_series, bkmove):
    """ Returns the best datetime to insert a trip of type bkmove to reduce the gap_error."""
    
    nb_control = gap_series.size
    
    # If the size of the series is equal to 1, insert the patch trips right before the date of the gap
    if nb_control == 1:
        return gap_series.iloc[0].index - datetime.timedelta(seconds=1) 

    left_index = int(nb_control)/4
    left_series = gap_series
    left_series.iloc[left_index:] += bkmove
    left_error = (left_series**2).sum()

    middle_index = int(nb_control)/2
    middle_series = gap_series
    middle_series.iloc[middle_index:] += bkmove
    middle_error = (middle_series**2).sum()

    right_index = 3 * int(nb_control)/4
    right_series = gap_series
    right_series.iloc[right_index:] += bkmove
    right_error = (right_series**2).sum()

    best_error = (gap_series**2).sum()
    if left_error < best_error:
        lbound = 0
        rbound = middle_index
    if middle_error < best_error:
        lbound = left_index
        rbound = right_index
    if right_error < best_error:
        lbound = middle_index
        rbound = nb_control
        
    return compute_best_insertion_dt(gap_series.iloc[lbound:rbound], bkmove)


##################################################################################
###                           compute_patch_trips                              ###
##################################################################################
def compute_patch_trips(gap_series):
    """ Returns a set of trips to add to the trajectory in trajectory_df to match the control measures in measures_df."""
    gap_error = (gap_series**2).sum()

    # Compute the best trip to add to the sequence
    bkmove = np.sign(gap_error.sum())
    insertion_dt = compute_best_insertion_dt(gap_series, bkmove)
    # Compute the improvement in the gap error
    corrected_gap = gap_series
    corrected_gap.loc[insertion_dt:] += bkmove
    corrected_error = (corrected_gap**2).sum()

    patch_trips = pd.Series()

    while corrected_error < gap_error:
        # If the correction improves the matching, add the trip to the patch series
        gap_error = corrected_error
        patch_trips.loc[insertion_dt] = bkmove

        # Try to add an other corrective trip to the series
        bkmove = np.sign(gap_error.sum())
        insertion_dt = compute_best_insertion_dt(gap_series, bkmove)
        corrected_gap.loc[insertion_dt:] += bkmove
        corrected_error = (corrected_gap**2).sum()

    return patch_trips

##################################################################################
###                         match_trips_to_measures                            ###
##################################################################################
def correct_inconsistencies(trips_series, patch_trips, control_df):
    """ Place the corrective trips in the dataframe trajectory_df to avoid boundaries violations with respect to control_df."""
    
    trajectory_series = control_df.ix[0,'freebk'] + trips_series.loc[:,'bkmove'].cumsum()

    zero_violations = trajectory_series[trajectory_series < 0]
    arrival_patch = patch_trips[patch_trips > 0]

    capacity_violations = trajectory_series[trajectory_series > (control_df['freebk'] + control_df['freebs']).asof(trajectory_series)]
    departure_patch = patch_trips[patch_trips < 0]

    for dt, bkavail in trajectory_series:
        control_df.asof(dt)

    # Create a series with original and patch trips together
    all_trips_df = trips_df.append(patch_trips_df)
    all_trips_df.sort_index()

    # Create a trajectory from the corrected trips and the starting number of bikes available the station
    trajectory_df = pd.DataFrame(columns=['freebk', 'freebs', 'bkmove', 'reason', 'blockedbk'])
    trajectory_df[['bkmove', 'reason']] = all_trips.loc[:,['bkmove', 'reason']]
    trajectory_df['blockedbk'] = control_df['blockedbk'].asof(trajectory_df.index)
    trajectory_df['freebk'] = control_df.ix[0,'freebk'] + all_trips.loc[:,'bkmove'].cumsum()
    trajectory_df['freebs'] = control_df.ix[0,'freebs'] - all_trips.loc[:,'bkmove'].cumsum()

##################################################################################
###                             build_trajectory                               ###
##################################################################################
def build_trajectory(trips_df, control_df):
    """Build a trajectory for the station based on the trips data, corrected with the occupancy measures at this station."""

    # Build a tentative trajectory from the first measure, using only trips information to compute the evolution of the number of bikes in the station
    trajectory_series = control_df.ix[0,'freebk'] + trips_df.loc[:,'bkmove'].cumsum()
    # Get the gaps between the built trajectory points and the control points 
    gap_series = (trajectory_series.asof(control_df.index).reindex(control_df.index) - control_df['freebk']).dropna()

    # Create another dataframe with the patch trips correcting inconsistencies between the trajectory and the control measures
    patch_trips_series = compute_patch_trips(gap_series)  

    # Correct inconsistencies in the trajectory and return the result
    return correct_inconsistencies(trips_df, patch_trips_series, control_df)




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

########################################################################
#### PHASE 2: SHIFT THE TRIPS DATETIME TO MATCH THE STATION MEASURES ###
########################################################################
#
## Compare slices of 6 hours of the trajectory with the availability control measures to determine possible time shifts between the two datasets
#slice_hours = 6
#slice_duration = datetime.timedelta(hours=slice_hours)
## Define the first slice as the 
#slice_dt = trajectory_df.index[0].replace(hour = slice_hours * int(trajectory_df.index[0].hour/slice_hours), minute = 0, second=0)
#
## Initialize the time shift to zero
#shift = datetime.timedelta(0)
#
#while slice_dt < last_trips_df:
#    # Compute the optimal timeshift between the control measures and the trips data
#    #shift = compute_optimal_timeshift(trajectory_df.loc[slice_dt:slice_dt+slice_duration, 'freebk'], avail_df.loc[avail_df.index.asof(slice_dt+shift):slice_dt+slice_duration+shift, 'freebk'])
#    shift = compute_optimal_timeshift(trajectory_df.loc[slice_dt:slice_dt+slice_duration, 'freebk'], avail_df.loc[avail_df.index.asof(slice_dt+shift):, 'freebk'], shift)
#
#    # Apply the shift to the the control measures during the corresponding time interval
#    avail_df.loc[slice_dt:slice_dt+slice_duration].index += shift
#    
#    print("Done. Plotting...")
#    trajectory_df.loc[slice_dt:slice_dt+slice_duration,'freebk'].plot(color='b')
#    avail_df.loc[slice_dt:slice_dt+slice_duration,'freebk'].plot(color='g')
#    plt.show()
#
#    # Iterate to the next slice
#    slice_dt = slice_dt + slice_duration
#
#
##############################################################################
#### PHASE 3: ADD MISSING TRIPS TO THE TRAJECTORY TO AVOID INCONSISTENCIES ###
##############################################################################
#
#dt_corrected = trajectory_df.index[0]
#problematic_records = trajectory_df[trajectory_df['freebk'] < 0 or trajectory_df['freebs'] < 0]
## If there are problematic records, add some trips to the trajectory until that date and time
#while not problematic_records.empty:
#    dt_prob = problematic_records.index[0]
#    # Select all data before problematic record and correct the trajectory over this time interval
#    missing_trips_df = compute_patch_trips(trajectory_df[dt_corrected:dt_prob], avail_data[dt_corrected:dt_prob])
#    trajectory_df.append(missing_trips_df)
#    dt_corrected = dt_prob
#    
#    
#
#trajectory_control = trajectory_df['freebk'].asof(avail_df.index)
#slack_series = (trajectory_control.reindex(avail_df.index) - avail_df['freebk']).dropna()
#
##
### Adjust the trajectory by comparing its evolution with the station measures
##remaining_measures = avail_df
##while not remaining_measures.empty:
##    
##
#traj_occubs = avail_df.loc[:,'blockedbk'].asof(trajectory_df.index)
#trajectory_df.loc[:,'freebk'] -= traj_occubs.loc[:]
##
##
###corrected_slck = slack_series - avail_df.loc[trajectory_df.index[0]:,'occubs']
##
##slack_lz = slack_series[slack_series<0]
##slack_gz = slack_series[slack_series>0]
##
##diff_series = slack_series.diff().dropna()
##
#
## Select the shift that impacts the most the remainder of the planning horizon
##index, missing_trips = locate_missing_trips(slack_series, trajectory_df['freebs'])
##modify_trajectory(trajectory_df, trajectory_control.iloc[index].index, missing_trips)
##use nb_trips_to_add = fabs(missing_trips)
#
##print(trajectory_df['freebk'])
##print(traj_occubs)
##print(trajectory_control)
##print(slack_series)
##best_gap = (slack_series**2).sum()
##print(slack_series.min())
##print(slack_series.max())
##
##print(diff_series.min())
##print(diff_series.cumsum())#.drop_duplicates(keep='first'))
##print(slack_lz)
##print(slack_gz)
