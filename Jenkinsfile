pipeline{
    agent any

    environment{
        VENV_DIR = 'venv'
    }
    stages{
        stage("Cloning the github repository to jenkins"){
            steps{
               script{
                echo "Cloning the github repository to jenkins"
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/rajuraj1994/HotelReservation-MLOPS']])
               }
            }
        }
        stage('Setting up our Virtual Environment and Installing dependancies'){
            steps{
                script{
                    echo 'Setting up our Virtual Environment and Installing dependancies............'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }

    }
}