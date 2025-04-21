FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    qemu-system-arm \
    python3 python3-pip \
    curl wget unzip git \
    ipmitool \
    xvfb \
    chromium-browser \
    libglib2.0-dev libnss3 libxss1 libappindicator3-1 \
    && apt-get clean

RUN pip3 install --no-cache-dir \
    selenium \
    pytest \
    requests \
    locust \
    junit-xml

RUN CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

ENV DISPLAY=:99

CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & tail -f /dev/null"]

# docker build -t openbmc-ci-agent .
# org.codehaus.groovy.control.MultipleCompilationErrorsException: startup failed:
# WorkflowScript: 3: Invalid agent type "docker" specified. Must be one of [any, label, none] @ line 3, column 9.
# docker {
