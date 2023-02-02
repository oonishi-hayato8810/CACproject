import os
import logging
from slack_bolt import App, Ack, Say, BoltContext, Respond
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient
from mysql_connection import query
import datetime
import ast

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))






@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        user=event["user"]
        sql = 'SELECT class_name FROM users INNER JOIN class ON users.class_id = class.class_id\
                where slack_number = "' + user + '"'
        result = query(sql)
        class_name = result[0].get('class_name')
        if class_name == "教員":
            try:
            # views.publish is the method that your app uses to push a view to the Home tab
                client.views_publish(
                # the user that opened your app's app home
                user_id=event["user"],
                # the view object that appears in the app home
                view={
                    "type": "home",
                    "callback_id": "home_view",

                    # body of the view
                    "blocks": [
                        
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "出欠確認"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "出欠確認を開く",
                            },
                            "value": "clicked",
                            "action_id": "open_select_group_button"
                        }
                    }
                    ]
                }
                )
            except Exception as e:
                logger.error(f"Error publishing home tab: {e}")
        elif class_name == "在校生":
            # ホーム画面の上部の基本情報の取得
            sql = 'select cleaning_teams_name, cleaning_groups_name, cleaning_location_name, name\
                    FROM cleaning_teams\
                    INNER JOIN cleaning_groups ON cleaning_groups.cleaning_groups_id = cleaning_teams.cleaning_groups_id\
                    INNER JOIN cleaning_period ON cleaning_period.cleaning_period_id = cleaning_groups.cleaning_period_id\
                    INNER JOIN cleaning_teams_configuration ON cleaning_teams_configuration.cleaning_teams_id = cleaning_teams.cleaning_teams_id\
                    INNER JOIN users ON cleaning_teams_configuration.slack_number = users.slack_number\
                    INNER JOIN cleaning_location ON cleaning_location.cleaning_location_id = cleaning_teams.cleaning_location_id\
                    where cleaning_period_start <= CURRENT_DATE() AND CURRENT_DATE() <= cleaning_period_end AND users.slack_number = "' + user +'";'
            result = query(sql)
            user_info = result[0].get("name", {})+"さんは"+result[0].get("cleaning_teams_name", {})+"班です。\n掃除場所："+result[0].get("cleaning_location_name", {})+"\n担当曜日："+result[0].get("cleaning_groups_name",{})
            # 掃除日の取得
            sql = "select cleaning_date.cleaning_date\
            from cleaning_date\
            inner join cleaning_groups on cleaning_date.cleaning_groups_id = cleaning_groups.cleaning_groups_id\
            inner join cleaning_teams on cleaning_groups.cleaning_groups_id = cleaning_teams.cleaning_groups_id\
            inner join cleaning_teams_configuration on cleaning_teams.cleaning_teams_id = cleaning_teams_configuration.cleaning_teams_id\
            where cleaning_date.cleaning_date >= CURRENT_DATE()\
            and cleaning_teams_configuration.slack_number = '" + user + "'\
            ;"
            db_cleaning_date = query(sql)
            view_cleaning_date = []
 

    
            for i in db_cleaning_date:
                date = i.get("cleaning_date").strftime("%Y-%m-%d")
                view_cleaning_date.append({"text": {"type": "plain_text","text":date ,},"value": date})
            
            
            blocks = [{
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": user_info
                                    },
                        },
                        {
                        "type": "divider"
                        },
                        {
                        "type": "section",
                        "block_id": "cleaning_date",
                        "text": {
                            "type": "mrkdwn",
                            "text": "出欠確認：掃除日を選択してください"
                            },
                        "accessory": {
                            "type": "static_select",
                            "action_id": "static_select-action",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "掃除日を選ぶ",
                            },
                            "options": view_cleaning_date,
                        },
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "出欠連絡"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "出欠連絡を開く",
                            },
                            "value": "clicked",
                            "action_id": "attendance_contact_button"
                        }
                    }]
            client.views_publish(
                # the user that opened your app's app home
                user_id=event["user"],
                # the view object that appears in the app home
                view={
                    "type": "home",
                    "callback_id": "home_view",
                    # body of the view
                    "blocks": blocks
                }
                )
        else:
            client.views_publish(
            user_id=event["user"],
            view={
                    "type": "home",
                    "callback_id": "home_view",
                    "blocks": 		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "*あなたは登録されていません。管理者に相談してください。*",
			}
            }
            }
            )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


