
import speech_recognition as sr
import pyttsx3
import re
from langdetect import detect  # Import langdetect module

import tkinter as tk
from tkinter import scrolledtext

#--------------------------------------------------
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

#---------------------------------------------------

import threading
recognizer = sr.Recognizer()

#---------------------------------------------------------
import pathlib
import textwrap
import google.generativeai as genai

#from google.colab import userdata
from IPython.display import display
from IPython.display import Markdown
import os
from dotenv import load_dotenv

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
res=""
def to_markdown(text):
  text = text.replace('.', ' *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

model = genai.GenerativeModel('gemini-pro')

#------------------------------------------------------------------------------------------

class SpeechApp:
    def __init__(self, master):
        self.master = master
        master.title("Speech-to-Text and Text-to-Speech")

        self.input_label = tk.Label(master, text="Input Method:")
        self.input_label.pack()

        # Radio button for input selection
        self.input_var = tk.IntVar()
        self.voice_input_radio = tk.Radiobutton(master, text="Voice Input", variable=self.input_var, value=1)
        self.voice_input_radio.pack()
        self.text_input_radio = tk.Radiobutton(master, text="Text Input", variable=self.input_var, value=2)
        self.text_input_radio.pack()

        self.input_frame = tk.Frame(master)
        self.input_frame.pack()

        # Text input area
        self.input_text = scrolledtext.ScrolledText(self.input_frame, width=50, height=5)
        self.input_text.pack(side=tk.LEFT)

        # Record button for voice input
        self.record_button = tk.Button(self.input_frame, text="Reply", command=self.process_audio)
        self.record_button.pack(side=tk.LEFT)

        self.output_label = tk.Label(master, text="Output:")
        self.output_label.pack()

        self.output_text = scrolledtext.ScrolledText(master, width=50, height=10)
        self.output_text.pack()

        # Initialize speech recognition
        self.recognizer = sr.Recognizer()

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')

        for voice in voices:
            print("Voice:")
            print(" - ID: ", voice.id)
            print(" - Name: ", voice.name)
            print(" - Languages: ", voice.languages)
            print(" - Gender: ", voice.gender)


    def process_audio(self):
        # Check input method selected
        input_method = self.input_var.get()
        if input_method == 1:  # Voice Input
            # Record audio
            with sr.Microphone() as source:
                self.output_text.insert(tk.END, "Listening...\n")
                self.output_text.update()
                audio_data = self.recognizer.listen(source)

            try:
                # Convert speech to text
                text = self.recognizer.recognize_google(audio_data)
                # Detect language of the input text
                language = detect(text)  # Modified: Language detection
                print("Detected language:", language)  # Debugging statement
                # Set the voice language based on detected language
                #self.engine.setProperty("voice", language)  # Modified: Set voice language
                # Sanitize input to remove special characters
                text = self.sanitize_input(text)
                self.input_text.delete('1.0', tk.END)
                self.input_text.insert(tk.END, text)
            except sr.UnknownValueError:
                self.output_text.insert(tk.END, "Could not understand audio\n")
            except sr.RequestError as e:
                self.output_text.insert(tk.END, "Error with the service: {0}\n".format(e))
        else:  # Text Input
            text = self.input_text.get('1.0', tk.END).strip()
            # Validate input text
            if not self.validate_input(text):
                self.output_text.insert(tk.END, "Invalid input\n")
                return

        text2 = text + ", in not more than three sentence"
        print("query: ", text2)


        responsee = model.generate_content(text2, stream=True)

        for chunk in responsee:
            print("Mahesh: ", chunk.text)
        to_markdown(responsee.text)
        res = responsee.text

        if text.lower() == "hello" or text.lower() == "hi":
            response = "Hello, I am your AI assistant. How can I help you?"
            # Return the response
            # print("print: ", res)
        else:
            response = res
        #return response

        self.output_text.insert(tk.END, response + "\n")
        self.output_text.update_idletasks()  # Ensure text is updated immediately
        tts_hindi = gTTS(text=res, lang='gu')
        # Save temporary audio files
        tts_hindi.save("tmp.mp3")
        # Open the audio file
        sound = AudioSegment.from_mp3("tmp.mp3")
        # Play the audio
        play(sound)
    def sanitize_input(self, input_text):
            # Remove special characters using regular expressions
            sanitized_text = re.sub(r'[^\w\s]', '', input_text)
            return sanitized_text

    def validate_input(self, input_text):
            # Perform validation checks here
            # For example, you can check if the input_text meets certain criteria
            # Here, we're just checking if the input is not empty
            if input_text:
                return True
            return False



def main():
    root = tk.Tk()
    app = SpeechApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()