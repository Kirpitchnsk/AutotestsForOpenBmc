pipeline {
     agent any

    environment {
        IMAGE_FILE = ''
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
                        tmux

                    wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
                    tar -xvzf geckodriver-v0.34.0-linux64.tar.gz
                    chmod +x geckodriver  
                    mv geckodriver /usr/local/bin/          

                    pip3 install pytest requests selenium locust robotframework --break-system-packages
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
                    tmux new-session -d -s openbmc 'IMAGE_FILE=$(find romulus/ -name "obmc-phosphor-image-romulus-*.static.mtd" -print -quit) ; qemu-system-arm -m 256 -M romulus-bmc -nographic -drive file=$IMAGE_FILE,format=raw,if=mtd -net nic -net user,hostfwd=:0.0.0.0:2222-:22,hostfwd=:0.0.0.0:2443-:443,hostfwd=udp:0.0.0.0:2623-:623,hostname=qemu'

                    sleep 90
                '''
            }
        }

        stage('API tests') {
            steps {
                
                sh '''
                   pytest tests/api/test_redfish.py -v \
                     --junitxml=api_results.xml \
                     --capture=tee-sys \
                     --log-file=openbmc_tests.log \
                     --log-file-level=INFO
                '''
            }
            post {
                always {
                    junit 'api_results.xml'
                    archiveArtifacts artifacts: 'openbmc_tests.log', fingerprint: true
                }
            }
        }

        stage('UI tests') {
            steps {
                
                sh '''
                   pytest tests/ui/openbmc_ui_tests.py -v \
                     --capture=tee-sys \
                     --log-file=ui_tests.log \
                     --log-file-level=INFO
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'ui_tests.log', fingerprint: true
                }
            }
        }

        stage('Load tests') {
            steps {
                
                sh '''
                   locust \
                     -f tests/load/locustfile.py \
                     --headless \
                     -u 50 -r 5 \
                     -t 1m \
                     --csv=locust_report \
                     --logfile=load_tests.log \
                     --loglevel INFO
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'load_tests.log, locust_report*.csv', fingerprint: true
                }
            }
        }
    }

    post {
        always {
            sh '''
                tmux kill-session -t openbmc 2>/dev/null || true
            '''
            cleanWs()
        }
    }
}
