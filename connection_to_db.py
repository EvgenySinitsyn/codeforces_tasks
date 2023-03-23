import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import maskpass


class Database:
    def __init__(self):
        try:
            file = open('pass.txt', 'rb')
            self.password = file.readline().decode()
            file.close()
        except:
            file = open('pass.txt', 'wb')
            self.password = maskpass.askpass('Введите пароль БД: ', mask='*')
            to_save = input('Сохранить пароль? (Д/Н): ').lower()
            if to_save in 'дy':
                file.write(self.password.encode())
                file.close()
            else:
                file.close()

    def set_db(self):
        try:
            self.connection = psycopg2.connect(user="postgres",
                                               password=self.password,
                                               host="localhost",
                                               port="5432")
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor()
            sql_create_database = 'create database codeforces_tasks'
            self.cursor.execute(sql_create_database)
            print('Успешно')
        except Exception as ex:
            pass
        finally:
            self.close_connection()

        try:
            self.connection = psycopg2.connect(user="postgres",
                                               password=self.password,
                                               host="localhost",
                                               port="5432",
                                               database="codeforces_tasks")

            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor()
            sql_create_category_table = "CREATE table category (id SERIAL PRIMARY KEY, name VARCHAR)"
            sql_create_task_table = """
            CREATE TABLE task (
            id SERIAL PRIMARY KEY,
            number VARCHAR(30),
            title VARCHAR(256),
            link VARCHAR(128),
            difficulty INTEGER,
            solved_quantity INTEGER,
            is_in_contest BOOLEAN DEFAULT FALSE
            )"""
            sql_create_task_category_table = """
            CREATE TABLE task_category
            (
            id SERIAL PRIMARY KEY,
            task_id INTEGER NOT NULL REFERENCES task,
            category_id   INTEGER NOT NULL REFERENCES category,
            UNIQUE (task_id, category_id)
            );
            """
            self.cursor.execute(sql_create_category_table)
            self.cursor.execute(sql_create_task_table)
            self.cursor.execute(sql_create_task_category_table)
        except Exception as ex:
            pass
        finally:
            self.close_connection()

    def connect_to_db(self):

        try:
            self.connection = psycopg2.connect(user="postgres",
                                               password=self.password,
                                               host="127.0.0.1",
                                               port="5432",
                                               database="codeforces_tasks")

            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor()

        except (Exception, Error) as error:
            print("Необходимые таблицы уже существуют")

        self.cursor.execute(f"SELECT number FROM task")
        self.existing_tasks = [number[0] for number in self.cursor.fetchall()]

    def close_connection(self):
        if self.connection:
            self.connection.close()
