import random

from db_connect import Database


def kpp_patrol(kyrsant):
    """
    Функция подсчёта разницы между суточными нарядами в кпп и патруле
    :param kyrsant:
    :return:
    """
    return kyrsant[6] - kyrsant[7]  # Сутки кпп - патруль


def rating(kyrsant):
    """
    Функция подсчёта рейтинга
    :param kyrsant:
    :return:
    """
    return kyrsant[9] + kyrsant[10] + kyrsant[11]


def get_day_of_sytki(kyrsant):
    return kyrsant[9]


def get_day_of_holydays(kyrsant):
    return kyrsant[10]


def get_day_of_weekends(kyrsant):
    return kyrsant[11]


def pool_sort(pool, key):
    """
    Функция сортировки курсантов по количеству суток (праздничных/выходных/будних) и рейтингу
    :param pool:
    :param key:
    :return:
    """
    days_of_sytki = {}
    s = set()
    for kyrsant in pool:
        days_of_sytki[key(kyrsant)].append(kyrsant)
        s.add(9)
    for group in days_of_sytki.values():
        group.sort(key=rating)
    result = list()
    for i in s:
        result += days_of_sytki[i]
    return result


def del_exceptions(pool: list, exceptions: list):
    """
    Функция удаляет курсантов, которые не могут заступить в данный день, из списка курсантов на этот день.
    :param pool:
    :param exceptions:
    :return:
    """
    for item in pool:
        if item[0] in exceptions:
            pool.remove(item)


def split_by_course(pool):
    """
    Функция разбиения курсантов на курсы
    :param pool:
    :return:
    """
    courses = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: []
    }
    for kyrsant in pool:
        courses[kyrsant[2]].append(kyrsant)
    return courses


