from flask import Flask, render_template, request
from db_connect import *
# из библиотеки импортируем класc
app = Flask(__name__)
# создаем приложение, которое равно конструктору класса Flask с именем приложения. name - директива,
# которая указывает на имя текущего файла

#бд подключена, закинул в отдельный файл db_connect, подключается пока к локалке
#Если бд мешает, заккоментируй 2ую строку



# декоратор вызывает ссылку (переход)
# для создания страницы объвляем функцию с названием страницы и возвращаем значение (ссылку на сайт)
@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", title="Авторизация")


@app.route("/lk")
def lk():
    return render_template("lk.html", title="Личный кабинет")


@app.route("/statistic")
def statistic():
    return render_template("statistic.html", title="Статистика")


@app.route("/video")
def video():
    return render_template("video.html", title="Видео")


@app.route("/anketa", methods = ['POST','GET'])
def anketa(): #данные с формы анкеты загружаются сюда и отправляются в бд
    if request.method == 'POST':
        cursor = connection.cursor()
        cursor.execute("INSERT INTO kyrsants (surname, name, middlename, birthday, phone_number, telegram, faculty,"
                       "course, platoon, male, photo, title, post, commander, card_number, sytki_pd, "
                       "sytki_kpp, sytki_patrol, days_of_sluzhba, days_of_sytki, sytki_on_weekends, sytki_on_holidays) "
                       "VALUES (" + "'" + request.form['surname'] + "'," +
                                    "'" + request.form['name'] + "'," +
                                    "'" + request.form['middlename'] + "'," +
                                    "'" + request.form['birthday'] + "'," +
                                    "'" + request.form['phone_number'] + "'," +
                                    "'" + request.form['telegram'] + "'," +
                                    "'" + request.form['faculty'] + "'," +
                                    "'" + request.form['course'] + "'," +
                                    "'" + request.form['platoon'] + "'," +
                                    "'" + request.form['male'] + "'," +
                                    "'" + request.form['photo'] + "'," +
                                    "'" + request.form['title'] + "'," +
                                    "'" + request.form['post'] + "'," +
                                    "'" + request.form['commander'] + "'," +
                                    "'" + request.form['card_number'] + "'," +
                                    "'" + request.form['sytki_pd'] + "'," +
                                    "'" + request.form['sytki_kpp'] + "'," +
                                    "'" + request.form['sytki_patrol'] + "'," +
                                    "'" + request.form['days_of_sluzhba'] + "'," +
                                    "'" + request.form['days_of_sytki'] + "'," +
                                    "'" + request.form['sytki_on_weekends'] + "'," +
                                    "'" + request.form['sytki_on_holidays'] + "'" +
                                ");")
        cursor.close()
    return render_template("anketa.html", title="Анкета")


@app.route("/create")
def create():
    return render_template("create.html", title="Расстановка")


@app.route("/iskl")
def iskl():
    return render_template("iskl.html", title="Исключения")


@app.route("/documents")
def documents():
    return render_template("documents.html", title="Документы")


if __name__ == '__main__':
# если текущее приложение/файл является основным и мы будем запускать только текущий файл/приложение,
# то вызываем метод run c возможностью автоматического перезапуска сервера для наблюдения изменений в реальном режиме времени.
    app.run(debug=True)


'''
@app.route('/user/<string:name>/<int:id>/<float:weight>')
def user(name, id, weight):
    return "Личный кабинет " + name + "-" + str(id) + "-" + str(weight)
'''
