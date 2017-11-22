#!/usr/bin/env bash

ulimit -n 2048

make

echo "*********************************"
echo "Cleaning previous result files..."

find ../data/availability/done/* ! -name '*.txt*' | rm
#Only if we want to extract all the data by station again
#rm ../data/availability/done/*
#rm ../data/availability/station_data/*

echo "done."
echo "*********************************"

echo " "

echo "******************************************"
echo "Extracting data from availability files..."

for i in ../data/availability/*.gz; do
    file=`echo $i | sed 's/..\/data\/availability\///' | sed 's/.gz//'`
    if [ ! -e "../data/availability/done/$file" ]; then
	echo "extracting data from $file..."
	cp $i .
	if [ -e "$file" ]; then rm $file; fi;
	gunzip -c $file.gz | ./clean_data | grep tstp > ${file}_cleaned
	python3 split_avail_to_stations.py ${file}_cleaned
	touch "../data/availability/done/$file"
	rm ${file}.gz ${file}_cleaned
    else
	echo "file $file already treated";
    fi
done

echo "done."
echo "******************************************"

echo " "

echo "********************************************"
echo "Converting the data to pandas HDF5 format..."

python3 convert_to_pdata.py

echo "done."
echo "********************************************"

echo " "

echo "****************************************************"
echo "Correcting corrupted data and building final data..."

python3 correct_all_data.py

echo "done."
echo "****************************************************"
