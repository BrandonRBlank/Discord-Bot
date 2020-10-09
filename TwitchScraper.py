from requests import Session
import json
from twitch import TwitchClient
import re

CLIENT_ID = 'a0n3609z67vl4lzpv9fm0t43wafnhu'
CHANNEL_OAUTH = 'h0wbwgdoakv9n9k2lap0ltrbt7sldl'
client = TwitchClient(client_id=CLIENT_ID, oauth_token=CHANNEL_OAUTH)


def streamer_data(streamer):
    streamData = {}
    session = Session()
    channelId = ""
    channelName = re.split('.tv/', streamer)[-1]
    channelIdUrl = "https://api.twitch.tv/kraken/users?login=" + channelName

    response = session.get(channelIdUrl, headers={
        'Client-ID': CLIENT_ID,
        'Accept': 'application/vnd.twitchtv.v5+json',
        'Content-Type': 'application/json'
    })
    # noinspection PyBroadException
    try:
        result = json.loads(response.text)
    except Exception:
        result = None

    if result:
        channelId = result["users"][0]["_id"]

    streamData['game'] = client.channels.get_by_id(channelId)['game']
    streamData['title'] = client.channels.get_by_id(channelId)['status']
    streamData['logo'] = client.channels.get_by_id(channelId)['logo']
    streamData['banner'] = client.channels.get_by_id(channelId)['profile_banner']
    streamData['views'] = client.channels.get_by_id(channelId)['views']
    streamData['followers'] = client.channels.get_by_id(channelId)['followers']

    return streamData
