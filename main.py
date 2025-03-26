import requests
import os
import functions_framework
from flask import Response


discord_token = str(os.environ.get("DISCORD_TOKEN"))
discord_channel = int(os.environ.get("DISCORD_CHANNEL_ID"))

twitch_token = str(os.environ.get("TWITCH_TOKEN")) #app access tokenの方
twitch_client_id = str(os.environ.get("TWITCH_CLIENT_ID"))

@functions_framework.http
def main(request):
    if request.method != "POST":
        return "無効です"

    # ここにシグネチャの確認をするかもしれない

    send(request)
    
def send(request):
    try:
        headers = {
            "Authorization": discord_token,
            "Content-Type": "application/json"
        }

        stream_info = request.get_json()

        content = {
            "content": f"**{stream_info['user_name']}** is live on **{stream_info['game_name']}**! \nhttps://www.twitch.tv/{stream_info['user_name']}"
        }

        response = requests.post(f"https://discord.com/api/channels/{discord_channel}/messages", headers=headers, json=content)

        return "Success", 200 # 2XXを返さないと何回も送られてくるらしい

    except Exception as e:
        print(e)


# 配信開始したらその情報を取得する。app access tokenでOK
def get_stream_info(user_name):
    streamer_id = get_streamer_id(user_name)
    url = f"https://api.twitch.tv/helix/channels?broadcaster_id={streamer_id}"
    headers = {
        "Client-ID": twitch_client_id,
        "Authorization": f"Bearer {twitch_token}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data["data"][0]


# 配信者のIDを取得する。app access tokenでOK
def get_streamer_id(user_name):
    url = f"https://api.twitch.tv/helix/users?login={user_name}"
    headers = {
        "Client-ID": twitch_client_id,
        "Authorization": f"Bearer {twitch_token}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data["data"][0]["id"]