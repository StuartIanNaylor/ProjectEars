# trim
Silence trim

./trim.py provides scripts & utils to automatically trim silence from sound files ./trim.py -h (--help) to get parameter help

If trim fails and few files are processed or the results are corrupt its likely the source was not good.
You can use the trim routine as a quick quality test of recorded sound files even if the trimmed files might not be needed.
If you have start or end clicks or too much noise the trim will likely fail.
So start off @ `./trim.py --target_length=0.9` and work down 0.1 until all fail which should work as good info.
The default location is './in' and the default save folder is './out' but you can specificy locations in the run paramters by
`./trim.py --source_dir=[source_dir] --dest_dir=[dest_dir]` to change.
The default target trim length is 1.0s with a silence target percent of 0.1%
`./trim.py --target_length=[target_length] --silence_percentage=[silence_percentage]` to change.

`./trim.py --target_length=0.4 ---min_pass_len=0.2` are the main parameters as it will fail anything over target but also likely dud samples less than the min pass length


Folder contains `dc-offset.sh` that will try to correct bad offset in audio files that causes much problems with silence trimming `./dc-offset.sh' in the folder containing audio files.






