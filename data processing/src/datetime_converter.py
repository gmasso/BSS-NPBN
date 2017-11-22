from datetime import datetime, timedelta, time
from time import mktime
from pytz import utc, timezone

##################################################################################
###                           date_format_checker                              ###
##################################################################################
def date_format_checker(dt_string):
    """Check if the date format is correct and returns a standard string of type YYYYMMDDHHMMSS corresponding to that date. If the date format is not correct, prints precisions on the date format expected and stop the execution with exit code 1"""
    
    format_type_1 = (len(dt_string) == 14 and 1969 < int(dt_string[:4]) < 2038 and 0 < int(dt_string[4:6]) < 13 and 0 < int(dt_string[6:8]) < 32 and -1 < int(dt_string[8:10]) < 25 and -1 < int(dt_string[10:12]) < 61 and -1 < int(dt_string[12:14]) < 61)

    format_type_2 = (len(dt_string) == 19 and 1969 < int(dt_string[:4]) < 2038 and dt_string[4] == '-' and 0 < int(dt_string[5:7]) < 13 and dt_string[7] == '-' and 0 < int(dt_string[8:10]) < 32 and dt_string[10] == ' ' and -1 < int(dt_string[11:13]) < 25 and dt_string[13] == ':' and -1 < int(dt_string[14:16]) < 61 and dt_string[16] == ':' and -1 < int(dt_string[17:19]) < 61)

    format_type_2 = (len(dt_string) == 19 and 1969 < int(dt_string[:4]) < 2038 and dt_string[4] == '-' and 0 < int(dt_string[5:7]) < 13 and dt_string[7] == '-' and 0 < int(dt_string[8:10]) < 32 and dt_string[10] == ' ' and -1 < int(dt_string[11:13]) < 25 and dt_string[13] == ':' and -1 < int(dt_string[14:16]) < 61 and dt_string[16] == ':' and -1 < int(dt_string[17:19]) < 61)

    # Check (roughly) if the date format is correct
    if format_type_1:
        return dt_string

    elif format_type_2:
        return dt_string[:4]+dt_string[5:7]+dt_string[8:10]+dt_string[11:13]+dt_string[14:16]+dt_string[17:19]

    # If not, print precisions on the date format expected and stop the program with exit code 1
    else:
        print ("""ERROR: Wrong date format! Please use one of the following date format:
        \t YYYYMMDDHHMMSS
        \t YYYY-MM-DD HH:MM:SS""")
        exit(1)


##################################################################################
###                     convert_datestring_to_datetime                         ###
##################################################################################
def convert_datestring_to_datetime(dt_string):
    """Returns the datetime corresponding to the string 'dt_string'."""
    # Check if the string date_string is in the right format
    # Make sure the input is a string
    dt_string = str(dt_string)

    datetime_string = date_format_checker(dt_string)

    dt = datetime(int(datetime_string[:4]), int(datetime_string[4:6]), int(datetime_string[6:8]), int(datetime_string[8:10]), int(datetime_string[10:12]), int(datetime_string[12:14]))
    #return dt
    paris_tz = timezone('Europe/Paris')
    #paris_dt = paris_tz.localize(dt, is_dst=True)
    paris_dt = paris_tz.localize(dt, is_dst=True).astimezone(paris_tz)

    return paris_dt

##################################################################################
###                       convert_velibtstp_to_datetime                        ###
##################################################################################
def convert_velibtstp_to_datetime(velib_tstp):
    """Convert the timestamp velib_tstp to a datetime in paris timezone."""

    # Convert tstp to a datetime object
    dt = datetime.utcfromtimestamp(int(velib_tstp/1000))
    
    tz_paris = timezone("Europe/Paris")
    # Convert dt to Paris timezone
    dt_paris = (tz_paris.localize(dt, is_dst=True)).astimezone(tz_paris)

    return dt_paris


##################################################################################
###                        convert_tstp_sec_to_datetime                        ###
##################################################################################
def convert_tstp_sec_to_datetime(tstp):
    """Convert the timestamp velib_tstp to a datetime in paris timezone."""

    # Convert tstp to a datetime object
    dt = datetime.utcfromtimestamp(int(tstp))

    
    tz_paris = timezone("Europe/Paris")
    ## Convert dt to Paris timezone
    dt_paris = (utc.localize(dt, is_dst=True)).astimezone(tz_paris)

    return dt_paris


##################################################################################
###                       convert_datetime_to_string                           ###
##################################################################################
def convert_datetime_to_string(dt):
    """Returns a string representing the datetime 'dt'."""
    return dt.strftime('%Y%m%d%H%M%S')

##################################################################################
###                       extract_hour_minute_string                           ###
##################################################################################
def extract_hour_minute_string(dt):
    """Returns a string representing the datetime 'dt'."""
    return dt.strftime('%H:%M')

##################################################################################
###                           is_public_holiday                                ###
##################################################################################
def is_public_holiday(dt):
    """Return True if the datetime object 'dt' corresponds to a french public holiday, False otherwise."""
    month = dt.month
    day = dt.day
    if dt.year == 2014:
        if month == 1 and (day == 1 or day == 6): 
            return True
        elif month == 2 and day == 14:
            return True
        elif month == 3 and day == 4:
            return True
        elif month == 4 and day == 21:
            return True
        elif month == 5 and (day == 1 or day == 8 or day == 29):
            return True
        elif month == 6 and day == 9:
            return True
        elif month == 7 and day == 14:
            return True
        elif month == 8 and day == 15:
            return True
        elif month == 11 and (day == 1 or day == 11):
            return True
        elif month == 12 and (day == 25 or day == 31):
            return True

    return False

##################################################################################
###                             is_workingday                                  ###
##################################################################################
def is_workingday(dt):
    """Return True if the datetime object 'dt' corresponds to a working day, False otherwise."""
    return dt.weekday() < 5 and not is_public_holiday(dt)

##################################################################################
###                          string_type_of_day                                ###
##################################################################################
def string_type_of_day(dt):
    """ Return a string corresponding to the type of day of dt."""
    if is_workingday(dt):
        return 'wd'
    else:
        return 'we'

##################################################################################
###                        convert_duration_to_seconds                         ###
##################################################################################
def convert_duration_to_seconds(duration):
    """Convert a string representing a duration into a timedelta object."""
    # Check if the string 'duration' is in the right format
    duration_string = duration_format_checker(duration)
    
    timedelta_duration = timedelta(hours=int(duration_string[:2]), minutes=int(duration_string[2:4]), seconds=int(duration_string[4:6]))
    return timedelta_duration.seconds
