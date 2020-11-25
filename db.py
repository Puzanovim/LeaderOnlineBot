import pymysql
import pymysql.cursors

from config import MYSQL_DB, MYSQL_USER, MYSQL_HOST, MYSQL_PWD


class Db:
    def __init__(self):
        self.conn = pymysql.connect(host=MYSQL_HOST,
                                    user=MYSQL_USER,
                                    password=MYSQL_PWD,
                                    db=MYSQL_DB,
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)

    def connect(self):
        pass

    def query(self, query, params=()):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
        except pymysql.OperationalError:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
        return cursor

    def add(self, user_id, name="", institute=""):
        sql = "INSERT INTO `leader_users` (`user_id`, `name`, `institute`) VALUES (%s, %s, %s)"
        self.request = self.query(sql, (user_id, name, institute))
        sql = "INSERT INTO `points_table` (`user_id`, `current_question`) VALUES (%s, %s)"
        self.request = self.query(sql, (user_id, 10))
        print("Db().add(): Created")

    def get_result(self, user_id):
        sql = "SELECT `result` FROM `points_table` WHERE `user_id`=%s"
        self.request = self.query(sql, user_id)
        self.result = self.request.fetchone()
        print("Db().get_result(): Done")

        return self.result

    def get_current_question(self, user_id):
        sql = "SELECT `current_question` FROM `points_table` WHERE `user_id`=%s"
        self.request = self.query(sql, user_id)
        self.result = self.request.fetchone()
        print("Db().get_current_question(): Done")

        return self.result

    def set_point(self, user_id, question):
        result = self.get_result(user_id)
        new_result = int(result['result']) + 1
        sql = "UPDATE `points_table` SET `%s`='1', `result`=%s WHERE `user_id`=%s"
        self.request = self.query(sql, (question, str(new_result), user_id))
        print("Db().set_point(): Done")

    def increment_current_question(self, user_id, current_question):
        new_question = int(current_question['current_question']) + 1
        sql = "UPDATE `points_table` SET `current_question`=%s WHERE `user_id`=%s"
        self.request = self.query(sql, (str(new_question), user_id))
        print("Db().increment_current_question(): Done")


def test():
    user = 8909
    db = Db()
    db.add(user, "Nowhere man", "simple")
    question = db.get_current_question(user)
    db.set_point(user, 5)
    db.increment_current_question(user, question)
    print(db.get_result(user))
