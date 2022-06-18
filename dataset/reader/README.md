# reader
reader is an on screen prompter of words for your dataset
prompting for words like this can make dictation and seperation into audio files much easier

If you want a CLI VU meter then change `plughw:x` to you mic soundcard index `arecord -D plughw:1 -V mono -r 16000 -f S16_LE -c 1 /dev/null`
This will just test the selected source of `plughw:1` and display a cli VU meter without creating any files for test `aplay -l` will list devices.
Its advisable to do a quick test to make sure the input levels are ok

./reader provides the onscreen reader and will count down to zero before it starts.
The default 2.5 second recording window gives plenty of time to read the word and pronounce so no rush.

./reader.py -h (--help) to get parameter help

The default save location is 'out' and each key word will be given a sub folder with all the unknown not key word going into !kw

`./reader.py --device=12 --key_word="hey,marvin" --sample_rate=44100` you may have to use the default sample rate of your soundcard.
Or set-up a PCM in /etc/asound.conf with a plughw device

Either way resampling later is no problem.

It prob helps to be a native speaker to collect phonetic pangrams for your language and being English struggled with other languages.
If anyone can please create your own phonetic pangrams and request addition on github.
Examples can be found on
https://clagnut.com/blog/2380/
https://www.liquisearch.com/list_of_pangrams/english_phonetic_pangrams





