from typing import Dict  # noqa
from jsonschema import FormatChecker, Draft4Validator
from flask import Flask, jsonify, request, make_response

import config
from sftp import SFTP

app = Flask(__name__)

schema = {
    'type': 'object',
    'properties': {
        'ip': {'type': 'string', 'format': 'ipv4'},
        'path': {'type': 'string', 'minLength': 1}
    },
    'additionalProperties': False,
    'required': ['ip', 'path']
}
validator = Draft4Validator(schema, format_checker=FormatChecker(('ipv4',)))

sftp_cache = {}  # type: Dict[str, SFTP]


def sftp_manager(ip: str) -> SFTP:
    if ip in sftp_cache:
        if not sftp_cache[ip].is_active():
            sftp_cache[ip].close()
            del sftp_cache[ip]
            sftp_cache[ip] = SFTP(ip)
    else:
        sftp_cache[ip] = SFTP(ip)
    return sftp_cache[ip]


@app.route('/sftp/api/v1.0/get-file', methods=['GET'])
def get_file() -> dict:
    ip = request.args.get('ip')
    path = request.args.get('path')
    validation_errors = [error.message for error in validator.iter_errors(request.args)]
    if validation_errors:
        return make_response(jsonify({'error': validation_errors}), 400)
    if ip not in config.hosts:
        return make_response(jsonify({'error': 'Specified ip address is not registered in service!'}), 400)
    sftp = sftp_manager(ip)
    exists = sftp.file_exists(path)
    if not exists:
        return make_response(jsonify({'error': 'File not found!'}), 404)
    hostname = sftp.hostname
    content = sftp.read_file(path)
    return jsonify({'hostname': hostname, 'ip': ip, 'path': path, 'content': content})


if __name__ == '__main__':
    app.run(debug=True)
