# -*- coding: utf-8 -*-
"""
v1. March 2023. 
@author: https://github.com/polyzentrik, https://www.polyzentrik.com .
 
# DESCRIPTION
-------------
This Python script creates transcripts from audio files (.wav), 
with minimal speaker segmentation.

It uses OpenAI's Whisper (https://github.com/openai/whisper) 
and pyannote's Speaker Segmentation (https://huggingface.co/pyannote/speaker-segmentation).

For scripts without segmentation or diarization, 
check Polyzentrik's website: https://www.polyzentrik.com .


# HOW TO USE THIS FILE
----------------------
Before running the file:
* Create an "input" folder on the Desktop (all lowercase)
* Place the audio files to be transcribed in this input folder
* Select the Whisper model you want to use in the "MODEL SELECTION" section
* Input your HuggingFace / Pyannote token, in the "MODEL SELECTION" section.

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

# ----
# IMPORTS
# .......

import os
import time
import operator
import whisper
from pydub import AudioSegment
from pyannote.audio import Pipeline
import concurrent.futures as cf


# ----
# MODEL SELECTION
# ...............

# Enter your HuggingFace (HF) pyannote token (model publicly available via HF but token required -- see https://huggingface.co/pyannote/speaker-segmentation for details)
pipeline = Pipeline.from_pretrained("pyannote/speaker-segmentation", use_auth_token="ADD_YOUR_TOKEN_HERE")

# Choose the whisper model version to run (tiny, base, small, medium, and large -- see https://github.com/openai/whisper for details)
model = whisper.load_model("large")


# ----
# SEGMENTATION FUNCTION
# .....................

def run_segmentation(filename, input_folder):
    '''This f(x) calls Pyannote and writes the result to a temporary TXT file in the output folder'''
    
    # Start timer for f(x)
    s_start = time.perf_counter()
    
    # Split audio file in chunks (to avoid memory shutdown)
    audio = AudioSegment.from_file(file = input_folder + filename, format="wav") 
    mins_per_chunks = 10
    msecs_per_chunk = mins_per_chunks*60*1000
    no_of_chunks = int(len(audio)/msecs_per_chunk)
    for i in range(0, no_of_chunks):
        extract = audio[int(i*msecs_per_chunk):int((i+1)*msecs_per_chunk)]
        extract.export( input_folder + filename[:-4] + "-" + str(i+1) + ".wav", format="wav")
    extract = audio[int(no_of_chunks*msecs_per_chunk):]
    extract.export( input_folder + filename[:-4] + "-" + str(no_of_chunks+1) + ".wav", format="wav")

    # Segment each of these chunks and delete the temp chunks
    L = []
    for i in range (1, no_of_chunks+2):
        segmentation = pipeline(input_folder + filename[:-4] + "-" + str(i) + ".wav")
        for turn, _, speaker in segmentation.itertracks(yield_label=True):
            L.append([turn.start + ((i-1)*(msecs_per_chunk/1000)), speaker])
        os.remove(input_folder + filename[:-4] + "-" + str(i) + ".wav")
    
    # Write resulting array to temporary text file
    with open(input_folder + "temp-segments.txt", "w") as f:
        for l in L:
            f.write(str(l[0]) + " " + l[1] + "\n")
        f.close()
    
    # Calculate and print run time.
    s_end = time.perf_counter()
    return f'Finished segmentation for {filename} in {(s_end-s_start)/60} minutes'


# ----
# TRANSCRIPTION FUNCTION
# ......................

def run_whisper(filename, input_folder):
    '''This f(x) calls Whisper and writes the segmented result to a temporary TXT file in the output folder'''
    
    # Start timer for f(x)
    w_start = time.perf_counter()
    
    # Perform transcription & dump it to a temporary file
    result = model.transcribe(input_folder + filename)
    segments = result["segments"]
    with open(input_folder + "temp-transcript.txt","w") as f:
        for segment in segments:
            line = str('%.2f'%segment['start']) + "-" + segment['text'] + "\n"
            try:
                f.write(f'{line}')
            except Exception:
                pass
        f.close()
    
    # Calculate and print run time.
    w_end = time.perf_counter()
    return f'Finished whisper for {filename} in {(w_end-w_start)/60} minutes'



# ----
# JOIN FUNCTION
# ......................

def better_together(filename, input_folder):
    '''This f(x) joins temp segmentation and transcript into a single .TXT transcript in output folder'''
        
    # Join the contents of temporary files from transcription and segmentation functions
    LINES = []
    speaker = ""
    with open(input_folder + "temp-segments.txt", "r") as txt:
        for line in txt.readlines():
            line = line.split()
            line = ['1', float(line[0])-0.25, line[1]]
            if line[2] != speaker:
                LINES.append(line)
                speaker = line[2]
    LINES[0][1] = -0.01
    with open(input_folder + "temp-transcript.txt", "r") as txt:
        for line in txt.readlines():
            line = line.split("-")
            line = ['2', float(line[0]), line[1]]
            LINES.append(line)
    LINES = sorted(LINES, key=operator.itemgetter(1))
    LINES.insert(0, ['2', "A", "TRANSCRIPT OF file " + filename[:-4] + ".wav" + "\n\n"])

    # Clean the resulting array to avoid empty speaker segments
    L = []
    for i in range(0, len(LINES)):
        if i >= len(LINES)-1:
            pass
        else:
            if LINES[i][0] == '1' and LINES[i+1][0] == '1':
                    pass
            else:
                L.append(LINES[i])
    LINES = L
    
    # Write to the final transcription file
    desktop = os.path.expanduser("~/Desktop") 
    with open(desktop + "/" + filename[:-4] + ".txt","w") as f:
        for line in LINES:
            try:
                if line[0] == '1':
                    f.write("\n\n\n")
                elif line[1] == "A":
                    f.write(f'{line[2]} ')
                else:
                    f.write(f'{line[2].strip()} ')
            except Exception:
                pass
        f.close()


# ----
# MAIN FUNCTION
# ......................

def main():
    '''This f(x) organises the process into multiple threads'''
    # Start timer for the entire sequence
    start = time.perf_counter()
    
    # Define locations & ID files
    input_folder = os.path.expanduser("~/Desktop") + "/" + "input/"
    FILENAMES = os.listdir(input_folder)
    
    # Call transcription & segmentation f(x)s, then join
    for filename in FILENAMES:
        if filename.endswith(".wav"):
            filename_start = time.perf_counter()
            
            # Run segmentation and whisper models, in parallel because, why not?
            with cf.ThreadPoolExecutor() as executor:
                results = [executor.submit(run_whisper, filename, input_folder), executor.submit(run_segmentation, filename, input_folder)]
            for func in cf.as_completed(results):
                print(func.result())
            
            # Join temp files from segmentation and transcription
            better_together(filename, input_folder)
            
            # Remove audio file after transcribing it
            os.remove(input_folder + filename)
            
            # End timer for single file and return runtime
            filename_end = time.perf_counter()
            print(f'Finished transcription of {filename} in {(filename_end-filename_start)/60} minutes')
    
    # Remove temp files
    os.remove(input_folder + "temp-segments.txt")
    os.remove(input_folder + "temp-transcript.txt")
    
    # Finish time counter and print duration of full sequence
    end = time.perf_counter()
    print(f'The whole program took {(end-start)/60} minutes')


# ----
# TRIGGER
# ......................
if __name__ == '__main__':
    main()
