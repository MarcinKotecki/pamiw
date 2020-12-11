# Paczka+

Heroku: paczkaplus.herokuapp.com

### Setup
Just run this (.env will be generated for you)
```
./rundocker.sh
```

OR (the long way)

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

### Usage

web application for sender: 
localhost:8000

shell app for delivery person:
run from courierapp/
```
python app.py
```

