pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        //stage('Install requirements') {
            //steps {
                // //install all requirements listed in requirements.txt
                //bat "pip install -r requirements.txt"
            //}
        //}
        stage('run') {
            steps {
                bat "python synthetic-data-generation"
            }
        }
    }
}
