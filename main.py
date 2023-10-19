from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager,login_user, UserMixin, logout_user, login_required, current_user

from db_connect import *
# из библиотеки импортируем класc
app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"
# создаем приложение, которое равно конструктору класса Flask с именем приложения. name - директива,
# которая указывает на имя текущего файла

#бд подключена, закинул в отдельный файл db_connect, подключается пока к локалке
#Если бд мешает, заккоментируй 2ую строкe


login_manager = LoginManager(app)


class User(UserMixin):
    pass

@login_manager.user_loader  #проверяет авторизацию юзера при каждом запросе к серверу
def user_loader(email):
    if email == Session_log(email):
        user = User()
        user.id = email
        print(user.id,"LOGINMANAGER")
    return user


@app.route('/logout') #функция выхода и аккаунта, если юзер нажимает кнопку, пользователя направялет на страницу разлога и затем на страницу логина
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# декоратор вызывает ссылку (переход)
# для создания страницы объвляем функцию с названием страницы и возвращаем значение (ссылку на сайт)
@app.route('/', methods = ['POST','GET'] )
@app.route('/index', methods = ['POST','GET'])
def index():
    if current_user.is_authenticated: #если пользователь уже был авторизован, он не попадет на страницу логина, пока не выйдет из аккаунта
       return redirect(url_for('lk'))
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if password == LogDB(email): #logdb прописан в db_connect и ищет в бд пользователя по email, если нашел, то возвращает пароль и сравнивает
            user = User()
            user.id = email
            login_user(user)
            return redirect(url_for('lk')) #при успешном логине юзер направляется в кабинет
        else:
            print("ЛОГИН ИЛИ ПАРОЛЬ ВВЕДЕНЫ НЕВЕРНО!")
    return render_template("index.html", title="Авторизация")


@app.route("/lk")
@login_required
def lk():
    return render_template("lk.html", title="Личный кабинет")


@app.route("/statistic")
@login_required
def statistic():
    cur_user = current_user.id
    if Post_user(cur_user) == 'admin' or 'officer':
        print("Админ определен успешно")
        return render_template("statistic.html", title="Статистика")
    else:
        print("Вы не являетесь админом, P.S. можно привязать другие функции")
        return redirect(url_for('lk'))

@app.route("/video")
@login_required
def video():
    return render_template("video.html", title="Видео")


@app.route("/anketa", methods = ['POST','GET'])
@login_required
def anketa(): #данные с формы анкеты загружаются сюда и отправляются в бд
    if request.method == 'POST':
        cursor = connection.cursor()
        cursor.execute("INSERT INTO kyrsants (surname, name, middlename, birthday, phone_number, login_email, faculty,"
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
@login_required
def create():
    return render_template("create.html", title="Расстановка")


@app.route("/iskl")
@login_required
def iskl():
    return render_template("iskl.html", title="Исключения")


@app.route("/documents")
@login_required
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
