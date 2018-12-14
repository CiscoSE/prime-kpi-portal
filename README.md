**Prime KPI Portal**

Portal for Access Point KPIs taken from Prime Infrastructure. 

HTML user interface works better in Chrome and Firefox

Contacts:

* Vince Pandolfi ( vpandolf@cisco.com )
* Santiago Flores ( sfloresk@cisco.com )


**Source Installation**

It might make sense for you to create a Python 3.7 Virtual Environment before installing the requirements file. For information on utilizing
a virtual environment please read http://docs.python-guide.org/en/latest/dev/virtualenvs/. Once you have a virtual environment active then
install the packages in the requirements file.

`(virtualenv) % pip install -r requirements.txt
`

You will need to set up the following env variables:
```
DB_HOST 
DB_PORT
DB_NAME
DB_PASSWORD
DB_USER
PRIME_URL
PRIME_USER
PRIME_PASSWORD
```

You can also set the variables modifying the envs.py file

The next step is to install the database, at this moment only postgresql is supported. The easiest way is to run a container:

```bash
docker run -p 5432:5432 -d --name primekpiportaldb postgres

```

Then, create the database:

```bash
# Open a bash shell into the container
docker exec -it primekpiportaldb /bin/bash

# Get into the database
psql --user postgres

# Create database 
CREATE DATABASE kpiportal2;

# Use "\q" to exit the database
```

Finally, run the the application executing in the root directory of the distribution:
 - python manage.py makemigrations
 - python manage.py migrate
 - python manage.py runserver 0.0.0.0:8080
 
Open a browser to http://0.0.0.0:8080 to access the portal

