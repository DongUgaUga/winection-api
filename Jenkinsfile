pipeline {
    agent any

    environment {
        DEEPSEEK_API_KEY = credentials('deepseek_api_key')
        GOOGLE_CLOUD_API_KEY = credentials('google_cloud_api_key')
        PROJECT_ID = credentials('project_id')
        DISCORD = credentials('discord_webhook')
    }

    stages {
        stage('Start Notification') {
            steps {
                script {
                    discordSend description: "🚀 젠킨스 배포를 시작합니다!", 
                        footer: "빌드 진행 중...", 
                        link: env.BUILD_URL, 
                        title: "젠킨스 빌드 시작", 
                        webhookURL: env.DISCORD
                }
            }
        }

        stage('Checkout') {
            steps {
                git branch: 'main', credentialsId: 'github_token', url: 'https://github.com/DongUgaUga/winection-api.git'
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

    post {
        success {
            discordSend description: "젠킨스 배포 완료!", 
                footer: "빌드 성공!", 
                link: env.BUILD_URL, result: currentBuild.currentResult, 
                title: "서버 배포 성공", 
                webhookURL: env.DISCORD
        }
        failure {
            script {
                def logs = currentBuild.rawBuild.join("\n")
                discordSend description: "젠킨스 빌드 실패", 
                    footer: "⚠️ 빌드 실패 로그 ⚠️\n```\n${logs}\n```", 
                    link: env.BUILD_URL, result: currentBuild.currentResult, 
                    title: "서버 배포 실패", 
                    webhookURL: env.DISCORD
            }
        }
    }
}