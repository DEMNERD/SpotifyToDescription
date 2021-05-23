import configparser
import logging
import re
import time

import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from telethon import connection
from telethon.sync import TelegramClient
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest

from bot import Bot


logging.basicConfig(filename='main.log', level=logging.DEBUG)

config = configparser.ConfigParser()
config.read("config.ini")

telegram_bot_token = config['Telegram']['bot_token']

telegram_api_id = int(config['Telegram']['api_id'])
telegram_api_hash = config['Telegram']['api_hash']

channel_id = int(config['Telegram']['channel_id'])
telegram_username = config['Telegram']['channel_id']

country = config['Spotify']['country_code']

bot = Bot(telegram_bot_token)
spotify_api = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config['Spotify']['client_id'],
                                                        client_secret=config['Spotify']['client_secret'],
                                                        redirect_uri=config['Spotify']['redirect_uri'],
                                                        scope="user-read-playback-state"))

client = TelegramClient(telegram_username, telegram_api_id, telegram_api_hash,
                        connection=connection.ConnectionTcpIntermediate)
client.start()

common_about = client(GetFullUserRequest(client.get_me())).about
last_song = last = None

while True:
    try:
        currently_playing = spotify_api.currently_playing()

        if currently_playing and currently_playing['item'] and currently_playing['item'] != last:
            artists = ', '.join(i['name'] for i in currently_playing['item']['artists'])
            track = currently_playing["item"]["name"]
            for i in [' digital remaster ', ' remaster ', ' mono ', 'single version']:
                if i in track.lower() and track[:track.lower().find(i)].rstrip(" -1234567890("):
                    track = track[:track.lower().find(i)].rstrip(" -1234567890(")
            
            track_list = track.split()
            cropped_track_split = track[:67 - len(artists)].split()
            track = (
                    ' '.join(cropped_track_split[:-1]) +
                    (' ' + cropped_track_split[-1] * (cropped_track_split[-1] in track_list))
            ).strip(" -")

            track += '...' if len(track) <= 64 - len(artists) and track_list != cropped_track_split else ''
            text = f'{track.strip(" -")} — {artists}'
            text = ''.join(re.split(r'\(.*\)', text)) if len(text) > 70 else text
            
            client(UpdateProfileRequest(
                about=text
            ))
            last = currently_playing['item']
            if currently_playing['item'] != last_song:
                currently_playing_spotify_link = currently_playing['item']['external_urls']['spotify']
                
                others_platforms_url = 'https://songwhip.com' + requests.post(
                    'https://songwhip.com/api/',
                    data='{"url":"%s","country":"%s"}' %
                         (currently_playing_spotify_link, country),
                    headers={'Content-Type': 'application/json'}
                ).json()['data']['url']
                keyboard = [{"text": 'Spotify', "url": currently_playing_spotify_link},
                            {'text': 'Other platforms', 'url': others_platforms_url}]
                
                bot.send_photo_by_id(channel_id, photo_id=currently_playing['item']['album']['images'][0]['url'],
                                     caption=f'{currently_playing["item"]["name"]} — {artists}',
                                     reply_markup=keyboard)
            last_song = last
            logging.info(text)
        elif not currently_playing and last != common_about:
            last = common_about
            client(UpdateProfileRequest(
                about=common_about
            ))
            logging.info(common_about)
        time.sleep(8)
    except Exception as e:
        logging.error(e)
        client(UpdateProfileRequest(
            about=common_about
        ))
        logging.info(common_about)
        time.sleep(10)
