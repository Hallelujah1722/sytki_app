from flask import Flask, render_template
# из библиотеки импортируем класс
#gut test1
app = Flask(__name__)
# создаем приложение, которое равно конструктору класса Flask с именем приложения. name - директива,
# которая указывает на имя текущего файла



# КАК ПОДКЛЮЧИТЬ ЭТУ БАЗУ!!!!!!!!!????????????



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


@app.route("/anketa")
def anketa():
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
