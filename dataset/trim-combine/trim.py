#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import argparse
import glob
import os
import random
import soundfile as sf
import uuid
import sox

def trim(source_dir='./in', dest_dir='./out', target_length=1.0, min_pass_len=0.2, silence_percentage=0.1, tries=5, increment=2, min_silence_duration=0.05, fade_len=0.05):

  if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
  if not os.path.exists(source_dir):
    print("Source_dir = " + source_dir + " does not exist!")
    exit()
    
  logging.getLogger('sox').setLevel(logging.ERROR)
  sample_rate = 16000
  sp = silence_percentage
  source = glob.glob(os.path.join(source_dir, '*.wav'))
  tfm = sox.Transformer()
  count = 0
  fail = 0

  for wav in source:
    sp = silence_percentage
    t = 0
    #try t times
    while t < tries:
      tfm.clear_effects()
      tfm.norm(-0.1)
      tfm.silence(location=1, silence_threshold=sp, min_silence_duration=min_silence_duration)
      tfm.silence(location=-1, silence_threshold=sp, min_silence_duration=min_silence_duration)
      tfm.fade(fade_in_len=fade_len, fade_out_len=fade_len)
      array_out = tfm.build_array(input_filepath=wav, sample_rate_in=sample_rate)
      #Silence increments in steps so that trim is done in 1 pass
      #Incrementing over multiple passes tends to create more errors
      if len(array_out) <= sample_rate * min_pass_len:
        print(wav + " Failed! length = " + str(len(array_out) / sample_rate) + 's')
        t = tries
        count += 1
        fail += 1
        continue
      if len(array_out) <= sample_rate * target_length:
        print(sample_rate * min_pass_len)
        tfm.build_file(input_array=array_out, sample_rate_in=sample_rate, output_filepath=dest_dir + '/' + str(uuid.uuid4()) + '.wav')
        print(dest_dir + '/' + str(uuid.uuid4()) + '.wav  Sucess! length = ' + str(len(array_out) / sample_rate) + 's')
        count += 1
        t = tries
        continue
      #increment silence_percentage by increment factor
      sp = sp * increment
      print(sp)
      t += 1
      if t == tries:
        print(wav + " Failed! length = " + str(len(array_out) / sample_rate) + 's')
        count += 1
        fail += 1
    
  if count == 0:
    print("Source_dir " + source_dir + " is empty no .wav files found or are larger than target size")
  else:
    print(str(fail) + " failed out of " + str(count))

    
    
def main_body():
  parser = argparse.ArgumentParser()
  parser.add_argument('--source_dir', default='./in', help='source dir location default=./in')
  parser.add_argument('--dest_dir', type=str, default='./out', help='dest dir location default=./out')
  parser.add_argument('--target_length', type=float, default=1.0, help='Minimum trimmed length default=1.0s')
  parser.add_argument('--silence_percentage', type=float, default=0.1, help='Start trim level silence percentage default=0.1s')
  parser.add_argument('--tries', type=int, default=5, help='The number of tries to trim incrementing silence_percentage by the increment factor')
  parser.add_argument('--increment', type=int, default=2, help='The increment factor for each try default=2')
  parser.add_argument('--min_silence_duration', type=float, default=0.05, help='min silence duration default=0.05s')
  parser.add_argument('--fade_len', type=float, default=0.05, help='fade in & out length default=0.05s')
  parser.add_argument('--min_pass_len', type=float, default=0.2, help='min length before fail default=0.2s')
  args = parser.parse_args()

  if args.dest_dir == None:
    args.dest_dir = "./out"
  
  trim(args.source_dir, args.dest_dir, args.target_length, args.min_pass_len, args.silence_percentage, args.tries, args.increment, args.min_silence_duration, args.fade_len)

    
if __name__ == '__main__':
  main_body()







