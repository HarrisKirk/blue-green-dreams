container_id=$(docker run --rm --name gwa --detach cjtkirk1/gwa:latest)
echo "The container_id is '${container_id}'"
sleep 3
docker logs ${container_id}
docker container rm -f ${container_id}

