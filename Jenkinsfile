pipeline {
    agent any

    stages {
        stage('Checkout Info') {
            steps {
                echo 'Code pulled from GitHub successfully'
            }
        }

        stage('Build') {
            steps {
                sh 'echo "Hello from Jenkins Build Stage"'
            }
        }

        stage('Test') {
            steps {
                sh 'echo "Running test stage"'
            }
        }

        stage('System Info') {
            steps {
                sh 'echo "Current folder:"'
                sh 'pwd'
                sh 'echo "Files:"'
                sh 'ls -la'
                sh 'echo "Git version:"'
                sh 'git --version'
            }
        }
    }
}
