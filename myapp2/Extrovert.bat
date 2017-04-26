cd %cd%
python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations login
python manage.py migrate login
python manage.py runserver | start "" http://127.0.0.1:8000/