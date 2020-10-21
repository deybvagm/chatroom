# Browser-Based Chat Application
The goal of this exercise is to create a simple browser-based chat application using Python

This application allow several users to talk in a chatroom and also to get stock quotes
from an API using a specific command (`/stock=STOCK_CODE`). This command is intercepted by a bot that performs the corresponding query to a web API

## Approach
In order to keep the communication active between all browsers (users) within the chatroom, `Webscokets are used`.
Since all participants could send and receive messages, and also the bot can listen to specific commands, an event based approach is used to solve the case. In particular the message broker RabbitMQ is used to allow users and the bot publishing messages but also subscribe to messages from other participants. Here is the detail:
- Web participants can publish information to the topic `public` but also can subscribe to this topic in order to get other user messages
- The bot listen to the topic `/stock` and publish to the topic `public` in order to make the message public to other participants

The authentication mechanism that validate user credentials was built using one of the most advanced hashing algorithms, according to OWASP, the `Argon2id` algorithm. [Here you can find more information](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)  
   
## Setup
This project needs to following components to work properly:
- The RabbitMQ server. Using docker, you can start the server with the command:
`docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management`
- A postgres database. The connection params can be configured in the yaml configuration file. Below are the commands (linux) to create the database, the user and the privileges for the user on the database (assuming you have a database already installed):
```bash
sudo -u postgres psql;
create database chatroomdb;
create user chatroom with encrypted password chatroom;
grant all privileges on database chatroomdb to chatroom;

CREATE TABLE participant(
   id SERIAL PRIMARY KEY,
   username VARCHAR NOT NULL,
   password VARCHAR NOT NULL
);

CREATE TABLE message (
   id SERIAL PRIMARY KEY,
   username VARCHAR NOT NULL,
   message VARCHAR NOT NULL,
   date timestamp NOT NULL
);
```  
- To add users to the database, it is necessary to execute the script `create_user` in the following way:

`python create_user.py -u my_username -p my_password`    
 

## Running instructions
1. In order to execute the application, all the dependencies must be installed. They could be installed with the command:
`pip install -r requirements.txt`

2. In order to run the app, a RabbitMQ instance should be running. The configuration files define a local configuration. In my case I used docker to get a running RabbitMQ server. The command is as follows:
`docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management` 

3. Once RabbitMQ is running, the web application could be launched with the following command:
`python app.py`

4. The bot could be launched with the following command:
`python bot.py`

5. Now the application could be used. Open the browser on the url `http://localhost:9091`

6. Login with one of the previous registered users (executing the script `create_user` as explained above):


 
Note: The configuration files could be edited to change the default settings

## Running test
The following command executes the tests under the module `/tests`:
```
python -m unittest discover -s tests

``` 

## Satisfied Requirements
- Allow registered users to log in and talk with other users in a chatroom. 
- Allow users to post messages as commands into the chatroom with the following format
`/stock=stock_code`. To test The functionality to could put the command `/stock=aapl.us` 
- The bot request an external API and extracts the data to build a message like "APPL.US quote is $93.42 per share". The post owner is the bot
the chatroom using a message broker like RabbitMQ
- Chat messages are ordered by their timestamps and show only the last 50
- Unit test are added for the main functionality.


## Project structure
The following is the project structure, focusing only on the main components

```
Chatroom
│   readme.md
│   app.py
|   bot.py
|   containers.py
|   ...    
│
└───config
│   │   config.yml
│   │   config_bot.yml
│   │
└───handlers
│   │   auth.py
│   │   bot_handler.py
|   |   chat_participant
|   |   ws_handler
│   |
└───rabbitmq
|    │   pubsub.py
└───static
└───template
└───tests
    
```

The main components are listed below:
- `app.py`: Executes the web application which allows users to join the chatroom. Also serves the static files. In order to join the chatroom a web browser should be opened in the url `http://localhost:9091`. When the websocket connection is established, the rabbitmq is also launched 
- `bot.py`: Launches the bot as a decoupled component also connecting to the rabbitmq component 

- `config/config.yml`: Defines the configuration for web participants. Most the configuration is related to the RabbitMQ params
- `config/config_bot.yml`: Defines the configuration for the bot. Includes RabbitMQ configuration but also things like the api URL

- `handlers/`: Contains all the modules that perform the heavy work. Specificaly, contains handlers for websocket, handlers for the bot, for authentication.
- `rabbitmq/pubsub`: Contains the client to the RabbitMQ component
- `static/`: Contains js and css code for the front end
- `templates/`: Contains the html page for the Chatroom
- `tests/`: Contains tests and files required to perform the unit tests 