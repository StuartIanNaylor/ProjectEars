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
import configparser as CP

def augment(source_dir='./in', dest_dir='./out', target_qty=4000, target_length=1.0, debug=0, volume=1, random_vol=0, offset_trim=0, background_db=0.0, noise_dir=""):

  if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
  if not os.path.exists(source_dir):
    print("Source_dir = " + source_dir + " does not exist!")
    exit()
  if debug == 0:  
    logging.getLogger('sox').setLevel(logging.ERROR)
  else:
    logging.getLogger('sox').setLevel(logging.DEBUG)
    
  sample_rate = 16000
  source = glob.glob(os.path.join(source_dir, '*.wav'))
  if len(source) < 2:
    print("No source files found *.wav")
    exit()
  if background_db != 0.0:
    if not os.path.exists(noise_dir):
      print("Noise_dir = " + noise_dir + " does not exist!")
      exit()
    noise = glob.glob(os.path.join(noise_dir, '*.wav'))
    if len(noise) < 2:
      print("No noise files found *.wav")
      exit()
     
  if not os.path.exists('effects.ini'):
    print("effects.ini is missing")
    exit()
  
  cfg = CP.ConfigParser()
  cfg.read('effects.ini')
  
  history = []
  history_element = []  
  history_effect = ""
  qty = 0
  while qty < target_qty:
    foreground_wav = source[random.randrange(0, len(source) -1)]
    augment_wav(foreground_wav, background_db, cfg, history, sample_rate, random_vol, volume, offset_trim, dest_dir, qty, target_length, False)
    out = dest_dir + '/' + os.path.basename(history[-1][1])
    if background_db != 0.0:
      background_wav = noise[random.randrange(0, len(noise) -1)]
      augment_wav(background_wav, background_db, cfg, history, sample_rate, random_vol, volume, True, dest_dir, qty, target_length, True)
      cbn = sox.Combiner()
      cbn.build(['/tmp/foreground.wav', '/tmp/background.wav'], out, 'mix')

    qty += 1

    if debug == 1:
      for history_element in history:
        print(history_element)

