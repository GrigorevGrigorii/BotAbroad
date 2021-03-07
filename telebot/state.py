# import json


# Временно закомментированны участки кода, обращающиесе к файлам.
# На Heroku нет файловой системы и это сломет приложение.
# Надо будет переделать на базы данных.


class State:
    __n = 0

    def __init__(self):
        # try:
        #     with open('files/states.json', 'r') as states_file:
        #         self.__state = {int(k): v for k, v in json.load(states_file).items()}
        # except FileNotFoundError:
        #     self.__state = dict()
        self.__state = dict()

    def __contains__(self, item):
        return item in self.__state

    def __getitem__(self, key):
        if type(key) is not int:
            raise TypeError
        if key not in self.__state:
            self.__state[key] = []
            return []

        return self.__state[key]

    def __setitem__(self, key, value):
        if type(key) is not int:
            raise TypeError

        # if key not in self.__state or self.__state[key] != value:
        #     self.__state[key] = value
        #     with open('files/states.json', 'w') as states_file:
        #         json.dump(self.__state, states_file)
        # else:
        #     self.__state[key] = value
        self.__state[key] = value

    def __str__(self):
        return str(self.__state)

    def __new__(cls):
        if cls.__n == 0:
            cls.__n = 1
            return object.__new__(cls)
