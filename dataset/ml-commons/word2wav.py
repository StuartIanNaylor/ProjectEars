#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import glob
from shutil import which
import subprocess
import uuid

def word2wav(word, source_dir='en/clips', dest_dir='./out', rate=16000, limit=-1):

  if not os.path.exists(source_dir):
    print("Source_dir " + source_dir + " does not exist")
    exit()

  if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

  if not os.path.exists(dest_dir + "/" + word):
    os.makedirs(dest_dir + "/" + word)
  else:
    print("Word dir " + word + " already exists")
    exit()
      
  if which('opusdec') == None:
    print("opusdec not installed sudo apt-get install opusdec")
    exit()
    
  


  #acts as a test also
  source_path = os.path.abspath(source_dir + "/" + word)
  dest_path = os.path.abspath(dest_dir + "/" + word)
  
  count = 1
  for filename in glob.glob(os.path.join(source_path, '*.opus')):
    bashCommand = "opusdec --quiet --rate " + str(rate) + " " + filename + " " + dest_path + "/" + str(uuid.uuid4()) + ".wav"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error == None:
      print(filename, "Converted to " + dest_path + "/" + str(uuid.uuid4()) + ".wav")
    else:
      print(error)
    if count == limit:
      break
    count += 1
  if 'filename' not in locals():
    print(word + " returned no files")
    exit()

  
def main_body():
  parser = argparse.ArgumentParser()
  parser.add_argument('--source_dir', type=str, default='en/clips', help='source dir location default=en/clips')
  parser.add_argument('--dest_dir', type=str, default='./out', help='dest dir for word dir default=out')
  parser.add_argument('--word', type=str, help='word dir to convert default=word')
  parser.add_argument('--rate', type=int, default=16000, help='sample rate to convert to default=16000')
  parser.add_argument('--limit', type=int, default=-1, help='limit to x number of files default=-1')
  args = parser.parse_args()

   
  
  word2wav(args.word, args.source_dir, args.dest_dir, args.rate, args.limit)

    
if __name__ == '__main__':
  main_body()
  
  
  

