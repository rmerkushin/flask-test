import json
import pytest
from jsonschema import FormatChecker, Draft4Validator, ValidationError

from app import app


file_content = 'Welcome,\r\n\r\nyou are connected to an FTP or SFTP server used for testing purposes by Rebex FTP/SSL' \
               ' or Rebex SFTP sample code.\r\nOnly read access is allowed and the FTP download speed is limited to ' \
               '16KBps.\r\n\r\nFor infomation about Rebex FTP/SSL, Rebex SFTP and other Rebex .NET components, please' \
               ' visit our website at http://www.rebex.net/\r\n\r\nFor feedback and support, contact ' \
               'support@rebex.net\r\n\r\nThanks!\r\n'
schema_200 = {
    'type': 'object',
    'properties': {
        'ip': {'type': 'string', 'format': 'ipv4', 'enum': ['195.144.107.198']},
        'hostname': {'type': 'string', 'format': 'hostname', 'enum': ['test.rebex.net']},
        'path': {'type': 'string', 'enum': ['/readme.txt']},
        'content': {'type': 'string', 'enum': [file_content]}
    },
    'additionalProperties': False,
    'required': ['ip', 'hostname', 'path', 'content']
}


@pytest.fixture
def client(request):
    return app.test_client()


def test_successful(client):
    response = client.get('/sftp/api/v1.0/get-file?ip=195.144.107.198&path=/readme.txt')
    response_json = json.loads(response.data)
    assert response.status_code == 200
    validator = Draft4Validator(schema_200, format_checker=FormatChecker(('ipv4', 'hostname')))
    validation_errors = [error.message for error in validator.iter_errors(response_json)]
    if validation_errors:
        raise ValidationError(validation_errors)


def test_unknown_ip(client):
    response = client.get('/sftp/api/v1.0/get-file?ip=127.0.0.1&path=/readme.txt')
    response_json = json.loads(response.data)
    assert response.status_code == 400
    assert response_json == {'error': 'Specified ip address is not registered in service!'}


def test_incorrect_ip(client):
    response = client.get('/sftp/api/v1.0/get-file?ip=a.b.c.d&path=/readme.txt')
    response_json = json.loads(response.data)
    assert response.status_code == 400
    assert response_json == {'error': ["'a.b.c.d' is not a 'ipv4'"]}


def test_ip_is_absent(client):
    response = client.get('/sftp/api/v1.0/get-file?path=/readme.txt')
    response_json = json.loads(response.data)
    assert response.status_code == 400
    assert response_json == {'error': ["'ip' is a required property"]}


def test_path_is_absent(client):
    response = client.get('/sftp/api/v1.0/get-file?ip=195.144.107.198')
    response_json = json.loads(response.data)
    assert response.status_code == 400
    assert response_json == {'error': ["'path' is a required property"]}


def test_path_is_empty(client):
    response = client.get('/sftp/api/v1.0/get-file?ip=195.144.107.198&path=')
    response_json = json.loads(response.data)
    assert response.status_code == 400
    assert response_json == {'error': ["'' is too short"]}


def test_path_is_not_exists(client):
    response = client.get('/sftp/api/v1.0/get-file?ip=195.144.107.198&path=/unknown.txt')
    response_json = json.loads(response.data)
    assert response.status_code == 404
    assert response_json == {'error': 'File not found!'}


def test_incorrect_request(client):
    response = client.get('/sftp/api/v1.0/get-file')
    response_json = json.loads(response.data)
    assert response.status_code == 400
    assert response_json == {'error': ["'ip' is a required property", "'path' is a required property"]}


def test_unexpected_post(client):
    response = client.post('/sftp/api/v1.0/get-file?ip=195.144.107.198&path=/readme.txt')
    assert response.status_code == 405
