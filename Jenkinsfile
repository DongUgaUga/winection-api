pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/DongUgaUga/winection-api.git'
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sh "docker-compose down"
                    sh "docker-compose up -d --build api"
                }
            }
        }
    }
}