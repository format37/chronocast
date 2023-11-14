sudo docker stop site
sudo docker rm site
#   --restart always \  
#   -d \
sudo docker run \
    --name site \
    --network host \
    -t site
