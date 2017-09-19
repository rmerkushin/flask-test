# Тестовое задание

Создать Web сервис REST API на Python. Функции сервиса: возвращать содержимое файлов с удаленных Linux систем. В параметрах GET запроса передаются параметры:
1.	IP адрес удаленной машины.
2.	Путь до файла, содержимое которого мы хотим вернуть.

Доступ к удаленным машинам происходит по протоколу ssh. Логины/пароли от удаленных машин хранятся в конфигурационном файле сервиса.

# Требования

- Python 3.6+
- flask
- jsonschema
- paramiko
- mypy

# Описание

Серивс реализован с применением [Type Hints](https://www.python.org/dev/peps/pep-0484/). JSON Schema используется для тестов и валидации аргументов GET запроса (не стал усложнять сервис и добавлять лишних зависимостей вроде WTF, Flask-RESTFull и т.п.). MyPy используется для валидации типов и не является обязательной зависимостью. В конфиге прописан хост для общедоступного тестового SSH сервера `test.rebex.net` и все unit-тесты завязаны на него.

# API

`GET /sftp/api/v1.0/get-file?{ip}&{path}`

JSON Schema:
```json
{
    'type': 'object',
    'properties': {
        'ip': {'type': 'string', 'format': 'ipv4'},
        'path': {'type': 'string', 'minLength': 1}
    },
    'additionalProperties': False,
    'required': ['ip', 'path']
}
```

# Запуск

```shell
python app.py
```

# Тесты

```shell
mypy --ignore-missing-imports *.py
pytest tests.py
```
