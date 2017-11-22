#!/usr/bin/env bash


ulimit -n 2048

make

#echo "Removing the previous result files..."
#rm ../data/availability/done/*
rm ../data/availability/clean/*

for i in ../data/availability/*.gz; do
    file=`echo $i | sed 's/..\/data\/availability\///' | sed 's/.gz//'`
    if [ ! -e "../data/availability/done/$file" ]; then
	echo "treating $file..."
	cp $i .
	if [ -e "$file" ]; then rm $file; fi;
	gunzip -c $file.gz | ./clean_data | grep tstp > ../data/availability/clean/${file}_cleaned
        python3 extract_all_avail.py ../data/availability/clean/${file}_cleaned
        #echo "Error: trying line by line..."
        #python3 treat_prob_stations.py ../data/availability/clean/${file}_cleaned	
        #python3 divide_day_into_stations.py ${file}_cleaned
	touch "../data/availability/done/$file"
	rm ${file}.gz
        rm ../data/availability/clean/${file}_cleaned
    else
	echo "file $file already treated";
    fi
done

#echo "now, we sort the results";
#for i in results/*; do
#    sort -g ${i} | uniq > ${i}_sorted;
#    mv ${i}_sorted $i
#done
