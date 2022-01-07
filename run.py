from components import settings
from components.settings import DEFAULT_PORT
from my_framework.main import Framework
from wsgiref.simple_server import make_server
from views import routes

# Создаем объект WSGI-приложения
application = Framework(settings, routes)

with make_server('', DEFAULT_PORT, application) as httpd:
    print("Запуск на порту 8080...")
    httpd.serve_forever()