# action_id にマッチング（block_id ではないので注意）
@app.action("open_select_group_button")
def open_select_group_button_clicks(ack: Ack, body: dict, client: WebClient):
    # 受信した旨を 3 秒以内に Slack サーバーに伝えます
    ack()
    sql = "select cleaning_date from cleaning_date\
            where cleaning_date >= DATE_ADD(CURRENT_DATE(), INTERVAL -1 MONTH) and cleaning_date <= CURRENT_DATE()"
    result, options = query(sql), []
    for i in result:
        options.append({"text": {"type":"plain_text", "text":i.get("cleaning_date").strftime("%Y-%m-%d")}, "value":i.get("cleaning_date").strftime("%Y-%m-%d")})
    # views.open という API を呼び出すことでモーダルを開きます
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
	"type": "modal",
    "callback_id": "open_select_group",
    "submit": {"type": "plain_text", "text": "送信"},
	"close": {
		"type": "plain_text",
		"text": "戻る",
	},
	"title": {
		"type": "plain_text",
		"text": "班選択画面",
	},
	"blocks": [
		{
			"type": "divider"
		},
        {
			"type": "input",
            "block_id": "cleaning_date",  
			"label": {
				"type": "plain_text",
				"text": "掃除日を選択してください"
			},
			"element": {
				"type": "static_select",
                "action_id": "select_date",
				"placeholder": {
					"type": "plain_text",
					"text": "掃除日を選ぶ",
				},
				"options": options,
            },
        },]
        }
    )

@app.view("open_select_group")
def select_date(ack: Ack, body: dict, client: WebClient, view: dict):
    inputs = view["state"]["values"]
    
    select_cleaning_date =inputs.get("cleaning_date", {}).get("select_date").get("selected_option").get("value")
    
    sql = "select cleaning_teams_name\
            from cleaning_teams\
            inner join cleaning_groups on cleaning_teams.cleaning_groups_id = cleaning_groups.cleaning_groups_id\
            inner join cleaning_date on cleaning_groups.cleaning_groups_id = cleaning_date.cleaning_groups_id\
            where cleaning_date = '" + select_cleaning_date + "';"
    result, options = query(sql), []
    for i in result:
        options.append({"text": {"type":"plain_text", "text":i.get("cleaning_teams_name")+"班"}, "value":i.get("cleaning_teams_name")})
    ack(
        response_action="push",
        view={
		"type": "modal",
        "callback_id": "open_select_group_update",
        "submit": {"type": "plain_text", "text": "送信"},
        "private_metadata": "{'cleaning_date':'" + select_cleaning_date + "'}",
		"close": {
			"type": "plain_text",
			"text": "戻る",
		},
		"title": {
			"type": "plain_text",
			"text": "班選択画面出席確認表",
		},
		"blocks": [
            {
			"type": "divider"
            },
            {
				"type": "section",
				"text": {
					"type": "plain_text",
					"text": "掃除日："+select_cleaning_date,
				}
			},
            {
			"type": "input",
            "block_id": "cleaning_groups",
			"label": {
				"type": "plain_text",
				"text": "掃除班を選んでください"
			},
			"element": {
				"type": "static_select",
                "action_id": "select_date",
				"placeholder": {
					"type": "plain_text",
					"text": "掃除班を選ぶ",
				},
				"options": options,
            },
        },],
        }
    )
