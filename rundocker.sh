#!/bin/bash
if ! grep -q "SECRET_KEY=" ".env"; then
    key="$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)"
    echo -e "\nSECRET_KEY=${key}" >> .env
fi
docker-compose up
