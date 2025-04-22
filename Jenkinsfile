pipeline {
    agent any

    environment {
        BMC_URL = "https://127.0.0.1:2443"
        USERNAME = "root"
        PASSWORD = "0penBmc"
    }

    stages {
        stage('Setup Environment') {
            steps {
                sh '''
                    sudo apt-get update
                    sudo apt-get install docker.io
                    sudo systemctl start docker
                    sudo systemctl enable docker
                    docker pull jenkins/jenkins:lts
                    docker run -d -p 8080:8080 -p 50000:50000 --name jenkins -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
                    sleep 60 # Wait for Jenkins to start
                '''
                script {
                    sh 'pip install pytest requests selenium locust'
                }
            }
        }

        stage('Run OpenBMC in QEMU') {
            steps {
                sh '''
                    qemu-system-arm -m 256 -M romulus-bmc -nographic \
                    -drive file=romulus/obmc-phosphor-image-romulus-20250212052422.static.mtd,format=raw,if=mtd \
                    -net nic -net user,hostfwd=:0.0.0.0:2222-:22,hostfwd=:0.0.0.0:2443-:443,hostfwd=udp:0.0.0.0:2623-:623 \
                    -monitor telnet:127.0.0.1:5555,server,nowait -serial mon:stdio &
                    sleep 120 # Wait for OpenBMC to boot
                '''
            }
        }

        stage('Run API Tests') {
            steps {
                sh 'pytest test_redfish.py -v --junitxml=api_test_results.xml'
            }
            post {
                always {
                    junit 'api_test_results.xml'
                    archiveArtifacts artifacts: 'api_test_results.xml', fingerprint: true
                }
            }
        }

        stage('Run UI Tests') {
            steps {
                sh 'pytest openbmc_ui_tests.py -v --junitxml=ui_test_results.xml'
            }
            post {
                always {
                    junit 'ui_test_results.xml'
                    archiveArtifacts artifacts: 'ui_test_results.xml', fingerprint: true
                }
            }
        }

        stage('Run Load Tests') {
            steps {
                sh 'locust -f locustfile.py --headless -u 100 -r 10 --run-time 1m --html=load_test_report.html'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'load_test_report.html', fingerprint: true
                }
            }
        }
    }

    post {
        always {
            sh '''
                pkill qemu-system-arm || true
            '''
            cleanWs()
        }
    }
}