@app.view("open_select_group_update")
def open_select_group_update_click(ack: Ack, body: dict, client: WebClient, view: dict):
    inputs = view["state"]["values"]
    cleaning_date = ast.literal_eval(view["private_metadata"]).get("cleaning_date")
    strcleaning_date = datetime.datetime.strptime(cleaning_date,'%Y-%m-%d')
    cleaning_teams_name = inputs.get("cleaning_groups").get("select_date").get("selected_option").get("value")
    sql = 'SELECT users.name, users.department, users.school_year, hoge.attendance, hoge.nonparticipation_reason, cleaning_location_name, cleaning_groups_name\
            FROM users\
            JOIN cleaning_teams_configuration ON users.slack_number = cleaning_teams_configuration.slack_number\
            JOIN cleaning_teams ON cleaning_teams_configuration.cleaning_teams_id = cleaning_teams.cleaning_teams_id\
            JOIN cleaning_location ON cleaning_teams.cleaning_location_id = cleaning_location.cleaning_location_id\
            JOIN cleaning_groups ON cleaning_teams.cleaning_groups_id = cleaning_groups.cleaning_groups_id\
            LEFT JOIN (select * from cleaning_attendance_record where cleaning_date = "' + cleaning_date +'") hoge ON users.slack_number = hoge.slack_number\
            where cleaning_teams_name = "' + cleaning_teams_name + '";'
    result = query(sql)
    

    blocks = [{
				"type": "section",
				"text": {
					"type": "plain_text",
					"text": str(strcleaning_date.strftime("%Y年%m月%d日")),
				}
			},
			{
				"type": "section",
				"text": {
					"type": "plain_text",
					"text": cleaning_teams_name,
				}
			},
			{
				"type": "section",
				"text": {
					"type": "plain_text",
					"text": "掃除場所：" + result[0].get("cleaning_location_name"),
				}
			},
			{
				"type": "section",
				"text": {
					"type": "plain_text",
					"text": "担当曜日：" + result[0].get("cleaning_groups_name"),
				}
			},
			{
				"type": "divider"
			},
            ]
    for i in result:
        name, department, school_year, attendance, nonparticipation_reason = i.get("name"),i.get("department"), i.get("school_year"),  i.get("attendance"), i.get("nonparticipation_reason")
        if attendance is None:
            attendance = 'まだ連絡がありません'
        if nonparticipation_reason is None:
            nonparticipation_reason = ''
        blocks.append({"type": "section","text": {"type": "plain_text","text":department+str(school_year)+"年"+name+ "\n"+attendance+"\n"+nonparticipation_reason}})
        blocks.append({"type": "divider"})
    
    ack(
        response_action="push",
        view={
		"type": "modal",
		"close": {
			"type": "plain_text",
			"text": "戻る",
		},
		"title": {
			"type": "plain_text",
			"text": "出席確認表",
		},
		"blocks": blocks
        }
	)


@app.action("static_select-action")
def handle_open_modal_button_clicks(ack: Ack, body:dict, client: WebClient, view: dict):
    # 受信した旨を 3 秒以内に Slack サーバーに伝えます
    ack()
    cleaning_date = body.get("actions", {})[0].get("selected_option", {}).get("value", {})
    strcleaning_date =datetime.datetime.strptime(cleaning_date,'%Y-%m-%d')
    user = body["user"]["id"]
    # views.open という API を呼び出すことでモーダルを開きます


    sql = "select cleaning_teams_name\
            from cleaning_teams\
            JOIN cleaning_teams_configuration ON cleaning_teams.cleaning_teams_id = cleaning_teams_configuration.cleaning_teams_id\
            JOIN cleaning_groups ON cleaning_teams.cleaning_groups_id = cleaning_groups.cleaning_groups_id\
            JOIN cleaning_period ON cleaning_groups.cleaning_period_id = cleaning_period.cleaning_period_id\
            where slack_number = '"+user+"' AND cleaning_period_start <= '"+cleaning_date+"' AND cleaning_period_end >= '"+cleaning_date+"';"

    result = query(sql)

    cleaning_teams_name = result[0].get("cleaning_teams_name", {})

    sql = 'SELECT users.name, users.department, users.school_year, hoge.attendance, hoge.nonparticipation_reason, cleaning_location_name, cleaning_groups_name\
            FROM users\
            JOIN cleaning_teams_configuration ON users.slack_number = cleaning_teams_configuration.slack_number\
            JOIN cleaning_teams ON cleaning_teams_configuration.cleaning_teams_id = cleaning_teams.cleaning_teams_id\
            JOIN cleaning_location ON cleaning_teams.cleaning_location_id = cleaning_location.cleaning_location_id\
            JOIN cleaning_groups ON cleaning_teams.cleaning_groups_id = cleaning_groups.cleaning_groups_id\
            LEFT JOIN (select * from cleaning_attendance_record where cleaning_date = "' + cleaning_date +'") hoge ON users.slack_number = hoge.slack_number\
            where cleaning_teams_name = "' + cleaning_teams_name + '";'
    result = query(sql)
    

    blocks = [{
				"type": "section",
				"text": {
					"type": "plain_text",
					"text": str(strcleaning_date.strftime("%Y年%m月%d日")),
				}
			},
			{
				"type": "section",
				"text": {
					"type": "plain_text",
					"text": cleaning_teams_name,
				}
			},
			{
				"type": "section",
				"text": {
					"type": "plain_text",
					"text": "掃除場所：" + result[0].get("cleaning_location_name"),
				}
			},
			{
				"type": "section",
				"text": {
					"type": "plain_text",
					"text": "担当曜日：" + result[0].get("cleaning_groups_name"),
				}
			},
			{
				"type": "divider"
			},
            ]
    for i in result:
        name, department, school_year, attendance, nonparticipation_reason = i.get("name"),i.get("department"), i.get("school_year"),  i.get("attendance"), i.get("nonparticipation_reason")
        if attendance is None:
            attendance = 'まだ連絡がありません'
        if nonparticipation_reason is None:
            nonparticipation_reason = ''
        blocks.append({"type": "section","text": {"type": "plain_text","text":department+str(school_year)+"年"+name+ "\n"+attendance+"\n"+nonparticipation_reason}})
        blocks.append({"type": "divider"})
    
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
		"type": "modal",
		"close": {
			"type": "plain_text",
			"text": "戻る",
		},
		"title": {
			"type": "plain_text",
			"text": "出席確認表",
		},
		"blocks": blocks
        }
	)


