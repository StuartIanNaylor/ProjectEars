#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import argparse
import glob
import os
import time
import random
import soundfile as sf
import uuid
import sys
import sounddevice as sd
from cfonts import render, say


def record(dest_dir, read_time, sample_rate):  

  filename = dest_dir + '/' + str(uuid.uuid4()) + '.wav'
  time.sleep(0.05) #small reading delay
  # Make sure the file is opened before recording anything:
  with sf.SoundFile(filename, mode='x', samplerate=sample_rate, channels=1) as file:
    myrecording = sd.rec(int(read_time * sample_rate))
    sd.wait()
    file.write(myrecording)


def reader(key_words=['kw1'], dest_dir='./out', read_time=2.5, device=0, sample_rate=16000, language='en', list_devices=0, debug=0):

  if list_devices:
   print(sd.query_devices())
   exit()
 
  if device:
    sd.default.device = device
  
  sd.default.samplerate = sample_rate
  sd.default.channels = 1
  
  if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
  else:
    print("Dest_dir " + dest_dir + " already exists")
    exit()

  count = 1
  for kw in key_words:
    if not os.path.exists(dest_dir + "/kw" + str(count)):
      os.makedirs(dest_dir + "/kw" + str(count))
    else:
      print("kw_dir " + dest_dir + "/kw" + str(count) + " already exists")
      exit()
    count += 1
    
  if not os.path.exists(dest_dir + "/!kw"):
    os.makedirs(dest_dir + "/!kw")
  else:
    print("!kw_dir " + dest_dir + "/!kw" + " already exists")
    exit()
  
  print("Setup up you mic @ approx 0.3m and test volumes are as high as possible")
  
  sentences = glob.glob(language + '/*.txt')
  sentence_count = 1
  for sentence in sentences:
    f1=open(sentence, "r")
    fl =f1.readlines()
    print("Start recording on the count of 0")
    for count in range(5,0,-1):
      sys.stdout.write(str(count)+' ')
      sys.stdout.flush()
      time.sleep(1)
      
    for x in fl:    
      count = 1
      for kw in key_words: 
        os.system('clear')
        output = render(kw, font='huge', align='center')
        print(output)
        record(dest_dir + "/kw" + str(count), read_time, sample_rate)
        count += 1
      
      os.system('clear')
      output = render(x, font='huge', align='center')
      print(output)  
      record(dest_dir + "/!kw", read_time, sample_rate)
      
    os.system('clear')
    print("Ok you have " + str(sentence_count) + " out of " + str(len(sentences)) + " completed")
    if sentence_count == 1:
      print("Are you ready to try another and this time vary where you face the mic from away onside to the other")
    elif sentence_count ==2:
      print("Try a different expression with your key words and maybe this time sound tired or bored")
    elif sentence_count ==3:
      print("Varying your key words matter more than the other words maybe go back to your normal expression or try other expressions happy / surprised?")
    elif sentence_count >=4:
      print("If you can keep at it as more makes more accuracy...")
    input("Press Enter to continue... or press ctl+c to end")
    sentence_count += 1
  
def main_body():
  parser = argparse.ArgumentParser()
  parser.add_argument('--key_word', type=str, default='kw1', help='Key word text comma seperate for multipe [kw1,kw2,kw3...]')
  parser.add_argument('--dest_dir', type=str, default='./out', help='dest dir location default=out')
  parser.add_argument('--read_time', type=float, default=2.5, help='Record window time for each word default = 2.5s')
  parser.add_argument('--device', type=int, default=0, help='Input device [index] use --list_devices to display devices')
  parser.add_argument('--sample_rate', type=int, default=16000, help='sampling rate default=16000')
  parser.add_argument('--list_devices', help='list input devices', action="store_true")
  parser.add_argument('--language', type=str, default='en', help='Language folder to read !kw words from default=en')
  parser.add_argument('--debug', help='debug effect settings to cli', action="store_true")
  args = parser.parse_args()

  if args.dest_dir == None:
    args.dest_dir = "./out"
    
  key_words=args.key_word.split(",")
  count = 1
  for kw in key_words:
    if len(kw) == 0:
      print("Invalid key word " + str(count) + " = ", kw)
      exit()
    count += 1
   
  
  reader(key_words, args.dest_dir, args.read_time, args.device, args.sample_rate, args.language, args.list_devices, args.debug)

    
if __name__ == '__main__':
  main_body()
  
  
  

