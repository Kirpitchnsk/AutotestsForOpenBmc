FROM ubuntu:24.04

# Установка базовых инструментов
RUN apt-get update && apt-get install -y \
    qemu-system-arm \
    python3 python3-pip \
    curl wget unzip git \
    ipmitool \
    xvfb \
    chromium-browser \
    libglib2.0-dev libnss3 libgconf-2-4 libxss1 libappindicator3-1 libasound2 \
    && apt-get clean

# Установка Python-библиотек
RUN pip3 install --no-cache-dir \
    selenium \
    pytest \
    requests \
    locust \
    junit-xml

# Скачивание ChromeDriver (под Chromium)
RUN CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# Установка переменных среды
ENV DISPLAY=:99

# Запуск Xvfb по умолчанию (для headless Selenium)
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & tail -f /dev/null"]
