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
import numpy as np


def sox_combine(kw1, kw2, dest_dir, overlap, kw1_duration):
  
  duration = kw1_duration - (random.randint(100, int(overlap * 1000)) / 1000)
  tfm = sox.Transformer()
  tfm.pad(start_duration = duration)
  tfm.build(kw2, '/tmp/kw2_padded.wav')
  cbn = sox.Combiner()
  cbn.build([kw1, '/tmp/kw2_padded.wav'], dest_dir + '/' + str(uuid.uuid4()) + '.wav', 'mix-power')

def combine(kw1_dir='./kw1', kw2_dir='./kw2', dest_dir='./out', kw_target=1000, kw_range=20, overlap=0.1):

  if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
  if not os.path.exists(kw1_dir):
    print("Kw1_dir = " + kw1_dir + " does not exist!")
    exit()
  if not os.path.exists(kw2_dir):
    print("Kw2_dir = " + kw2_dir + " does not exist!")
    exit()
    
  logging.getLogger('sox').setLevel(logging.ERROR)
  sample_rate = 16000

  kw1_files = glob.glob(os.path.join(kw1_dir, '*.wav')) 
  kw1 = []
  for wav in kw1_files:
    info = sox.file_info.stat(wav)
    #print(info)
    #print(info['Rough   frequency'], wav)
    kw1.append([info['Rough   frequency'], wav,info['Length (seconds)']])
  kw1 = sorted(kw1)


  kw2_files = glob.glob(os.path.join(kw2_dir, '*.wav')) 
  kw2 = []
  for wav in kw2_files:
    info = sox.file_info.stat(wav)
    #print(info)
    #print(info['Rough   frequency'], wav)
    kw2.append([info['Rough   frequency'], wav,info['Length (seconds)']])
  kw2 = sorted(kw2)
  
  kw1_count = 0
  
  while kw1_count < kw_target:
    kw1_index = random.randint(0, len(kw1) - 1)
    target_freq = kw1[kw1_index][0]
    kw2_count = 0
    match = False
    while kw2_count < len(kw2):
      if target_freq <= kw2[kw2_count][0]:
        if kw2_count - kw_range >= 0:
          kw_min = kw2_count - kw_range
        else:
          kw_min = 0
        if kw2_count + kw_range < len(kw2):
          kw_max = kw2_count + kw_range
        else:
          kw_max = len(kw2) -1
        match = True
        kw2_index = random.randint(kw_min, kw_max)
        #print(target_freq, kw2[kw2_index][0], kw1_count, kw2_count)
        sox_combine(kw1[kw1_index][1], kw2[kw2_index][1], dest_dir, overlap, kw1[kw1_index][2])
        break
      kw2_count += 1
    if match == True:
      kw1_count += 1

    
def main_body():
  parser = argparse.ArgumentParser()
  parser.add_argument('--kw1_dir', default='./kw1', help='source dir location default=./kw1')
  parser.add_argument('--kw2_dir', default='./kw2', help='source dir location default=./kw2')
  parser.add_argument('--dest_dir', type=str, default='./out', help='dest dir location default=./out')
  parser.add_argument('--kw_target', type=int, default=1000, help='kw target qty default=1000')
  parser.add_argument('--kw_range', type=int, default=10, help='Random range of freq match (+/-) default=10')
  parser.add_argument('--overlap', type=float, default=0.1, help='kw overlap duration default=0.1s')
  args = parser.parse_args()

  if args.dest_dir == None:
    args.dest_dir = "./out"
  
  combine(args.kw1_dir, args.kw2_dir, args.dest_dir, args.kw_target, args.kw_range, args.overlap)

    
if __name__ == '__main__':
  main_body()







