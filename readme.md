# Flight Booking Application using Microservices

This is a flight booking system implemented using Micro-Service Architecture. It consists of several microservices including Listing Service, Booking Service, Authentication Service, Notify Service, and API Gateway.

## Features
### Micro-Service Architecture: Implemented using 5 microservices:
- [Listing Service](ticket-listing-service)
- Booking Service
- Authentication Service
- Notify Service
- API Gateway
### RabbitMQ Message Queue Service: 
- Utilized for sending notifications to users. 
- The Notify Service interacts with RabbitMQ for reliable message delivery.


## Demo and Images


## Installation 
Follow instructions on [medium.com](https://medium.com/@xhefri/a-beginners-guide-to-creating-microservices-with-flask-a71f29c9647) to start and run the server

## Build Docker Container
`docker build -t flask_microservice .`

## Run the Docker Container
`docker run -p 5000:5000 flask_microservice`


## License

[MIT](https://choosealicense.com/licenses/mit/)