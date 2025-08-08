import requests
import os
import functions_framework
from flask import Response
from crypto import verify_twitch_signature

twitch_token = str(os.environ.get("TWITCH_TOKEN")) #app access tokenの方
twitch_client_id = str(os.environ.get("TWITCH_CLIENT_ID"))
webhook_secret = os.environ.get('TWITCH_WEBHOOK_SECRET')
webhook_url = str(os.environ.get("WEBHOOK_URL"))

@functions_framework.http
def main(request):
    print("request json:", request.get_json())

    # Message-Typeがwebhook_callback_verificationかnotificationで分けてChallengeと通知の関数を切り分けておく
    message_type = request.headers.get("Twitch-Eventsub-Message-Type")

    if message_type == "webhook_callback_verification":
        print("challenge認証が来ました")
        return challenge(request)
    if message_type == "notification":
        print("配信の通知が来ました")
        return send(request)
    
def send(request):
    try:
        # 署名を検証
        verification = verify_twitch_signature(request, webhook_secret)
        
        if not verification:
            print("署名が無効です")
            return "署名が無効です", 403
        
        headers = {
            "Content-Type": "application/json"
        }

        stream_info = request.json["event"]
        print("stream_info:", stream_info)

        content = {
            "content": f"@everyone {stream_info['broadcaster_user_name']} is live now! \nhttps://www.twitch.tv/{stream_info['user_name']}"
        }
        
        response = requests.post(webhook_url, headers=headers, json=content)
        print(response)

        return Response(response="Success", status=200) # 2XXを返さないと何回も送られてくるらしい

    except Exception as e:
        print(e)
        return Response(response="Failed because of server error", status=500)


# イベントのサブスクライブ後に一番最初にChallengeが送られてくるのでそれの認証
def challenge(request):
    challenge_string = request.json["challenge"]
    print("challenge_string:", challenge_string)
    return Response(response=f'{challenge_string}', status=200, mimetype='text/plain')


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