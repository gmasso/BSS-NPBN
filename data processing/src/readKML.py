import pandas as pd

fileName = "../../data/velib.kml"
fp = open(fileName, 'r');

df_coords = pd.DataFrame(columns=["x", "y"])
print(df_coords)
s=" ";
has_error = 0;
i = 0;
station_id = 0;
while( s != ''):
    s = fp.readline();
    try:
        if "coordinates>" in s:
            coords_start = s.index("coordinates>") + 12;
            coords_end = s.index("</coordinates>")
            coords_string = s[coords_start:coords_end];
            x = float(coords_string[:coords_string.index(",")]);
            y = float(coords_string[coords_string.index(",")+1:]);
            if station_id > 0:
                df_coords.loc[station_id, "x"] = x
                df_coords.loc[station_id, "y"] = y
                station_id = 0;
            else:
                print("Problem");
        if "Placemark id" in s:
            substring = s[s.index("Placemark id"):];
            name_start = substring.index("name>") + 5;
            name_end = substring.index("</name>");
            station_id = int(substring[name_start:name_end])
            print(station_id)

    except ValueError as e:
        print ("Unexpected error on line "+ str(i) + ":" + s + ", " + str(e))
        has_error = i+1;
    except:
        raise
    #print(str(i)+" lines treated",end="\r");
    i = i+1;

fp.close()

df_coords.to_csv("../../data/station_coords.csv")
#for child in root.findall