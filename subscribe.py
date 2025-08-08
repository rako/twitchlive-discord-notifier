import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

def subscribe():
    try:
        with open("channels.json", "r", encoding="utf-8") as f:
            json_data = json.load(f)

        if json_data is None:
            return "JSONデータがありません", 400
        
        print(f"受信したJSON: {json_data}") # デバッグ用

        client_id = os.environ.get("clientId")
        client_secret = os.environ.get("clientSecret")
        bearertoken = os.environ.get("bearertoken")
        webhook_url = os.environ.get("webhook_url")

        for streamer_info in json_data["data"]:
            broadcaster_id = streamer_info["broadcaster_id"]

            url = f"https://api.twitch.tv/helix/eventsub/subscriptions"
            headers = {
                "Client-ID": f"{client_id}",
                "Authorization": f"Bearer {bearertoken}",
                "Content-Type": "application/json"
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
                    "secret": f"{client_secret}"

                }
            }
            
            response = requests.post(url, headers=headers, json=subscribe_json)
            if not response.ok:
                print(response.text)
                print(f"{streamer_info['broadcaster_name']}の配信開始のサブスクリプション作成に失敗しました")
            else:
                print(response.text)
                print(f"{streamer_info['broadcaster_name']}の配信開始のサブスクリプションを作成しました")
                
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
                    "secret": f"{client_secret}"
                }
            }

            response = requests.post(url, headers=headers, json=subscribe_json)
            if not response.ok:
                print(response.text)
                print(response.status_code)
                print(f"{streamer_info['broadcaster_name']}の配信終了のサブスクリプション作成に失敗しました")
            else:
                print(response.text)
                print(f"{streamer_info['broadcaster_name']}の配信終了のサブスクリプションを作成しました")

        # 成功した結果を返す
        return {
            "message": "サブスクリプション処理完了",
        }, 200

    except Exception as e:
        print(f"エラー発生: {e}")
        return f"内部エラー: {str(e)}", 500

subscribe()