import os
import time
import json
import requests

GROQ_URL = "https://groq.com"
FISH_AUDIO_URL = "https://fish.audio"

def call_groq_brain(topic):
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    prompt = (
        f"You are the lead technical content strategist for Optispark Media Co. "
        f"Write a 45-second high-impact training lesson for teenagers about: '{topic}'. "
        f"Return a strict JSON object with exactly two keys: "
        f"'hook' (a punchy 5-second attention-grabbing opening problem statement) and "
        f"'lesson' (the step-by-step breakdown using clear real-world tech analogies). "
        f"Do not write conversational filler text outside the JSON."
    )
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(GROQ_URL, json=payload, headers=headers).json()
        return json.loads(res['choices']['message']['content'])
    except Exception as e:
        print(f"❌ Groq Parsing Failure: {e}")
        return None

if __name__ == "__main__":
    while True:
        print("📡 Polishing and scanning content sheet records...")
        time.sleep(30)
