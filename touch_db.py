import sqlite3
import random
# это я сам напишу ;)
db_file = "law_database.db"

class Touch:
    def __init__(self):
        self.db_file = db_file

    def connect(self):
        return sqlite3.connect(self.db_file)

    def fetch_all(self):
        pass

    def fetch_chapters(self, section):
        pass

    def fetch_articles(self, chapter):
        pass

    def fetch_article_content(self, article):
        pass

    def fetch_random(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Статья FROM laws")
            articles = cursor.fetchall()
            random_article = random.choice(articles)
            return random_article[0]

    def filter(self, keyword):
        pass
