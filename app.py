import my_view
import os
import logging
from slack_bolt import App, Ack, Say, BoltContext, Respond
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
import pymysql.cursors
import datetime

'''
connection = pymysql.connect(host='localhost',
                            user='root',
                            password='',
                            database='cac_project',
                            cursorclass=pymysql.cursors.DictCursor)
'''

SLACK_BOT_TOKEN = "xoxb-4617576541650-4646680034466-m6B5rtkfabTiIX5cjFujW6fB"
SLACK_APP_TOKEN = "xapp-1-A04K33SU160-4640071884438-d1fad32aba64fcf00be44d6a7479c3657f550fbd9d365a0775ab5bbb169277b3"

# デバッグレベルのログを有効化
logging.basicConfig(level=logging.DEBUG)
# これから、この app に処理を設定していきます
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


#------------------------



@app.event("app_home_opened")
def update_home_tab(client, event, logger, user_id):
    print()
    print(user_id)
    print()
    print(event)
    print()
    try:
        # 組み込みのクライアントを使って views.publish を呼び出す
        client.views_publish(
            # イベントに関連づけられたユーザー ID を使用
            user_id=event["user"],
            # アプリの設定で予めホームタブが有効になっている必要がある
		view= {
			"type": "home",
            "private_metadata": user_id,
			"blocks": [
				{
				"type": "header",
				"text": {
				"type": "plain_text",
				"text": "テスト"
				}
			},
			{
			"type": "actions",
			"elements": [
				{
					"type": "button",
                    
					"text": {
						"type": "plain_text",
						"text": user_id + "先生用ボタン",
						"emoji": True
					},
					"value": "click_me_123",
					"action_id": "open_select_group"
				}
			]
		    },
			{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "班を選んでください"
			},
			"accessory": {
				"type": "static_select",
				"action_id": "attendance_check_student",
				"placeholder": {
					"type": "plain_text",
					"text": "班のリストを入れる",
					"emoji": True
				},
				
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "A5班",
							"emoji": True,
						},
						"value": "value_A6"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "B6班",
							"emoji": True
						},
						"value": "value_B6"
					},
                    ]
                }
            }
		    ]
		    
			
		}
		#view = my_view.home_view
        
        )

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

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

@app.action("attendance_chack_student")
def handle_some_command(ack: Ack, body: dict, client: WebClient):
    # 受信した旨を 3 秒以内に Slack サーバーに伝えます
    ack()
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
				"text": "1月12日木曜日",
				"emoji": True
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Welcome!* \nThis is a home for Stickers app. You can add small notes here!"
			},
			"accessory": {
				"type": "button",
				"action_id": "add_note",
				"text": {
					"type": "plain_text",
					"text": "Add a Stickie"
				}
			}
		},
		{
			"type": "divider"
		}
	]
},     
    )

# 先生用　班選択画面
@app.action("open_select_group")
def handle_some_command(ack: Ack, body: dict, client: WebClient):
    # 受信した旨を 3 秒以内に Slack サーバーに伝えます
    ack()
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
		"text": "班選択画面",
		"emoji": True
	},
	"submit": {
		"type": "plain_text",
		"text": "決定",
		"emoji": True
	},
	"close": {
		"type": "plain_text",
		"text": "戻る",
		"emoji": True
	},
	"title": {
		"type": "plain_text",
		"text": "班選択画面",
		"emoji": True
	},
	"blocks": [
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "日付を選んでください"
			},
			"accessory": {
				"type": "static_select",
                "action_id": "update",
				"placeholder": {
					"type": "plain_text",
					"text": "班のリストを入れる",
					"emoji": True
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "1月30日",
							"emoji": True
						},
						"value": "value_A5"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "2月2日",
							"emoji": True
						},
						"value": "value_B6"
					}
				]
			}
		}
	]
}
	
        
        
        
    )

# これから説明するサンプルコードはここに追加していってください
# modal画面を開くにはview.open()を呼び出す
# trigeer_idが必要





if __name__ == "__main__":
    # ソケットモードのコネクションを確立
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()