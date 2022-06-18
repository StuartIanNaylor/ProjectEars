#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tflite_runtime.interpreter as tflite
import numpy as np
import soundfile as sf
import soundcard as sc
import glob
import os
import argparse
import sys,tty,os,termios
import random

def get_id(list_item):
  item = os.path.basename(list_item)
  item = item.split('-')
  #print(item)
  return int(item[0])


def getkey():
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        while True:
            b = os.read(sys.stdin.fileno(), 3).decode()
            if len(b) == 3:
                k = ord(b[2])
            else:
                k = ord(b)
            key_mapping = {
                127: 'backspace',
                10: 'return',
                32: 'space',
                9: 'tab',
                27: 'esc',
                65: 'up',
                66: 'down',
                67: 'right',
                68: 'left'
            }
            return key_mapping.get(k, chr(k))
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def kw_test(rec, label_index=0, sample_length=16000):
    global input_details1
    global output_details1
    global inputs1

    hit = 0
  
    shape = np.shape(rec)
    padded_rec = np.zeros((sample_length),dtype=np.float32)
    padded_rec[:shape[0]] = rec
    rec = np.reshape(padded_rec, (1, sample_length))
    
    # Make prediction from model
    interpreter1.set_tensor(input_details1[0]['index'], rec)
    # set input states (index 1...)
    for s in range(1, len(input_details1)):
      interpreter1.set_tensor(input_details1[s]['index'], inputs1[s])
  
    interpreter1.invoke()
    output_data = interpreter1.get_tensor(output_details1[0]['index'])
    # get output states and set it back to input states
    # which will be fed in the next inference cycle
    for s in range(1, len(input_details1)):
      # The function `get_tensor()` returns a copy of the tensor data.
      # Use `tensor()` in order to get a pointer to the tensor.
      inputs1[s] = interpreter1.get_tensor(output_details1[s]['index'])
   
    hit = output_data[0][label_index]

    return hit
    
def play_wav(wav, filename, samplerate):
  default_speaker = sc.default_speaker()
  default_speaker.play(wav, samplerate=samplerate)
  try:
    while True:
        k = getkey()
        if k == 'p':
            default_speaker.play(wav, samplerate=samplerate)
        elif k == 'd':
            os.remove(filename)
            print(filename + " removed")
            break
        elif k == 'n':
            print("next")
            break          
  except (KeyboardInterrupt, SystemExit):
    os.system('stty sane')
    print('stopping.')
    exit()



parser = argparse.ArgumentParser()
parser.add_argument('--model_path', default='non_stream.tflite', help='tflite model path default=stream_state_external.tflite')
parser.add_argument('--source_path', default='./out', help='kw sample files path default=./out')                
parser.add_argument('--label_index', type=int, default=0, help='kw label index of hit test default=0')
parser.add_argument('--kw_length', type=float, default=1.0, help='length of kw (secs) default=1.0')
parser.add_argument('--sample_rate', type=int, default=16000, help='Sample rate default=16000')
parser.add_argument('--hit_sensitivity', type=float, default=0.70, help='kw_sensitivity default=0.70')
parser.add_argument('--greater_than', help='compare > than default < than', action="store_true")
args = parser.parse_args()

sample_length = int(args.kw_length * args.sample_rate)
# Load the TFLite model and allocate tensors.
interpreter1 = tflite.Interpreter(model_path=args.model_path)
interpreter1.allocate_tensors()
# Get input and output tensors.
input_details1 = interpreter1.get_input_details()
output_details1 = interpreter1.get_output_details()
inputs1 = []

for s in range(len(input_details1)):
  inputs1.append(np.zeros(input_details1[s]['shape'], dtype=np.float32))

count = 0    
#source = sorted(glob.glob(os.path.join(args.source_path, '*.wav')), key=get_id)
source = glob.glob(os.path.join(args.source_path, '*.wav'))
print(len(source), args.source_path)
for filename in source:
  wav, samplerate = sf.read(filename,dtype='float32')
  if len(wav) > sample_length:
    offset = len(wav) - sample_length
    rnd_start = random.randrange(0, offset)
    wav = wav[rnd_start:rnd_start+sample_length]
  hit = kw_test(wav, args.label_index, sample_length)
  if args.greater_than:
    if hit > args.hit_sensitivity:
      print(filename, hit)
      #os.remove(filename)
      play_wav(wav, filename, args.sample_rate)
      count += 1
  else:
    if hit < args.hit_sensitivity:
      print(filename, hit)
      #os.remove(filename)
      play_wav(wav, filename, args.sample_rate)
      count += 1
print("total found " + str(count))


