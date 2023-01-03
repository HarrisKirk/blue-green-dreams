#!/bin/bash
# 
# Launch and test the container
#
TMP_SITE_OUT=/tmp/gwa_site.out
CONTAINER_NAME="gwa"
docker container rm -f $CONTAINER_NAME 2> /dev/null
container_id=$(docker container run --rm -it --name $CONTAINER_NAME --network host --detach cjtkirk1/gwa:latest)
sleep 2
rm -f $TMP_SITE_OUT 
curl --silent -o $TMP_SITE_OUT http://0.0.0.0:8000
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "[ERROR] flask server is not responding"
    echo "" 
    exit 1
fi
grep --silent "Hello World" $TMP_SITE_OUT
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "[ERROR] Invalid ~/site result"
    docker logs ${container_id}
    cat $TMP_SITE_OUT
    echo "" 
    exit 1
fi

# clean up 
docker container rm -f ${container_id} >/dev/null
rm -f $TMP_SITE_OUT 
echo "Tests Passed"
