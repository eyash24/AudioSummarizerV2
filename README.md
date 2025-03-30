# AudioSummarizerV2

## Download the VOSK and Recasepunc Model
Vosk model can either be downlaoded through the link
[vosk-model-en-us-0.22](https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip) link
or throught the
[website](https://alphacephei.com/vosk/models).<br>
Recasepunc model can be downloaded from the same website. It is listed under the Punctuation models as vosk-recasepunc-en-0.22. <br>
Do rename the file and pass the file path to the voice.ipynb

## Setup Environment
Create a new environment and download the required libraries using requirements.txt file

## Run the project
Execute the Run All option inside the voice.ipynb notebook. <br>
This will download the additional models required by the project to run. <br>
After running it for the first time, remember to comment out the Download & Save commands in the voice.ipynb notebook <br>
In case of Recasepunc not working, comment out the blocks that do utilise recasepunc model. Rerun the notebook. <br>
