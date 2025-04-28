pipeline {
    agent {
        docker {
            image 'ubuntu:20.04'
            args '--user root --privileged -v /dev:/dev'
        }
    }

    environment {
        BMC_URL = "https://127.0.0.1:2443"
        USERNAME = "root"
        PASSWORD = "0penBmc"
    }

    stages {
        stage('Setup Environment') {
            steps {
                sh '''
                    apt-get update && apt-get install -y \
                        python3 \
                        python3-pip \
                        qemu-system-arm \
                        wget \
                        unzip \
                        firefox \
                        xvfb

                    wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
                    tar -xvzf geckodriver-v0.34.0-linux64.tar.gz
                    mv geckodriver /usr/local/bin/
                    chmod +x /usr/local/bin/geckodriver

                    pip3 install pytest requests selenium locust robotframework
                '''
            }
        }

        stage('Download OpenBMC Image') {
            steps {
                sh '''
                    wget https://jenkins.openbmc.org/job/ci-openbmc/lastSuccessfulBuild/distro=ubuntu,label=docker-builder,target=romulus/artifact/openbmc/build/tmp/deploy/images/romulus/*zip*/romulus.zip
                    unzip romulus.zip
                '''
            }
        }

        stage('Run OpenBMC in QEMU') {
            steps {
                sh '''
                    IMAGE_FILE=$(find romulus/ -name "obmc-phosphor-image-romulus-*.static.mtd" -print -quit)
                    [ -z "$IMAGE_FILE" ] && { echo "Image file not found"; exit 1; }

                    nohup qemu-system-arm -m 256 -M romulus-bmc -nographic \
                        -drive file=${IMAGE_FILE},format=raw,if=mtd \
                        -net nic \
                        -net user,hostfwd=:0.0.0.0:2222-:22,hostfwd=:0.0.0.0:2443-:443,hostfwd=udp:0.0.0.0:2623-:623,hostname=qemu > qemu.log 2>&1 &

                    sleep 120
                '''
            }
        }

        stage('Run API Tests') {
            steps {
                sh '''
                    curl -k ${BMC_URL}/redfish/v1/ || { echo "BMC not ready"; exit 1; }
                    pytest tests/api/test_redfish.py -v --junitxml=api_test_results.xml
                '''
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
                sh '''
                    Xvfb :99 -screen 0 1024x768x16 &> xvfb.log &
                    export DISPLAY=:99
                    pytest tests/ui/openbmc_ui_tests.py -v --junitxml=ui_test_results.xml
                '''
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
                sh '''
                    locust -f tests/load/locustfile.py \
                        --headless \
                        -u 100 \
                        -r 10 \
                        --run-time 1m \
                        --html=load_test_report.html \
                        --host=${BMC_URL}
                '''
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
                pkill -f qemu-system-arm || true
                pkill -f Xvfb || true
            '''
            archiveArtifacts artifacts: 'qemu.log,xvfb.log', fingerprint: true
            cleanWs()
        }
    }
}