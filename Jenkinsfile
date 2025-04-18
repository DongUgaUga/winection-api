pipeline {
    agent any

    environment {
        OPENAI_API_KEY = credentials('openai_api_key')
        GOOGLE_CLOUD_API_KEY = credentials('google_cloud_api_key')
        PROJECT_ID = credentials('project_id')
        DISCORD = credentials('discord_webhook')

        DB_USER = credentials('db_user')
        DB_PASSWD = credentials('db_passwd')
        DB_PORT = credentials('db_port')
        DB_HOST = credentials('db_host')
        DB_NAME = credentials('db_name')
        SECRET_KEY = credentials('secret_key')
    }

    stages {
        stage('Start Notification') {
            steps {
                script {
                    discordSend description: "젠킨스 배포를 시작합니다!", 
                        link: "${env.BUILD_URL}console", 
                        title: "${env.JOB_NAME} : ${currentBuild.displayName} 시작", 
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
                    echo "OPENAI_API_KEY=$OPENAI_API_KEY" > .env
                    echo "GOOGLE_CLOUD_API_KEY=$GOOGLE_CLOUD_API_KEY" >> .env
                    echo "PROJECT_ID=$PROJECT_ID" >> .env
                    echo "DB_USER=$DB_USER" >> .env
                    echo "DB_PASSWD=$DB_PASSWD" >> .env
                    echo "DB_PORT=$DB_PORT" >> .env
                    echo "DB_HOST=$DB_HOST" >> .env
                    echo "DB_NAME=$DB_NAME" >> .env
                    echo "SECRET_KEY=$SECRET_KEY" >> .env
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
            discordSend description: """
                        제목 : ${currentBuild.displayName}
                        결과 : ${currentBuild.result}
                        실행 시간 : ${currentBuild.duration / 1000}s
                        """, 
                    footer: "빌드 성공!", 
                    link: "${env.BUILD_URL}console", result: currentBuild.currentResult, 
                    title: "${env.JOB_NAME} : ${currentBuild.displayName} 성공", 
                    webhookURL: env.DISCORD
        }
        failure {
            script {
                discordSend description: """
                        제목 : ${currentBuild.displayName}
                        결과 : ${currentBuild.result}
                        실행 시간 : ${currentBuild.duration / 1000}s
                        """, 
                    footer: "⚠️ 빌드 실패 : 상세 로그는 링크 들어가서 확인하세요 ⚠️", 
                    link: "${env.BUILD_URL}console", result: currentBuild.currentResult, 
                    title: "${env.JOB_NAME} : ${currentBuild.displayName} 실패", 
                    webhookURL: env.DISCORD
            }
        }
    }
}