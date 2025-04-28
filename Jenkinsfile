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
                    sudo apt install python3 python3-pip

                    sudo apt install qemu-system-arm

                    wget https://jenkins.openbmc.org/job/ci-openbmc/lastSuccessfulBuild/distro=ubuntu,label=docker-builder,target=romulus/artifact/openbmc/build/tmp/deploy/images/romulus/*zip*/romulus.zip
                    unzip romulus.zip

                    sudo apt install firefox
                    wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
                    tar -xvzf geckodriver-v0.34.0-linux64.tar.gz
                    sudo mv geckodriver /usr/local/bin/
                    sudo chmod +x /usr/local/bin/geckodriver
                '''
                script {
                    sh 'pip3 install pytest requests selenium locust'
                }
            }
        }

        stage('Run OpenBMC in QEMU') {
            steps {
                sh '''
                    IMAGE_FILE=$(find romulus/ -name "obmc-phosphor-image-romulus-*.static.mtd" -print -quit)
                    if [ -z "$IMAGE_FILE" ]; then
                        echo "Error: No matching image file found in romulus/" >&2
                        exit 1
                    fi

                    qemu-system-arm -m 256 -M romulus-bmc -nographic /
                    -drive file=${IMAGE_FILE},format=raw,if=mtd /
                    -net nic /
                    -net user,hostfwd=:0.0.0.0:2222-:22,hostfwd=:0.0.0.0:2443-:443,hostfwd=udp:0.0.0.0:2623-:623,hostname=qemu
                    
                    root
                    0penBmc
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
                sh 'pytest tests/ui/openbmc_ui_tests.py -v --junitxml=ui_test_results.xml'
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
                sh 'locust -f tests/load/locustfile.py --headless -u 100 -r 10 --run-time 1m --html=load_test_report.html'
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