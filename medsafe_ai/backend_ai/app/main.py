from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
import json

app = FastAPI(title="Medsafe AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

HF_MODEL = os.getenv("HF_MODEL", "ibm-granite/granite-3.3-2b-instruct")
HF_ASR_MODEL = os.getenv("HF_ASR_MODEL", "ibm-granite/granite-speech-3.3-8b")
HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def call_hf_model(model_name, prompt):
    api_url = f"https://api-inference.huggingface.co/models/{model_name}"
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}
    res = requests.post(api_url, headers=HEADERS, json=payload, timeout=60)
    res.raise_for_status()
    return res.json()

def extract_drugs_from_text(text):
    prompt = (
        "You are a medical text assistant.\n"
        "Extract drugs in JSON format:\n"
        "Fields: name, dose_mg, frequency, duration_days, route\n"
        f"Input: {text}\nOutput:"
    )
    out = call_hf_model(HF_MODEL, prompt)
    if isinstance(out, list):
        text_out = "".join([item.get("generated_text", "") if isinstance(item, dict) else str(item) for item in out])
    else:
        text_out = str(out)
    import re
    m = re.search(r"\{[\s\S]*\}", text_out)
    try:
        return json.loads(m.group(0)) if m else {"drugs": []}
    except:
        return {"drugs": []}

def transcribe_audio(file_path):
    with open(fi
