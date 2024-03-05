## Description 
It is my college diplom project. It is an app which lets users create wishlists and gifts in them. Also you can make friends and share your wishlists. 
This is backend of the app which exposes an API to do corresponding actions and pass authorization.

## Installation
For installation of the app you need to have Docker on your PC

Write the command below in your terminal
```
docker-compose up -d
```
Make migration yourself
```
docker-compose run django python manage.py migrate
```
Create superuser to gain access to the admin panel
```
docker-compose run django python manage.py createsuperuser
```

## Demo
You can try demo version of my app with a frontend using the uri: http://185.248.103.225:5173/