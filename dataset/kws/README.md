# KWS
Run scripts for tflite models

kws-test-non-stream.py is a testing tool for labels on a pretrained model.
You can do relatively short training runs and use kws-test-non-stream.py to listen to low scoring samples
p=play, n=next & d=delete wav from dataset.

```
./kws-test-non-stream.py -h
usage: kws-test-non-stream.py [-h] [--model_path MODEL_PATH] [--source_path SOURCE_PATH] [--label_index LABEL_INDEX] [--kw_length KW_LENGTH]
                              [--sample_rate SAMPLE_RATE] [--hit_sensitivity HIT_SENSITIVITY] [--greater_than]

options:
  -h, --help            show this help message and exit
  --model_path MODEL_PATH
                        tflite model path default=stream_state_external.tflite
  --source_path SOURCE_PATH
                        kw sample files path default=./out
  --label_index LABEL_INDEX
                        kw label index of hit test default=0
  --kw_length KW_LENGTH
                        length of kw (secs) default=1.0
  --sample_rate SAMPLE_RATE
                        Sample rate default=16000
  --hit_sensitivity HIT_SENSITIVITY
                        kw_sensitivity default=0.70
  --greater_than        compare > than default < than
```

--source_path is the labels folder you wish to test
--label_index is the label index you wish to do the hit test on
--hit_sensitivity is target hit level
--greater_than the default is to check for lower than the --hit_sensitivity but you can check accross labels for labels that have high scores in another label



