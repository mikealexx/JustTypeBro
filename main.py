import os
from transformers import pipeline
import logging
from neonize.client import NewClient
from neonize.events import (
    ConnectedEv,
    MessageEv
)

# Initializations
whisper = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")
client = NewClient("just_type_bro.sqlite3")
logger = logging.getLogger("Whisper")

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
    transcription = whisper(mp3_path)
    client.send_message(chat, transcription)

if __name__ == "__main__":
    client.connect()
    