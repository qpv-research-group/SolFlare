# django-linode-deployment
# SolFlare

# Run using Docker

Docker is useful tool for building and deploying web applications. You can run Docker locally and use exactly the same tool when running on Linode; it simplifies things quite a bit. For example, you do not need to install a particular version of Python on Linode, you simply tell Docker which version of Python you need to run you code and it handles all the details.

To install Docker on the Linode:
* Ubuntu, https://docs.docker.com/engine/install/ubuntu
* Debian, https://docs.docker.com/engine/install/debian

To install locally download the Docker application:
* macOS, https://www.docker.com/products/docker-desktop

## Build and run the Docker image

You whole application will become a Docker "image" but we first need to build the image.

You can do this on the Linode or locally and the instructions are exactly the same. Change directory so your Django files are in the current working directory of the shell e.g. `cd /usr/dan/mycode` so when you do `ls` you can see the `"Dockerfile"` in the local directory.

To build the image,

    docker build --no-cache -t solflare-app .

To run the application locally,

    docker run -it -p 8000:8000 solflare-app

Kill the terminal to quit the application.

To run the application on Linode you want to run in the background so include the extra commands,

    docker run -it -p 8000:8000 -d solflare-app

Open your browser to http://localhost:8000/siliconabsorption to see the application locally. Replace with Linode IP address to access online.

# Azure Container Deploy

Deployment to Azure is currently manual, documenting the steps here, eventually we can automate this.

Ensure code is update to date and we are on the pero_si branch,

    git checkout pero_si
    git pull

We need to run on x86 processors but I am building on an M2 Mac,

    docker buildx build --platform linux/amd64 --tag solflareauseast.azurecr.io/samples/test1 --no-cache .

Finally, push to the container repo.

    docker push solflareauseast.azurecr.io/samples/test1
    
    
