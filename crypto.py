import hmac
import hashlib
from flask import Response

def verify_twitch_signature(request, secret):
    try:
        # リクエストヘッダーから必要な値を取得
        message_signature = request.headers.get('Twitch-Eventsub-Message-Signature')
        message_id = request.headers.get('Twitch-Eventsub-Message-Id')
        message_timestamp = request.headers.get('Twitch-Eventsub-Message-Timestamp')
        
        # すべてのヘッダーが存在することを確認
        if not message_signature or not message_id or not message_timestamp:
            print("必要なヘッダーが見つかりません")
            return False
            
        # リクエストボディを取得（バイト形式で）
        message_body = request.data.decode('utf-8')
        
        # HMACメッセージの作成（ID + タイムスタンプ + ボディ）
        hmac_message = message_id + message_timestamp + message_body
        
        # HMAC-SHA256署名を計算
        signature = hmac.new(
            key=secret.encode('utf-8'),
            msg=hmac_message.encode('utf-8') if isinstance(hmac_message, str) else hmac_message,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # 'sha256='プレフィックスを付けて署名を比較
        expected_signature = f'sha256={signature}'
        
        # 署名の比較（タイミング攻撃を防ぐためにhmac.compare_digestを使用）
        return hmac.compare_digest(expected_signature, message_signature)
        
    except Exception as e:
        print(f"署名検証エラー: {e}")
        return Response("署名検証エラー", status=500)