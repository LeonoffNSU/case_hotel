import numpy as np
import ru_local as ru


class Loading:
    type_room = {'one': 2900, 'two': 2300, 'middle_luxe': 3200, 'luxe': 4100}
    coefficient = {'standart': 1, 'improve_standart': 1.2, 'apartment': 1.5}
    food = {'without': 0, 'breakfast': 280, 'half_board': 1000}

    def __init__(self):
        self.fund_dict = Loading.fund_parsing()
        self.matrix = Loading.booking_parsing()

    @staticmethod
    def transformer(bad_date):
        good_date = bad_date[-4:] + '-' + bad_date[-7:-5] + '-' + bad_date[0:2]
        return good_date

    @staticmethod
    def fund_parsing():
        with open('fund.txt', encoding='utf-8') as chrt:
            fund_dict = {}
            for line in chrt:
                if ru.ONE in line:
                    line = line.replace(ru.ONE, 'one')
                if ru.TWO in line:
                    line = line.replace(ru.TWO, 'two')
                if ru.MIDDLE in line:
                    line = line.replace(ru.MIDDLE, 'middle_luxe')
                if ru.LUXE in line:
                    line = line.replace(ru.LUXE, 'luxe')
                if ru.IMPROVE in line:
                    line = line.replace(ru.IMPROVE, 'improve_standart')
                if ru.STANDART in line:
                    line = line.replace(ru.STANDART, 'standart')
                if ru.APARTMENT in line:
                    line = line.replace(ru.APARTMENT, 'apartment')
                line = line.split()
                fund_dict[line[0]] = [line[1], int(line[2]), line[3]]

        for key in fund_dict:
            coeff = fund_dict[key][2]
            tp_room = fund_dict[key][0]
            fund_dict[key].append(int(Loading.type_room[tp_room] * Loading.coefficient[coeff]))
            fund_dict[key].append(int(fund_dict[key][3] / 10 * 7))
        return fund_dict

    @staticmethod
    def booking_parsing():
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

        matrix[:, 0] = np.vectorize(Loading.transformer)(matrix[:, 0])
        matrix[:, 5] = np.vectorize(Loading.transformer)(matrix[:, 5])
        return matrix


class Busy(Loading):

    def __init__(self):
        super().__init__()
        self.busy = self.create_busy()[0]
        self.days = self.create_busy()[1]

    def create_busy(self):
        day_1 = np.datetime64(self.matrix[0][0])
        days = []

        for i in range(31):
            days.append(np.str_(day_1 + np.timedelta64(i, 'D')))

        quantity_of_rooms = len(self.fund_dict)
        numbers = [np.str_(num) for num in range(1, quantity_of_rooms + 1)]

        busy = {day: dict.fromkeys(numbers, 0) for day in days}
        return busy, days


