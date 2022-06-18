#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import uuid
import sox
import logging

logging.getLogger('sox').setLevel(logging.ERROR)
dest_dir = "/home/stuart/test/data2/_background_noise_"
source = glob.glob(os.path.join('./', '*.wav'))
       
for wav in source:
  tfm = sox.Transformer()  
  tfm.norm(-0.1)
  tfm.vol(gain=0.7, gain_type='amplitude')  
  out = dest_dir + '/' + str(uuid.uuid4()) + '.wav'
  tfm.build_file(wav, out)




