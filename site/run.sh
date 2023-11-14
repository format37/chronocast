sudo docker stop site
sudo docker rm site
#   --restart always \  
#   -d \
sudo docker run \
    -d \
    --name site \
    --network host \
    --restart always \    
    -t site
