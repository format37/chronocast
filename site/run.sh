sudo docker stop site
sudo docker rm site
#   --restart always \  
#   -d \
# --network host \
sudo docker run \
    --name site \
    -p 443:443 \
    -t site
