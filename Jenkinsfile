pipeline {
    agent any

    environment {
        SECRET_KEY = credentials('SECRET_KEY')

        DEBUG = 'False'
        ALLOWED_HOSTS = '*'
        CORS_ALLOW_ALL_ORIGINS = 'True'

        DB_ENGINE = 'django.db.backends.sqlite3'
        DB_NAME = 'fouzi'
        DB_USER = 'postgres'
        DB_PASSWORD = credentials('DB_PASSWORD')
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
    }

    stages {
        stage('Show Environment Info') {
            steps {
                sh 'echo "Starting Django Jenkins Pipeline"'
                sh 'pwd'
                sh 'ls -la'
                sh 'python3 --version'
            }
        }

        stage('Create Virtual Environment') {
            steps {
                sh 'python3 -m venv venv'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '. venv/bin/activate && python -m pip install --upgrade pip'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Verify Installed Packages') {
            steps {
                sh '. venv/bin/activate && pip show python-dotenv'
                sh '. venv/bin/activate && pip show Django'
            }
        }

        stage('Run Django Check') {
            steps {
                sh '. venv/bin/activate && python manage.py check'
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