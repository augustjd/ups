pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/augustjd/ups'
            }
        }
        stage('Install Requirements') {
            steps {
                sh 'python3.6 -mvenv env'
                sh 'env/bin/pip3.6 install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh 'env/bin/pytest --junitxml build/results.xml'
            }
        }
        stage('Collect Test Results') {
            steps {
                junit 'build/results.xml'
            }
        }
    }
}
