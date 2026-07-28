import os
import time
import json
import threading
import requests
from flask import Flask
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# Essential global configuration arrays
SPREADSHEET_ID = "1U8mc48nwNkxdCVs5KsUQq4rcLeFTv53gTJO78LgzuTw"
TOTAL_SLIDES = 20

@app.route('/')
def home():
    return "🚀 Optispark 20-Slide Content Engine is Online 24/7!"

def connect_google_sheets():
    """Authenticates securely using your background credentials JSON file"""
    scopes = ['https://googleapis.com']
    try:
        # Assumes credentials.json is saved directly in your root repository folder
        creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=scopes)
        service = build('sheets', 'v4', credentials=creds)
        return service.spreadsheets()
    except Exception as e:
        print(f"❌ Google Sheets Connection Failure: {e}")
        return None

def generate_curriculum_via_groq(topic):
    """Queries Llama 3 to output paired text and keywords for all 20 slides in strict JSON"""
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    # We dynamically construct the schema template to keep the AI focused
    schema = '{\n  "[Hook Script]": "text",\n  "[Hook Keyword]": "keyword",\n'
    for i in range(1, TOTAL_SLIDES + 1):
        schema += f'  "[Slide {i} Script]": "text",\n  "[Slide {i} Keyword]": "keyword",\n'
    schema = schema.rstrip(',\n') + '\n}'

    prompt = (
        f"You are the master curriculum architect for Optispark Media Co. "
        f"Write a deep-dive, professional technical lecture training module about: '{topic}'.\n\n"
        f"CRITICAL RULES:\n"
        f"1. Break the content down chronologically across exactly {TOTAL_SLIDES} separate, sequential slides.\n"
        f"2. For every single slide, generate a unique script text and a distinct visual search keyword.\n"
        f"3. Do not repeat video keywords. Every keyword must be a fresh, non-repetitive concept.\n"
        f"4. Output your response as a single, raw, strict JSON object. No conversational filler.\n\n"
        f"JSON SCHEMA TO FOLLOW EXACTLY:\n{schema}"
    )
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post("https://groq.com", json=payload, headers=headers).json()
        return json.loads(res['choices']['message']['content'])
    except Exception as e:
        print(f"❌ Groq API Processing Crash: {e}")
        return None

def core_automation_loop():
    """Main processing frame that continuously scans your sheets matrix"""
    while True:
        sheets = connect_google_sheets()
        if sheets:
            try:
                # 1. Read your spreadsheet structure columns
                result = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A:B").execute()
                rows = result.get('values', [])
                
                # 2. Iterate through rows starting at index 1 (skipping Row 1 headers)
                for index, row in enumerate(rows[1:], start=2):
                    if len(row) >= 2 and row[1].strip().lower() == "pending":
                        topic = row[0]
                        print(f"📡 Found pending row! Processing Topic: {topic}")
                        
                        # Generate data from Groq engine
                        ai_data = generate_curriculum_via_groq(topic)
                        if ai_data:
                            # Map the AI JSON dictionary elements straight out into a sequential flat array list
                            output_row = [
                                ai_data.get("[Hook Script]", ""),
                                ai_data.get("[Hook Keyword]", "")
                            ]
                            for s in range(1, TOTAL_SLIDES + 1):
                                output_row.append(ai_data.get(f"[Slide {s} Script]", ""))
                                output_row.append(ai_data.get(f"[Slide {s} Keyword]", ""))
                            
                            # Update the spreadsheet data matrix (columns C onwards)
                            sheets.values().update(
                                spreadsheetId=SPREADSHEET_ID,
                                range=f"Sheet1!C{index}",
                                valueInputOption="RAW",
                                body={"values": [output_row]}
                            ).execute()
                            
                            # Flip row status marker from 'pending' to 'completed'
                            sheets.values().update(
                                spreadsheetId=SPREADSHEET_ID,
                                range=f"Sheet1!B{index}",
                                valueInputOption="RAW",
                                body={"values": [["completed"]]}
                            ).execute()
                            print(f"✅ Row {index} content generation batch successfully completed!")
                            
            except Exception as e:
                print(f"❌ Error scanning row matrix logs: {e}")
        time.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=core_automation_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
