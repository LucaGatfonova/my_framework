from datetime import date

from my_framework.templator import render
from patterns.architectural_system_pattern_mappers import MapperRegistry
from patterns.architectural_system_pattern_unit_of_work import UnitOfWork
from patterns.behavioral_patterns import EmailNotifier, SmsNotifier, ListView, CreateView, BaseSerializer
from patterns.structural_patterns import AppRoute, Debug
from patterns.сreational_patterns import Engine, Logger

site = Engine()
logger = Logger('main')
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)

routes = {}


@AppRoute(routes=routes, url='/')
class Index:
    @Debug(name='Index')
    def __call__(self, request):
        return '200 OK', render('index.html', object_list=site.locations)


@AppRoute(routes=routes, url='/about/')
class About:
    @Debug(name='About')
    def __call__(self, request):
        return '200 OK', render('about.html')


@AppRoute(routes=routes, url='/contact/')
class Contact:
    @Debug(name='Contact')
    def __call__(self, request):
        return '200 OK', render('contact.html')


@AppRoute(routes=routes, url='/schedule/')
class Schedule:
    @Debug(name='Schedule')
    def __call__(self, request):
        return '200 OK', render('schedule.html', data=date.today())


class NotFound404:
    @Debug(name='NotFound404')
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


# контроллер - список занятий
@AppRoute(routes=routes, url='/sports_list/')
class SportsList:
    @Debug(name='SportsList')
    def __call__(self, request):
        logger.log('Список занятий')
        try:
            location = site.find_location_by_id(int(request['request_params']['id']))
            return '200 OK', render('sports_list.html', objects_list=location.sports, name=location.name,
                                    id=location.id)
        except KeyError:
            return '200 OK', 'No sports have been added yet'


# контроллер - создать занятие
@AppRoute(routes=routes, url='/create_sport/')
class CreateSport:
    location_id = -1

    @Debug(name='CreateSport')
    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            location = None
            if self.location_id != -1:
                location = site.find_location_by_id(int(self.location_id))

                sport = site.create_sport('record', name, location)
                # Добавляем наблюдателей на занятие
                sport.observers.append(email_notifier)
                sport.observers.append(sms_notifier)
                site.sports.append(sport)

            return '200 OK', render('sports_list.html', objects_list=location.sports,
                                    name=location.name, id=location.id)

        else:
            try:
                self.location_id = int(request['request_params']['id'])
                location = site.find_location_by_id(int(self.location_id))

                return '200 OK', render('create_sport.html', name=location.name, id=location.id)
            except KeyError:
                return '200 OK', 'No locations have been added yet'


# контроллер - создать локацию
@AppRoute(routes=routes, url='/create_location/')
class CreateLocation:
    @Debug(name='CreateLocation')
    def __call__(self, request):

        if request['method'] == 'POST':
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            location_id = data.get('location_id')

            location = None
            if location_id:
                location = site.find_location_by_id(int(location_id))

            new_location = site.create_location(name, location)
            site.locations.append(new_location)
            site.clients.append(new_location)
            new_location.mark_new()
            UnitOfWork.get_current().commit()

            return '200 OK', render('index.html', objects_list=site.locations)
        else:
            locations = site.locations
            return '200 OK', render('create_location.html', locations=locations)


# контроллер - список локаций
@AppRoute(routes=routes, url='/location_list/')
class LocationList:
    @Debug(name='LocationList')
    def __call__(self, request):
        logger.log('Список локаций')
        return '200 OK', render('location_list.html', objects_list=site.locations)


# @AppRoute(routes=routes, url='/location_list/')
# class LocationListView(ListView):
#     template_name = 'location_list.html'
#
#     def get_queryset(self):
#         mapper = MapperRegistry.get_current_mapper('location')
#         return mapper.all()


# контроллер - копировать занятие
@AppRoute(routes=routes, url='/copy_sport/')
class CopySport:
    @Debug(name='CopySport')
    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']
            old_sport = site.get_sport(name)
            if old_sport:
                new_name = f'copy_{name}'
                new_sport = old_sport.clone()
                new_sport.name = new_name
                site.sports.append(new_sport)

            return '200 OK', render('sports_list.html', objects_list=site.sports)
        except KeyError:
            return '200 OK', 'No sports have been added yet'


@AppRoute(routes=routes, url='/client_list/')
class ClientListView(ListView):
    template_name = 'client_list.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('client')
        return mapper.all()


@AppRoute(routes=routes, url='/trainer_list/')
class TrainerListView(ListView):
    template_name = 'trainer_list.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('trainer')
        return mapper.all()


@AppRoute(routes=routes, url='/create_client/')
class ClientCreateView(CreateView):
    template_name = 'create_client.html'

    def create_obj(self, data: dict):
        name = data['name']
        if not name.isnumeric():
            UnitOfWork.new_current()
        try:
            name = site.decode_value(name)
            new_obj = site.create_user('client', name)
            site.clients.append(new_obj)
            new_obj.mark_new()
            UnitOfWork.get_current().commit()
        except:
            print("Неверное значение")


@AppRoute(routes=routes, url='/create_trainer/')
class TrainerCreateView(CreateView):
    template_name = 'create_trainer.html'

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        new_trainer = site.create_trainer('trainer', name)
        site.trainers.append(new_trainer)
        new_trainer.mark_new()
        UnitOfWork.get_current().commit()


@AppRoute(routes=routes, url='/add_client/')
class AddClientBySportCreateView(CreateView):
    template_name = 'add_client.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['sports'] = site.sports
        context['clients'] = site.clients
        return context

    def create_obj(self, data: dict):
        sport_name = data['sport_name']
        sport_name = site.decode_value(sport_name)
        sport = site.get_sport(sport_name)
        client_name = data['client_name']
        client_name = site.decode_value(client_name)
        client = site.get_client(client_name)
        sport.add_client(client)


@AppRoute(routes=routes, url='/add_client_trainer/')
class AddClientByTrainerCreateView(CreateView):
    template_name = 'add_client_trainer.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['trainers'] = site.trainers
        context['clients'] = site.clients
        return context

    def create_obj(self, data: dict):
        trainer_name = data['trainer_name']
        trainer_name = site.decode_value(trainer_name)
        sport = site.get_sport(trainer_name)
        client_name = data['client_name']
        client_name = site.decode_value(client_name)
        client = site.get_client(client_name)
        sport.add_client(client)


@AppRoute(routes=routes, url='/api/')
class SportApi:
    @Debug(name='SportApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.sports).save()
