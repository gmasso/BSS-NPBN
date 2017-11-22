#!/usr/bin/env bash


ulimit -n 2048

make


for i in ../data/station_data/*.h5; do
    python3 correct_station_data.py $i
done

#echo "now, we sort the results";
#for i in results/*; do
#    sort -g ${i} | uniq > ${i}_sorted;
#    mv ${i}_sorted $i
#done
