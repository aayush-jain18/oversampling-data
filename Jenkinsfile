pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Install requirements') {
            steps {
                // install all requirements listed in requirements.txt
                sh "pip install -r requirements.txt"
            }
        }
        stage('run') {
            steps {
                sh 'python synthetic-data-generation'
            }
        }
    }
}
