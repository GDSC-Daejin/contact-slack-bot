import datetime
import pymysql
import os

class DB:
    def __init__(self,host,username,password):
        self.host = host
        self.username = username
        self.password = password
    def get_database_connection(self,db):
        try:
            connection = pymysql.connect(host=self.host, user=self.username, password=self.password, db=db)
            return connection
        except pymysql.err.OperationalError as e:
            print("Failed to connect to the database:", e)
            raise Exception("Failed to connect to the database:", e)
    def get_api_key(self):
        api_key = {}
        connection = self.get_database_connection("token")
        with connection.cursor() as cursor:
            try:
                # Execute the SQL query
                cursor.execute("select * from api_key")
                res = cursor.fetchall()
                for a in res:
                    api_key[a[0]] = a[1]

            except Exception as e:
                pass

        # Commit the changes and close the connection
        connection.commit()
        connection.close()
        return api_key
    def get_info(self):
        data = {}
        connection = self.get_database_connection("slack")
        with connection.cursor() as cursor:
            try:
                # Execute the SQL query
                cursor.execute("SELECT Nickname, Real_Name, Phone FROM Members WHERE Phone IS NOT NULL;")
                res = cursor.fetchall()
                data = res
                
                json_data = [
                    {
                        "nickname": item[0],
                        "name": item[1],
                        "phone": item[2]
                    }
                    for item in data
                ]

            except Exception as e:
                pass

        # Commit the changes and close the connection
        connection.commit()
        connection.close()
        return json_data
    def insert_db_to_member(self,data):
        connection = self.get_database_connection("slack")
        today = datetime.date.today()
        # today = datetime.date.today() - datetime.timedelta(days=2)
        with connection.cursor() as cursor:
            try:
                    cursor.execute(
                        "delete from Members"
                        
                    )
                    # Execute the SQL query

            except Exception as e:
                    print(e)
                    pass
            for js in data:
                Display_name=js["Nickname"]
                Real_name=js["Real_Name"]
                isAdmin=js["Admin"]
                Phone=js["phone"]
                Slack_id=js["slack_id"]
                Team_id=js["team_id"]
                Avatar_hash=js["avatar_hash"]
                Profile_image=js["profile_image"]
                try:
                    cursor.execute(
                        "INSERT INTO Members (Nickname, Real_Name,isAdmin,Phone,Slack_Id,Team_Id,Avatar_Hash,Profile_Image) VALUES (%s, %s,%s,%s, %s,%s,%s, %s)",
                        (Display_name,Real_name,isAdmin,Phone,Slack_id,Team_id,Avatar_hash,Profile_image),
                    )
                    # Execute the SQL query

                except Exception as e:
                    print(e)
                    pass
             
        # Commit the changes and close the connection
        connection.commit()
        connection.close()