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
                    echo "Python path:"
                    which python3 || true
                    echo "Python version:"
                    python3 --version || true
                    echo "Available python binaries:"
                    ls -l /usr/bin/python* || true
                '''
            }
        }

        stage('Check python3-venv Support') {
            steps {
                sh '''
                    echo "Checking whether venv module works..."
                    python3 -m venv --help > /dev/null 2>&1 || {
                        echo "ERROR: python3 venv support is missing on Jenkins server."
                        echo "Install it on Ubuntu/Debian using:"
                        echo "sudo apt update && sudo apt install -y python3.12-venv"
                        exit 1
                    }
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
                    ${VENV_DIR}/bin/pip show python-dotenv || true
                    ${VENV_DIR}/bin/pip list
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