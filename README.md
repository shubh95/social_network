*Social Networking App*

- To setup project, make sure you have already setup docker your local machine
- Save .env.dev on your local system in the root folder of project. You can take reference of what variables to define in .env.dev from demo.env.dev
- after setting up .env.dev, you can build docker container by running "docker compose up -d --build"
- Access the running project on 0.0.0.0:8000
- URL of postman collection is https://api.postman.com/collections/6493711-f811d88c-8d11-4021-9572-bc19ce191751?access_key=PMAT-01J98DF045NH35MCVGCAKS1KP7
- The docker for production build is maintained seperately, you just have to save .env.prod similar to .env.dev and run "docker compose -f ./docker-compose.prod.yml up -d --build"