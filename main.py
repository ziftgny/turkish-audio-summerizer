from fastapi import FastAPI, Form, UploadFile, File
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import whisper
import torch
import os
import time

app = FastAPI()

# ✅ Whisper Model (Unchanged, but now with a timer)
whisper_model = whisper.load_model("medium",device="cpu")

# ✅ Load Helsinki-NLP Turkish-to-English Translation Model
TR_TO_EN_MODEL = "Helsinki-NLP/opus-mt-tc-big-tr-en"
tr_to_en_tokenizer = AutoTokenizer.from_pretrained(TR_TO_EN_MODEL)
tr_to_en_model = AutoModelForSeq2SeqLM.from_pretrained(
    TR_TO_EN_MODEL, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
).to("cuda" if torch.cuda.is_available() else "cpu")

# ✅ Load Helsinki-NLP English-to-Turkish Translation Model
EN_TO_TR_MODEL = "Helsinki-NLP/opus-mt-tc-big-en-tr"
en_to_tr_tokenizer = AutoTokenizer.from_pretrained(EN_TO_TR_MODEL)
en_to_tr_model = AutoModelForSeq2SeqLM.from_pretrained(
    EN_TO_TR_MODEL, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
).to("cuda" if torch.cuda.is_available() else "cpu")

# ✅ Load Faster Summarization Model (DistilBART)
SUMMARIZER_MODEL = "facebook/bart-large-cnn"
summarizer_tokenizer = AutoTokenizer.from_pretrained(SUMMARIZER_MODEL)
summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(
    SUMMARIZER_MODEL,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
).to("cuda" if torch.cuda.is_available() else "cpu")


# ✅ Optimized Turkish ➝ English Translation
def translate_to_english(text):
    start_time = time.time()
    inputs = tr_to_en_tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to("cuda" if torch.cuda.is_available() else "cpu")
    outputs = tr_to_en_model.generate(**inputs)
    translated_text = tr_to_en_tokenizer.decode(outputs[0], skip_special_tokens=True)
    elapsed_time = time.time() - start_time
    print(f"🚀 Translation (TR ➝ EN) Time: {elapsed_time:.2f} sec")
    return translated_text

# ✅ Faster Summarization (DistilBART)
def summarize_text(text):
    start_time = time.time()
    inputs = summarizer_tokenizer(text, return_tensors="pt", truncation=True, max_length=1024).to("cuda" if torch.cuda.is_available() else "cpu")
    outputs = summarizer_model.generate(
        **inputs,
        max_new_tokens=225,
        do_sample=False,
        top_k=50,
        repetition_penalty=1.8
    )
    summary = summarizer_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    elapsed_time = time.time() - start_time
    print(f"🔥 Summarization Time: {elapsed_time:.2f} sec")
    return summary

# ✅ Optimized English ➝ Turkish Translation
def translate_to_turkish(text):
    start_time = time.time()
    inputs = en_to_tr_tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to("cuda" if torch.cuda.is_available() else "cpu")
    outputs = en_to_tr_model.generate(**inputs)
    translated_text = en_to_tr_tokenizer.decode(outputs[0], skip_special_tokens=True)
    elapsed_time = time.time() - start_time
    print(f"🚀 Translation (EN ➝ TR) Time: {elapsed_time:.2f} sec")
    return translated_text

# ✅ Transcription API (With Timer)
@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    start_time = time.time()
    result = whisper_model.transcribe(file_path, language="tr")
    transcription_time = time.time() - start_time
    os.remove(file_path)

    print(f"🎤 Transcription Time: {transcription_time:.2f} sec")
    
    return {"transcription": result["text"], "time_taken": f"{transcription_time:.2f} sec"}

# ✅ Summarization API
@app.post("/summarize/")
async def summarize_turkish_text(text: str = Form(...)):
    if len(text.split()) < 10:
        return {"error": "Text is too short for summarization"}

    start_time = time.time()
    english_text = translate_to_english(text)
    summarized_english = summarize_text(english_text)
    final_summary = translate_to_turkish(summarized_english)
    summary_time = time.time() - start_time

    return {"summary": final_summary, "time_taken": f"{summary_time:.2f} sec"}

# ✅ Full Pipeline: Transcription ➝ Summarization
@app.post("/transcribe-and-summarize/")
async def transcribe_and_summarize(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    start_time = time.time()
    result = whisper_model.transcribe(file_path, language="tr")
    transcription = result["text"]
    transcription_time = time.time() - start_time
    os.remove(file_path)

    print(f"🎤 Transcription Time: {transcription_time:.2f} sec")

    if len(transcription.split()) < 10:
        return {"transcription": transcription, "summary": "Text too short for summarization."}

    english_text = translate_to_english(transcription)
    summarized_english = summarize_text(english_text)
    final_summary = translate_to_turkish(summarized_english)
    total_time = time.time() - start_time

    return {
        "transcription": transcription,
        "transcription_time": f"{transcription_time:.2f} sec",
        "summary": final_summary,
        "total_time": f"{total_time:.2f} sec"
    }
