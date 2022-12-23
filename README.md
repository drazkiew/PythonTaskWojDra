# Python Task
This project is a Django app build according to the specifications described in [this page](https://gitlab.futuremind.dev/fm-public/python-task).

## Summary
This project containst code for a Django app with an REST API, which allows for:

- Uploading, changing size and setting a title of an image file in commonly used image formats.
- Retrieving stored image objects, which contain their title, size, as well as URI to download the associated image file.
- Searching for image objects by their titles.

App's API is documented via Swagger, which is exposed at the default page (URI "/") of the app, once it has been launched.

## Setup
Please follow steps below to launch this app:

### Project files
Clone this repository onto your local machine, open your system's command window, and navigate into the root folder of the project.

### Setting up virtual environment
To launch this app, you need to have [Python](https://www.python.org/) (3.9+) and [pip](https://pip.pypa.io/en/stable/getting-started/) installed on your machine.
Once that is done, create a [virtual environment for your project](https://docs.python.org/3/library/venv.html). Example:

```bash
python3 -m venv venv
```

And then activate it.

```bash
source venv/bin/activate
```

Once it's active, you can install the app's requirements using the following command:

```bash
pip install -r requirements.txt
```

### Setting up environmental variables
Inside project's root folder exists a file `.env_example`. Create a copy of it called `.env` and fill out its fields:

- **SECRET_KEY** - A secret key of your Django app. There are many ways of creating one, but here's an example how to generate one 
while in an active virtual environment:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- **DEBUG** - A variable that will activate or disable Django's debug mode. Can be either "True" or "False".

An example of a filled `.env` file:

```
SECRET_KEY=3yulqh_rtdzz*=86j_6&5$1(%1gz6(m7j!oh*2s7g(o*i2_e47
DEBUG=True
```

### Setting up PostgreSQL connection
The app expects a connection with a PostgreSQL database to work properly.
To set it up, a [connection service file](https://www.postgresql.org/docs/current/libpq-pgservice.html) must be created/modified (for examplen in Linux systems, you can create a `.pg_service.conf` file in your home directory).
Add the following declaration inside it:
```
[task_service]
host=HOST
user=USERNAME
dbname=DATABASE_NAME
port=PORT
```
And fill the fields with your database's connection parameters.

Next, inside project's root folder exists an example of a [password file](https://www.postgresql.org/docs/current/libpq-pgpass.html), called `.pgpass_example`: 
```
HOST:PORT:DB_NAME:USER:PASSWORD
```
Create a copy of it called `.pgpass`, and fill it with your database's connection parameters.
For `.pgpass` file to work properly, it needs to have specific permissions applied (0600). They can be set, using the following command:
```bash
chmod 0600 .pgpass
```

Examples of both files filled:
```
[task_service]
host=localhost
user=admin
dbname=pythontaskdb
port=5433
```
```
localhost:5433:pythontaskdb:admin:averysecurepassword1
```

### Migrate the database
Once the connection has been established, you can create all the required database structures using Django's manage tool:
```bash
python manage.py migrate
```

### Launch Django app
Once all the above steps have been completed, the app can be launched:
```bash
python manage.py runserver
```

## Testing
This project has tests written using PyTest. They are all located inside the `tests` folder. Tests will use a temporarily created SQLite database to test app's functionality.

To launch this app's tests, use the following command in project's root directory, inside its virtual environment:
```bash
pytest
```
