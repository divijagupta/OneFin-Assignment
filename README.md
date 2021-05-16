# Credy Assignment

## Versions and prerequisite
* Python 3.6.9
* Django 2.2
* sqliteDb


## Installation

 * Setup the virtual env using command and activate it.
   ```shell script
   virtualenv -p python3 env
   source env/bin/activate
   ``` 

 * Install requirements for the project.
   ```shell script
   pip install -r requirements.txt
   ```
   
 * Run migrations.
   ```shell script
   python manage.py migrate 
   ```
   
 * Set the environment variables value in credyassignment.env at the root and run command
   ```shell script
   source credyassignment.env
   ```
   
 * Run test cases.
   ```shell script
   python manage.py test 
   ``` 
   
 * Run server.
   ```shell script
   python manage.py runserver 
   ```
   
   
 