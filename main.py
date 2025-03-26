import requests
import os
import functions_framework
from flask import Response


discord_token = str(os.environ.get("DISCORD_TOKEN"))
discord_channel = int(os.environ.get("DISCORD_CHANNEL_ID"))

twitch_token = str(os.environ.get("TWITCH_TOKEN"))
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

        return "Success"

    except Exception as e:
        print(e)