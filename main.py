import numpy as np


def transformer(bad_date):
    good_date = bad_date[-4:] + '-' + bad_date[-7:-5] + '-' + bad_date[0:2]
    return good_date


def filter_cost(rooms: dict, opportunity: np.str_, arg_amount: int):
    opportunity = int(opportunity)
    cost = {}
    if arg_amount == int(clt[4]):
        for room in rooms.keys():
            if opportunity >= fund_dict[room][3]:
                cost[room] = rooms[room]
        return cost

    else:
        for room in rooms.keys():
            if opportunity >= fund_dict[room][4]:
                cost[room] = rooms[room]
        return cost


def suitable_quantity_filter(rooms: dict, requirement: int):
    output_rooms = {}
    for room in rooms:
        if fund_dict[room][1] == requirement:
            output_rooms[room] = rooms[room]
    return output_rooms


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


def profit(good_rooms: dict, opportunity: np.str_, arg_amount: int):
    opportunity = int(opportunity)
    rooms = []
    list_for_max = []

    if arg_amount == int(clt[4]):
        for room in good_rooms:
            rooms.append(room)
            list_for_max.append(fund_dict[room][3])

        list_for_max = np.array(list_for_max)
        with_breakfast = list_for_max + food['breakfast'] * int(clt[6])
        with_half_board = list_for_max + food['half_board'] * int(clt[6])
        table_for_max = np.vstack([list_for_max, with_breakfast, with_half_board])

        potential_max = table_for_max.max()
        while opportunity < potential_max:
            table_for_max[table_for_max == potential_max] = 0
            potential_max = table_for_max.max()

        if potential_max in list_for_max:
            profit_room_index = np.where(list_for_max == potential_max)[0][0]
        elif potential_max in with_breakfast:
            profit_room_index = np.where(with_breakfast == potential_max)[0][0]
        else:
            profit_room_index = np.where(with_half_board == potential_max)[0][0]

        profit_room = rooms[profit_room_index]
        return profit_room, potential_max

    else:
        for room in good_rooms:
            rooms.append(room)
            list_for_max.append(fund_dict[room][4])

        list_for_max = np.array(list_for_max)
        with_breakfast = list_for_max + food['breakfast'] * int(clt[6])
        with_half_board = list_for_max + food['half_board'] * int(clt[6])
        table_for_max = np.vstack([list_for_max, with_breakfast, with_half_board])

        potential_max = table_for_max.max()
        while opportunity < potential_max:
            table_for_max[table_for_max == potential_max] = 0
            potential_max = table_for_max.max()

        if potential_max in list_for_max:
            profit_room_index = np.where(list_for_max == potential_max)[0][0]
        elif potential_max in with_breakfast:
            profit_room_index = np.where(with_breakfast == potential_max)[0][0]
        else:
            profit_room_index = np.where(with_half_board == potential_max)[0][0]

        profit_room = rooms[profit_room_index]
        return profit_room, potential_max


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
    fund_dict[key].append(int(type_room[tp_room] * coefficient[coeff]))
    fund_dict[key].append(int(fund_dict[key][3] / 10 * 7))
print(fund_dict, 'словарь fund_dict из файла fund')


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

quantity_of_rooms = len(fund_dict)
numbers = [np.str_(num) for num in range(1, quantity_of_rooms + 1)]

busy = {day: dict.fromkeys(numbers, 0) for day in days}
#print(busy, 'словарь состояний')

for clt in matrix:
    date_entry = clt[5]
    free_numbers = busy[date_entry]
    max_clt_cost = clt[7]       # сколько готов заплатить
    amount = int(clt[4])        # сколько мест требуется челу
    print(free_numbers, 'до фильтров')

    flag_string = 'content'
    free_numbers = future_busy(free_numbers, date_entry, clt[6])
    print(free_numbers, 'по занятости на будущие даты')     # первый фильтр применен
    if len(free_numbers) == 0:      #!!!
        flag_string = 'empty'

    while amount <= 6:
        if len(suitable_quantity_filter(free_numbers, amount)) != 0:
            free_numbers = suitable_quantity_filter(free_numbers, amount)
            break
        else:
            amount += 1

    if amount == 7:
        free_numbers = {}
        flag_string = 'empty'
    print(free_numbers, 'по нужному количеству человек')        # второй фильтр применен

    free_numbers = filter_cost(free_numbers, max_clt_cost, amount)
    print(free_numbers, 'по цене')
    if len(free_numbers) == 0:      #!!! x2
        flag_string = 'empty'

    if flag_string == 'content':
        # подсчитать профит (сделано, реализовал функцию profit)
        clt_profit = profit(free_numbers, max_clt_cost, amount)[1]
        room_for_clt = profit(free_numbers, max_clt_cost, amount)[0]
        print(room_for_clt, 'комната для клиента')
        print(clt_profit, 'выручка')
    else:
        pass
        # подсчитать убыток

    # после того, как все посчитали, надо изменить словарь состояний busy и можно в следующую итерацию
    # в начале цикла тоже нужно будет реализовать, чтоб "с утра" все понаехавшие съезжали

    break




