#!/opt/local/bin/python
import json;
import sys

my_files = {};
def my_station_file( i ):
    if (not i in my_files):
        f = open('../data/availability/station_data/stationAvail_{0}'.format(i),'a');
        my_files[i] = f;
    return my_files[i];

fileName = sys.argv[1];
fp = open(fileName, 'r');

date_string = fileName
date_string = date_string.replace("data-", "")
date_string = date_string.replace(".txt_cleaned", "")

if len(date_string) == 10:
    date_string = date_string.replace("-", "")
elif len(date_string) == 8:
    date_string = date_string.replace("-", "0")
elif date_string[6] == "-":
    date_string = date_string.replace("-", "0", 1)
    date_string = date_string.replace("-", "")
elif date_string[7] == "-":
    date_string = date_string.replace("-", "", 1)
    date_string = date_string.replace("-", "0")
else:
    print("Problem while trying to correct the date for the file name: Length of " + str(date_string) + " is " + str(len(date_string)))

date_of_day = convert_datestring_to_date(date_string)

# Set the starting tstp slightly at the beginning of the day indicated in the file name
starting_tstp = set_starting_tstp_day(date_of_day)

s=" ";
has_error = 0;
i = 0;

while( s != ''):
    s = fp.readline();
    if ( len(s) > 2 ):
        try:
            d = json.loads(s);
            for data in d["ststates"]:
                text=" ".join([time_stamp,str(data["state"]), str(data["freebk"]),str(data["freebs"]),"\n"]);
                my_station_file(data["nb"]).write(text);
        except ValueError as e:
            print ("Unexpected error on line "+str(i)+":"+str(e))
            has_error = i+1;
        except:
            raise
    print(str(i)+" lines treated",end="\r");
    i = i+1;

print("");
fp.close()

for st_file in my_files:
    st_file.close();
