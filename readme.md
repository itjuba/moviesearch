# Movie Search Tool Backend Service

## Introduction

This backend service is designed to provide a movie search tool that allows users to search for movies. The service retrieves movie data from a third-party provider through their API endpoint. This README provides an overview of the project, its goals, and bonus features, as well as instructions on how to use and deploy the service.
The user can register and obtain an access token, allowing them to interact with the app, search for movies, and upvote or downvote the

## Functionalities


*    Fetching movies and allowing users to upvote and downvote movies from the search results, with a feature for users to view the movies they've rated.
*    JWT authentication (register, login, and refresh token).
*    CORS configuration.
*    Data pagination.
*    Containerization with Docker.


## Tools Used:

*    Docker and Docker Compose. 
*    FastAPI Python framework.
*    PostgreSQL relational database.
*    Pydantic for serialization and data validation.
*    SQLAlchemy ORM.
*    FastAPI JWT Auth Library.


## Future Improvements (Optional)

*   Implementing Caching (Redis): Introducing caching with Redis to optimize data retrieval and improve the service's performance.

*   Adding Unit Tests: Enhancing the codebase with comprehensive unit tests to ensure the reliability and stability of the service.

## AI Tools Utilization

    AI Tools: I used ChatGPT for code generation, optimization, commenting, and documentation processes.


## Database Initialization

This backend Service handles database initialization seamlessly during the Docker container startup. This process ensures that the required tables and schema are ready to store essential data. As part of this process, a SQL script is mounted to the PostgreSQL service, enabling the database to be set up and configured appropriately.



## How to Run

To run the Movie Search Tool Backend Service using Docker Compose, follow these steps:


### Setup

1. Add the environment Variables (`.env`)

In your `.env` file, you can use the following environment variables to configure the application:

        DATABASE_URL=postgresql://tigo:tigo@db:5432/tigo
        POSTGRES_USER=tigo
        POSTGRES_PASSWORD=tigo
        POSTGRES_DB=tigo
        SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7

2. Start the application using Docker Compose:

       docker-compose up -d

### Access the API

## Access the API

You can access the API at [http://localhost:8008](http://localhost:8008) in your web browser or via API clients like [Postman](https://www.postman.com/) or [curl](https://curl.se/).

For detailed API endpoints, request examples, and further information, please refer to the provided [http://localhost:8008/docs](http://localhost:8008/docs) .


