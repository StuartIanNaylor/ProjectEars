#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tflite_runtime.interpreter as tflite
import sounddevice as sd
import numpy as np
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--device', type=int, help='Record device index --list_devices to list indexes')
parser.add_argument('--model_path', default='stream_state_external.tflite', help='tflite model path default=stream_state_external.tflite')
parser.add_argument('--window_stride', type=float, default=0.020, help='window_stride default=0.020')
parser.add_argument('--sample_rate', type=int, default=16000, help='Sample rate default=16000')
parser.add_argument('--kw_sample_size', type=int, default=30, help='Moving average kw sample size default=30')
parser.add_argument('--kw_index', type=int, default=0, help='kw label index default=0')
parser.add_argument('--noise_index', type=int, default=1, help='noise label index default=1')
parser.add_argument('--noise_sample_size', type=int, default=30, help='Moving average noise sample size default=30')
parser.add_argument('--kw_sensitivity', type=float, default=0.70, help='kw_sensitivity default=0.70')
parser.add_argument('--list_devices', help='list input devices', action="store_true")
parser.add_argument('--noise_sensitivity', type=float, default=0.90, help='noise_sensitivity default=0.90')
parser.add_argument('--debug', help='debug effect settings to cli', action="store_true")
args = parser.parse_args()
 
if args.list_devices:
 print(sd.query_devices())
 exit()
 
if args.device:
  sd.default.device = args.device

num_channels = 1
kw_window = np.zeros(args.kw_sample_size)
kw_window_size = args.kw_sample_size
kw_window_count = 0
kw_max = 0
kw_sensitivity = args.kw_sensitivity
kw_index = args.kw_index

noise_window = np.zeros(args.noise_sample_size)
noise_window_size = args.noise_sample_size
noise_window_count = 0
noise_max = 0
noise_sensitivity = args.noise_sensitivity
noise_index = args.noise_index

# Load the TFLite model and allocate tensors.
interpreter1 = tflite.Interpreter(model_path=args.model_path)
interpreter1.allocate_tensors()

# Get input and output tensors.
input_details1 = interpreter1.get_input_details()
output_details1 = interpreter1.get_output_details()

inputs1 = []

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def sd_callback(rec, frames, ftime, status):
     
    global kw_window, kw_window_count, kw_max, kw_sensitivity, kw_index
    global noise_window, noise_window_count, noise_max, noise_sensitivity, noise_index
    # Notify if errors
    if status:
        print('Error:', status)
    
    rec = np.reshape(rec, (1, 320))

    # Make prediction from model
    interpreter1.set_tensor(input_details1[0]['index'], rec)
    # set input states (index 1...)
    for s in range(1, len(input_details1)):
      interpreter1.set_tensor(input_details1[s]['index'], inputs1[s])
    interpreter1.invoke()
    output_data1 = interpreter1.get_tensor(output_details1[0]['index'])
    # get output states and set it back to input states
    # which will be fed in the next inference cycle
    for s in range(1, len(input_details1)):
      # The function `get_tensor()` returns a copy of the tensor data.
      # Use `tensor()` in order to get a pointer to the tensor.
      inputs1[s] = interpreter1.get_tensor(output_details1[s]['index'])

    kw = output_data1[0][kw_index]
    kw_window[kw_window_count] = kw
    kw_window_count += 1
    if kw_window_count > kw_window_size -1:
      kw_window_count = 0
    kw_hit = moving_average(kw_window, kw_window_size)
    if kw_hit[0] > kw_max:
      kw_max = kw_hit[0]
    if kw_hit[0] > kw_sensitivity:
      if kw_max > kw_hit[0]:
        print("KW hit", kw_max)
        kw_max = 0
        kw_window.fill(0)
        for s in range(len(input_details1)):
          inputs1.append(np.zeros(input_details1[s]['shape'], dtype=np.float32))
             
    noise = output_data1[0][noise_index]
    noise_window[noise_window_count] = noise
    noise_window_count += 1
    if noise_window_count > noise_window_size -1:
      noise_window_count = 0
    noise_hit = moving_average(noise_window, noise_window_size)
    if noise_hit[0] > noise_max:
      noise_max = noise_hit[0]
    if noise_hit[0] > noise_sensitivity:
      if noise_max > noise_hit[0]:
        print("Noise", noise_max)
        noise_max = 0
        noise_window.fill(0)



for s in range(len(input_details1)):
  inputs1.append(np.zeros(input_details1[s]['shape'], dtype=np.float32))

print("Loaded")
    
# Start streaming from microphone
with sd.InputStream(channels=num_channels,
                    samplerate=args.sample_rate,
                    blocksize=int(args.sample_rate * args.window_stride),
                    callback=sd_callback):
  threading.Event().wait()                        



