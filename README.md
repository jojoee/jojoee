<img src="https://jojoee.jojoee.com/api/utcnow" width="120" height="20">

<!--
1. Install Python3 and Miniconda
2. Run
```
conda create --name jojoee.jojoee python=3.7.5
conda activate jojoee.jojoee

# dev
pip freeze > requirements.txt
uvicorn main:app --reload

# prod
pip install -r requirements.txt
uvicorn main:app
```
3. Test `curl localhost:8000/api/utcnow`
-->
