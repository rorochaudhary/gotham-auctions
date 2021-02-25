# gotham-auctions
The combination of average car prices increasing within recent years coupled with recent technological advancements abstracting the driver from the traditional feeling of 'connectedness' on the road leaves the modern car enthusiast wanting more. Enter Gotham Auctions, a full-stack car auction website that supports car enthusiasts finding the car of their dreams.

## Getting Started (Local Version)
These instructions will get you started with a local version of this app for which you can develop, explore, and test.

### Prerequisites
In order to run this app locally, you will at minimum need:
- a Code Editor/IDE (Microsoft Visual Studio Code, PyCharm, etc.)
- a recent version of [Python](https://www.python.org/downloads/) (3.6+) installed and configured
- [MySQL Server](https://dev.mysql.com/downloads/mysql/) installed and configured
- your favorite web browser (Chrome, Firefox, etc.)
- a terminal application (cmd, Powershell, Terminal, etc.)
- this repo cloned or forked into your computer

### Installing
From your terminal out of the root folder where this project is located, execute the command:
```
pip3 install -r requirements.txt
```
This will install the required dependencies (Flask, Jinja, etc.) that this app uses.
NOTE: If using a [virtual environment](https://docs.python.org/3/tutorial/venv.html) or [environment manager](https://docs.conda.io/en/latest/miniconda.html), make sure to have it activated before running the above command.

To setup and prepopulate the database, navgiate to your command-line out of the local project-folder base directory and access 'root' of your local SQL server (Windows Cmd Prompt shown here):
```
# open the mysql shell
mysqlsh

# enter \sql mode
\mysql

# connect to your local admin account (default is root)
\connect root@localhost

# enter your password (option to save pwd also presents)

# create the new database and setup the tables using our file
CREATE DATABASE gotham;
USE DATABASE;
source ./database/gotham_db.sql;
```

And last but not least, to have the app access this new database, get onto your code editor/IDE and open to the `gotham-auctions` project.
Create a new file titled `.env` into which you will add the following lines (feel free to copy/paste and replace with your info):
```
340DBHOST={localhost or name of your machine}
340DBUSER={root or admin}
340DBPW={your password used to login to MySQL}
340DB=gotham
```

### Running
At this point the app is ready to run. From `gotham-auctions` project root, open terminal (or within the code editor/IDE terminal), execute:
```
python3 app.py
```
Head over to http://127.0.0.1:9112/ to see the site. In the terminal, Flask will output the end url to which the app is currently active.

Thanks for interacting!

### Built With
- [Flask](https://palletsprojects.com/p/flask/) Python-based web framework (mainly back-end)
- [MySQL](https://dev.mysql.com/downloads/mysql/) database on which this app is built
- [Jinja2](https://jinja.palletsprojects.com/en/2.11.x/) webpage templating within Flask
- [Bootstrap](https://getbootstrap.com/) front-end styling

### Authors
A tag-team effort from [Rohit Chaudhary](https://github.com/rorochaudhary) and [Paldin Bet Eivaz](https://github.com/beteivap)

### Acknowledgements
Sources used throughout this app:
- [George Kochera](https://github.com/gkochera/CS340-demo-flask-app) Databases Course (CS 340) TA
- [Flask](https://flask.palletsprojects.com/en/1.1.x/tutorial/) tutorial
- [Boostrap](https://getbootstrap.com/docs/5.0/getting-started/introduction/) documentation
- [StackOverflow](https://stackoverflow.com/)
