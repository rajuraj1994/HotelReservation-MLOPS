pipeline{
    agent any
    stages{
        stage("Cloning the github repository to jenkins"){
            steps{
               script{
                echo "Cloning the github repository to jenkins"
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/rajuraj1994/HotelReservation-MLOPS']])
               }
            }
        }
    }
}