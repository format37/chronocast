# get id of running container with image name
container_id=$(sudo docker ps | grep chronocast_archiver | awk '{print $1}')
echo "container id: $container_id"
# get logs
sudo docker logs -f -t $container_id
# connect to container
# sudo docker exec -it $container_id /bin/bash
