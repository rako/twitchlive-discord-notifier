import requests
import os
from dotenv import load_dotenv

load_dotenv()

def unsubscribe():
    try:
        client_id = os.environ.get("clientId")
        bearertoken = os.environ.get("bearertoken")

        # まず現在のサブスクリプション一覧を取得
        list_url = "https://api.twitch.tv/helix/eventsub/subscriptions"
        headers = {
            "Client-ID": f"{client_id}",
            "Authorization": f"Bearer {bearertoken}",
            "Content-Type": "application/json"
        }

        response = requests.get(list_url, headers=headers)
        
        if not response.ok:
            print(f"サブスクリプション一覧の取得に失敗しました: {response.text}")
            return f"エラー: {response.text}", response.status_code

        subscriptions = response.json()
        print(f"現在のサブスクリプション数: {subscriptions['total']}")

        success_count = 0
        fail_count = 0

        # 各サブスクリプションを削除
        for subscription in subscriptions['data']:
            subscription_id = subscription['id']
            subscription_type = subscription['type']
            broadcaster_id = subscription['condition'].get('broadcaster_user_id', 'Unknown')
            
            # 削除リクエスト
            delete_url = f"https://api.twitch.tv/helix/eventsub/subscriptions?id={subscription_id}"
            
            delete_response = requests.delete(delete_url, headers=headers)
            
            if delete_response.status_code == 204:  # 成功時は204 No Content
                print(f"削除成功: {subscription_type} (Broadcaster ID: {broadcaster_id})")
                success_count += 1
            else:
                print(f"削除失敗: {subscription_type} (Broadcaster ID: {broadcaster_id}) - {delete_response.text}")
                fail_count += 1

        return {
            "message": "サブスクリプション削除処理完了",
            "success": success_count,
            "failed": fail_count,
            "total_processed": success_count + fail_count
        }, 200

    except Exception as e:
        print(f"エラー発生: {e}")
        return f"内部エラー: {str(e)}", 500

def unsubscribe_by_broadcaster_id(broadcaster_id):
    """
    特定の配信者のサブスクリプションのみを削除する関数
    """
    try:
        client_id = os.environ.get("clientId")
        bearertoken = os.environ.get("bearertoken")

        # 特定の配信者のサブスクリプションを取得
        list_url = f"https://api.twitch.tv/helix/eventsub/subscriptions?user_id={broadcaster_id}"
        headers = {
            "Client-ID": f"{client_id}",
            "Authorization": f"Bearer {bearertoken}",
            "Content-Type": "application/json"
        }

        response = requests.get(list_url, headers=headers)
        
        if not response.ok:
            print(f"サブスクリプション取得に失敗しました: {response.text}")
            return f"エラー: {response.text}", response.status_code

        subscriptions = response.json()
        
        if subscriptions['total'] == 0:
            print(f"Broadcaster ID {broadcaster_id} のサブスクリプションが見つかりませんでした")
            return {"message": "対象のサブスクリプションが見つかりません"}, 404

        success_count = 0
        fail_count = 0

        # 各サブスクリプションを削除
        for subscription in subscriptions['data']:
            subscription_id = subscription['id']
            subscription_type = subscription['type']
            
            delete_url = f"https://api.twitch.tv/helix/eventsub/subscriptions?id={subscription_id}"
            
            delete_response = requests.delete(delete_url, headers=headers)
            
            if delete_response.status_code == 204:
                print(f"削除成功: {subscription_type} (Broadcaster ID: {broadcaster_id})")
                success_count += 1
            else:
                print(f"削除失敗: {subscription_type} - {delete_response.text}")
                fail_count += 1

        return {
            "message": f"Broadcaster ID {broadcaster_id} のサブスクリプション削除完了",
            "success": success_count,
            "failed": fail_count
        }, 200

    except Exception as e:
        print(f"エラー発生: {e}")
        return f"内部エラー: {str(e)}", 500

if __name__ == "__main__":
    # 全てのサブスクリプションを削除する場合
    result = unsubscribe()
    print("結果:", result)
    
    # 特定の配信者のサブスクリプションのみ削除する場合（例）
    # result = unsubscribe_by_broadcaster_id("279534156")
    # print("結果:", result)