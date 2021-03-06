# Paczka+

Heroku: paczkaplus.herokuapp.com

### Setup (1st method)
1. Just run this script (basic .env will be generated for you)
```
rundocker.sh
```

If you want to use Auth0, provide additional variables (from auth0.com) in .env file:
```
AUTH0_CLIENT_ID=
AUTH0_CLIENT_SECRET=
AUTH0_API_BASE_URL=
AUTH0_DOMAIN=
API_IDENTIFIER=
``` 

### Setup (2nd method)
1. Create `.env` file with these variables:
```
POSTGRES_URI=postgresql://dev:dev@db:5432/dev
WEBSERVICE_URL=http://172.17.0.1:8001
AUTH0_CALLBACK_URL=http://localhost:8000/callback
SECRET_KEY=             #long random string
JWT_SECRET=             #long random string
AUTH0_CLIENT_ID=        #from auth0.com
AUTH0_CLIENT_SECRET=    #from auth0.com
AUTH0_API_BASE_URL=     #from auth0.com (url needs 'https://' at the start!)
AUTH0_DOMAIN=           #from auth0.com
API_IDENTIFIER=         #from auth0.com

```
2. Run with docker compose
```
docker-compose build
docker-compose up
```

### Usage

web application for sender: 
https://localhost

shell app for delivery person:
```
./runcourierapp.sh
```

