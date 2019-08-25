#!/usr/bin/env python
# coding: utf-8

# In[25]:


# Import necessary packages
import speech_recognition as sr
import os

# Instantiate a recognizer class of speech_recognition module
r = sr.Recognizer()

# Get the list of all I/O audio devices in the system
sr.Microphone.list_microphone_names()

# Read from google cloud credentials file
with open('MyFirstProject-0727af21246d.json', 'r') as rf:
    mf = rf.read()
    
# Create an instance of microphone class and use the first audio device of the device
mic = sr.Microphone(device_index=0)
with mic as source:
    # Listen to the audio from the microphone
    audio = r.listen(source)
    
# Make a request to google speech api along with the credentials
reponse = r.recognize_google_cloud(audio, credentials_json=mf)
print(response)

