def response(data):
  size = 1
  if isinstance(data, type(None)):
    size = 0
  elif isinstance(data, type(dict)):
    size = 1
  else:
    size = len(data)
  return {'data': data, 'size': size}