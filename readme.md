# Paczka+

Heroku: paczkaplus.herokuapp.com

### Setup
1. Create `.env` file with these variables:
```
SECRET_KEY=
POSTGRES_URI=
JWT_SECRET=
WEBSERVICE_URL=
COURIER_TOKEN=
```
2. Run with docker compose
```
docker-compose build
docker-compose up
```

Or just run this (.env will be generated for you)
```
./rundocker.sh
```
