import pymysql.cursors

def query(sql):
    connection = pymysql.connect(
            host = '10.146.221.105',
            user = 'slack_bot',
            password = 'P@ssw0rd',
            database = 'cac_project',
            charset = 'utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            connection.commit()
        return result

    except Exception as e:
        print('error:', e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


