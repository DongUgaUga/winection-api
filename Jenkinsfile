pipeline {
    agent any

    environment {
        DEEPSEEK_API_KEY = credentials('deepseek_api_key')
        GOOGLE_CLOUD_API_KEY = credentials('google_cloud_api_key')
        PROJECT_ID = credentials('project_id')
        DISCORD = credentials('discord_webhook')
    }

    post {
            success {
                discordSend description: "알림테스트", 
                    footer: "빌드가 성공했습니다.", 
                    link: env.BUILD_URL, result: currentBuild.currentResult, 
                    title: "테스트 젠킨스 job", 
                    webhookURL: env.DISCORD
            }
            failure {
                discordSend description: "알림테스트", 
                    footer: "빌드가 실패했습니다.", 
                    link: env.BUILD_URL, result: currentBuild.currentResult, 
                    title: "테스트 젠킨스 job", 
                    webhookURL: env.DISCORD
            }
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/DongUgaUga/winection-api.git'
            }
        }

        stage('Setup') {
            steps {
                script {
                    sh '''
                    echo "DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY" > .env
                    echo "GOOGLE_CLOUD_API_KEY=$GOOGLE_CLOUD_API_KEY" >> .env
                    echo "PROJECT_ID=$PROJECT_ID" >> .env
                    chmod 600 .env
                    '''
                }
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