**PYTHON 3.6**


**Tasks Completed:**

1. CRUD API for Shop
2. Rest-ful APIs for shipments and shipment-details.
3. Authentication using access-token generated from client-id and client-secret

**Tasks TBD:**

1. Need to write test cases.
2. Error handling mechanism. (along with creating a custom exception handler)
3. Proper structured response data. (creating a custom renderer)


**Assumptions Taken:**
Assumed that multiple Shipments can have same Transporter, Customer and Billing Details.
Shops to be synced will be more the 20. IF they are less, then the current logic written will take more time than expected.
 

**Deployment Steps:**

Firstly create a DB.

1. Clone the repo:      
   git clone https://github.com/Raghava-NR/boloo-assignment.git
2. Navigate to the _boloo_ folder present in the project.
3. Create a virtualenv using python 3.6:
   _python3 -m venv env_name_
4. Activate the virtualenv:
   _source env_name/bin/activate_
5. Install requirements:
   _pip install -r requirements.txt_
6. Create a config file with name config.ini:
   _touch config.ini_
7. Edit the config.ini with the required values. Sample is shown below.
   
   _[main]
   secret_key = project_secret_key
   
   [database_default]
   host = 127.0.0.1
   name = db_name
   user = user_name
   password = user_password_
   
8. Run migrations and migrate:
   ./manage.py makemigrations
   ./manage.py migrate
   
9. Run server:
   _./manage.py runserver_
   
   
To run redis and celery:
redis: _redis-server_
celery: navigate to project file, activate venv and run _celery worker -A boloo --loglevel=INFO --concurrency=4 -n worker1_
set concurrency to no.of cpu cores