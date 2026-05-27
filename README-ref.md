# Server

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.14.5
2. Run

```bash
uv python install 3.14.5
uv venv --python 3.14.5
source .venv/bin/activate
uv pip install -r requirements.txt -r requirements-dev.txt

# dev
uv pip freeze > requirements.txt
uvicorn app.main:app --reload

# prod
uv pip install -r requirements.txt
uvicorn app.main:app &

# prod restart
ps -ax | grep uvicorn
kill <id>

# docker
docker ps -a
docker rm ctn_jojoee
docker build -f ./Dockerfile -t jojoee/jojoee:dev .
docker run -d --name ctn_jojoee -p 8000:8000 jojoee/jojoee:dev
docker restart ctn_jojoee
docker logs ctn_jojoee
```

3. Test

```bash
curl localhost:8000/api/utcnow
curl localhost:8000/api/utcnowimage
curl localhost:8000/api/utcnowgif
```

## GitHub Actions workflow to generate README.md

```bash
python event.py
python event.py --dryrun
python event.py --debug
```

## Example

```markdown Insert image into GitHub Markdown
![Current UTC time](https://jojoee.jojoee.com/api/utcnow?refresh)
<img src="https://jojoee.jojoee.com/api/utcnow?refresh" width="120" height="20">
```

## Reference

- https://developer.github.com/v3/activity/events/
- https://developer.github.com/v3/activity/event_types/
- https://developer.github.com/v3/#pagination
