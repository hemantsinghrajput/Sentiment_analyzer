import openai
import os
import requests
import json
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
# Path to the audio file



def extract_transcript(json_data):
    try:
        data = json.loads(json_data)
        transcript = data['results']['channels'][0]['alternatives'][0]['transcript']
        return transcript
    except (KeyError, json.JSONDecodeError):

        print("Error: Transcript not found or invalid JSON format.")
        return None

def analyze(AUDIO_FILE):
    try:
        # STEP 1 Create a Deepgram client using the API key
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)

        with open(AUDIO_FILE, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        #STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )
        print('before deepgram')
        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

        # STEP 4: Print the response
        res = (extract_transcript(response.to_json(indent=4)))
        print('after deepgram')

        openai.api_key= OPENAI_API_KEY

        # Define OpenAI API endpoint
        OPENAI_API_URL = 'https://api.openai.com/v1/engines/gpt-3.5-turbo/completions'
        print('before opapi')
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "So, in input of Web interface Hiring manager attaches audio with any human conversation. In output Hiring manager should get sentiment or psychological insights derived from the conversation, some insights about speakers. Please don’t provide summary of conversation, key words, etc. Output should be related to sentimental analysis.",
                "role": "user", "content": res}
            ]
        )

        # Extract the message content from the completion response
        message_content = completion['choices'][0]['message']['content']
        print('after opapi')
        # Remove newlines and concatenate into a single line
        message_content_single_line = ' '.join(message_content.splitlines())
        return message_content_single_line

    except Exception as e:
        print(f"Exception: {e}")




def main():
    AUDIO_FILE = "temp_audio.wav"
    print(analyze(AUDIO_FILE))

if __name__ == "__main__":
    main()
