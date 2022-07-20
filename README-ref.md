# Server

1. Install Python3 and Miniconda
2. Run

```bash
conda activate base
conda remove --name jojoee.jojoee --all
conda create --name jojoee.jojoee python=3.7.5
conda activate jojoee.jojoee

# dev
pip freeze > requirements.txt
uvicorn main:app
uvicorn main:app --reload

# prod
pip install -r requirements.txt
uvicorn main:app &

# prod restart
ps -ax | grep uvicorn
kill <id>
```

3. Test `curl localhost:8000/api/utcnow`

## GitHub Actions workflow to generate README.md

```bash
python event.py
python event.py --dryrun
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
