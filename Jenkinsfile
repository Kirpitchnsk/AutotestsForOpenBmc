pipeline {
    agent {
        docker {
            image 'python:3.10-slim'
            args '--privileged -v /dev/kvm:/dev/kvm'
        }
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                apt-get update && apt-get install -y qemu-system-arm
                pip install pytest pytest-html selenium
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                cd tests/webui
                pytest test_login.py --html=report.html
                '''
            }
        }

        stage('Deploy') {
            when { branch 'main' }
            steps {
                sh 'echo "Deploying to production..."'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'tests/**/report.html', fingerprint: true
        }
    }
}