def success_response(data):
    response = {
        "status": True,
        "data": data,
        "error": None
    }
    return response


def error_response(data):
    response = {
        "status": False,
        "data": None,
        "error": data
    }
    return response
