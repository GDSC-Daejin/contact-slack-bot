import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from db.main import DB
import yaml


def read_config_yaml():
    with open("config.yaml", "r") as yaml_file:
        config_data = yaml.safe_load(yaml_file)
    return config_data


def db_connect():
    config_data = read_config_yaml()
    username = config_data["database"]["username"]
    password = config_data["database"]["password"]
    try:
        host = os.environ["DB_IP_ADDR"]
    except Exception:
        host = config_data["database"]["host"]
    database = DB(host, username, password)
    return database


database = db_connect()
api_key = database.get_api_key()

app_token = api_key["CONTACT_SLACK_APP_TOKEN"]
bot_token = api_key["CONTACT_SLACK_BOT_TOKEN"]
signing_secret = api_key["CONTACT_SLACK_SIGNING_SECRET"]
app = App(token=bot_token, signing_secret=signing_secret)
client = WebClient(token=bot_token)


def send_message(channel, data, thread_ts=None):
    def create_vcard(name, nickname, phone):
        vcard = f"BEGIN:VCARD\n"
        vcard += f"VERSION:3.0\n"
        vcard += f"N:{name}({nickname})\n"
        vcard += f"FN:{name}({nickname})\n"
        # vcard += f"EMAIL:{email}\n"
        vcard += f"TEL:{phone}\n"
        vcard += f"END:VCARD\n"
        return vcard

    nickname = data["nickname"]
    name = data["name"]
    phone = data["phone"]
    vcard_data = create_vcard(name, nickname, phone)
    file_name = f"{name}.vcf"
    with open(file_name, "w") as vcard_file:
        vcard_file.write(vcard_data)
    # try:
    #     client.chat_postMessage(channel=channel, text=f"{nickname}({name}) : {phone}", thread_ts=thread_ts)

    # except SlackApiError as e:
    #     print(text, e)
    #     text = f"Error sending message: {e.response['error']}"
    #     client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)
    try:
        response = client.files_upload(
            channels=channel,
            file=file_name,
            title=f"{name}({nickname}) 전화번호",
            initial_comment=f"{name}({nickname}) : {phone}",
            thread_ts=thread_ts,
        )

    except SlackApiError as e:
        print(text, e)
        text = f"Error sending message: {e.response['error']}"
        client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)

    # Remove the temporary vcf file
    os.remove(file_name)


@app.event("app_mention")
def handle_mention(body, say, logger, event, message):
    logger.info(body)

    ts = event["ts"]
    channel = event["channel"]
    data = database.get_info()
    for a in data:
        send_message(channel=channel, data=a, thread_ts=ts)


if __name__ == "__main__":
    data = database.get_info()

    # Start the bot

    handler = SocketModeHandler(app_token=app_token, app=app)
    handler.start()
