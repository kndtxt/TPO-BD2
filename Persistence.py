#============ Connection to db ==================>

import redis
r = redis.Redis()
r.mset({"Croatia": "Zagreb", "Bahamas":"Nassau", "Argentina":"Chuwut"})
print(r.get("Argentina").decode("utf-8"))