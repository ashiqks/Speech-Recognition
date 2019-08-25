#!/usr/bin/env python
# coding: utf-8

# In[28]:




# Import necessary packages
from __future__ import division
import pyaudio
import math
import wave
import time
import struct
import os
import re
import sys
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio

# Path to the google credentials file
file_path = 'MyFirstProject-0727af21246d.json'
# Add the credentials file as 'GOOGLE_APPLICATION_CREDENTIALS' environment variable 
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = file_path

# Set a threshold value in dB (decibel) to detect speech
Threshold = 10
# Set values for helper constants
SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
swidth = 2
# Timeout for stop listening after silence
TIMEOUT_LENGTH = 1

language_code = 'en-US'  # a BCP-47 language tag

# Create gcloud speech-to-text client
client = speech.SpeechClient()
# Create a configuratin for the audio for speech client 
config = types.RecognitionConfig(
                                encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16, # Type of encoding of audio
                                sample_rate_hertz=RATE, # Sample rate in Hertz
                                language_code=language_code) 
# Create a configuration for streaming the audio to the api
streaming_config = types.StreamingRecognitionConfig(
                                                config=config,  # The config for audio
                                                interim_results=True) # If intermediate results have to shown


# Create a class to for listening the audio and making speech-to-text api calls
class Recorder:
    # Function to determine the rms value of the frames of audio for thresholding 
    def rms(self, frame):
        count = len(frame) / swidth
        formats = "%dh" % (count)
        shorts = struct.unpack(formats, frame)
        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self):
        # Create pyaudio interface
        self.p = pyaudio.PyAudio()
        # Open the pyaudio interface
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  frames_per_buffer=chunk)
    # Function to print the results
    def listen_print_loop(self, responses):
        # Loop over the responses object
        for response in responses:
            # Loop over the results of the responses
            for result in response.results:
                # Only the final result  
                if result.is_final:
                    alternatives = result.alternatives
                    for alt in alternatives:
                        print(alt.transcript)

    # Function to record the audio     
    def record(self):
        print('Noise detected, recording beginning')
        rec = []
        # Get the current time
        current = time.time()
        # Set the timeout time if there is no audio
        end = time.time() + TIMEOUT_LENGTH
        while current <= end:
            # Read the audio from the pyaudio stream
            data = self.stream.read(chunk)
            # If the rms value of the stream is higher than threshold then detect audio
            if self.rms(data) >= Threshold: 
                # Update timeout time
                end = time.time() + TIMEOUT_LENGTH
            # Get again the current time
            current = time.time()
            # Append the audio data in a list
            rec.append(data)
        # Stop the audio stream
        self.stream.stop_stream()
        # Close the audio stream
        self.stream.close()
        # Terminate the pyaudio interface
        self.p.terminate()
        # Make streaming request of gcloud speech-to-text api of the audio data
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in rec)
        # Get the responses from the request
        responses = client.streaming_recognize(streaming_config, requests)
        # Print the result
        self.listen_print_loop(responses)
    
    # Define function to listen to audio initially
    def listen(self):
        print('Listening beginning')
        while True:
            # Read the input audio from the stream
            input_audio = self.stream.read(chunk)
            # Determine the rms value of the streamed audio
            rms_val = self.rms(input_audio)
            # If the rms value is greater than threshold
            if rms_val > Threshold:
                # Call the record method
                self.record()
                return

# Create an instance of the recorder class
a = Recorder()
# Call the listen method
a.listen()


# In[46]:





# In[ ]:




