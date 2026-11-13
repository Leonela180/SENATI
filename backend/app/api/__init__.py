from flask import jsonify


def ok(data=None, status=200):
    return jsonify(data=data, error=None), status


def fail(code, message, status):
    return jsonify(data=None, error={"code": code, "message": message}), status
