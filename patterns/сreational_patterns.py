import copy
import quopri


# абстрактный пользователь
from patterns.architectural_system_pattern_unit_of_work import DomainObject
from patterns.behavioral_patterns import Subject, ConsoleWriter


class User:
    def __init__(self, name):
        self.name = name


# Клиент
class Client(User, DomainObject):

    def __init__(self, name):
        self.sports = []
        self.trainers = []
        super().__init__(name)


class Trainer(User, Subject, DomainObject):
    def __init__(self, name):
        self.clients = []
        super().__init__(name)

    def __getitem__(self, item):
        return self.clients[item]

    def add_client(self, client: Client):
        self.clients.append(client)
        client.trainers.append(self)
        self.notify()


# порождающий паттерн Абстрактная фабрика - фабрика пользователей
class UserFactory:
    types = {
        'client': Client,
        'trainer': Trainer
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name):
        return cls.types[type_](name)


# порождающий паттерн Прототип - Вид зянятия
class SportPrototype:
    # прототип занятий фитнес

    def clone(self):
        return copy.deepcopy(self)


class Sport(SportPrototype, Subject):

    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.location.sports.append(self)
        self.clients = []
        super().__init__()

    def __getitem__(self, item):
        return self.clients[item]

    def add_client(self, client: Client):
        self.clients.append(client)
        client.sports.append(self)
        self.notify()


# Интерактивное занятие
class InteractiveSport(Sport):
    pass


# занятие в записи
class RecordSport(Sport):
    pass


# Локация
class Location(DomainObject):
    # реестр
    auto_id = 0

    def __init__(self, name, location):
        self.id = Location.auto_id
        Location.auto_id += 1
        self.name = name
        self.location = location
        self.sports = []

    def sport_count(self):
        result = len(self.sports)
        if self.location:
            result += self.location.sport_count()
        return result


# порождающий паттерн Абстрактная фабрика - фабрика занятий
class SportFactory:
    types = {
        'interactive': InteractiveSport,
        'record': RecordSport
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, location):
        return cls.types[type_](name, location)


# Основной интерфейс проекта
class Engine:
    def __init__(self):
        self.trainers = []
        self.clients = []
        self.sports = []
        self.locations = []

    @staticmethod
    def create_user(type_, name):
        return UserFactory.create(type_, name)

    @staticmethod
    def create_trainer(type_, name):
        return UserFactory.create(type_, name)

    def find_trainer_by_id(self, id):
        for item in self.trainers:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет тренера с id = {id}')

    @staticmethod
    def create_location(name, location=None):
        return Location(name, location)

    def find_location_by_id(self, id):
        for item in self.locations:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_sport(type_, name, location):
        return SportFactory.create(type_, name, location)

    def get_sport(self, name):
        for item in self.sports:
            if item.name == name:
                return item
        return None

    def get_client(self, name) -> Client:
        for item in self.clients:
            if item.name == name:
                return item

    def get_trainer(self, name) -> Trainer:
        for item in self.trainers:
            if item.name == name:
                return item

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = quopri.decodestring(val_b)
        return val_decode_str.decode('UTF-8')


# порождающий паттерн Синглтон
class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name, writer=ConsoleWriter()):
        self.name = name
        self.writer = writer

    def log(self, text):
        text = f'log---> {text}'
        self.writer.write(text)