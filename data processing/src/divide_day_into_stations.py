#!/opt/local/bin/python
import json;
import sys

from datetime_converter import convert_datestring_to_date, set_starting_tstp_day

my_files = {};
def my_station_file( i ):
    if (not i in my_files):
        f = open('results/stationAvail_{0}'.format(i),'a');
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
tstp = starting_tstp - 60000

while( s != ''):
    s = fp.readline();
    if ( len(s) > 2 ):
        try:
            d = json.loads(s);

            diff_tstp = d["tstp"] - tstp

            # Pb si grands sauts en avant!!!
            if  diff_tstp < -900000 or diff_tstp > 300000:
            #if  diff_tstp < 10000 or diff_tstp > 300000:
                #bad_tstp_count += 1
                tstp += 60000
                continue
            #elif diff_tstp > 300000:
            #    #bad_tstp_count += 1
            #    tstp += 60000
            #    continue

            #bad_tstp_count = 0

            if diff_tstp < 20000:
                tstp += 60000
            else:
                tstp = d["tstp"]

            time_stamp = str(int(tstp));
            
            for data in d["ststates"]:
                if (data["state"] == "open"):
                    text=" ".join([time_stamp,str(data["freebk"]),str(data["freebs"]),"\n"]);
                else:
                    text=" ".join([time_stamp,"NaN","NaN\n"]);
                my_station_file(data["nb"]).write(text);
                #with open('results/stationAvail_{0}'.format(data["nb"]),'a') as my_st_file:
                #    my_st_file.write(text)
        except ValueError as e:
            print ("Unexpected error on line "+str(i)+":"+str(e))
            has_error = i+1;
        except:
            raise
    print(str(i)+" lines treated",end="\r");
    i = i+1;

print("");
fp.close()

#for st_file in my_files:
#    st_file.close();
