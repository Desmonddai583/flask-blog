import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import sqlalchemy

from flask_blog import app, db

from author.models import *
from blog.models import *


class UserTest(unittest.TestCase):
    def setUp(self):
        db_username = app.config["DB_USERNAME"]
        db_password = app.config["DB_PASSWORD"]
        db_host = app.config["DB_HOST"]
        self.db_uri = "mysql+pymysql://%s:%s@%s/" % (db_username, db_password, db_host)
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["BLOG_DATABASE_NAME"] = "test_blog"
        app.config["SQLALCHEMY_DATABASE_URI"] = self.db_uri + app.config["BLOG_DATABASE_NAME"]
        engine = sqlalchemy.create_engine(self.db_uri)
        conn = engine.connect()
        conn.execute("commit")
        conn.execute("CREATE DATABASE " + app.config["BLOG_DATABASE_NAME"])
        db.create_all()
        conn.close()
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        engine = sqlalchemy.create_engine(self.db_uri)
        conn = engine.connect()
        conn.execute("commit")
        conn.execute("DROP DATABASE " + app.config["BLOG_DATABASE_NAME"])
        conn.close()

    def create_blog(self):
        return self.app.post('/setup', data=dict(
            name="test blog1",
            fullname="desmond",
            email="desmond@123.com",
            username="desmond.dai",
            password="098567",
            confirm="098567"
            ), follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
            ), follow_redirects=True)

    def logout(self):
        return self.app.get('logout', follow_redirects=True)

    def test_create_blog(self):
        rv = self.create_blog()
        assert "Blog created" in str(rv.data)

    def test_login_logout(self):
        self.create_blog()
        rv = self.login("desmond.dai", "098567")
        assert "User desmond.dai logged in" in str(rv.data)
        rv = self.logout()
        assert "User logged out" in str(rv.data)
        rv = self.login("desmond.dai", "test")
        assert "Incorrect username and password" in str(rv.data)

if __name__ == "__main__":
    unittest.main()