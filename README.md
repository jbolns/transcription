# AI transcription scripts

## Intro
This repo contains AI transcription resources for low-frequency transcription performed locally (or on the 'edge') on relatively humble devices.<sup>1</sup>

The scripts have been tested on a decent (CORE i7, 16MB RAM) but still affordable (€500) computer. Waiting times are significant, up to 3 or 4 times the audio length for the most complex script. That said, the quality of outputs is very satisfactory – comparable to commercial alternatives.

**Examples**. The examples folder contains examples of transcriptions performed with the scripts in this repo.

## Justification
Transcriptions are a surprisingly problematic data/AI ethics dilemma. Interviews, statements, and oral stories can hold delicate personal identifiable information (PII). Speakers often use names and readily disclose locations and sometimes even personal or confidential details under the assumption that the conversation will remain private.

When recordings are transcribed online, all PII contained in them is transferred between several parties. This is not problematic if all due consents and safeguards are in place, of course. However, without appropriate consents and safeguards, the use of centralised transcription services becomes problematic.

We therefore believe that while centralised/cloud-based transcription have a place in the market, alternatives are also needed.

Our AI transcription scripts can run without a connection to the Internet (excl. downloading any necessary models, of course). They are one such alternative.<sup>1<sup>

## Status
There is a lot to improve. That said, the scripts can already help people wishing to do transcriptions locally and have therefore been open-sourced.

## License.
The scripts are under an Apache 2.0 open-source license ammended to require explicit and visible attribution. Read the [license](LICENSE-2.0.txt) and [NOTICE](NOTICE.txt) file for more details. 

Please note the license does **NOT** cover the examples folder. The recordings used for testing have licenses that allow such usage. However, they have their own licenses. Refer to the original licenses for usage conditions.

## Usage
**Guided implementation services.** I can help researchers, businesses, and organisations implement the scripts as part or their digital infrastructure.

**Transcription services.** I offer transcription services for selected users/projects via my tiny-but-very-cool company [polyzentrik](https://www.polyzentrik.com/).

**Free usage.** As per the license terms, the scripts can be used by others provided the conditions in the license are met. 

## Instructions for external usage
1. Choose which script better fits your needs.
   * **Simple.** No segmentation. No diarisation. A simple transcription of the pure audio using OpenAI's Whisper. Best for very dynamic conversations where segmentation/diarisation is would be challenging. 
   * **w. Segmentation.** Adds speaker segmentation to simple transcriptions using pyannote's diarisation model. The output is a TXT file split into paragraphs roughly based on speaker changes (and pauses). However, the paragraphs are not labelled. Best for conversations that are not entirely messy but still not fully structured.
   * **w. Diarisation.** This script takes a more sophisticated approach to speaker diarisation. It detects and labels speakers, breaks the main audio file into smaller audio segments corresponding to each speaker, transcribes each audio segment, and finally joins everything into a single TXT file split into sections labelled by speaker.
2. Save the script anywhere on your computer.
3. Create an "input" folder on the Desktop (all lowercase) and place the audio files to be transcribed in this folder.
4. Select the Whisper model you want to use in the "MODEL SELECTION" section
5. If using the segmentation or diarisation script, input your HF token in the "MODEL SELECTION" section (you need a HF account for this).
7. Run the script.

An internet connection is needed the first time scripts run or if models needs to be re-downloaded. After that, the scripts have been tested to run without an Internet connection.<sup>1</sup>

--
### Notes
<p>1. Please note I cannot and do not guarantee data is not being fed back somehow.</p>

