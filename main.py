import numpy as np


def transformer(bad_date):
    good_date = bad_date[-4:] + '-' + bad_date[-7:-5] + '-' + bad_date[0:2]
    return good_date


def filter_cost(rooms: dict, requirement: np.str_):
    requirement = int(requirement)
    cost = {}
    for room in rooms.keys():
        if requirement >= fund_dict[room][3]:
            cost[room] = rooms[room]
    return cost


def free_room(bussy: dict):
    free_rooms = {}
    for room, free in bussy.items():
        if free == 0:
            free_rooms[room] = free
    return free_rooms


def suitable_quantity_filter(numbers: dict, requirement: int):
    output_numbers = {}
    for number in numbers:
        if fund_dict[number][1] == requirement:
            output_numbers[number] = numbers[number]

    return output_numbers


def future_busy(free_rooms: dict, entry_date: np.str_, amount_days: np.str_):
    entry_day = np.datetime64(entry_date)
    stay_dates = []
    for day in range(int(amount_days)):
        delta = np.timedelta64(day, 'D')
        stay_dates.append(np.str_(entry_day + delta))

    final_rooms = {}
    for room in free_rooms:
        flag = True
        for date in stay_dates:
            if busy[date][room] == 1:
                flag = False
        if flag:
            final_rooms[room] = 0
    return final_rooms


type_room = {'one': 2900, 'two': 2300, 'middle_luxe': 3200, 'luxe': 4100}
coefficient = {'standart': 1, 'improve_standart': 1.2, 'apartment': 1.5}
food = {'without': 0, 'breakfast': 280, 'half_board': 1000}


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

for key in fund_dict:
    coeff = fund_dict[key][2]
    tp_room = fund_dict[key][0]
    fund_dict[key].append(type_room[tp_room]*coefficient[coeff])
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
#print(matrix)

day_1 = np.datetime64(matrix[0][0])
days = []

for i in range(31):
    days.append(np.str_(day_1 + np.timedelta64(i, 'D')))

number_of_room = len(fund_dict)
numbers = [np.str_(num) for num in range(1, number_of_room+1)]

busy = {day: dict.fromkeys(numbers, 0) for day in days}
#print(busy)


for clt in matrix:
    date_entry = clt[5]
    print(clt[1])
    free_numbers = busy[date_entry]
    max_costs = clt[7]
    amount = int(clt[4])
    print(free_numbers, 'до фильтров')
    free_numbers = filter_cost(free_numbers, max_costs)
    print(free_numbers, 'по цене и занятости на будущие даты')
    free_numbers = future_busy(free_numbers, date_entry, clt[6])
    check_free_numbers = free_numbers.copy()

    free_numbers = suitable_quantity_filter(free_numbers, amount)
    if len(free_numbers) == 0:
        if amount < 6:
            for i in range(1, 7 - amount):
                free_numbers = check_free_numbers
                free_numbers = suitable_quantity_filter(free_numbers, amount + i)
                print(amount + i)
                if len(free_numbers) != 0:
                    break
                if amount + i == 6:
                    print('Not free1')

        else:
            print('Not free')

    if len(free_numbers) != 0:
        max_cost = max(fund_dict[key][3] for key in free_numbers.keys())
        for room in free_numbers:
            if fund_dict[room][1] != amount:
                max_cost = max_cost * 0.7
                break

        print(max_cost)
        print(free_numbers)
    print(free_numbers)
    break




