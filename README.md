# TestsForOpenBMC

Набор автоматизированных тестов для OpenBMC. Проект охватывает Web UI, Redfish API и нагрузочное тестирование. Тесты можно запускать через Jenkins.

## Структура проекта
tests/ <br />
├── ui/ <br />
├──── openbmc_ui_tests.py # Тесты Web-интерфейса <br />
├── api/ <br />
├──── test_redfish.py # Тесты Redfish API <br />
├── load/<br />
├──── locustfile.py # Нагрузочное тестирование <br />
docker-compose.yml # docker-compose file для запуска  Jenkins в контейнере
Jenkinsfile # CI/CD конфигурация

# Описание тестов

## Тесты Web-интерфейса с использованием Selenium <br />
#### Тест для успешной авторизации <br />
После успешной авторизации пользователь попадает на главную страницу. <br />
Проверяется наличие на ней титула и кнопки "Log Out". <br />

#### Тест для неверных данных
1. После неудачной попытки входа ссылка остается прежней.
2. Проверяется, вернулся ли пользователь на страницу авторизации.

#### Тест для блокировки учетной записи
1. Учетная запись блокируется приблизительно после пяти безуспешных попыток входа.
2. При блокировке страница и заголовок не отображаются. Проверяется, виден ли заголовок на странице.

## Тесты для Redfish API
#### Тест аутентификации в OpenBMC через Redfish API <br />
1. Отправляем POST-запрос для создания сессии.  <br />
2. Проверяем код ответа: 200 означает успешную аутентификацию.  <br />
3. Убеждаемся, что в ответе есть токен сессии.  <br />

#### Тест получения информации о системе  <br />
1. Отправляем GET-запрос на `/redfish/v1/Systems/system`.
2. Проверяем статус-код: 200 говорит об успешном выполнении запроса. <br />
3. Убеждаемся, что в JSON-ответе есть поля `Status` и `PowerState`. 

#### Тест управления питанием (включение/выключение сервера)
1. Отправляем POST-запрос на `/redfish/v1/Systems/system/Actions/ComputerSystem.Reset`.  
2. Добавляем параметр `ResetType`: `On`.  
3. Проверяем, что ответ содержит статус 202 `Accepted`.  
4. Убеждаемся, что после обновления информации статус системы изменился на `PowerState`: `On`.

## Нагрузочное тестирование с использованием Locust
#### Тестирование OpenBMC API
1. Запрос на получение информации о системе: /redfish/v1/Systems/system.
2. Запрос состояния питания: PowerState.

#### Тестирование публичного API
1. Запрос списка постов на JSONPlaceholder: /posts. 
2. Запрос погоды на wttr.in: https://wttr.in/Novosibirsk?format=j1.

Тестирование проходит по адресу `http://localhost:8089`. Загружаем 100 пользователей и добавляем по 10 в секунду. 
После этого откроется мониторинг.

### Или запустить тестирование с помощью команды:

```bash
locust -f locustfile.py --headless -u 100 -r 10 -t 5m
```

# Быстрый старт
### Клонировать репозиторий:

```bash
git clone https://github.com/Kirpitchnsk/TestsForOpenBmc.git
cd TestsForOpenBmc
```

### Установить зависимости:

```bash
sudo apt install qemu-system-arm
pip install pytest requests selenium locust
```

### Запустить OpenBMC в QEMU:

```bash
qemu-system-arm -m 256 -M romulus-bmc -nographic \
-drive file=romulus/obmc-phosphor-image-romulus-*.static.mtd,format=raw,if=mtd \
-net nic -net user,hostfwd=:0.0.0.0:2443-:443
```
Вместо * нужно подставить цифры из файла на устройстве.
### Запустить тесты:
#### API тесты
```bash
pytest test_redfish.py -v
```

#### UI тесты
```bash
pytest openbmc_ui_tests.py
```

#### Нагрузочные тесты
```bash
locust -f locustfile.py
```

# Запуск CI/CD в Jenkins
1. Запустить Docker-Compose в Jenkins
```bash
sudo docker-compose up -d
```
2. Перейти по ссылке `https://localhost:8080` чтобы открыть web-интерфейс jenkins
3. Создать пайплайн, указав в качестве ссылки на Git ссылку на данный репозиторий
4. Запустить пайплайн

### Шаги сборки в Jenkins

1. Настройка окружения и установка необходимых компонентов.
2. Установка romulus.  
3. Запуск QEMU с OpenBMC через Pipeline.  
4. Выполнение api тестов для OpenBMC.  
5. Запуск WebUI тестов OpenBMC.  
6. Проведение нагрузочного тестирования OpenBMC.
7. Закрытие сессии.

Каждый шаг сопровождается отчетом, который сохраняется в артефактах Jenkins.

# Note
Проект разработан в рамках учебного курса. <br />
Актуальная версия OpenBMC: `https://github.com/openbmc/openbmc`
