# Dataset-builder
KWS dataset builder for KWS

```
sudo apt update -y
sudo apt install -y python3-dev python3-pip python3-venv libsndfile1 libportaudio2 libsox-fmt-all sox ffmpeg libavcodec-extra bc
python3 -m venv --system-site-packages ./venv
source ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt 
```
`deactivate` to exit venv

Dataset-builder is just a collection of scripts to make it easier to create high quality datasets as quickly as possible.
The scripts are split into folders of specific function and so named.

./trim-combine provides scripts & utils to automatically trim silence from wav files and combine kw, also can be used to test record quality

If you want a CLI VU meter then change `plughw:x` to you mic soundcard index `arecord -D plughw:1 -V mono -r 16000 -f S16_LE -c 1 /dev/null`
This will just test the selected source of `plughw:1` and display a cli VU meter without creating any files for test `aplay -l` will list devices.
Its advisable to do a quick test to make sure the input levels are ok

./augment provides scripts to augent audio files into many more with variance by sox effects

./reader provides an on screen reader to simply collect keyword and a not keyword dataset

./ml-commons creates sqlite ml-commons database for analysis and various other ml-commons tools


