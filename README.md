# App service
This repository contains the backend app service our REMLA25 project.

# Usage
```sh
# Clone repository 
git clone git@github.com:remla25-team13/app-service.git
cd app-service

# Build docker image
docker build -t app-service .

# Run the image
docker run -it --rm -p 5000:5000 app-service
```

Or, you can use the [hosted image](https://github.com/remla25-team13/app-service/pkgs/container/app-service).
```sh
# Pull image
docker pull ghcr.io/remla25-team13/app-service:0.1.0

# Run image
docker run -it --rm -p 5000:5000 ghcr.io/remla25-team13/app-service:0.1.0
```
