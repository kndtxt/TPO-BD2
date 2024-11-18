from datetime import datetime
from bson import ObjectId

non_serializable_objects = [
  ObjectId,
  datetime
]

def is_non_serializable(value):
  return any(isinstance(value, obj) for obj in non_serializable_objects)

def remove_non_json_serializable(data):
  if isinstance(data, list):
    for item in data:
      remove_non_json_serializable(item)
  elif isinstance(data, dict):
    for key, value in data.items():
      if is_non_serializable(value):
        data[key] = str(value)
      elif isinstance(value, dict) or isinstance(value, list):
        remove_non_json_serializable(value)  
  return data

def clean_data(data):
  list_data = data
  if not isinstance(data, list):
    list_data = list(data)
  return remove_non_json_serializable(list_data)