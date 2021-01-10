docker build courierapp/ -t koteckim-courierapp
docker run -it --env-file .env koteckim-courierapp