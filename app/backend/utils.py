from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
import json
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

FRAME_RATE = 16000
CHANNELS = 1
MODEL_VOSK_PATH = "vosk-model-en-us-0.22"
MODEL_SUMMARY_NAME = "sshleifer/distilbart-cnn-12-6"
SAVE_SUMMARY_PATH = "saved_model"


model_vosk = Model(model_name="vosk-model-en-us-0.22")
rec = KaldiRecognizer(model_vosk, FRAME_RATE)
rec.SetWords(True)

# model_bert = AutoModelForSeq2SeqLM.from_pretrained(MODEL_SUMMARY_NAME)
# tokenizer = AutoTokenizer.from_pretrained(MODEL_SUMMARY_NAME)

# model_bert.save_pretrained(SAVE_SUMMARY_PATH)
# tokenizer.save_pretrained(SAVE_SUMMARY_PATH)

def voice_recognition(filename):
    print("Voice Recognition has begun!")
    wav_file = AudioSegment.from_wav(filename)
    wav_file = wav_file.set_channels(CHANNELS)
    wav_file = wav_file.set_frame_rate(FRAME_RATE)
    
    step = 45000
    transcript = ""
    for i in range(0, len(wav_file), step):
        print(f"Progress: {i/len(wav_file)}")
        segment = wav_file[i:i+step]
        rec.AcceptWaveform(segment.raw_data)
        result = rec.Result()
        text = json.loads(result)["text"]
        transcript += text
    
    return transcript

# Download & save
def summarise(docs):
    print("Sumamrisation has begun!")

    summarizer2 = pipeline(
        "summarization",
        model="./saved_model",
        tokenizer="./saved_model"
    )

    split_tokens = docs.split(" ")
    docs_2 = []
    for i in range(0, len(split_tokens), 850):
        selection = " ".join(split_tokens[i:(i+850)])
        docs_2.append(selection)
    
    summaries = summarizer2(docs_2)
    summary = "\n\n".join([d["summary_text"] for d in summaries])

    return summary