@app.action("attendance_contact_button")
def attendance_contact_button_clicks(ack: Ack, body: dict, client: WebClient):
    # 受信した旨を 3 秒以内に Slack サーバーに伝えます
    ack()
    user = body["user"]["id"]
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    sql = "select cleaning_date.cleaning_date\
            from cleaning_date\
            inner join cleaning_groups on cleaning_date.cleaning_groups_id = cleaning_groups.cleaning_groups_id\
            inner join cleaning_teams on cleaning_groups.cleaning_groups_id = cleaning_teams.cleaning_groups_id\
            inner join cleaning_teams_configuration on cleaning_teams.cleaning_teams_id = cleaning_teams_configuration.cleaning_teams_id\
            where cleaning_date.cleaning_date >= CURRENT_DATE()\
            and cleaning_teams_configuration.slack_number = '" + user + "'\
            ;"
    db_cleaning_date = query(sql)

    view_cleaning_date = []

    
    for i in db_cleaning_date:
        date = i.get("cleaning_date").strftime("%Y-%m-%d")
        view_cleaning_date.append({"text": {"type": "plain_text","text":date ,},"value": date})

    view_blocks = [{"type": "section", "text": {"type": "mrkdwn","text": "合同環境整備への出欠連絡をお願いします。"}},
            {"type": "divider"},
            {"type": "input", "block_id": "cleaning_date", 
            "element": {"type": "static_select","action_id": "static_select-action",
				"placeholder": {"type": "plain_text","text": "掃除日を選択してください"},
				"options": view_cleaning_date},
			"label": {
				"type": "plain_text",
				"text": "出欠連絡：掃除日を選択してください"}
            },

        {"type": "input","block_id": "attendance",
		"element": {"type": "radio_buttons","action_id":"element","options": [
			{"text": {"type": "plain_text","text": "参加する"},"value": "参加"},
			{"text": {"type": "plain_text","text": "参加できない"},"value": "不参加"}]},
			"label": {"type": "plain_text","text": "連絡項目"}},]

    # views.open という API を呼び出すことでモーダルを開きます
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "attendance_contact",
            "title": {"type": "plain_text", "text": "出欠連絡"},
            "submit": {"type": "plain_text", "text": "送信"},
            "close": {"type": "plain_text", "text": "戻る"},
            "blocks": view_blocks
        }
    )



