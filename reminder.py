#
# remainder.py
#

import pymysql, logging, os, schedule, time, pymysql
from slack_sdk import WebClient

remainder_id = []

# データベースに接続する
connection = pymysql.connect(
    host='10.146.221.105',
    user='slack_bot',
    password='P@ssw0rd',
    database='cac_project',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        cursor = connection.cursor()
        # 本日が掃除日であることを確認するsqlを実行
        sql_A = """
                SELECT cleaning_date
                FROM cleaning_date 
                WHERE cleaning_date = "2023-02-03";
                """
        cursor.execute(sql_A)
        cursor.fetchall()
        
        # 出欠連絡をしていない学生のSlack番号を抽出するsqlを実行
        sql_B = """
                SELECT u.slack_number
                FROM users u
                JOIN cleaning_teams_configuration ctc
                ON u.slack_number = ctc.slack_number
                JOIN cleaning_teams ct
                ON ctc.cleaning_teams_id = ct.cleaning_teams_id
                JOIN cleaning_date cd
                ON ct.cleaning_groups_id = cd.cleaning_groups_id
                WHERE cd.cleaning_date = "2023-02-03" 
                AND u.slack_number NOT IN (
                    SELECT slack_number
                    FROM cleaning_attendance_record
                    WHERE cleaning_date = "2023-02-03"
                );
                """
                # CURRENT_DAY()…sql内での日付を

        cursor.execute(sql_B)
        results = cursor.fetchall()
        for row in results:
            slack_number = row["slack_number"]
            remainder_id.append(slack_number)
    
    connection.commit()

except Exception as e:
    print('error:', e)
    connection.rollback()
finally:
    connection.close()

# Web API クライアントを初期化します
client = WebClient(os.environ["SLACK_BOT_TOKEN"])

# reminder()関数
def reminder():
    if len(remainder_id) != 0:
        for i in range(0, len(remainder_id)):
            slack_number = remainder_id[i]
            # chat.postMessage API を呼び出します
            response = client.chat_postMessage(
                channel="{}".format(slack_number),
                text=f"出欠連絡をお願いします。",
            )

# 指定時刻に関数reminder()を実行する
schedule.every().day.at('13:15').do(reminder)

# 無限ループ時に実行
while True:
    schedule.run_pending()
    time.sleep(1)
