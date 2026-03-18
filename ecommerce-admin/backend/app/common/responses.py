from flask import jsonify

def success_response(data=None, message="success", code=200):
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    }), code

def error_response(message="error", code=400, data=None):
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    }), code
