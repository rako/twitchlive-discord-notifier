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

        webhook_url = os.environ.get("WEBHOOK_URL")
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
                    "callback": f"{webhook_url}",
                    "secret": f"{hmac_secret}"
                }
            }
            
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
            

    except Exception as e:
        print(e)