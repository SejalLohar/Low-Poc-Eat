pipeline {
    agent any

    environment {
        SONAR_SCANNER = tool 'SonarScanner'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/SejalLohar/health-diet-app.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarServer') {
                    sh "sonar-scanner"
                }
            }
        }

        stage('Docker Build & Deploy Locally') {
            steps {
                sh 'docker-compose down || true'
                sh 'docker-compose up -d --build'
            }
        }
    }
}