class Rasstanovka:
    def __init__(self, database: Database):
        self.db = database

    def run(self, days):
        """
        Функция осуществляет расстановку суточного наряда (с/н), исходя из статистики курсантов.
        На вход в функцию приходит список содержащий в себе дату наряда, количество человек от каждого курса,
        тип дня (будний, выходной или праздничный), кто заступает (М/Ж), номер курса, от которого заступает
        помощник дежурного.
        В ходе работы алгоритма сгенерированные наряды добавляются в базу данных.
        Последовательность генерации:
        1) С/н помощников дежурного в праздничные дни
        2) С/н помощников дежурного в выходные дни
        3) С/н помощников дежурного в будние дни
        4) С/н курсантов в праздничные дни
        5) С/н курсантов в выходные дни
        6) С/н курсантов в будние дни

        Сначала в с/н расставляются помощники дежурного, потом в эти же с/н расставляются смены кпп и патруля

        List[(date, 1k, 2k, 3k, 4k, 5k, day_of_week, gender, pd_course_number)]
        :param days: List[(date, int, int, int, int, int, str, str, int)]
        """
        exceptions = {}
        # {date: List[int]}  словарь, где ключ - день,
        # а значение - идентификаторов (id) курсантов, которые не могут заступать в данный день

        final = {day[0]: [] for day in days}
        # {date: List[int]}  словарь, где ключ - день,
        # а значение - 9 идентификаторов (id) курсантов, которые не могут заступать в данный день

        kyrsants = self.db.get_kyrsants()
        girls = [kyrsant for kyrsant in kyrsants if kyrsant[1].upper() == 'Ж' and kyrsant[3] == 'нет']
        boys = [kyrsant for kyrsant in kyrsants if kyrsant[1].upper() == 'М' and kyrsant[3] == 'нет']
        pds = [kyrsant for kyrsant in kyrsants if kyrsant[3] == 'да']

        boys_holydays = pool_sort(pds, key=get_day_of_holydays)
        boys_weekends = pool_sort(pds, key=get_day_of_weekends)
        girls_holydays = pool_sort(pds, key=get_day_of_holydays)
        girls_weekends = pool_sort(pds, key=get_day_of_weekends)

        pds_pool = pool_sort(pds, key=get_day_of_sytki)
        pds_pool_dict = split_by_course(pds_pool)

        pds_holydays = pool_sort(pds, key=get_day_of_holydays)
        pds_holydays_dict = split_by_course(pds_holydays)

        pds_weekends = pool_sort(pds, key=get_day_of_weekends)
        pds_weekends_dict = split_by_course(pds_weekends)

        workdays = []
        weekends = []
        holydays = []
        for day in days:
            if day[6] == 'Будний день':
                workdays.append(day)
            elif day[6] == 'Выходной день':
                weekends.append(day)
            elif day[6] == 'Праздничный день':
                holydays.append(day)

        for day in holydays:
            pool = pds_holydays_dict[day[8]]    # Выбираем необходимый курс. На вход идёт номер курса.
            for i in range(len(pool)):
                if pool[i][0] not in exceptions[day[0]]:
                    # Если кандидат подходит (не находится в исключениях на этот день), то назначаем его и добавляем в
                    # итоговую выборку на этот день. Заступивший из списка на месяц удаляется (в это месяце в праздник
                    # больше не идёт).
                    # Иначе: выходим из итерации и выбираем следующего кандидата.
                    pd = pool.pop(i)
                    pds_weekends_dict[day[8]].remove(pd)
                    pds_pool_dict[day[8]].remove(pd)
                    pds_pool_dict[day[8]].append(pd)
                    exceptions[day[0] - 2].append(pd[0])
                    exceptions[day[0] - 1].append(pd[0])
                    exceptions[day[0] + 1].append(pd[0])
                    exceptions[day[0] + 2].append(pd[0])
                    final[day[0]].append(pd[0])
                    break

        for day in weekends:
            pool = pds_weekends_dict[day[8]]    # Выбираем необходимый курс
            for i in range(len(pool)):
                if pool[i][0] not in exceptions[day[0]]:
                    # Если кандидат подходит (не находится в исключениях на этот день), то назначаем его и добавляем в
                    # итоговую выборку на этот день. Заступивший переносится в конец списка
                    # Иначе: выходим из итерации и выбираем следующего кандидата.
                    pd = pool.pop(i)
                    pds_weekends_dict[day[8]].remove(pd)
                    pds_pool_dict[day[8]].remove(pd)
                    pds_pool_dict[day[8]].append(pd)
                    exceptions[day[0] - 2].append(pd[0])
                    exceptions[day[0] - 1].append(pd[0])
                    exceptions[day[0] + 1].append(pd[0])
                    exceptions[day[0] + 2].append(pd[0])
                    final[day[0]].append(pd[0])
                    break

        for day in workdays:
            pool = pds_pool_dict[day[8]]    # Выбираем необходимый курс
            for i in range(len(pool)):
                if pool[i][0] not in exceptions[day[0]]:
                    # Если кандидат подходит (не находится в исключениях на этот день), то назначаем его и добавляем в
                    # итоговую выборку на этот день. Заступивший переносится в конец списка
                    # Иначе: выходим из итерации и выбираем следующего кандидата.
                    pd = pool.pop(i)
                    pds_weekends_dict[day[8]].remove(pd)
                    pds_pool_dict[day[8]].remove(pd)
                    pds_pool_dict[day[8]].append(pd)
                    exceptions[day[0] - 2].append(pd[0])
                    exceptions[day[0] - 1].append(pd[0])
                    exceptions[day[0] + 1].append(pd[0])
                    exceptions[day[0] + 2].append(pd[0])
                    final[day[0]].append(pd[0])
                    break

        # Последующие три цикла почти полностью идентичны, поэтому в описание работы п
        for day in holydays:
            pool = boys_holydays if day[7].upper() == 'М' else girls_holydays
            pool_weekends = boys_weekends if day[7].upper() == 'М' else girls_weekends
            pool_workdays = boys if day[7].upper() == 'М' else girls
            cards = []  # Номера карточек заместителя в наряде
            kpp = []
            patrol = []

            # Шаблон для подсчёта распределения нагрузки на курсы
            nagruzka = {
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0
            }
            for kyrsant in pool:
                if kyrsant[0] in exceptions[day[0]]:  # Проверка: есть ли человек в исключениях?
                    continue
                if len(kpp) == 4 and len(patrol) == 4:  # Проверка: набрана ли смена?
                    break
                if nagruzka[kyrsant[2]] < day[kyrsant[2]]:  # Проверка: набраны ли курсанты из этого курса?
                    if kyrsant[4] not in cards:             # Проверка: есть ли совпадения по карточкам заместителя?
                        kp = kpp_patrol(kyrsant)
                        if kp > 2 and len(kpp) < 4:
                            # Если суток в кпп на 3 больше чем в патруле, то курсант определяется в патруль
                            patrol.append(kyrsant)
                            cards.append(kyrsant[4])
                            nagruzka[kyrsant[2]] += 1
                        elif kp < -2 and len(patrol) < 4:
                            # Если суток в патруле на 3 больше чем в кпп, то курсант определяется в патруль
                            kpp.append(kyrsant)
                            cards.append(kyrsant[4])
                            nagruzka[kyrsant[2]] += 1
                        elif kp > 2 and len(kpp) == 4 or kp < -2 and len(patrol) == 4:  # Если кпп/набраны
                            continue
                        else:
                            if len(kpp) == 4:       # Если кпп набран, то идёт в патруль
                                post = patrol
                            elif len(patrol) == 4:  # Если патруль набран, то идёт в кпп
                                post = kpp
                            else:                   # Если не набраны, то выбирается случайно
                                post = random.choice([kpp, patrol])
                            post.append(kyrsant[0])         # Добавляем на выбранный пост курсанта
                            cards.append(kyrsant[4])        # Записываем его номер карточки в общий список
                            nagruzka[kyrsant[2]] += 1       # Добавляем запись в учёт нагрузки
            smena = []
            for kyrsant in kpp:
                pool.remove(kyrsant)                    # Удаляем курсанта из суток в праздники в этом месяце
                pool_weekends.remove(kyrsant)           # Удаляем из списка на месяц на выходные и добавляем в его конец
                pool_weekends.append(kyrsant)
                pool_workdays.remove(kyrsant)           # Удаляем из списка на месяц на будни и добавляем в его конец
                pool_workdays.append(kyrsant)
                exceptions[day[0] - 2].append(kyrsant[0])       # Добавляем курсанта в исключения на соседние 2 дня
                exceptions[day[0] - 1].append(kyrsant[0])
                exceptions[day[0] + 1].append(kyrsant[0])
                exceptions[day[0] + 2].append(kyrsant[0])
                kyrsant[6] += 1     # Добавляем в статистику 1 сутки в кпп
                kyrsant[9] += 1     # Добавляем в общий зачёт 1 сутки
                kyrsant[11] += 1    # Добавляем в статистику 1 сутки в праздники
                smena.append(kyrsant[0])

            for kyrsant in patrol:
                pool.remove(kyrsant)
                pool_weekends.remove(kyrsant)
                pool_weekends.append(kyrsant)
                pool_workdays.remove(kyrsant)
                pool_workdays.append(kyrsant)
                exceptions[day[0] - 2].append(kyrsant[0])
                exceptions[day[0] - 1].append(kyrsant[0])
                exceptions[day[0] + 1].append(kyrsant[0])
                exceptions[day[0] + 2].append(kyrsant[0])
                kyrsant[7] += 1     # Добавляем в статистику 1 сутки в патруль
                kyrsant[9] += 1     # Добавляем в общий зачёт 1 сутки
                kyrsant[11] += 1    # Добавляем в статистику 1 сутки в праздники
                smena.append(kyrsant[0])    # Добавляем в список суток id курсанта

            final[day[0]] += smena
            self.db.add_naryad(day[0], final[day[0]])

        for day in weekends:
            pool = boys_weekends if day[7].upper() == 'М' else girls_weekends
            pool_workdays = boys if day[7].upper() == 'М' else girls
            cards = []
            kpp = []
            patrol = []
            nagruzka = {
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0
            }
            for kyrsant in pool:
                if kyrsant[0] in exceptions[day[0]]:
                    continue
                if len(kpp) == 4 and len(patrol) == 4:
                    break
                if nagruzka[kyrsant[2]] < day[kyrsant[2]]:
                    if kyrsant[4] not in cards:
                        kp = kpp_patrol(kyrsant)
                        if kp > 2 and len(kpp) < 4:
                            kpp.append(kyrsant)
                            cards.append(kyrsant[4])
                            nagruzka[kyrsant[2]] += 1
                        elif kp < -2 and len(patrol) < 4:
                            patrol.append(kyrsant)
                            cards.append(kyrsant[4])
                            nagruzka[kyrsant[2]] += 1
                        elif kp > 2 and len(kpp) == 4 or kp < -2 and len(patrol) == 4:
                            continue
                        else:
                            if len(kpp) == 4:
                                post = patrol
                            elif len(patrol) == 4:
                                post = kpp
                            else:
                                post = random.choice([kpp, patrol])
                            post.append(kyrsant[0])
                            cards.append(kyrsant[4])
                            nagruzka[kyrsant[2]] += 1
            smena = []
            for kyrsant in kpp:
                pool.remove(kyrsant)
                pool.append(kyrsant)
                pool_workdays.remove(kyrsant)
                pool_workdays.append(kyrsant)
                exceptions[day[0] - 2].append(kyrsant[0])
                exceptions[day[0] - 1].append(kyrsant[0])
                exceptions[day[0] + 1].append(kyrsant[0])
                exceptions[day[0] + 2].append(kyrsant[0])
                kyrsant[6] += 1
                kyrsant[9] += 1
                kyrsant[10] += 1
                smena.append(kyrsant[0])

            for kyrsant in patrol:
                pool.remove(kyrsant)
                pool.append(kyrsant)
                pool_workdays.remove(kyrsant)
                pool_workdays.append(kyrsant)
                exceptions[day[0] - 2].append(kyrsant[0])
                exceptions[day[0] - 1].append(kyrsant[0])
                exceptions[day[0] + 1].append(kyrsant[0])
                exceptions[day[0] + 2].append(kyrsant[0])
                kyrsant[7] += 1
                kyrsant[9] += 1
                kyrsant[10] += 1
                smena.append(kyrsant[0])

            final[day[0]] += smena
            self.db.add_naryad(day[0], final[day[0]])
        count = 0
        for day in workdays:
            pool = boys if day[7].upper() == 'М' else girls

            # Каждые несколько дней алгоритм заново сортирует общий список, чтобы учитывались уже поставленные наряды
            if count == 6:
                pool_sort(pool, get_day_of_sytki)
                count = 0
            cards = []
            kpp = []
            patrol = []
            nagruzka = {
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0
            }
            for kyrsant in pool:
                if kyrsant[0] in exceptions[day[0]]:
                    continue
                if len(kpp) == 4 and len(patrol) == 4:
                    break
                if nagruzka[kyrsant[2]] < day[kyrsant[2]]:
                    if kyrsant[4] not in cards:
                        kp = kpp_patrol(kyrsant)
                        if kp > 2 and len(kpp) < 4:
                            kpp.append(kyrsant)
                            cards.append(kyrsant[4])
                            nagruzka[kyrsant[2]] += 1
                        elif kp < -2 and len(patrol) < 4:
                            patrol.append(kyrsant)
                            cards.append(kyrsant[4])
                            nagruzka[kyrsant[2]] += 1
                        elif kp > 2 and len(kpp) == 4 or kp < -2 and len(patrol) == 4:
                            continue
                        else:
                            if len(kpp) == 4:
                                post = patrol
                            elif len(patrol) == 4:
                                post = kpp
                            else:
                                post = random.choice([kpp, patrol])
                            post.append(kyrsant[0])
                            cards.append(kyrsant[4])
                            nagruzka[kyrsant[2]] += 1
            smena = []
            for kyrsant in kpp:
                pool.remove(kyrsant)

                exceptions[day[0] - 2].append(kyrsant[0])
                exceptions[day[0] - 1].append(kyrsant[0])
                exceptions[day[0] + 1].append(kyrsant[0])
                exceptions[day[0] + 2].append(kyrsant[0])
                kyrsant[6] += 1
                kyrsant[9] += 1
                smena.append(kyrsant[0])

            for kyrsant in patrol:
                pool.remove(kyrsant)
                pool.append(kyrsant)
                exceptions[day[0] - 2].append(kyrsant[0])
                exceptions[day[0] - 1].append(kyrsant[0])
                exceptions[day[0] + 1].append(kyrsant[0])
                exceptions[day[0] + 2].append(kyrsant[0])
                kyrsant[7] += 1
                kyrsant[9] += 1
                smena.append(kyrsant[0])

            final[day[0]] += smena
            self.db.add_naryad(day[0], final[day[0]])
            count += 1
