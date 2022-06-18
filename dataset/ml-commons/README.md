# ml-commoms
ml-commoms provides scripts for the large spoken word data of https://mlcommons.org/en/multilingual-spoken-words/
The scripts allow to to create a database so that analysis and selection can be processed more easily

https://mlcommons.org/en/multilingual-spoken-words/ is not static but updates are infrequent so a premade database is provided
cmudict is provided create pohone & slyable tables for word analysis and selection.
cmudict is quite slow and with the size of https://mlcommons.org/en/multilingual-spoken-words/ can take considerable time
Further lang models can be found some are on https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/ in *.dic format

Download the dataset https://mlcommons.org/en/multilingual-spoken-words/ and extract and the examples here are for the english subset

./create-db.py --source_dir=en/clips --database=ml-commons.db

./create-db.py -h for parameter help

This will create a new database and overwrite existing but will take considerable time due ro cmudict being quite slow.
The repo does contain the en dataset already in ml-commons.db but may become out of date or you may wish to use a different language


./word2wav.py --word=test convert all opus files to 16k 16bit wav from ./en/clips/test to ./out/test

./word2wav.py -h for parameter help


