pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/Asaf01/CICD_4Danimals_Wordpress'
        IMAGE_NAME = 'wordpress'
        DOCKERFILE_DIR = 'docker_ci'
        DOCKERHUB_CREDENTIALS = 'dockerhublogin'  
        DOCKERHUB_REPO = 'bendrorasaf/wordpress'

    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: "${REPO_URL}"
            }
        }

        stage('Determine Version') {
            steps {
                script {
                    def latestTag = sh(
                        script: """
                        curl -s https://hub.docker.com/v2/repositories/${DOCKERHUB_REPO}/tags/?page_size=1 | jq -r '.results[].name' | grep -E 'v[0-9]+' | sort -V | tail -n 1 | cut -d 'v' -f 2
                        """,
                        returnStdout: true
                    ).trim()

                    def versionNumber = latestTag ? latestTag.toInteger() + 1 : 1
                    env.VERSION = "v${versionNumber}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${DOCKERHUB_REPO}:${VERSION} ${DOCKERFILE_DIR}"
                }
            }
        }

        stage('Test Docker Image') {
    steps {
        script {
            sh 'echo "Testing the Docker image..."'
            sh 'docker run -d --name wordpress ${DOCKERHUB_REPO}:${VERSION}'
            sh 'docker stop wordpress'
            sh 'echo "Testing stage done !!!!"'
              }
           }
       }
        


        stage('Push Docker Image') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: "${DOCKERHUB_CREDENTIALS}", passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USERNAME')]) {
                        sh """
                        echo ${DOCKERHUB_PASSWORD} | docker login -u ${DOCKERHUB_USERNAME} --password-stdin
                        docker push ${DOCKERHUB_REPO}:${VERSION}
                        """
                    }
                }
            }
        }

        stage('Delete Workspace') {
            steps {
                deleteDir()
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
