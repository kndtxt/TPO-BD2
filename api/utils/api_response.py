from fastapi import Response, status
import json

class ResponseStatus():
  def __init__(self, code: int, message: str):
    self.code = code
    self.message = message

NO_CACHE_HEADERS = {
  'Content-Type': 'application/json',
  'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
  'Pragma': 'no-cache',
  'Expires': '0'
}

def wrap_headers(content, response: Response):
  response.headers.update({**response.headers, **NO_CACHE_HEADERS})
  response.body = json.dumps(content).encode('utf-8')
  if not response.status_code:
    response.status_code = status.HTTP_202_ACCEPTED
  return response

def error_wrapper(response_status: ResponseStatus, response: Response):
  response.status_code = response_status.code
  content = {
    'data': [],
    'code': response_status.code,
    'message': response_status.message
  }
  return wrap_headers(content, response)

def response_wrapper(data, response: Response):
  if isinstance(data, ResponseStatus):
    return error_wrapper(data, response)
  size = 1
  if isinstance(data, type(None)):
    size = 0
  elif isinstance(data, dict) or isinstance(data, bool):
    size = 1
  else:
    size = len(data)
  content = {'data': data, 'size': size}
  return wrap_headers(content, response)
