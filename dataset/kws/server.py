#!/usr/bin/env python

import asyncio
import websockets
import soundcard as sc
import numpy as np
import threading
import argparse

async def echo(websocket):
    async for message in websocket:
        wav = np.frombuffer(message, dtype='float32')
        wav = np.reshape(wav, (320, 1))
        default_speaker = sc.default_speaker()
        default_speaker.play(wav, samplerate=16000)
        

async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever


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
 

dtype='float32'
num_channels = 1


asyncio.run(main())
