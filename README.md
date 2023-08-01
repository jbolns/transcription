# Open-source sustainability transcription resources

## Intro
This repo contains down-to-earth transcription resources for low-frequency tasks.

The goal is to offer resources for people and organisations that need sustainability transcriptions sporadically.

As such, the scripts are *designed to run on relatively humble personal computers*. 

They have been tested on a good (CORE i7, 16MB RAM) but still affordable (€500) computer. Waiting times are significant, up to 3 or 4 times the audio length for the most complex script. However, the quality of the results is very satisfactory – comparable to commercial alternatives.

## Scripts
There are currently three scripts available.

### Simple
This script performs a simple transcription. Audio is transcribed into a TXT file with many lines.

### w. Segmentation
This script adds speaker segmentation to the results of the simple model. It detects when there are speaker changes and then matches Whisper’s transcription to these timings. The output is a TXT file split into paragraphs roughly based on speaker changes (and pauses).

### w. Diarisation
This script takes a more sophisticated approach to speaker diarisation. It detects and labels speakers, breaks the main audio file into smaller audio segments corresponding to each speaker, transcribes each audio segment, and finally joins everything into a single TXT file split into sections labelled by speaker.

> Prompts: The diarisation script allows the usage of an external prompt file, which can increase the quality of the output. The prompts folder contains examples of prompt files applicable to sustainability.

## Instructions
Pending.

## Examples
The examples folder contains examples of transcriptions performed with the scripts in this repo.

## License
The scripts in this repo are under an Apache 2.0 license. The license file is available at the root of this repo.

! Please note the Apache 2.0 license does not cover the files in the examples folder. While the videos and recordings used for testing are under licensing terms that allow such usage, they have their own licenses. Refer to the original licenses for usage conditions. 