class Optimum(Busy):
    objects = []

    def __init__(self):
        super().__init__()
        self.total_lost_profit = 0
        self.profit_per_day = {day: 0 for day in self.days}
        self.lost_profit_per_day = {day: 0 for day in self.days}
        self.dates_modeling = {self.matrix[0][0]: 0}
        Optimum.objects.append(self)

    @staticmethod
    def busy_cnt(rooms: dict):
        cnt = 0
        for room, value in rooms.items():
            if value == 1:
                cnt += 1
        return cnt

    @staticmethod
    def busy_categories(rooms: dict):
        busy_rooms_ctg = dict.fromkeys(['one', 'two', 'luxe', 'middle_luxe'], 0)
        free_rooms_ctg = dict.fromkeys(['one', 'two', 'luxe', 'middle_luxe'], 0)

        for room in rooms:
            room_type = Optimum.objects[-1].fund_dict[room][0]
            free_rooms_ctg[room_type] += 1
            if rooms[room] == 1:
                busy_rooms_ctg[room_type] += 1

        shares = {}
        for key in busy_rooms_ctg:
            shares[key] = round(busy_rooms_ctg[key] / free_rooms_ctg[key] * 100, 2)

        return shares

    @staticmethod
    def filter_cost(rooms: dict, opportunity: np.str_, arg_amount: int):
        opportunity = int(opportunity)
        cost = {}
        if arg_amount == int(Optimum.client[4]):
            for room in rooms.keys():
                if opportunity >= Optimum.objects[-1].fund_dict[room][3]:
                    cost[room] = rooms[room]
            return cost

        else:
            for room in rooms.keys():
                if opportunity >= Optimum.objects[-1].fund_dict[room][4]:
                    cost[room] = rooms[room]
            return cost

    @staticmethod
    def suitable_quantity_filter(rooms: dict, requirement: int):
        output_rooms = {}
        for room in rooms:
            if Optimum.objects[-1].fund_dict[room][1] == requirement:
                output_rooms[room] = rooms[room]
        return output_rooms

    @staticmethod
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
                if Optimum.objects[-1].busy[date][room] == 1:
                    flag = False
            if flag:
                final_rooms[room] = 0
        return final_rooms

    @staticmethod
    def profit(good_rooms: dict, opportunity: np.str_, arg_amount: int):
        opportunity = int(opportunity)
        rooms = []
        list_for_max = []

        if arg_amount == int(Optimum.client[4]):
            for room in good_rooms:
                rooms.append(room)
                list_for_max.append(Optimum.objects[-1].fund_dict[room][3])

            list_for_max = np.array(list_for_max)
            with_breakfast = list_for_max + Loading.food['breakfast']
            with_half_board = list_for_max + Loading.food['half_board']
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
                list_for_max.append(Optimum.objects[-1].fund_dict[room][4])

            list_for_max = np.array(list_for_max)
            with_breakfast = list_for_max + Loading.food['breakfast']
            with_half_board = list_for_max + Loading.food['half_board']
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

    def start_modeling(self):
        for clt in self.matrix:
            Optimum.client = clt

            if clt[0] not in self.dates_modeling:
                daily_income = 0
                trans_date = list(self.dates_modeling.keys())[-1]
                busy_rooms = Optimum.busy_cnt(self.busy[trans_date])
                free_rooms = len(self.fund_dict) - busy_rooms

                print(f'{ru.BUSY_ROOMS} {trans_date}: {busy_rooms}')
                print(f'{ru.FREE_ROOMS} {trans_date}: {free_rooms}')
                print(f'{ru.PERCENT_HOTEL}: {round(busy_rooms / len(self.fund_dict) * 100, 2)}%')

                busy_ctg = Optimum.busy_categories(self.busy[trans_date])
                print(f'''{ru.PERCENT_CATEGORY}:                                                       
                {ru.ONE}: {busy_ctg["one"]}%                                                                               
                {ru.TWO}: {busy_ctg["two"]}%                                                                               
                {ru.MIDDLE}: {busy_ctg["middle_luxe"]}%                                                                          
                {ru.LUXE}: {busy_ctg["luxe"]}%''')

                print(f'{ru.PROFIT} {trans_date}: {self.profit_per_day[trans_date]}')
                print(f'{ru.LOST_PROFIT} {trans_date}: {self.lost_profit_per_day[trans_date]}')
                self.dates_modeling[clt[0]] = 0

            date_entry = clt[5]
            free_numbers = self.busy[date_entry]
            max_clt_cost = clt[7]
            amount = int(clt[4])

            entry_day = np.datetime64(date_entry)
            stay_dates = []
            for day in range(int(clt[6])):
                delta = np.timedelta64(day, 'D')
                stay_dates.append(np.str_(entry_day + delta))

            entry_day = np.datetime64(date_entry)
            stay_dates = []
            for day in range(int(clt[6])):
                delta = np.timedelta64(day, 'D')
                stay_dates.append(np.str_(entry_day + delta))

            flag_string = 'content'
            free_numbers = Optimum.future_busy(free_numbers, date_entry, clt[6])
            if len(free_numbers) == 0:
                flag_string = 'empty'

            if flag_string == 'content':
                while amount <= 6:
                    if len(Optimum.suitable_quantity_filter(free_numbers, amount)) != 0:
                        free_numbers = Optimum.suitable_quantity_filter(free_numbers, amount)
                        break
                    else:
                        amount += 1

                if amount == 7:
                    free_numbers = {}
                    flag_string = 'empty'

            if flag_string == 'content':
                free_numbers = Optimum.filter_cost(free_numbers, max_clt_cost, amount)
                if len(free_numbers) == 0:
                    flag_string = 'empty'

            if flag_string == 'content':
                clt_profit = Optimum.profit(free_numbers, max_clt_cost, amount)[1]
                room_for_clt = Optimum.profit(free_numbers, max_clt_cost, amount)[0]

                if np.random.random() <= 0.25:
                    lost_profit = int(max_clt_cost) * int(clt[6]) * int(clt[4])
                    self.lost_profit_per_day[clt[0]] += lost_profit
                    self.total_lost_profit += lost_profit
                    print(f'{clt[1]} {clt[2]} {clt[3]} {ru.REFUSE}')

                else:
                    for stay_date in stay_dates:
                        self.busy[stay_date][room_for_clt] = 1
                    self.profit_per_day[clt[0]] += clt_profit * int(clt[4]) * int(clt[6])

                    print(f'{clt[1]} {clt[2]} {clt[3]}')
                    print(f'{ru.BOOKING_DATE}: {clt[0]}')
                    if clt[4] == '1':
                        print(f'{ru.CHECK_INTO} {clt[4]} {ru.PERSON} {clt[6]} {ru.DAYS}: {", ".join(stay_dates)}')
                    else:
                        print(f'{ru.CHECK_INTO_1} {clt[4]} {ru.PEOPLE} {clt[6]} {ru.DAYS}: {", ".join(stay_dates)}')
                    print(f'{ru.MAX_AMOUNT}: {clt[7]}')
                    print(
                        f'{ru.ROOM_FOR_CLIENT}: {room_for_clt} - {self.fund_dict[room_for_clt][0]}'
                        f' {self.fund_dict[room_for_clt][2]}')

            else:
                lost_profit = int(max_clt_cost) * int(clt[6]) * int(clt[4])
                self.lost_profit_per_day[clt[0]] += lost_profit
                self.total_lost_profit += lost_profit
                print(f'{ru.CLIENT} {clt[1]} {clt[2]} {clt[3]} {ru.NO_ROOMS} {clt[4]} {ru.PLACE}')

            last_date = clt[0]

        total = 0
        for value in self.profit_per_day.values():
            total += value

        busy_rooms = Optimum.busy_cnt(self.busy[last_date])
        free_rooms = len(self.fund_dict) - busy_rooms
        print(f'{ru.BUSY_ROOMS} {last_date}: {busy_rooms}')
        print(f'{ru.FREE_ROOMS} {last_date}: {free_rooms}')
        print(f'{ru.PERCENT_HOTEL}: {round(busy_rooms / len(self.fund_dict) * 100, 2)}%')

        busy_ctg = Optimum.busy_categories(self.busy[last_date])
        print(f'''{ru.PERCENT_CATEGORY}:                                                       
        {ru.ONE}: {busy_ctg["one"]}%                                                                               
        {ru.TWO}: {busy_ctg["two"]}%                                                                               
        {ru.MIDDLE}: {busy_ctg["middle_luxe"]}%                                                                          
        {ru.LUXE}: {busy_ctg["luxe"]}%''')
        print(f'{ru.PROFIT} {last_date}: {self.profit_per_day[last_date]}')
        print(f'{ru.LOST_PROFIT} {last_date}: {self.lost_profit_per_day[last_date]}')

        print(f'{ru.TOTAL_PROFIT}: {total}')
        print(f'{ru.TOTAL_LOST}: {self.total_lost_profit}')

optimum = Optimum()
optimum.start_modeling()
