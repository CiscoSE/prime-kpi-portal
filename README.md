**Prime KPI Portal**

Portal for Access Point KPIs taken from PRIME Infrastructure. 

HTML user interface works better in Chrome and Firefox

Contacts:

* Vince Pandolfi ( vpandolf@cisco.com )
* Santiago Flores ( sfloresk@cisco.com )


**Source Installation**

Usually will be something like below:

As this is a Django application you will need to either integrate the application in your production environment or you can
get it operational in a virtual environment on your computer/server. In the distribution is a requirements.txt file that you can
use to get the package requirements that are needed. The requirements file is located in the root directory of the distribution.

It might make sense for you to create a Python Virtual Environment before installing the requirements file. For information on utilizing
a virtual environment please read http://docs.python-guide.org/en/latest/dev/virtualenvs/. Once you have a virtual environment active then
install the packages in the requirements file.

`(virtualenv) % pip install -r requirements.txt
`

You will need to set up the following env variables:
```
DB_HOST #Only postgresql is supported
DB_PORT
DB_NAME
DB_PASSWORD
DB_USER
PRIME_URL
PRIME_USER
PRIME_PASSWORD
```


After your sourced the env variables, run the the application executing in the root directory of the distribution:
 - python manage.py makemigrations
 - python manage.py migrate
 - python manage.py runserver 0.0.0.0:YOUR_PORT