def augment_wav(wav, background_db, cfg, history, sample_rate, random_vol, volume, offset_trim, dest_dir, qty, target_length, is_background):

    history_element = [wav, "", ""]
    history_effect = ""
    rand_effect = random.random()
    wav_length = sox.file_info.num_samples(wav)
    target_samples = int(sample_rate * target_length)
    tfm = sox.Transformer()
    tfm.clear_effects()
    if offset_trim == 1:
      offset = random.randrange(0, wav_length - target_samples ) / sample_rate
      tfm.trim(offset, offset + target_length)

    #norm low so gain doesn't clip
    tfm.norm(-6)
    if rand_effect < 0.25:
      pitch = random.randrange(int(cfg['pitch']['n_semitones_min']), int(cfg['pitch']['n_semitones_max'])) / 1000
      tfm.pitch(n_semitones=pitch)
      str_effect ="-pit"
      history_effect = "pitch=" + str(pitch)
    elif rand_effect < 0.50:
      tempo = random.randrange(int(cfg['tempo']['factor_min']), int(cfg['tempo']['factor_max'])) / 1000
      tfm.tempo(factor=tempo, audio_type='s')
      str_effect ="-tem"
      history_effect = "tempo=" + str(tempo)
    elif rand_effect < 0.75:
      speed = random.randrange(int(cfg['speed']['factor_min']), int(cfg['speed']['factor_max'])) / 1000
      tfm.speed(factor=speed)
      str_effect ="-spd"
      history_effect = "speed=" + str(speed)
    else:
      str_effect =""
    rand_effect = random.random()
    if rand_effect < 0.33:
      gain = random.randrange(int(cfg['treble']['gain_min']), int(cfg['treble']['gain_max'])) / 1000
      freq = random.randrange(int(cfg['treble']['freq_min']), int(cfg['treble']['freq_max'])) / 10
      slope = random.randrange(int(cfg['treble']['slope_min']), int(cfg['treble']['slope_max'])) / 1000
      tfm.treble(gain_db=gain, frequency=freq, slope=slope)
      str_effect = str_effect + "t"
      history_effect = history_effect + " treble=" + str(gain) + ", " + str(freq) + ", " + str(slope)
    rand_effect = random.random()
    if rand_effect < 0.33:
      gain = random.randrange(int(cfg['bass']['gain_min']), int(cfg['bass']['gain_max'])) / 1000
      freq = random.randrange(int(cfg['bass']['freq_min']), int(cfg['bass']['freq_max'])) / 100
      slope = random.randrange(int(cfg['bass']['slope_min']), int(cfg['bass']['slope_max'])) / 1000
      tfm.bass(gain_db=gain, frequency=freq, slope=slope)
      str_effect = str_effect + "b"
      history_effect = history_effect + " bass=" + str(gain) + ", " + str(freq) + ", " + str(slope)
    rand_effect = random.random() 
    if rand_effect < 0.33:
      reverb = random.randrange(int(cfg['reverb']['reverb_min']), int(cfg['reverb']['reverb_max'])) / 10000
      damping = random.randrange(int(cfg['reverb']['damping_min']), int(cfg['reverb']['damping_max'])) / 10000
      scale = random.randrange(int(cfg['reverb']['scale_min']), int(cfg['reverb']['scale_max'])) / 1000
      depth = random.randrange(int(cfg['reverb']['depth_min']), int(cfg['reverb']['depth_max'])) / 10000
      tfm.reverb(reverberance=reverb, high_freq_damping=damping, room_scale=scale, stereo_depth=depth)
      str_effect = str_effect + "r"
      history_effect = history_effect + " reverb=" + str(reverb) + ", " + str(damping) + ", " + str(scale) + ", " + str(depth)
    rand_effect = random.random()
    if rand_effect < 0.33:
      delay = random.randrange(int(cfg['echo']['delay_min']), int(cfg['echo']['delay_max'])) / 100
      decay = random.randrange(int(cfg['echo']['decay_min']), int(cfg['echo']['decay_max'])) / 10000
      tfm.echo(delays=[delay], decays=[decay])
      str_effect = str_effect + "e"
      history_effect = history_effect + " echo=" + str(delay) + ", " + str(decay)
           
    array_out = tfm.build_array(input_filepath=wav, sample_rate_in=sample_rate)
    #print(len(array_out)/sample_rate)
    tfm.clear_effects()
    if is_background == False:
      tfm.norm(-0.1)
    else:
      # -10.5 = 0.3 amplitude
      tfm.norm(background_db)
    tfm.fade(fade_in_len=0.02, fade_out_len=0.02)
    if len(array_out) < target_samples:
      target_pad = ((target_samples - len(array_out)) / 2) / target_samples
      tfm.pad(start_duration = target_pad, end_duration = target_pad + 0.1)
    tfm.trim(0, target_length)

    if random_vol == 1:
      vol = random.randrange(int(1000 * volume), 1000) / 1000
      #print(vol)
      tfm.vol(gain=vol, gain_type='amplitude')
    else:
      tfm.vol(gain=volume, gain_type='amplitude')
    if offset_trim == 1:
      out = dest_dir + '/' + str(qty) + str_effect + "-" + os.path.basename(wav)
    else:
      out = dest_dir + '/' + str(uuid.uuid4()) + str_effect + '.wav'
    history_element[1] = out
    history_element[2] = history_effect
    history.append(history_element)
    if background_db != 0.0:
      out = '/tmp/foreground.wav'
    if is_background == True:
      out = '/tmp/background.wav'

    
    tfm.build_file(input_array=array_out, sample_rate_in=sample_rate, output_filepath=out)

    
def main_body():
  parser = argparse.ArgumentParser()
  parser.add_argument('--source_dir', default='./in', help='source dir location')
  parser.add_argument('--dest_dir', type=str, default='./out', help='dest dir location')
  parser.add_argument('--target_qty', type=int, default=4000, help='Final qty of augmented audio files')
  parser.add_argument('--target_length', type=float, default=1.0, help='Target length of audio files to be trimmed to (s)')
  parser.add_argument('--volume', type=float, default=1.0, help='Volume gain of audio files')
  parser.add_argument('--random_vol', help='randomise volume with volume = min vol', action="store_true")
  parser.add_argument('--offset_trim', help='offset trim for noise files', action="store_true")
  parser.add_argument('--debug', help='debug effect settings to cli', action="store_true")
  parser.add_argument('--noise_dir', type=str, default='./noise', help='noise dir location')
  parser.add_argument('--noise_db', type=float, default=0.0, help='Db gain of noise files 0.0 = no noise')
  args = parser.parse_args()

  if args.dest_dir == None:
    args.dest_dir = "./out"
  
  augment(args.source_dir, args.dest_dir, args.target_qty, args.target_length, args.debug, args.volume, args.random_vol, args.offset_trim, args.noise_db, args.noise_dir)
    
if __name__ == '__main__':
  main_body()







