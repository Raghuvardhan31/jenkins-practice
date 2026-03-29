pipeline {
    agent any

    environment {
        SECRET_KEY = credentials('SECRET_KEY')
        DB_PASSWORD = credentials('DB_PASSWORD')

        DEBUG = 'False'
        ALLOWED_HOSTS = '*'
        CORS_ALLOW_ALL_ORIGINS = 'True'

        DB_ENGINE = 'django.db.backends.sqlite3'
        DB_NAME = 'fouzi'
        DB_USER = 'postgres'
        DB_HOST = 'localhost'
        DB_PORT = '5432'

        LANGUAGE_CODE = 'en-us'
        TIME_ZONE = 'UTC'
        USE_I18N = 'True'
        USE_TZ = 'True'

        MEDIA_ROOT = 'media'
        MEDIA_URL = '/media/'
        STATIC_URL = 'static/'
        DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
        ROOT_URLCONF = 'BMS.urls'
        WSGI_APPLICATION = 'BMS.wsgi.application'

        VENV_DIR = 'venv'
    }

    stages {
        stage('Show Environment Info') {
            steps {
                sh '''
                    echo "Starting Django Jenkins Pipeline"
                    pwd
                    ls -la
                    which python3
                    python3 --version
                '''
            }
        }

        stage('Create Virtual Environment') {
            steps {
                sh '''
                    rm -rf ${VENV_DIR}
                    python3 -m venv ${VENV_DIR}
                    test -x ${VENV_DIR}/bin/python
                '''
            }
        }

        stage('Upgrade Pip') {
            steps {
                sh '''
                    ${VENV_DIR}/bin/python -m pip install --upgrade pip setuptools wheel
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    ${VENV_DIR}/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Verify Installed Packages') {
            steps {
                sh '''
                    ${VENV_DIR}/bin/python --version
                    ${VENV_DIR}/bin/pip --version
                    ${VENV_DIR}/bin/pip show Django || true
                    ${VENV_DIR}/bin/pip show djangorestframework || true
                '''
            }
        }

        stage('Run Makemigrations') {
            steps {
                sh '''
                    ${VENV_DIR}/bin/python manage.py makemigrations --noinput
                '''
            }
        }

        stage('Run Migrate') {
            steps {
                sh '''
                    ${VENV_DIR}/bin/python manage.py migrate --noinput
                '''
            }
        }

        stage('Run Django Check') {
            steps {
                sh '''
                    ${VENV_DIR}/bin/python manage.py check
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    ${VENV_DIR}/bin/python manage.py test
                '''
            }
        }

        stage('Collect Static') {
            steps {
                sh '''
                    ${VENV_DIR}/bin/python manage.py collectstatic --noinput
                '''
            }
        }
        stage('Deploy Application (CD)') {
            steps {
                sh '''
                    echo "Starting Deployment..."

                    # Kill old running Django runserver
                    pkill -f "manage.py runserver" || true

                    # Start Django server in background
                    nohup ${VENV_DIR}/bin/python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &

                    echo "Deployment completed. Server started at port 8000"
                '''
            }
        }
                }

    post {
        success {
            echo 'Django pipeline completed successfully.'
        }
        failure {
            echo 'Django pipeline failed. Check Console Output.'
        }
        always {
            echo 'Pipeline execution finished.'
        }
    }
}