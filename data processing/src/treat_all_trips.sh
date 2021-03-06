#!/usr/bin/env bash

ulimit -n 2048

#echo "Removing the previous result files..."
#rm ../data/trips/done/*

for i in ../data/trips/*.gz; do
    if [ ! -e $i ]; then echo 'problem...';  exit ; fi;
    file=`echo $i | sed 's/..\/data\/trips\///' | sed 's/.gz//'`
    if [ ! -e "../data/trips/done/$file" ]; then
	echo -n "treating $file: gunziping... "
	cp $i .
	if [ -e "$file" ]; then rm $file; fi;
	gunzip ${file}.gz
	echo -n "dividing..."
	python3 extract_trips.py ${file}
	touch "../data/trips/done/$file"
	rm ${file}
	echo "done"
    else
	echo "file $file already treated";
    fi
done

#echo "now, we sort the results";
#for i in results/*; do
#    sort -g ${i} > ${i}_sorted;
#    mv ${i}_sorted $i
#done
