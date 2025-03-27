import functions_framework
import requests
import os

@functions_framework.http
def main(request):
    if request.method != "POST":
        return "無効です"
    
    subscribe(request)

def subscribe(request):
    try:
        json_data = request.get_json()

        if json_data is None:
            return "JSONデータがありません", 400
        
        print(f"受信したJSON: {json_data}") # デバッグ用

        headers = {
            "Content-Type": "application/json"
        }

        callback_url = os.environ.get("CALLBACK_URL")
        hmac_secret = os.environ.get("TWITCH_HMAC_SECRET")

        for streamer_info in json_data["data"]:
            broadcaster_id = streamer_info["broadcaster_id"]

            url = f"https://api.twitch.tv/helix/eventsub/subscriptions"
            headers = {
                "Client-ID": os.environ.get("TWITCH_CLIENT_ID"),
                "Authorization": f"Bearer {os.environ.get('TWITCH_TOKEN')}"
            }

            # subscribe to online
            subscribe_json = {
                "type": "stream.online",
                "version": "1",
                "condition": {
                    "broadcaster_user_id": f"{broadcaster_id}"
                },
                "transport": {
                    "method": "webhook",
                    "callback": f"{callback_url}",
                    "secret": f"{hmac_secret}"
                }
            }
            
            response = requests.post(url, headers=headers, json=subscribe_json)
            if response.status_code != 202:
                print(response.text)
                print(f"{streamer_info["broadcaster_name"]}の配信開始のサブスクリプション作成に失敗しました")
                continue
            else:
                print(response.text)
                print(f"{streamer_info["broadcaster_name"]}の配信開始のサブスクリプションを作成しました")
                
            # subscribe to offline
            subscribe_json = {
                "type": "stream.offline",
                "version": "1",
                "condition": {
                    "broadcaster_user_id": f"{broadcaster_id}"
                },
                "transport": {
                    "method": "webhook",
                    "callback": f"{webhook_url}",
                    "secret": f"{hmac_secret}"
                }
            }

            response = requests.post(url, headers=headers, json=subscribe_json)
            if response.status_code != 202:
                print(response.text)
                print(f"{streamer_info["broadcaster_name"]}の配信開始のサブスクリプション作成に失敗しました")
                continue
            else:
                print(response.text)
                print(f"{streamer_info["broadcaster_name"]}の配信開始のサブスクリプションを作成しました")
            

    except Exception as e:
        print(e)