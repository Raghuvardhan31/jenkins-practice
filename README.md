To run backend

step1 : git clone https://github.com/PO-ArifMohammad/intern-otms

step2 : cd backend

step3 : create virtual environment (in BMS folder)
      1 : python -m venv env
      2 : env\Scripts\activate

step4 : install libraries
      pip install -r requirements.txt

step5 : connect to database
       change credentials in settings.py
       DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'tanvox_db',
            'USER': 'postgres',
            'PASSWORD': '123456',
            'HOST': 'localhost',
            'PORT': '5432',
               }
        }

step5 : apply all migrations
     1 : python manage.py makemigrations
     2 : python manage.py migrate

step6 : run server on ipaddress
     python manage.py runserver 0.0.0.0:8000