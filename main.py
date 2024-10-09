import requests, os
import logging
from neonize.client import NewClient
from neonize.events import (
    ConnectedEv,
    MessageEv
)

# Initializations
whisper_url = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
client = NewClient("just_type_bro.sqlite3")
logger = logging.getLogger("Whisper")

api_token = os.getenv("api_token")
headers = {"Authorization": f"Bearer {api_token}"}

if not os.path.exists('temp'):
    os.makedirs('temp')

@client.event(ConnectedEv)
def on_connected(_: NewClient, __: ConnectedEv):
    logger.info("\nConnected to WhatsApp\n")

@client.event(MessageEv)
def on_message(client: NewClient, message: MessageEv):
    handler(client, message)

def handler(client, message):
    #text = message.Message.conversation or message.Message.extendedTextMessage.text
    chat = message.Info.MessageSource.Chat
    #group_name = client.get_group_info(chat).GroupName.Name
    
    client.download_any(message.Message, path="media/audio.opus")
    opus_path = 'media/audio.opus'
    mp3_path = 'media/audio.mp3'
    os.system(f'ffmpeg -i "{opus_path}" -vn "{mp3_path}" -y')
    
    with open(mp3_path, 'rb') as f:
        data = f.read()

    # Send a POST request to the API with the audio data
    response = requests.post(whisper_url, headers=headers, data=data)

    # Check the response status
    if response.status_code == 200:
        # Parse and print the JSON response
        transcription = response.json()["text"]
        client.send_message(chat, transcription)
    else:
        client.send_message(chat, "Whisper service is currently unavailable. Please try again later.")

    os.remove(opus_path)
    os.remove(mp3_path)

if __name__ == "__main__":
    client.connect()
    