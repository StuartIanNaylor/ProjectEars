#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import glob
import os
import shutil

def split(source_dir='./in', dest_dir='./out', testing_percent=0.05, validation_percent=0.10, label="kw"):
  
  if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
  if not os.path.exists(dest_dir + "/training"):
    os.makedirs(dest_dir + "/training")    
  if not os.path.exists(dest_dir + "/testing"):
    os.makedirs(dest_dir + "/testing")  
  if not os.path.exists(dest_dir + "/validation"):
    os.makedirs(dest_dir + "/validation")  
  if not os.path.exists(dest_dir + "/training/" + label):
    os.makedirs(dest_dir + "/training/" + label)    
  if not os.path.exists(dest_dir + "/testing/" + label):
    os.makedirs(dest_dir + "/testing/" + label)  
  if not os.path.exists(dest_dir + "/validation/" + label):
    os.makedirs(dest_dir + "/validation/" + label)  
      
  if not os.path.exists(source_dir):
    print("Source_dir = " + source_dir + " does not exist!")
    exit()

  source = glob.glob(os.path.join(source_dir, '*.wav'))
  if len(source) < 2:
    print("No files found *.wav")
    exit()
  count = 0
  testing_qty = len(source) * testing_percent
  validation_qty = len(source) * validation_percent    
  for wav in source:
    if count < testing_qty:
      shutil.move(wav, dest_dir + "/testing/" + label + "/" + os.path.basename(wav))
    elif count < validation_qty + testing_qty:
      shutil.move(wav, dest_dir + "/validation/" + label + "/" + os.path.basename(wav))
    else:
      shutil.move(wav, dest_dir + "/training/" + label + "/" + os.path.basename(wav))
    count += 1


def main_body():
  parser = argparse.ArgumentParser()
  parser.add_argument('--source_dir', default='./in', help='source dir location')
  parser.add_argument('--dest_dir', type=str, default='./out', help='dest dir location')
  parser.add_argument('--testing_percent', type=float, default=0.05, help='decimal percentage of testing qty')
  parser.add_argument('--validation_percent', type=float, default=0.15, help='decimal percentage of validation qty')
  parser.add_argument('--label', type=str, default='kw', help='label name')
  args = parser.parse_args()

  if args.dest_dir == None:
    args.dest_dir = "./out"
  
  split(args.source_dir, args.dest_dir, args.testing_percent, args.validation_percent, args.label)
    
if __name__ == '__main__':
  main_body()



