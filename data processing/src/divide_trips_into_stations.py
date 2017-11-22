#!/opt/local/bin/python
import sys
import fileinput

def date_to_string(date, action, reason):
    return "{0} {1} {2}\n".format(date, action, reason);

my_files = {};
def my_station_file( i ):
    if (not i in my_files):
        f = open('results/stationTrips_{0}'.format(i),'a');
        my_files[i] = f;
    return my_files[i];

def convert_data(date, action, reason):
    
def add_to_hdf(i):
     = open('../data/Formated/stationTrips_{0}'.format(i),'a');

for line in fileinput.input():
    l = line.rstrip().split(';');
    my_station_file(l[2]).write(date_to_string(l[1],-1,l[0]));
    my_station_file(l[5]).write(date_to_string(l[4],1,l[0]));
