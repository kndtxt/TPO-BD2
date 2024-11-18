docker run --name mongo_bd2 -p 27017:27017 -d mongo
docker run --name redis_bd2 -p 6379:6379 -d redis
python3 api/populate.py
python3 -m streamlit run frontend/main.py > /dev/null &
python3 -m fastapi dev api/main.py