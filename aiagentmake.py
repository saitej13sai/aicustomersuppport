import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configure Google Gemini API
genai.configure(api_key="AIzaSyDUvbyMHm5M5fkQXR5itUs")
model = genai.GenerativeModel("gemini-1.5-pro")

# Google Sheets Setup
SHEET_CREDENTIALS = "C:/Users/saite/Downloads/aiagents-ai-f9a168db1bd0.json"
SHEET_NAME = "ApolloAppointments"

# Authenticate Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(SHEET_CREDENTIALS, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Load Apollo Hospitals document
def load_hospital_data():
    try:
        with open("C:/Users/saite/OneDrive/Documents/apollo_hospitals_data.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        return "Apollo Hospitals provides various treatments including cardiology, orthopedics, neurology, and more."

hospital_data = load_hospital_data()

# Initialize Speech Recognition & TTS
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty("rate", 160)

def say(text):
    engine.say(text)
    engine.runAndWait()

def take_command():
    """Capture voice input and convert it to text."""
    with sr.Microphone() as source:
        recognizer.pause_threshold = 1
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=10)
            print("Recognizing...")
            text = recognizer.recognize_google(audio, language="en-in").lower()
            print(f"User said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand.")
            say("Sorry, I did not understand. Please repeat.")
            return ""
        except sr.RequestError as e:
            print(f"Request failed: {e}")
            return ""

def validate_date_time(date, time):
    """Validates date (YYYY-MM-DD) and time (HH:MM AM/PM)."""
    try:
        datetime.strptime(date, "%Y-%m-%d")
        datetime.strptime(time, "%I:%M %p")
        return True
    except ValueError:
        return False

def book_appointment(name, date, time, doctor, treatment):
    """Store appointment details in Google Sheets."""
    if not validate_date_time(date, time):
        return "Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM AM/PM for time."
    try:
        sheet.append_row([name, date, time, doctor, treatment])
        return f"Appointment booked for {name} on {date} at {time} with Dr. {doctor} for {treatment}."
    except Exception as e:
        return f"Failed to book appointment due to: {e}"

def chatbot():
    """Main chatbot interaction loop."""
    say("Hello! I’m Apollo Assistant. What’s your name?")
    user_name = take_command()
    if not user_name:
        user_name = "User"
        say("I didn’t catch your name. I’ll call you User for now.")
    say(f"Nice to meet you, {user_name}! How can I assist you today?")

    while True:
        user_input = take_command()
        if not user_input:
            continue

        if "book an appointment" in user_input:
            say("Sure! Let's book an appointment. I'll ask for some details.")

            say("What date would you like to book your appointment?")
            date = take_command()

            say("What time do you prefer?")
            time = take_command()

            say("Which doctor would you like to consult?")
            doctor = take_command()

            say("What treatment are you looking for?")
            treatment = take_command()

            confirmation = book_appointment(user_name, date, time, doctor, treatment)
            say(confirmation)
        elif "exit" in user_input:
            say("Goodbye! Have a great day.")
            break
        else:
            prompt = f"You are a customer support assistant for Apollo Hospitals. Use this data: {hospital_data}. Only assist with Apollo-related queries.\nUser: {user_input}"
            response = model.generate_content(prompt).text
            say(response)

if __name__ == "__main__":
    chatbot()
