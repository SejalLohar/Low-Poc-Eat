properties([
  pipelineTriggers([]),
  durabilityHint('PERFORMANCE_OPTIMIZED')
])

pipeline {

    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: dind
    image: docker:dind
    securityContext:
      privileged: true
    command: ["dockerd-entrypoint.sh"]
    args:
      - "--host=tcp://0.0.0.0:2375"
      - "--insecure-registry=nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""
    - name: DOCKER_HOST
      value: "tcp://localhost:2375"
    volumeMounts:
    - name: workspace-volume
      mountPath: /home/jenkins/agent

  - name: sonar-scanner
    image: sonarsource/sonar-scanner-cli
    command: ["cat"]
    tty: true
    volumeMounts:
    - name: workspace-volume
      mountPath: /home/jenkins/agent

  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["sh", "-c", "while true; do sleep 30; done"]
    tty: true
    volumeMounts:
    - name: workspace-volume
      mountPath: /home/jenkins/agent

  volumes:
  - name: workspace-volume
    emptyDir: {}
"""
        }
    }

    options { skipDefaultCheckout() }

    environment {
        DOCKER_IMAGE = "lowpoceat"
        SONAR_TOKEN = "sqp_de0f929207bf50997ecf801ea0fd5cb41f4ae684"
        REGISTRY_HOST = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
        REGISTRY = "${REGISTRY_HOST}/2401116"
        NAMESPACE = "2401116"
    }

    stages {

        stage('Checkout Code') {
            steps {
                deleteDir()
                sh "git clone https://github.com/SejalLohar/Low-Poc-Eat.git ."
                echo '✔ Source code cloned successfully'
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh """
                        echo '🔧 Waiting for Docker daemon...'
                        until docker info >/dev/null 2>&1; do
                          echo 'Docker not ready, waiting 5s...'
                          sleep 5
                        done
                        echo '🐳 Docker ready! Building image...'
                        docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -t ${DOCKER_IMAGE}:latest .
                        docker image ls
                    """
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    sh """
                        sonar-scanner \
                          -Dsonar.projectKey=Low-Poc-Eat \
                          -Dsonar.projectName=Low-Poc-Eat \
                          -Dsonar.host.url=http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000 \
                          -Dsonar.python.coverage.reportPaths=coverage.xml \
                          -Dsonar.token=${SONAR_TOKEN}
                    """
                }
            }
        }

        stage('Login to Nexus') {
            steps {
                container('dind') {
                    sh """
                        echo '🔐 Logging into Nexus...'
                        docker login ${REGISTRY_HOST} -u admin -p Changeme@2025
                    """
                }
            }
        }

        stage('Push Image') {
            steps {
                container('dind') {
                    sh """
                        echo '⬆ Pushing image to Nexus...'
                        docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER}
                        docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${REGISTRY}/${DOCKER_IMAGE}:latest
                        docker push ${REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER}
                        docker push ${REGISTRY}/${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

        stage('Deploy MySQL Database') {
            steps {
                container('kubectl') {
                    sh """
                        echo '📌 Deploying MySQL first...'
                        kubectl apply -f k8s/mysql-secret.yaml -n ${NAMESPACE}
                        kubectl apply -f k8s/mysql-deployment.yaml -n ${NAMESPACE}
                        kubectl apply -f k8s/mysql-service.yaml -n ${NAMESPACE}
                        kubectl rollout status deployment/mysql -n ${NAMESPACE} --timeout=120s || true
                    """
                }
            }
        }

        stage('Deploy Application') {
            steps {
                container('kubectl') {
                    sh """
                        echo '🚀 Deploying Application...'
                        kubectl apply -f k8s/deployment.yaml -n ${NAMESPACE}
                        kubectl apply -f k8s/service.yaml -n ${NAMESPACE}
                        kubectl rollout status deployment/lowpoceat-app -n ${NAMESPACE} --timeout=120s || true
                    """
                }
            }
        }

    }  // ← Correctly closing `stages`

    post {
        success { echo "🎉 Pipeline completed successfully!" }
        failure { echo "❌ Pipeline failed" }
        always  { echo "🔄 Pipeline finished" }
    }
}