@app.view("attendance_contact")
def attendance_contact_clicks(ack: Ack, body, view: dict, logger: logging.Logger):
    inputs = view["state"]["values"]
    
    user = body["user"]["id"]
    attendance = inputs.get("attendance", {}).get("element", {}).get("selected_option", {}).get("value", {})
    cleaning_date = inputs.get("cleaning_date", {}).get("static_select-action", {}).get("selected_option", {}).get("value", {})
    sql = 'select * from cleaning_attendance_record where slack_number="' + user + '" and cleaning_date="' + cleaning_date + '";'
    result = query(sql)
    if result is None or result == ():
        data_flug = 'True'
    else:
        data_flug = 'False'
    if attendance == '参加':
        ack()
        if data_flug == 'True':
            sql = "insert into cleaning_attendance_record(cleaning_date, slack_number, attendance)\
                values ('" + cleaning_date + "', '" + user + "', '" + attendance +"')"

        else:
            sql = "update cleaning_attendance_record set slack_number='" + user + "', cleaning_date='" + cleaning_date + "', attendance='" + attendance +"', nonparticipation_reason=NULL\
                    where slack_number='" + user + "' and cleaning_date='" + cleaning_date + "';"
        result = query(sql)
        print(body)
        
    else:
        attendance_info = '{"attendance":"' + attendance + '", "cleaning_date":"' + cleaning_date + '", "data_flug":"' + data_flug +'"}'
        ack(
			response_action="update",
            view={
				"type": "modal",
            "callback_id": "nonparticipation_contact",
            "title": {"type": "plain_text", "text": "出欠連絡"},
            "submit": {"type": "plain_text", "text": "送信"},
            "close": {"type": "plain_text", "text": "戻る"},
            "private_metadata": attendance_info,
            "blocks": [
			{
			"type": "input",
            "block_id": "attendance",
			"element": {
				"type": "radio_buttons",
                "action_id":"element",
                
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "就職活動"
						},
						"value": "就職活動"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "体調不良"
						},
						"value": "体調不良"
					},
                    {
						"text": {
							"type": "plain_text",
							"text": "その他"
						},
						"value": "その他"
					},
				]
			},
			"label": {
				"type": "plain_text",
				"text": "不参加理由"
			},
            "hint": {
                "type": "plain_text", 
                "text": "参加できない場合参加できない理由を選択する"
            },
			},
            {
			"type": "input",
            "block_id": "nonparticipation",
            "optional": True,
        
			"element": {
				"type": "plain_text_input",
                "action_id":"element"
			},
			"label": {
				"type": "plain_text",
				"text": "その他",
			},
            "hint": {
                "type": "plain_text", 
                "text": "不参加理由がその他の場合、記入する"
                },
			}
			]
		}
		)
    
    
    




@app.view("nonparticipation_contact")
def nonparticipation_contact_clicks(ack: Ack, body, view: dict, logger: logging.Logger):
    try:
        attendace_info = view['private_metadata']
        attendace_info = ast.literal_eval(attendace_info)
        user, attendance, cleaning_date = body["user"]["id"], attendace_info.get("attendance", {}), attendace_info.get("cleaning_date", {})
        inputs = view["state"]["values"]
        nonparticipation_reason = inputs.get("attendance", {}).get("element", {}).get("selected_option", {}).get("value", {})
        if nonparticipation_reason == "その他" and inputs.get("nonparticipation", {}).get("element", {}).get("value", {}) is None:
            #ack(response_action="errors", errors={"question-block": "不参加理由をその他にしている場合はその他欄に不参加理由の記入をしてください"})
            #return
            pass
        ack()
        if inputs.get("nonparticipation", {}).get("element", {}).get("value", {}) is not None :
            nonparticipation_reason += " " + inputs.get("nonparticipation", {}).get("element", {}).get("value", {})
        if attendace_info.get("data_flug") == 'True':
            sql = "insert into cleaning_attendance_record(cleaning_date, slack_number, attendance, nonparticipation_reason) values ('" + cleaning_date + "', '" + user + "', '" + attendance +"', '" + nonparticipation_reason + "')"
        else:
            sql = "update cleaning_attendance_record set slack_number='" + user + "',cleaning_date='" + cleaning_date + "', attendance=\
                '" + attendance +"', nonparticipation_reason='" + nonparticipation_reason + "'where slack_number='" + user + "' and cleaning_date='" + cleaning_date + "';"
        result = query(sql)
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
            
            
# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()


