import os
import json
import pytesseract
from PIL import Image
import speech_recognition as sr
import pyttsx3
from openai import OpenAI
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Initialize DeepSeek API (retrieve API key from environment variable)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise EnvironmentError("DEEPSEEK_API_KEY environment variable is not set.")

deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")


# Initialize text-to-speech engine
engine = pyttsx3.init()

# File to store memory
MEMORY_FILE = "ds_memory.json"

# Google Drive and Docs API Scopes
SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents"]

# Function to authenticate and get Google API credentials
def get_google_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

# Function to create a Google Doc and write content
def create_google_doc(content, title="DS Manual"):
    creds = get_google_credentials()
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # Create a new Google Doc
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    # Insert content into the Google Doc
    requests = [
        {"insertText": {"location": {"index": 1}, "text": content}}
    ]
    docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

    # Share the document (optional)
    drive_service.permissions().create(
        fileId=doc_id, body={"type": "anyone", "role": "writer"}, fields="id"
    ).execute()

    print(f"Google Doc created: https://docs.google.com/document/d/{doc_id}")
    return doc_id

# Load memory from file
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    return {}

# Save memory to file
def save_memory(memory):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)

# Function to capture screen and extract text
def capture_and_extract_text():
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        screenshot.save("screen.png")
        text = pytesseract.image_to_string(Image.open("screen.png"))
        return text
    except ImportError:
        print("pyautogui is not available. Screen capture is disabled.")
        return "Screen capture is not supported in this environment."


# Function to listen for voice commands
def listen_for_command():
    command = input("Type your command: ")
    return command
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for a command...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        print("Sorry, I didn't understand that.")
        return None
    except sr.RequestError:
        print("Sorry, there was an issue with the speech recognition service.")
        return None

# Function to speak DS's response
def speak_response(response):
    print(f"DS says: {response}")
    engine.say(response)
    engine.runAndWait()

# Function to infer intent from the command
def infer_intent(command):
    command = command.lower()
    if any(word in command for word in ["screen", "display", "what's on"]):
        return "analyze_screen"
    elif any(word in command for word in ["remember", "save", "note"]):
        return "remember_info"
    elif any(word in command for word in ["recall", "what do you remember", "tell me what you know"]):
        return "recall_info"
    elif any(word in command for word in ["export manual", "save manual", "create doc"]):
        return "export_manual"
    else:
        return "general_query"


# Function to analyze text using OpenAI DeepSeek model
def analyze_text_with_deepseek(text):
    response = deepseek_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}
        ],
        stream=False
    )
    return response.choices[0].message.content


# Main loop for voice-controlled interaction
try:
    # Load memory at the start
    memory = load_memory()

    while True:
        # Listen for a voice command
        command = listen_for_command()
        if command:
            intent = infer_intent(command)

            if intent == "analyze_screen":
                # Capture screen and extract text
                screen_text = capture_and_extract_text()
                print("Extracted Text:", screen_text)
                # Save the extracted text to memory
                memory["last_screen_text"] = screen_text
                save_memory(memory)
                # Send the extracted text to DeepSeek AI
                response = analyze_text_with_deepseek(screen_text)
            elif intent == "remember_info":
                # Extract the information to remember
                information = command.lower().replace("remember", "").replace("save", "").replace("note", "").strip()
                memory["user_notes"] = memory.get("user_notes", []) + [information]
                save_memory(memory)
                response = f"I've remembered: {information}"
            elif intent == "recall_info":
                if "user_notes" in memory:
                    response = "Here's what I remember:\n" + "\n".join(memory["user_notes"])
                else:
                    response = "I don't have any notes saved yet."
            elif intent == "export_manual":
                # Create a manual content
                manual_content = "DS Assistant Manual\n\n"
                manual_content += "1. Permanent Memory System\n"
                manual_content += "2. Screen Reading (OCR)\n"
                manual_content += "3. Voice Dialog (Speech Recognition and Text-to-Speech)\n"
                manual_content += "4. Google Drive Integration\n"
                # Export to Google Docs
                doc_id = create_google_doc(manual_content, title="DS Assistant Manual")
                response = f"Manual exported to Google Docs: https://docs.google.com/document/d/{doc_id}"
            else:
                # Send the voice command to DeepSeek AI
                response = analyze_text_with_deepseek(command)
            # Speak DS's response
            speak_response(response)

except KeyboardInterrupt:
    print("Voice-controlled DS stopped by user.")
