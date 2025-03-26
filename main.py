import requests

discord_token = str(os.environ.get("DISCORD_TOKEN"))
discord_channel = int(os.environ.get("DISCORD_CHANNEL_ID"))

@functions_framework.http
def main(request):
    if request.method == "POST":
        send(request)
    
def send(request):
    pass