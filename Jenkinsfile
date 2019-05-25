
pipeline {
     	// Clean workspace before doing anything
    agent any
    stages {
        //stage('Stage 0: Clone') {
            //git url: Globals.GitRepo
        //}
        //stage('Stage 1: Clean') {
            //posh 'Invoke-Build Clean'
        //}
        //stage('Stage 2: Dependencies') {
            //steps {
                // //install all requirements listed in requirements.txt
                //bat "pip install -r requirements.txt"
            //}
        //}
        stage('Run') {
            steps {
                bat "python synthetic-data-generation"
            }
        }
        stage('Archive'){
            steps{
                // This step should not normally be used in your script. Consult the inline help for details.
                archiveArtifacts artifacts: 'tests\\reports\\*', caseSensitive: false, defaultExcludes: false
            }
        }
        stage('Clean Workspace'){
             steps{
                  cleanWs()
             }
        }
    }   
}
