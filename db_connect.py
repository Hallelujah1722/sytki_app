import psycopg2
from psycopg2 import Error #обработчик ошибок
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT





try:
    #Подключение к бд PostgeSQL(пока что на локальном сервере)
    connection = psycopg2.connect(user = "emir",
                                  dbname = "sytki",
                                  password = "password",
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

def LogDB(email):
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM vhod WHERE login ='"+email+"' LIMIT 1;")
    psw = cursor.fetchone()
    if not psw:
        print("Ошибка извлечения данных логина" + str(Error))
        return False
    else:
        password_db = psw[0]
        return password_db


