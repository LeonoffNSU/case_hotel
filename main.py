import numpy as np
import datetime


def transformer(bad_date):
    good_date = bad_date[-4:] + '-' + bad_date[-7:-5] + '-' + bad_date[0:2]
    return good_date


day_1 = datetime.datetime(2020, 3, 1)
type_room = {'one': 2900, 'two': 2300, 'middle_luxe': 3200, 'luxe': 4100}
coefficient = {'standart': 1, 'improve_standart': 1.2, 'apartment': 1.5}
food = {'without' : 0, 'breakfast' : 280, 'half_board': 1000}


with open('fund.txt', encoding= 'utf-8') as chrt:
    fund_dict = {}
    for line in chrt:
        if 'одноместный' in line:
            line = line.replace('одноместный', 'one')
        if 'двухместный' in line:
            line = line.replace('двухместный', 'two')
        if 'полулюкс' in line:
            line = line.replace('полулюкс', 'middle_luxe')
        if 'люкс' in line:
            line = line.replace('люкс', 'luxe')
        if 'стандарт_улучшенный' in line:
            line = line.replace('стандарт_улучшенный', 'improve_standart')
        if 'стандарт' in line:
            line = line.replace('стандарт', 'standart')
        if 'апартамент' in line:
            line = line.replace('апартамент', 'apartment')
        line = line.split()
        fund_dict[line[0]] = [line[1], int(line[2]), line[3]]
    print(fund_dict)

with open('booking.txt', encoding='utf-8') as clients:
    first_client = clients.readline()
    first_client = first_client.split()
    first_client = np.array(first_client)

    for index, client in enumerate(clients):
        client = client.split()
        client = np.array(client)
        if index == 0:
            matrix = np.vstack([first_client, client])
        else:
            matrix = np.vstack([matrix, client])

matrix[:, 0] = np.vectorize(transformer)(matrix[:, 0])
matrix[:, 5] = np.vectorize(transformer)(matrix[:, 5])
print(matrix)

days = []
for i in range(31):
    days.append(str((day_1 + datetime.timedelta(i)).date()))
print(days)
