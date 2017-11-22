import pandas as pd
import matplotlib.pyplot as plt

from sys import argv
import os.path

from datetime_converter import *
#from merge_data import extract_trips_data_period

##################################################################################
###                        add_trips_to_trajectory                             ###
##################################################################################
def add_trips_to_trajectory(tstp, avail, stands, bikes_moves, reasons, trajectory_file):
    """Writes the trips contained in 'trips' to the file trajectory_file."""

    # Write to the output file the trajectory computed for the current period at this station
    trips_iter = 0
    for trips_iter in range(len(tstp)):
    
        trajectory_line = "%s %s %s %s %s\n" % (tstp[trips_iter], avail[trips_iter], stands[trips_iter], bikes_moves[trips_iter], reasons[trips_iter])
        trajectory_file.write(trajectory_line)

#######################################################################
###                   PHASE 1: DATA COLLECTION                      ###
#######################################################################

# Get the data from the availability file and store it into a list
hdf_name = argv[1]
print("Treating hdf " + hdf_name +"...")

with pd.HDFStore(hdf_name) as data_hdf:
    ## Get the dataframe from the hdf5 file of the station data
    #avail_df = data_hdf['availability']
    ## Remove Nan value and duplicates and sort the dataframe
    #avail_df.dropna()
    #avail_df = avail_df.reset_index().drop_duplicates(subset='tstp', keep='first').set_index('tstp')
    #avail_df.index = avail_df.index.map(lambda x: convert_velibtstp_to_datetime(x))
    #avail_df.index.names = ['dt']
    #avail_df.sort_index(axis=0, inplace=True)
    #capacity = max(avail_df['freebk'] + avail_df['freebs'])
    #avail_df.loc[:,'occubs'] = capacity - (avail_df['freebk'] + avail_df['freebs'])
    #data_hdf.put('availability', avail_df, format='t')

    trips_df = data_hdf['trips']
    trips_df = trips_df.rename(columns = {'type':'bkmove'})
    # Remove Nan value and duplicates and sort the dataframe
    trips_df.dropna()
    trips_df.sort_index(axis=0, inplace=True)
    data_hdf.put('trips', trips_df, format='t')

#
#trips_df = data_hdf['trips']
## Remove Nan value and duplicates and sort the dataframe
#trips_df.dropna()
#trips_df.sort_index(axis=0, inplace=True)
#
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
#traj_df.loc[:].plot()
#avail_df.loc[starting_index:,'freebk'].plot()
#plt.show()

