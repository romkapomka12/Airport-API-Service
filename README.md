# Airport-API-Service
The Airport API service is a Django REST-based project designed to track flights from airports around the world. 
This API allows you to get information about airports, planes, flights, routes. 
This makes it an effective tool for managing and analyzing flight data. 
A registered user can purchase air tickets.

## Features of the project:
- **Restriction of information**: 
The information exchanged between the administrator and the regular user is restricted 
so that the user has access to only the information to which he is entitled.

- **Airport Information**: 
Get data on airports around the world, including names, airport codes, nearest major cities and countries.

- **Route Information**: 
Provides information about various routes, including the names of departure and destination airports 
and the distance between them.

- **Aircraft Information**: 
Get information about the name and type of aircraft, 
the number of rows for passengers and the number of seats in each row. 
It has a built-in function for downloading and storing aircraft images.

- **Flight Information**: Get flight details including route,
departure and arrival times, aircraft information, and seat availability. 
Ability to filter the list of flights by departure and arrival date.


- **Order Information**: 
Allows authenticated users to check their orders.

- **Ticket Information**: 
Allows you to add flight tickets specifying a specific row and seat number to the order.

- **Authentication**: 
User can create a profile by entering email address and password. 
API is secured by JWT (JSON Web Tokens) authentication to protect sensitive flight data.

## Installing using GitHub

Before you begin, ensure you have met the following requirements:
Install PostgresSQL and create db


## Installation
Clone the repository:
git clone https://github.com/romkapomka12/Airport-API-Service

```shell
cd airport-api-service

python -m venv venv 
source venv/bin/activate(on macOS)

venv\Scripts\activate

pip install -r requirements.txt
```

## Configuration Environment Variables:
  - Rename a file name .env_sample to .env in the project root directory.
  - Make sure to replace all enviroment keys with your actual enviroment data:

```shell
set POSTGRES_HOST=< db host name >
set POSTGRES_NAME=< db name >
set POSTGRES_USER=< db username >
set POSTGRES_PASSWORD=< password db >
set SECRET_KEY=< secret key >
```

```shell
python manage.py migrate

```
```shell
python manage.py runserver
```

# RUN with Docker

Docker should bу installed

```shell
docker-compose build
```
```shell
docker-compose up
```


# Getting access
 - create user api/user/register/
 - get access token api/user/token/

