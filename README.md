# Developing guidelines

## install python libraries

pip install -r requirements.txt

## initialize django application

1. python manage.py makemigrations
2. python manage.py migrate
3. python manage.py runscript generate_data
4. python manage.py runscript generate_jobs
5. python manage.py runserver
6. python manage.py qcluster

## Create local superuser

python manage.py createsuperuser

## API endpoints

http://localhost:8000/api/docs

## Generate random data for tests
```
python manage.py runscript delete_all_data

python manage.py runscript generate_data
```

## Test site

http://localhost:8000