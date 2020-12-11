#!/bin/bash
if ! grep -q "SECRET_KEY=" ".env"; then
    key="$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)"
    echo -e "\nSECRET_KEY=${key}" >> .env
fi
if ! grep -q "POSTGRES_URI=" ".env"; then
    key="postgresql://dev:dev@db:5432/dev"
    echo -e "\nPOSTGRES_URI=${key}" >> .env
fi
if ! grep -q "JWT_SECRET=" ".env"; then
    key="$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)"
    echo -e "\nJWT_SECRET=${key}" >> .env
fi
if ! grep -q "WEBSERVICE_URL=" ".env"; then
    key="http://172.17.0.1:8001"
    echo -e "\nWEBSERVICE_URL=${key}" >> .env
fi
if ! grep -q "COURIER_TOKEN=" ".env"; then
    key="$(python jwt_gen.py)"
    echo -e "\nCOURIER_TOKEN=${key}" >> .env
fi
docker-compose up --build
