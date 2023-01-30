import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# 'hello' を含むメッセージをリッスンします

@app.message("hello")
def message_hello(message, say):
    # イベントがトリガーされたチャンネルへ say() でメッセージを送信します
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text":"Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )


@app.event("app_home_opened")
def update_home_tab(client, event, logger, user_id):
    try:
        client.views_publish(
        user_id=event["user"],
        view={
            "type": "home",
            "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    #"text": "*大西さんはAD班です。*\n*掃除場所:301教室です。*\n*担当曜日：月*"
                    "text": f"*{user_id}さんはAD班です。* \n*掃除場所:301教室*\n*担当曜日：月*"
                },
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "出欠確認：掃除日を選択してください"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an item",
                        #"emoji": true
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "2023年1月20日",
                                #"emoji": true
                            },
                            "value": "value-0"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "2023年1月23日",
                                #"emoji": true
                            },
                            "value": "value-1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "2023年1月27日",
                                #"emoji": true
                            },
                            "value": "value-2"
                        }
                    ],
                    # 出欠確認画面へ
                    "action_id": "attendance_contact"
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "出欠連絡:"
                },
                "accessory": {
                    "type": "button",

                    # 出欠連絡画面へ
                    "action_id": "nonparticipation",
                    "text": {
                        "type": "plain_text",
                        "text": "出欠連絡を開く"
                    }
                }
            }
        ]
    }
)

        
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

