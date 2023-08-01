# -*- coding: utf-8 -*-
"""
v1. March 2023. 
@author: https://github.com/polyzentrik, https://www.polyzentrik.com .
 
# DESCRIPTION
------------- 
This script creates transcripts from audio files (tested with .mp3 and .wav files). 

It uses OpenAI's Whisper (https://github.com/openai/whisper).

There is no speaker segmentation or diarization.
For scripts with diarization, check Polyzentrik's website: https://www.polyzentrik.com .


# HOW TO USE THIS FILE
----------------------
Before running the file:
* Create an "input" folder on the Desktop (all lowercase)
* Place the audio files to be transcribed in this input folder
* Select the Whisper model you want to use in the "MODEL SELECTION" section.

The script will loop over all files in the input folder. Outputs will be placed on the Desktop.


# LICENSE
----------
Copyright 2023 Polyzentrik Tmi. 

Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Ps. Be cool and provide visible credits.

"""

import os
import time
import whisper
import concurrent.futures as cf

# ----
# MODEL SELECTION
# ----

# Choose the whisper model version to run (tiny, base, small, medium, and large -- see https://github.com/openai/whisper for details)
use_model = "large"

# ----
# TRANSCRIPTION FUNCTION
# ----
def run_whisper(filename, use_model, input_folder):
    '''This f(x) calls Whisper and writes the segmented result to a TXT file in the output folder'''
    
    # Start timer for the function
    w1 = time.perf_counter()
    
    # Define names & locations
    simpleName = filename[:-4] + ".txt"
    output = os.path.expanduser("~/Desktop") + "/" + simpleName
    
    # Select which Whisper model to use
    model = whisper.load_model(use_model)
    
    # Perform transcription.
    result = model.transcribe(input_folder + filename)         
    segments = result["segments"]                             
    
    # Write transcription to file
    with open(output,"w") as f:
        for segment in segments:
            line = segment['text']
            try:
                f.write(f'{line.strip()}\n')
            except Exception:
                f.write("!------ LINE IS MISSING --------!")
        f.close()
    
    # End timer for the function
    w2 = time.perf_counter()
    mins = (w2-w1)/60
    
    # Declare victory for this file
    return f'Finished transcribing {filename} in {mins} minutes'  


# ----
# MAIN FUNCTION
# ----
def main():
    '''This f(x) organises the process'''
    
    # Start timer for the function
    t1 = time.perf_counter()
    
    # Define locations and filename(s)
    input_folder = os.path.expanduser("~/Desktop") + "/" + "input/"
    FILENAMES = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".wav"):
            FILENAMES.append(filename)

    # Loop over files in input folder
    # Note for techies. Whisper is not particularly adept to multi-threading but, for some unexplicable reason, cf seems to help performance.
    with cf.ThreadPoolExecutor(max_workers=1) as executor:
        results = [executor.submit(run_whisper, filename, use_model, input_folder) for filename in FILENAMES]
        for f in cf.as_completed(results):
            print(f.result())
    
    # Remove audio files from input folder after running program
    for filename in FILENAMES:
        os.remove(input_folder + filename)
            
    # Finish time counter and print duration of the entire sequence
    t2 = time.perf_counter()
    mins = (t2-t1)/60
    print(f'Program took {mins} minutes')

# ----
# TRIGGER
# ----

if __name__ == '__main__':
    main()