pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        // Keeping variables at the top makes maintenance easier
        IMAGE_NAME = "ghcr.io/rajuraj1994/hotelreservation-mlops:latest"
    }

    stages {
        stage("Cloning the github repository") {
            steps {
                script {
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/rajuraj1994/HotelReservation-MLOPS']])
                }
            }
        }

        stage('Environment Setup') {
            steps {
                script {
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }

        stage('Data Ingestion & Training') {
            steps {
                script {
                    // This runs on your Windows/Host machine network
                     sh '''
                     . ${VENV_DIR}/bin/activate
                     python pipeline/training_pipeline.py
                     '''
                     }
            }
        }

        stage('Build and Push to GHCR') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'github-token', passwordVariable: 'GH_TOKEN', usernameVariable: 'GH_USER')]) {
                        echo "Logging into GitHub Container Registry..."
                        sh 'echo $GH_TOKEN | docker login ghcr.io -u $GH_USER --password-stdin'
                        
                        echo "Building Docker Image..."
                        sh "docker build -t ${IMAGE_NAME} ."
                        
                        echo "Pushing Image..."
                        sh "docker push ${IMAGE_NAME}"
                        
                        echo "Cleaning up local images..."
                        sh "docker rmi ${IMAGE_NAME}"
                    }
                }
            }
        }
    }
}