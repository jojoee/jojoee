# Server to serve an image

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
uvicorn main:app &

# prod restart
ps -ax | grep uvicorn
kill <id>
```
3. Test `curl localhost:8000/api/utcnow`

# GitHub Actions workflow to generate README.md

```bash
python event.py
```

## Reference
- https://developer.github.com/v3/activity/events/
- https://developer.github.com/v3/activity/event_types/
- https://developer.github.com/v3/#pagination
