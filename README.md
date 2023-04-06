# project1-shad-khan Website: https://twilight-pond-7871.fly.dev
## How to run Locally
## The technology used for this project was the deployment system fly.io to deploy a website
### The flask framework was used to run a local server for testing and render the html onto the website. This includes jinja2 which is used to add variables into the html.
### The libraries used were requests, dotenv, json, flask, os, random, wtforms, brypt, and sqlalchemy. Requests was used to get requests from the apis, dotenv was used to find and load the api key, json was used to access the data form the apis, flask allows the usage of the Flask framwork, os is to get the api key andrandom is used to generate a random number, wtforms allows easy access to form information, bcrypt enables encryption and decrytion for passwords, and sqlalchemy lets one conncect to a database. The apis used were the TMDB api to get movie data and the wikimedia api to get the wikipedia page.
### In order to run the app locally you will need to create an TMDB api key, secret cookie key, and a databse url and place it in a .env file 
### like this : TMDB_API_KEY={your_api_key} , COOKIE_KEY={your_key}, DATABASE_URL={url}
### You will also need to download the required packages listed in the requirements.txt file
### Finally you will need to add app.run() as the final line in the project1.py file

## Technical Problems
### Project would not deploy to fly.io, this was solved by just waiting something was wrong on their end.
### Figuresing out the encrytion for the passwords this was solved by googling
## Experience
### Deploying was harder than it should have been but that was due to an error on their end so it was frustrating