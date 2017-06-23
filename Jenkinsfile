pipeline {
    agent any
    stages {
        stage('Ansible') {
            steps {
                sh 'echo "Figure out ansible syntax for pipeline"; exit 0'
            }
        }
        stage('Test') {
            steps {
                sh 'echo "Fail!, commit hook working yet?"; exit 1'
            }
        }
        stage('Build') {
            steps {
                sh 'echo "Build stage"; exit 0'
            }
        }
    }
    post {
        always {
            echo 'Always'
        }
        success {
            echo 'successful'
        }
        failure {
            echo 'failed'
        }
        unstable {
            echo 'unstable'
        }
        changed {
            echo 'This will run only if the state of the Pipeline has changed'
            echo 'For example, if the Pipeline was previously failing but is now successful'
        }
    }
}
