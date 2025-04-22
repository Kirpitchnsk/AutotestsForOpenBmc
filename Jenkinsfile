pipeline {
    agent any

    environment {
        BMC_URL = "https://127.0.0.1:2443"
        USERNAME = "root"
        PASSWORD = "0penBmc"
    }

    stages {
        stage('Check Docker') {
            steps {
                script {
                    try {
                        sh 'docker --version'
                    } catch (Exception e) {
                        error "Docker is not installed or not available. Please install Docker and make sure it's in PATH."
                    }
                }
            }
        }

        stage('Setup Jenkins') {
            steps {
                script {
                    // Проверяем, не запущен ли уже Jenkins
                    def jenkinsRunning = sh(script: 'docker ps -q --filter name=jenkins', returnStatus: true) == 0
                    if (!jenkinsRunning) {
                        sh '''
                            docker pull jenkins/jenkins:lts
                            docker run -d -p 8080:8080 -p 50000:50000 \
                                --name jenkins \
                                -v jenkins_home:/var/jenkins_home \
                                -v /var/run/docker.sock:/var/run/docker.sock \
                                jenkins/jenkins:lts
                            sleep 30
                        '''
                    }
                }
            }
        }

        // Остальные этапы остаются без изменений
        stage('Run OpenBMC in QEMU') {
            steps {
                sh '''
                    qemu-system-arm -m 256 -M romulus-bmc -nographic \
                    -drive file=romulus/obmc-phosphor-image-romulus-20250212052422.static.mtd,format=raw,if=mtd \
                    -net nic -net user,hostfwd=:0.0.0.0:2222-:22,hostfwd=:0.0.0.0:2443-:443,hostfwd=udp:0.0.0.0:2623-:623 \
                    -monitor telnet:127.0.0.1:5555,server,nowait -serial mon:stdio &
                    sleep 120
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
                docker stop jenkins || true
                docker rm jenkins || true
            '''
            cleanWs()
        }
    }
}