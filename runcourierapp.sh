docker build courierapp/ -t koteckim-courierapp
docker run -it --network="host" --env-file .env koteckim-courierapp