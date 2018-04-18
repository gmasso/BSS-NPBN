import pandas as pd

fileName = "../../data/velib.kml"
fp = open(fileName, 'r');

df_coords = pd.DataFrame(columns=["x", "y"])
print(df_coords)
s=" ";
has_error = 0;
i = 0;

while( s != ''):
    s = fp.readline();
    try:
        if "coordinates>" in s:
            name_start = s.index("name>") + 5;
            name_end = s.index("</name>");
            coords_start = s.index("coordinates>") + 12;
            coords_end = s.index("</coordinates>")
            print("id: ", s[name_start:name_end], " coords: ",s[coords_start:coords_end]);
    except ValueError as e:
        print ("Unexpected error on line "+ str(i) + ":" + s + ", " + str(e))
        has_error = i+1;
    except:
        raise
    #print(str(i)+" lines treated",end="\r");
    i = i+1;

fp.close()

#for child in root.findall