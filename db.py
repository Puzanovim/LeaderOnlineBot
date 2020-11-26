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

    def count(self, user_id):
        sql = "SELECT COUNT(*) FROM `leader_users` WHERE `user_id`=%s"
        self.request = self.query(sql, user_id)
        self.result = self.request.fetchone()
        print("Db().count(): Counted")
        if self.result['COUNT(*)'] > 0:
            return True
        return False

    def create_user(self, user_id, name=""):
        exist = self.count(user_id)
        if not exist:
            sql = "INSERT INTO `leader_users` (`user_id`, `name`) VALUES (%s, %s)"
            self.request = self.query(sql, (user_id, name))
            sql = "INSERT INTO `points_table` (`user_id`, `current_question`) VALUES (%s, %s)"
            self.request = self.query(sql, (user_id, 0))
            print("Db().create_user(): Created")
        else:
            sql = "UPDATE `leader_users` SET `name`=%s WHERE `user_id`=%s"
            self.request = self.query(sql, (name, user_id))
            print("Db().create_user(): Updated")

    def add_institute(self, user_id, institute=""):
        exist = self.count(user_id)
        if exist:
            sql = "UPDATE `leader_users` SET `institute`=%s WHERE `user_id`=%s"
            self.request = self.query(sql, (institute, user_id))
            print("Db().add_institute(): Added")
        else:
            print("Db().add_institute(): User doesn't exist")

    def get_result(self, user_id):
        sql = "SELECT `result` FROM `points_table` WHERE `user_id`=%s"
        self.request = self.query(sql, user_id)
        self.result = self.request.fetchone()
        print("Db().get_result(): Done")

        return int(self.result['result'])

    def get_current_question(self, user_id: int) -> int:
        sql = "SELECT `current_question` FROM `points_table` WHERE `user_id`=%s"
        self.request = self.query(sql, user_id)
        self.result = self.request.fetchone()
        print("Db().get_current_question(): Done")

        return int(self.result['current_question'])

    def set_point(self, user_id: int, question: int):
        result = self.get_result(user_id)
        new_result = result + 1
        sql = "UPDATE `points_table` SET `%s`='1', `result`=%s WHERE `user_id`=%s"
        self.request = self.query(sql, (question, str(new_result), user_id))
        print("Db().set_point(): Done")

    def increment_current_question(self, user_id: int, current_question: int):
        new_question = current_question + 1
        sql = "UPDATE `points_table` SET `current_question`=%s WHERE `user_id`=%s"
        self.request = self.query(sql, (str(new_question), user_id))
        print("Db().increment_current_question(): Done")

    def have_hints(self, user_id):
        sql = "SELECT `count_of_hints` FROM `points_table` WHERE `user_id`=%s"
        self.request = self.query(sql, user_id)
        self.result = self.request.fetchone()
        print("Db().get_count_of_hints(): Done")

        if int(self.result['count_of_hints']) > 0:
            return True
        return False

    def set_hint(self, user_id):
        sql = "UPDATE `points_table` SET `count_of_hints`='1' WHERE `user_id`=%s"
        self.request = self.query(sql, user_id)
        print("Db().set_hint(): Done")

    def delete_hint(self, user_id):
        sql = "UPDATE `points_table` SET `count_of_hints`='0' WHERE `user_id`=%s"
        self.request = self.query(sql, user_id)
        print("Db().delete_hint(): Done")


def test():
    user = 8929
    db = Db()
    db.create_user(user, "Nowhere man")
    db.add_institute(user, "simple")
    question = db.get_current_question(user)
    db.set_point(user, 5)
    db.increment_current_question(user, question)
    print(db.get_result(user))
