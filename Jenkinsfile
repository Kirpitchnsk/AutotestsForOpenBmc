pipeline {
    agent {

    }

    environment {
        BMC_IMAGE = 'romulus/obmc-phosphor-image-romulus-20250212052422.static.mtd'
        BMC_LOGIN = 'root'
        BMC_PASS = '0penBmc'
        QEMU_CMD = """qemu-system-arm -m 256 -M romulus-bmc -nographic \
            -drive file=$BMC_IMAGE,format=raw,if=mtd \
            -net nic -net user,hostfwd=:0.0.0.0:2222-:22 \
            -net user,hostfwd=udp:0.0.0.0:2623-:623,hostname=qemu"""
    }

    stages {

        stage('Checkout') {
            steps {
                git 'https://github.com/Kirpitchnsk/TestsForOpenBmc'
            }
        }

        stage('Run OpenBMC in QEMU') {
            steps {
                sh '''
                    nohup $QEMU_CMD > qemu.log 2>&1 &
                    sleep 20
                    echo "QEMU started"
                '''
            }
        }

        stage('Run Selenium UI Tests') {
            steps {
                sh 'pytest tests/api/openbmc_ui_tests.py --junitxml=api_report.xml'
            }
        }

        stage('Run Redfish API Tests') {
            steps {
                sh 'pytest tests/api/test_redfish.py --junitxml=api_report.xml'
            }
        }

        stage('Run Locust Load Test') {
            steps {
                sh '''
                    locust -f tests/load/locustfile.py --headless \
                    -u 10 -r 2 --run-time 1m \
                    --host https://localhost:2443 \
                    --csv=load_test_result
                '''
            }
        }

        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: '**/*.xml, **/*.log, **/*.csv', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            sh 'pkill qemu-system-arm || true'
            echo 'QEMU terminated'
        }
    }
}
