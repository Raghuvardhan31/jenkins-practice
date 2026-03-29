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
                sh 'echo "Current Directory:"'
                sh 'pwd'
                sh 'echo "Files in Workspace:"'
                sh 'ls -la'
                sh 'echo "Git Version:"'
                sh 'git --version'
            }
        }
    }
}
