import os
import requests
import json

# Use your Hugging Face Granite token
HF_TOKEN = "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"
HF_MODEL = "ibm-granite/granite-3.3-2b-instruct"
HF_API = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

PROMPT_TEMPLATE = (
    "You are a medical text extraction assistant.\n"
    "Extract all drugs and doses from this prescription text as JSON:\n"
    "Return exactly a JSON object with 'drugs' (list of name and dose) and 'notes'.\n"
    "Do not add extra commentary.\n"
    "Input: {input_text}\nOutput:"
)

def extract_prescription_from_text(prescription_text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(input_text=prescription_text)
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}
    response = requests.post(HF_API, headers=HEADERS, json=payload, timeout=60)
    response.raise_for_status()
    out = response.json()

    # Parse JSON from model response
    text_output = ""
    if isinstance(out, list):
        for item in out:
            if isinstance(item, dict) and item.get("generated_text"):
                text_output += item["generated_text"]
            elif isinstance(item, str):
                text_output += item
    else:
        text_output = str(out)

    # Attempt to convert to JSON
    import re
    match = re.search(r"\{[\s\S]*\}", text_output)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass

    # fallback
    return {"drugs": [], "notes": text_output}