#######################################################################
###              PHASE 2: MERGE AND WRITE TO A FILE                 ###
#######################################################################


    # Merge the data collected from both the station and the trips
    station_index = 0
    trips_index = 0
    trips_progress_ind = 0
    nb_trips_added = 0
    
    # Merge the data only if they are available from both sets
    if tstp_station and tstp_trips:
        
        #trajectory_fileName = "".join(["trajectories/stationTraj_", station_id])
        with open(trajectory_fileName, 'w') as trajectory_file:
    
            # Initialize the values of the tstp of the start of the current and the next day  
            next_day_dt = get_next_day_start_dt(convert_tstp_sec_to_datetime(tstp_station[station_index]))
            next_day_tstp = convert_datetime_to_tstp_ms(next_day_dt)
        
            # Define the maximum time shift allowed between the two data sets
            max_shift = 600 # in seconds -> 10 min
        
            # Set the last tstp and the last station availability to their initial value
            last_tstp = tstp_station[station_index] - max_shift
            last_avail = avail_station[station_index]
            last_unavail = unavail_station[station_index]
            last_stands = free_station[station_index]
        
            # Position the trips progress indicator on the first value greater than the first station tstp (minus max_shift) 
            while tstp_trips[trips_progress_ind] < last_tstp:
                trips_progress_ind += 1
        
            # Loop trough the days and merge the two data sets for each day separately 
            while station_index < len(tstp_station):
        
                # Store the station tstp and availability for the current day
                station_tstp_period = []
                station_avail_period = []
                station_unavail_period = []
                station_free_period = []
            
                station_start_index = station_index
                while station_index < len(tstp_station) and convert_tstp_sec_to_datetime(tstp_station[station_index]) < next_day_dt:
                    # Fill the tables with the data until the beginning of the next day   
                    station_tstp_period.append(tstp_station[station_index])
                    station_avail_period.append(avail_station[station_index])
                    station_unavail_period.append(unavail_station[station_index])
                    station_free_period.append(free_station[station_index])
                    station_index += 1
                 
                if station_tstp_period:
                    # If there are trips available to compare with the station data, merge the two data sets
                    #print len(tstp_trips)
                    #print len(station_tstp_period)
                    if trips_progress_ind < len(tstp_trips) and tstp_trips[trips_progress_ind] < station_tstp_period[0]:

                        corrected_tstp, corrected_avail, corrected_stands, corrected_bikes_moves, corrected_reasons, nb_trips_extracted = extract_trips_data_period(tstp_station[station_start_index:station_index],
                                avail_station[station_start_index:station_index], unavail_station[station_start_index:station_index],
                                free_station[station_start_index:station_index], tstp_trips[trips_progress_ind:],
                                bikes_moves[trips_progress_ind:], reason_trips[trips_progress_ind:], last_tstp, last_avail, last_stands, max_shift, capacity)
        
                        # Store the trips tstp and bike move for the current day (including the shift and corrective trips)
                        #trips_tstp_period, trips_bikes_moves_period, reasons_period, nb_trips_extracted = extract_trips_data_period(station_tstp_period,
                        #        station_avail_period, station_unavail_period, station_free_period, tstp_trips[trips_progress_ind:],
                        #        bikes_moves[trips_progress_ind:], reason_trips[trips_progress_ind:], last_tstp, last_avail, max_shift, capacity)
                
                        # Update the progress in the trips data
                        trips_progress_ind += nb_trips_extracted
                        nb_trips_added += len(corrected_tstp) - nb_trips_extracted

                        add_trips_to_trajectory(corrected_tstp, corrected_avail, corrected_stands, corrected_bikes_moves, corrected_reasons, trajectory_file)
                        if corrected_tstp:
                            last_avail = corrected_avail[-1] + corrected_bikes_moves[-1]
                            last_stands = corrected_stands[-1] - corrected_bikes_moves[-1]
    
                        #print "done."
                        #trips_unavail = []
                        #trips_iter = 0
                        #current_unavail = station_unavail_period[0]
                        #for st_index, st_tstp in enumerate(station_tstp_period):
                        #    while trips_iter < len(trips_tstp_period) and trips_tstp_period[trips_iter] < st_tstp:
                        #        trips_iter += 1
                        #        get_unavail_station(trips_tstp_period, station_tstp_period, station_unavail_period)
        
                        # Write to the output file the trajectory computed for the current period at this station
                        #trips_iter = 0
                        #st_index = station_start_index
                        #for trips_iter in range(len(trips_tstp_period)):
            
                        #    last_tstp = trips_tstp_period[trips_iter]
                        #    next_move = trips_bikes_moves_period[trips_iter]
                        #    next_reason = reasons_period[trips_iter]
                                   
                        #    while st_index < station_index and tstp_station[st_index] <= last_tstp:
                        #        last_avail = avail_station[st_index]
                        #        last_stands = free_station[st_index]
#                       #         last_unavail = unavail_station[st_index]
                        #        st_index += 1
                                   
                        #    trajectory_line = "%s %s %s %s %s\n" % (last_tstp, last_avail, last_stands, next_move, next_reason)
                        #    trajectory_file.write(trajectory_line)
                        #    last_avail += next_move
                        #    last_stands -= next_move
                                   
                        #last_unavail = station_unavail_period[-1]
                            #if last_avail < 0 or last_avail > capacity:
                                 #print "Last asilability : %s" % last_avail
                                #print trips_bikes_moves_period
                                   
                # Change the start of the next period from which we want to collect trips data
                #adjusted_start_tstp = max(tstp_trips[trips_progress_ind], next_day_tstp)
                                   
                # Once we get out of the loop, station_index is positionned at the beginning of the following day
                if station_index < len(tstp_station):
                    #print "Current datetime: %s" % convert_velibtstp_to_datetime(tstp_station[station_index])
                    next_day_dt = get_next_day_start_dt(convert_tstp_sec_to_datetime(tstp_station[station_index]))
                    #print "Next day: %s" % next_day_dt
                    next_day_tstp = convert_datetime_to_tstp_ms(next_day_dt)
                                   
                                   
            if trips_progress_ind < len(tstp_trips) and tstp_trips[trips_progress_ind] < tstp_trips[trips_progress_ind] + 1:
                                   
                corrected_tstp, corrected_avail, corrected_stands, corrected_bikes_moves, corrected_reasons, nb_trips_extracted = extract_trips_data_period([],
                        [], [], [], tstp_trips[trips_progress_ind:], bikes_moves[trips_progress_ind:], reason_trips[trips_progress_ind:], last_tstp, last_avail,
                        last_stands, max_shift, -100)
                                   
                # Store the trips tstp and bike move for the current day (including the shift and corrective trips)
                nb_trips_added += len(corrected_tstp) - nb_trips_extracted
                                   
                add_trips_to_trajectory(corrected_tstp, corrected_avail, corrected_stands, corrected_bikes_moves, corrected_reasons, trajectory_file)
                                   
    print "Total number of trips added: %s" % nb_trips_added
