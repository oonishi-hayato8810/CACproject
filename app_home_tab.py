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

@app.action("attendance_check_student")
def handle_some_command(ack: Ack, body: dict, view: dict, client: WebClient, logger: logging.Logger):
    # 受信した旨を 3 秒以内に Slack サーバーに伝えます
    ack()
    dt = datetime.datetime.now()
    today = f"{dt.year}年{dt.month}月{dt.day}日"
    
    #print(private_metadata)
    '''
    print("                                                \n  \n \n \n")
    print(dt)
    print(view)
    print(logger)
    print()
    '''
    print("                                                \n  \n \n \n")
    print(body)
    print("                                                \n  \n \n \n")
    # bodyの中にいろいろ入ってるんゴよ
    my_slack_id = body.get('user').get('id')
    hoge = body.get('actions')
    print(hoge)
    print("                                                \n  \n \n \n")
    for i in hoge:
        print(i)
        print(i["selected_option"]["value"])
    print()
    clean_day = body['actions'][0]["selected_option"]["value"]
    print()
    #print(body)
    # views.open という API を呼び出すことでモーダルを開きます
    client.views_open(
        # 上記で説明した trigger_id で、これは必須項目です
        # この値は、一度のみ 3 秒以内に使うという制約があることに注意してください
        trigger_id=body["trigger_id"],
        # モーダルの内容を view オブジェクトで指定します
		view={
	"type": "modal",
	"title": {
		"type": "plain_text",
		"text": "出席確認表",
		"emoji": True
	},
	"close": {
		"type": "plain_text",
		"text": "戻る",
		"emoji": True
	},
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": clean_day + "←選択した日付のvalueの値\n" + my_slack_id + '←自分のslack番号'\
                    + 'この二つを使って掃除日、班名、掃除場所、担当曜日をDBから取得、出力',
				"emoji": True
			}
		},
		
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "だれか\n出家席\n理由",
				"emoji": True
			}
		},
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "上記を繰り返す",
				"emoji": True
			}
		},
	]
},
        
        
        
    )

        
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

