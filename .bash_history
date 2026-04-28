yum install docker -y
mkdir nodejs
ll
cd nodejs
ll
vim index.js
vim package.json
vi Dockerfile
docker build -t hotel-app .
systemctl start docker
docker build -t hotel-app .
docker image
docker images
docker run -p 3000:3000 hotel-app
