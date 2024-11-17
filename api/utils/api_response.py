from fastapi import status, Response

class ResponseStatus():
  code: status
  message: str

def error_wrapper(response_status: ResponseStatus, response: Response):
  response.status_code = response_status.code
  return {
    'data': [],
    'code': response_status.code,
    'message': response_status.message
  }

def response_wrapper(data, response: Response):
  if isinstance(data, type(ResponseStatus)):
    return error_wrapper(data, response)
  size = 1
  if isinstance(data, type(None)):
    size = 0
  elif isinstance(data, type(dict)):
    size = 1
  else:
    size = len(data)
  return {'data': data, 'size': size}
