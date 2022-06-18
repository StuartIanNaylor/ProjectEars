#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tflite_runtime.interpreter as tflite
import sounddevice as sd
import numpy as np
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--device', type=int, help='Record device index --list_devices to list indexes')
parser.add_argument('--model_path', default='non_stream.tflite', help='tflite model path default=stream_state_external.tflite')
parser.add_argument('--window_strides', type=int, default=2, help='rolling window strides per sample (2, 4 or 8)')
parser.add_argument('--sample_rate', type=int, default=16000, help='Sample rate default=16000')
parser.add_argument('--kw_length', type=float, default=1.0, help='length of kw (secs) default=1.0')
parser.add_argument('--kw_sensitivity', type=float, default=0.70, help='kw_sensitivity default=0.70')
parser.add_argument('--list_devices', help='list input devices', action="store_true")
parser.add_argument('--noise_sensitivity', type=float, default=0.90, help='noise_sensitivity default=0.90')
parser.add_argument('--kw_index', type=int, default=0, help='kw label index default = 0')
parser.add_argument('--noise_index', type=int, default=1, help='noise label index default = 1')
parser.add_argument('--debug', help='debug effect settings to cli', action="store_true")
args = parser.parse_args()
 
if args.list_devices:
 print(sd.query_devices())
 exit()
 
if args.device:
  sd.default.device = args.device

num_channels = 1
if args.window_strides == 2:
  blocksize = int(args.sample_rate / args.window_strides)
elif args.window_strides == 4:
  blocksize = int(args.sample_rate / args.window_strides)
elif args.window_strides == 8:
  blocksize = int(args.sample_rate / args.window_strides)
else:
  print("window_strides must equal 4 or 8")
  

kw_sensitivity = args.kw_sensitivity
kw_index = args.kw_index
noise_sensitivity = args.noise_sensitivity
noise_index = args.noise_index

rolling_window_size = int(args.sample_rate * args.kw_length)
rolling_window = np.zeros((rolling_window_size, 1),dtype=np.float32)
  
# Load the TFLite model and allocate tensors.
interpreter1 = tflite.Interpreter(model_path=args.model_path)
interpreter1.allocate_tensors()

# Get input and output tensors.
input_details1 = interpreter1.get_input_details()
output_details1 = interpreter1.get_output_details()

inputs1 = []


def sd_callback(rec, frames, ftime, status):

    global blocksize, rolling_window_size, rolling_window
    global kw_sensitivity, noise_sensitivity, kw_index, noise_index
    
    rolling_window = np.roll(rolling_window, -blocksize)
    rolling_window[rolling_window_size - blocksize:rolling_window_size] = rec
        
    rec = np.reshape(rolling_window, (1, rolling_window_size))
    
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
   
    kw = output_data[0][kw_index]
    if kw >= kw_sensitivity:
      print("KW hit", kw)
      for s in range(len(input_details1)):
        inputs1.append(np.zeros(input_details1[s]['shape'], dtype=np.float32))
    noise = output_data[0][noise_index]
    if noise >= noise_sensitivity:
      print("Noise detected", noise)
    


for s in range(len(input_details1)):
  inputs1.append(np.zeros(input_details1[s]['shape'], dtype=np.float32))

print("Loaded")
    
# Start streaming from microphone
with sd.InputStream(channels=num_channels,
                    samplerate=args.sample_rate,
                    blocksize=int(blocksize),
                    callback=sd_callback):
  threading.Event().wait()                        



