# -*- coding: utf-8 -*-
"""
v1. March 2023. 
@author: https://github.com/polyzentrik, https://www.polyzentrik.com .

# DESCRIPTION
-------------
This Python script creates transcripts from audio files (only .wav currently supported), 
WITH speaker segmentation/diarization.

It uses OpenAI's Whisper (https://github.com/openai/whisper) 
and pyannote's Speaker Segmentation (https://huggingface.co/pyannote/speaker-diarization).

The script auto-detects the number of speakers, and this guess can be wrong.
To set a specific number of speakers in advance, consult pyannote's documentation.

The script is best for clear conversations, i.e., when speakers do not speak over one another.
For scripts w. minimal segmentation and no diarization (better for more dynamic conversations), 
check Polyzentrik's website: https://www.polyzentrik.com .

(!) The models require significant computing resources. A good computer is needed.


# HOW TO USE THIS FILE
----------------------
Before running the file:
* Create an "input" folder on the Desktop (all lowercase)
* Place the audio files to be transcribed in this input folder
* Select the Whisper model you want to use in the "MODEL SELECTION" section
* Input your HuggingFace / Pyannote token in the "MODEL SELECTION" section.

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
from pydub import AudioSegment
from pyannote.audio import Pipeline
import whisper

# ----
# MODEL SELECTION
# ----

# Enter your HuggingFace (HF) pyannote token (model publicly available via HF but token required -- see https://huggingface.co/pyannote/speaker-segmentation for details)
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token="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")

# Choose the whisper model version to run (tiny, base, small, medium, and large -- see https://github.com/openai/whisper for details)
model = whisper.load_model("large")


# ----
# DIARIZATION FUNCTION
# ----
def run_diary(filename, input_folder):
    '''This f(x) calls Pyannote and writes the result to a temporary TXT file'''
    
    # Start timer for f(x).
    d_start = time.perf_counter()
    
    # Perform diarization & dump it to a temporary file
    temp_folder = input_folder + "/temp"
    diarization = pipeline(input_folder + "/" + filename)
    with open(temp_folder + "/temp-diary.txt", "w") as f:
        diarization.write_rttm(f)
        f.close()
    
    # Calculate and print run time
    d_end = time.perf_counter()
    print(f'Finished diarization for {filename} in {(d_end-d_start)/60} minutes')
    return

# ----
# AUDIO SPLITTING FUNCTION
# ----
def split_audio(filename, input_folder):
    '''This f(x) splits audio in as many chunks as speaker segments and saves each audio into a temporary folder'''
     
    # Build array to organise splitting
    temp_folder = input_folder + "/temp"
    CHUNKS = []
    currentSpeaker = ""
    with open(temp_folder + "/" + "temp-diary.txt", "r") as txt:
        for line in txt.readlines():
            l = line.split(" ")
            if l[7] != currentSpeaker:
                CHUNKS.append([l[7], float(l[3]), 0])
                currentSpeaker = l[7]
            txt.close()
    
    # Split audio into a file per speaker segment
    i = 0
    t = len(str(len(CHUNKS)))
    audio = AudioSegment.from_file(file = input_folder + "/" + filename, format="wav")
    for chunk in CHUNKS:
        if i < len(CHUNKS)-1:
            extract = audio[CHUNKS[i][1]*1000:CHUNKS[i+1][1]*1000]
            extract.export( temp_folder + "/" + filename[:-4] + "-" + str(i).zfill(t) + ".wav", format="wav")
            i += 1
    extract = audio[CHUNKS[i][1]*1000:]
    extract.export( temp_folder + "/" + filename[:-4] + "-" + str(i).zfill(t) + ".wav", format="wav")

    # Return the whole lot of CHUNKS for later usage
    return CHUNKS

# ----
# PROMPT FUNCTION
# ----
def prompt(input_folder, prompt_file_name):
    '''This f(x) imports a prompt with applicable jargon or offers a neutral prompt with punctuation.'''
    if os.path.isfile(input_folder + "/" + prompt_file_name + ".txt"):
        with open(input_folder + "/" + prompt_file_name + ".txt", "r") as txt:
            prompt = txt.read().replace('\n', ' ')
    else:
        prompt = "Carbon, CO2. UNFCCC, UNEP."
    return prompt

    
# ----
# TRANSCRIPTION FUNCTION
# ----
def run_whisper(filename, input_folder, prompt):
    '''This f(x) calls Whisper and writes the segmented result to a temporary TXT file in the output folder'''
    
    # Start timer for f(x).
    w_start = time.perf_counter()
    
    # Perform transcription on each temporary audio file.
    temp_folder = input_folder + "/temp/"
    for temp_file in os.listdir(temp_folder):
        if temp_file.endswith(".wav"):
            
            # Get transcription from Whisper
            result = model.transcribe(temp_folder + temp_file, initial_prompt='prompt')
            
            # Write transcription into a temporary TXT file
            with open(temp_folder + "temp-transcript-" + temp_file[:-4] + ".txt","w") as f:
                try:
                    f.write(result["text"])
                except Exception:
                    pass
                f.close()
            
            # Remove the temporary audio file
            os.remove(temp_folder + temp_file)
    
    # Calculate and print run time
    w_end = time.perf_counter()
    
    # Return time spent transcribing with Whisper
    print(f'Finished Whisper for {filename} in {(w_end-w_start)/60} minutes')
    return

# ----
# JOIN TEMPORARY FILES FUNCTION
# ----
def better_together(filename, input_folder, CHUNKS):
    '''This f(x) joins temp files to a joint array'''
        
    # Define stuff needed in function
    temp_folder = input_folder + "/temp"
    LINES = []
    
    # Join the diarisation array and contents of temporary TXT files
    i = 0
    for file in os.listdir(temp_folder):
        if file.startswith("temp-tra"):
            with open(temp_folder + "/" + file) as f:
                LINES.append([CHUNKS[i][0], f.read()])
                i += 1
    
    # Return the joint array
    return LINES
            

# ----
# WRITE FINAL TRANSCRIPT FUNCTION
# ----         
def write_out(filename, LINES):
    '''This f(x) writes the final result to a TXT file in the output folder'''
    
    # Write to the final transcription file
    desktop = os.path.expanduser("~/Desktop")
    with open(desktop + "/" + filename[:-4] + ".txt","w") as f:
        f.write(f'TRANSCRIPT OF file {filename} \n\n')
        for line in LINES:
            try:
                f.write(f'{line[0]} \n {line[1]} \n\n')
            except Exception:
                pass
        f.close()


# ----
# MAIN FUNCTION
# ----
def main():
    '''This f(x) organises the workflow'''
    # Start time counter for the entire sequence
    start = time.perf_counter()
    
    # Set locations & filenames
    input_folder = os.path.expanduser("~/Desktop/input")
    "TEMP folder exists" if os.path.isdir(input_folder + "/temp") else os.mkdir(input_folder + "/temp")
    FILENAMES = os.listdir(input_folder)
    
    # Prompt file for consumption by whisper (must be a .txt file)
    prompt_file_name = "prompt-sustainability-base" # Enter prompt file name (just the name, no extension) (leave empty "" string if NOT using a prompt file)
    
    # Main workflow per file in input folder
    for filename in FILENAMES:
        if filename.endswith(".wav"):
            
            # Start times for this file
            filename_start = time.perf_counter()
            
            # Call diarisation function
            run_diary(filename, input_folder)
            
            # Use results of diarisation to split the main audio into speaker chunks
            CHUNKS = split_audio(filename, input_folder)
            
            # Import a prompt with applicable jargon 
            p = prompt(input_folder, prompt_file_name)
            
            # Run whisper on each audio chunk, using a prompt for accuracy
            run_whisper(filename, input_folder, p)
            
            # Join all transcripts into a single array
            LINES = better_together(filename, input_folder, CHUNKS)
            
            # Write joint array to a transcript on Desktop
            write_out(filename, LINES)
            
            # Clean files not needed in the next run
            os.remove(input_folder + "/" + filename)
            for file in os.listdir(input_folder + "/temp"):
                os.remove(input_folder + "/temp/" + file)
            
            # Calculate and print runtime for this file
            filename_end = time.perf_counter()
            print(f'Finished transcription of {filename} in {(filename_end-filename_start)/60} minutes')
    
    # Clean up before closing
    for f in os.listdir(input_folder + "/temp"):
        os.remove(input_folder + "/temp/" + f)
    os.rmdir(input_folder + "/temp")
    
    # Finish time counter and print duration of the entire sequence
    end = time.perf_counter()
    print(f'The whole program took {(end-start)/60} minutes')


# ----
# TRIGGER
# ----
if __name__ == '__main__':
    main()

#input_folder = os.path.expanduser("~/Desktop/input")
#FILENAMES = os.listdir(input_folder)

# Main workflow per file in input folder
#for filename in FILENAMES:
#    if filename.endswith(".wav"):
#        print(filename)

#CHUNKS = split_audio("032a.wav", input_folder)
#CHUNKS
