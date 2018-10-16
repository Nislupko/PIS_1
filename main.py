from collections import OrderedDict
from operator import itemgetter
import json
from sys import argv

def get_data(path: str = 'data.csv'):
    """Чтение из файла и построчная запись в lines"""
    f = open(path)
    lines = [line.strip() for line in f]
    f.close()
    """Создание пустого словаря и переменной-итератора"""
    rates = {}
    k = 0
    """Запись в словарь всех данных"""
    for i in lines:
        user = i.split(',', -1)
        rates[k] = user
        k += 1
    return rates


"""Нахождение средних оценок и запись в словарь avg_rate"""
def get_avg_rate():
    avg_rate = {}
    accum = 0
    nums = 0
    for x in range(1, len(rates)):
        for y in range(1, len(rates[0])):
            if int(rates[x][y]) > 0:
                accum += int(rates[x][y])
                nums+=1
        avg_rate[x] = accum / nums
        accum = 0
        nums=0
    return avg_rate

"""Функция вычисления метрики "Косинус" возвращет отсортированный по убыванию список метрик для пользователя target_id"""

def sim(target_id: int):
    result = {}
    for a in range(1, len(rates)):
        if target_id != a:
            result[a] = 0
            sq_avg_target = 0
            sq_avg_a = 0
            for b in range(1, len(rates[0])):
                if int(rates[target_id][b]) != -1 and int(rates[a][b]) != -1:
                    result[a] += int(rates[target_id][b]) * int(rates[a][b])
                    sq_avg_target += int(rates[target_id][b]) ** 2
                    sq_avg_a += int(rates[a][b]) ** 2
            result[a] = result[a] / ((sq_avg_target * sq_avg_a) ** (1 / 2))
    result = list(OrderedDict(sorted(result.items(), key=itemgetter(1), reverse=True)).items())
    return result

"""Функция использует knn пользователей с наибольшими занчениями метрик для пользователя target_id для прогнозирования оценки фильма"""
def rate_films(_knn: int, target_id: int):
    json_file['rates'][rates[target_id][0]]={}
    for movie in range(1, len(rates[0])):
        if rates[target_id][movie] == ' -1':
            up_accum = 0
            down_accum = 0
            for friend, value in friends:
                if rates[friend][movie] != ' -1':
                    up_accum += value*(int(rates[friend][movie])-avg_rate[friend])
                    down_accum += value
            rates[target_id][movie] = round(avg_rate[target_id]+up_accum/down_accum, 3)
            json_file['rates'][rates[target_id][0]][rates[0][movie]]=rates[target_id][movie]


def get_recomendation(target_id: int, good_days, good_places):
    movie = 0
    max_rate = 0
    for i in range(1, len(prev_rates[0])):
        actual_rate = 0
        users_n=0
        if prev_rates[target_id][i] == ' -1':
            for j in range(1, len(prev_rates)):
                if prev_rates[j][i] != ' -1':
                    rate_part = rates[target_id][i]
                    if days[j][i] in good_days:
                        rate_part *= 2/7
                    if places[j][i] in good_places:
                        rate_part *= 3
                    actual_rate += rate_part
                    users_n+=1
        if users_n > 0 and actual_rate/users_n > max_rate:
            max_rate = actual_rate/users_n
            movie = i
    #print("Movie {} is {} for User {}".format(movie, round(max_rate, 3), target_id))
    if movie > 0:
        json_file['recomendations'][rates[target_id][0]] = rates[0][movie]
    else:
        json_file['recomendations'][rates[target_id][0]] = "Nothing to watch"

kNN = 7
if __name__ == '__main__':
    """Создаем необходимую структуру json-файла, получаем данные о пользователях из файлов и считаем средние оценки пользователей"""
    json_file = dict()
    json_file['rates'] = {}
    json_file['recomendations'] = {}
    prev_rates = get_data(); #исходные оценки с -1, меняться не будет
    rates = get_data() #оценки и прогнозы, будет меняться
    places = get_data('context_place.csv')
    days = get_data('context_day.csv')
    avg_rate = get_avg_rate()
    """Если программа запускается без аргументов - расчеты ведутся для всех пользователей. Если есть аргумент - для указанного пользователя"""
    if len(argv) == 1:
        for i in range(1, len(rates)):
            friends = sim(i)[0:kNN]
            rate_films(kNN, i)
            get_recomendation(i, (' Sun', ' Sat'), (' h'))
        with open('QUsers_results.json', 'w') as outfile:
            json.dump(json_file, outfile, indent=4, ensure_ascii=False)
    elif len(argv) == 2 and int(argv[1]) > 0:
        user=int(argv[1])
        friends = sim(user)[0:kNN]
        rate_films(kNN, user)
        get_recomendation(user,(' Sun', ' Sat'), (' h'))
        with open('QUser_{}_result.json'.format(argv[1]), 'w') as outfile:
            json.dump(json_file, outfile, indent=4, ensure_ascii=False)
    else:
        print("Error")




