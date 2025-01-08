
Предварительные требования
Перед началом убедитесь, что у вас установлены следующие компоненты на вашем устройстве:
```
Docker
Python
```
Настройка окружения
При необходимости создайте файл .env в корневой директории вашего проекта для хранения переменных окружения. Например:
```
POSTGRES_DB=Название БД
POSTGRES_USER=Логин
POSTGRES_PASSWORD=Пароль
```
Запуск приложения
Теперь вы готовы запустить приложение. Выполните следующую команду в корневой директории проекта:
```
docker-compose up --build
```

Проверка статуса контейнеров
Чтобы убедиться, что контейнеры запущены, выполните:
```
docker-compose ps
```
Доступ к приложению
После успешного запуска вы сможете получить доступ к вашему приложению через браузер по адресу:
```
http://localhost:8000
```
Проверка логов
Если что-то пошло не так, вы можете просмотреть логи с помощью:
```
docker-compose logs
```
Остановка приложения
Чтобы остановить приложение и контейнеры, выполните:
```
docker-compose down
```
Документация приложения хорошо описана и после запуска приложения с ней можно ознакомиться в swagger по адресу:
```
http://localhost:8000/docs
```
