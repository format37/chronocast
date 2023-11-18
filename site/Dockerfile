# Используйте официальный образ Python
FROM python:3.12.0

# Установите рабочую директорию в контейнере
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y gettext

# Скопируйте файлы проекта в контейнер
COPY . .

# Установите зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Copy SSL certificates
COPY cert/fullchain.pem /usr/src/app/
COPY cert/privkey.pem /usr/src/app/

COPY settings.txt /usr/src/app/settings.txt

# Определите порт, на котором будет работать приложение
EXPOSE 443

# Запустите сервер разработки Django
# CMD ["python", "manage.py", "runserver", "0.0.0.0:443"]
CMD ["gunicorn", "--certfile=fullchain.pem", "--keyfile=privkey.pem", "-b", "0.0.0.0:443", "myproject.wsgi:application"]

