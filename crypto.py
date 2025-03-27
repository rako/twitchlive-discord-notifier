import hmac
import hashlib
import os

def verify_twitch_signature(request, secret):
    """
    Twitchからのイベントメッセージの署名を検証する
    
    Args:
        request: Flask/Functions Frameworkのリクエストオブジェクト
        secret: Twitch EventSubサブスクリプション作成時に設定した秘密キー
        
    Returns:
        bool: 署名が有効な場合はTrue、そうでない場合はFalse
    """
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
        message_body = request.data
        
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
        return False

def verify_twitch_notification(request, secret):
    """
    Twitchからの通知を検証し、タイプを確認する
    
    Args:
        request: Flask/Functions Frameworkのリクエストオブジェクト
        secret: Twitch EventSubサブスクリプション作成時に設定した秘密キー
        
    Returns:
        dict: {'verified': bool, 'type': str}
    """
    verified = verify_twitch_signature(request, secret)
    
    # メッセージタイプを取得
    message_type = request.headers.get('Twitch-Eventsub-Message-Type', '')
    
    return {
        'verified': verified,
        'type': message_type
    }


def webhook_handler(request):
    webhook_secret = os.environ.get('TWITCH_WEBHOOK_SECRET')
    
    # 署名を検証
    verification = verify_twitch_notification(request, webhook_secret)
    
    if not verification['verified']:
        return "署名が無効です", 403
        
    # webhook_callbackかどうかを確認
    if verification['type'] == 'webhook_callback_verification':
        challenge = request.get_json().get('challenge')
        return challenge, 200, {'Content-Type': 'text/plain'}
        
    # 通常のイベント通知
    if verification['type'] == 'notification':
        event_data = request.get_json()
        
    return "", 204