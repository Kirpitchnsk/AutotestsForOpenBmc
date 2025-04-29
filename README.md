# TestsForOpenBMC

Набор автоматизированных тестов для OpenBMC. Проект включает тесты для Web UI, Redfish API и нагрузочного тестирования.
Тесты автоматически запускаются через jenkins

## Структура проекта
tests/
├── ui/openbmc_ui_tests.py # Тесты Web-интерфейса

├── api/test_redfish.py # Тесты Redfish API

├── load/locustfile.py # Нагрузочное тестирование

Jenkinsfile # CI/CD конфигурация

# Описание тестов

## Тесты Web-интерфейса с использованием Selenium
● Тест для успешной авторизации
После успешной авторизации пользователь попадает на главную страницу. 
Проверяется наличие на ней титула и кнопки "Log Out".
● Тест для неверных данных
После неудачной попытки входа ссылка остается прежней. 
Проверяется, вернулся ли пользователь на страницу авторизации.
● Тест для блокировки учетной записи
Учетная запись блокируется приблизительно после пяти безуспешных попыток входа. 
При блокировке страница и заголовок не отображаются. Проверяется, виден ли заголовок на странице. 

## Тесты для Redfish API
● **Тест аутентификации в OpenBMC через Redfish API**  
Отправляем POST-запрос для создания сессии.  
Проверяем код ответа: 200 означает успешную аутентификацию.  
Убеждаемся, что в ответе есть токен сессии.  

● **Тест получения информации о системе**  
Отправляем GET-запрос на `/redfish/v1/Systems/system`.  
Проверяем статус-код: 200 говорит об успешном выполнении запроса.  
Убеждаемся, что в JSON-ответе есть поля `Status` и `PowerState`.  

● **Тест управления питанием (включение/выключение сервера)**  
Отправляем POST-запрос на `/redfish/v1/Systems/system/Actions/ComputerSystem.Reset`.  
Добавляем параметр `ResetType`: `On`.  
Проверяем, что ответ содержит статус 202 `Accepted`.  
Убеждаемся, что после обновления информации статус системы изменился на `PowerState`: `On`.

## Нагрузочное тестирование с использованием Locust
● **Тестирование OpenBMC API**
Запрос на получение информации о системе: /redfish/v1/Systems/system.
Запрос состояния питания: PowerState.

● **Тестирование публичного API**
Запрос списка постов на JSONPlaceholder: /posts.
Запрос погоды на wttr.in: https://wttr.in/Novosibirsk?format=j1.

Тестирование проходит по адресу http://localhost:8089. Загружаем 100 пользователей и добавляем по 10 в секунду. 
После этого откроется мониторинг.

Или запустить с помощью команды:

bash
locust -f locustfile.py --headless -u 100 -r 10 -t 5m

# Быстрый старт
Клонировать репозиторий:

bash
git clone https://github.com/Kirpitchnsk/TestsForOpenBmc.git
cd TestsForOpenBmc

Установить зависимости:

bash
sudo apt install qemu-system-arm
pip install pytest requests selenium locust

Запустить OpenBMC в QEMU:

bash
qemu-system-arm -m 256 -M romulus-bmc -nographic \
-drive file=romulus/obmc-phosphor-image-romulus-*.static.mtd,format=raw,if=mtd \
-net nic -net user,hostfwd=:0.0.0.0:2443-:443

Запустить тесты:

# API тесты
pytest test_redfish.py -v

# UI тесты
pytest openbmc_ui_tests.py

# Нагрузочные тесты
locust -f locustfile.py

# Запуск CI/CD в Jenkins
1. Запустить Docker в Jenkins
bash
docker run -d -p 8080:8080 -p 50000:50000 --name jenkins -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
2. Перейти по ссылке https://localhost:8080
3. Создать пайплайн, указав в качестве ссылки на Git ссылку на данный репозиторий
4. Запустить пайплайн

Note
Проект разработан в рамках учебного курса.
Актуальная версия OpenBMC: https://github.com/openbmc/openbmc
