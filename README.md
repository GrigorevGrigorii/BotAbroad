# BotAbroad

✈🌏 Телеграм бот для получения актуальной информации об ограничениях других стран по отношению к России из-за коронавируса (все данные берутся с сайта Министерства иностранных дел России).

К боту можно обращаться с помощью следующих команд:
- `/help `- получить подсказки бота об имеющихся командах;
- `/borders` - получить информацию о границах между Россией и какой-либо страной;
- `/requirements` - получить информацию о требованиях для въезжающих в какую-либо страну россиян.

На данный момент бот может выдавать информацию по 168 странам.

## Как найти бота
Найти бота можно либо по [ссылке](https://t.me/BotAbroad_bot), либо введя в поиске `@BotAbroad` или `@BotAbroad_bot`.

## Как продолжить разработку бота
Бот написан на Python3. Сервер написан на Flask. Взаимодействие с базами данных реализовано с помощью Flask-SQLAlchemy. Сервер размещён на бесплатном веб хостинге Heroku.
### Установка ПО
Для того, чтобы продолжить разработку бота, необходимо иметь Python3.
### Установка зависимостей

Для установки необходимых для проекта пакетов Вам нужно в корне проекта ввести команду
```bash
$ pip3 install -r requirements.txt
```
В этом случае все пакеты установятся глобально, что не очень хорошо. Но можно создать виртуальное окружение и установить пакеты локально там.
- На Linux и MacOS:

В корне проекта введите команду
```bash
$ sh ./install_dependencies_linux.sh
```

- На Windows:

Запустите двойным щелчком правой кнопки мыши файл `install_dependencies_windows.bat`.


### Краткое описание файлов
- `app.py`
    
    Главный файл проекта. В нём находятся модели для базы данных и серверная часть. В серверной части описаны все ответы бота.


- `corona_restrictions.py`
    
    В данном файле находятся функции для получения информации об ограничениях из-за коронавируса и всё с этим связанное.


- `secondary_functions.py`
    
    В данном фале находятся вспомогательные функции, которые нужны для других модулей.
  

- `database.py`

    В данном файле находится всё необходимое для базы данных.



- `models.py`
  
    В данном файле находятся модели для базы данных.



- `install_dependencies_linux.sh`
    
    Скрипт для Linux и MacOS для установки зависимостей в виртуальном окружении.



- `install_dependencies_windows.bat`
    
    Скрипт для Windows для установки зависимостей в виртуальном окружении.

### Замечания
- В проекте используется база данных Heroku. Для того, чтобы использовать другую бд, нужно в `database.py` в строке
    ```
    engine = create_engine(os.environ.get('DATABASE_URL'), convert_unicode=True)
    ```
    заменить `os.environ.get('DATABASE_URL')` на url вашей базы данных.


- Токен бота берется из виртуального окружения Heroku, но Вы можете ввести свой токен бота в `app.py` в следующей строке
    ```
    bot_token = os.environ.get('TOKEN')
    ```

- У Вас не получится запустить бота локально, так как для этого необходимо установить webhook телеграма, а он требует https. Однако Вы без проблем можете разместить бота на Heroku (в этом проекте сделано всё необходимое для этого).
    #### webhook
    - Установить webhook можно перейдя по ссылке (надо заменить {bot_token} на токен Вашего бота и {url} на url Вашего сервера):
    
        [https://api.telegram.org/bot{bot_token}/setWebhook?url={url}]()
    - Получить информацию о webhook можно перейдя по ссылке (надо заменить {bot_token} на токен Вашего бота):
    
        [https://api.telegram.org/bot{bot_token}/getWebhookInfo]()
    - Установить webhook можно перейдя по ссылке (надо заменить {bot_token} на токен Вашего бота):
    
        [https://api.telegram.org/bot{bot_token}/deleteWebhook]()