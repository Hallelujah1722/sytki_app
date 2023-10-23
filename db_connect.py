import psycopg2
from psycopg2 import Error #обработчик ошибок
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT



try:
    #Подключение к бд PostgeSQL(пока что на локальном сервере)
    connection = psycopg2.connect(user = "postgres",
                                  dbname = "sytki",
                                  password = "mash78",
                                  host = "127.0.0.1",
                                  port = "5432")

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) #кажется это автосохранение измененный данных)
    #создаю курсор
    cursor = connection.cursor()
    print("Подключение к PostgreSQL")
    print(connection.get_dsn_parameters(), "\n")
    print("Вы подключены к - PostgreSQL 16.0 ", "\n")
    #cursor.execute("SELECT datname FROM pg_database;")
    #cursor.execute("SELECT * FROM kyrsants;")
    #print(cursor.fetchall())

except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error) #вывод ошибок
finally:
    if connection:
        cursor.close()
        #connection.close()
        #print("Соединение с PostgreSQL закрыто")

def LogDB(email):  #функция поиска пароля в бд по email
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM vhod WHERE login ='"+email+"' LIMIT 1;")
    psw = cursor.fetchone()
    if not psw:
        print("Ошибка извлечения Пароля")
        return False
    else:
        password_db = psw[0]
        return password_db


def Session_log(email): #функция проверки наличия логина в бд
    cursor = connection.cursor()
    cursor.execute("SELECT login FROM vhod WHERE login ='" + email + "' LIMIT 1;")
    log = cursor.fetchone()
    if not log:
        print("Проверка сессии провалилась")
        return False
    else:
        print("Проверка сессии прошла успешно")
        logging = log[0]
        return logging

def Post_user(cur_user): #функция извлечения из бд Статуса пользователя
    cursor = connection.cursor()
    cursor.execute("SELECT post FROM kyrsants WHERE login_email ='" + cur_user + "' LIMIT 1;")
    post = cursor.fetchone()
    if not post:
        print("Ошибка извлечения данных Статуса пользователя")
        return False
    else:
        print("Проверка Статуса прошла успешно")
        post_db = post[0]
        return post_db