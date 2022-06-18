#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import glob
import os
import soundfile as sf
import numpy
import random

def get_segment(source_dir='./in', dest_dir='./out', target_length=1.0):
  
  if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
  source = glob.glob(os.path.join(source_dir, '*.wav'))
  qty = 1 
  for filename in source:
    wav, samplerate = sf.read(filename,dtype='float32')
    sample_length = int(target_length * samplerate)
    if len(wav) >= sample_length:
      offset = len(wav) - sample_length
      rnd_start = random.randrange(0, offset)
      wav = wav[rnd_start:rnd_start + sample_length]
      out = dest_dir + '/' + str(qty) + "-" + os.path.basename(filename)
      sf.write(out, wav, samplerate)
      qty += 1


def main_body():
  parser = argparse.ArgumentParser()
  parser.add_argument('--source_dir', default='./in', help='source dir location')
  parser.add_argument('--dest_dir', type=str, default='./out', help='dest dir location')
  parser.add_argument('--target_length', type=float, default=1.0, help='Target length of audio files to be trimmed to (s)')
  args = parser.parse_args()

  if args.dest_dir == None:
    args.dest_dir = "./out"
  
  get_segment(args.source_dir, args.dest_dir, args.target_length)
    
if __name__ == '__main__':
  main_body()

