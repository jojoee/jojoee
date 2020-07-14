from fastapi import FastAPI
from datetime import datetime
from PIL import Image, ImageDraw
from io import BytesIO
from starlette.responses import StreamingResponse

app = FastAPI()


@app.get("/")
def root():
    return {"Hello": "World"}


def get_utcnow_image():
    """
    generate image

    :return:
    """
    W, H = (140, 30)
    github_bgcolor_code = (36, 41, 46)
    github_textcolor_code = (255, 255, 255)
    text = datetime.utcnow().replace(microsecond=0).isoformat()
    img = Image.new("RGB", (W, H), color=github_bgcolor_code)
    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(text)
    draw.text(((W - w) / 2, (H - h) / 2), text, fill=github_textcolor_code)

    return img


def serve_pil_image(img):
    buf = BytesIO()
    img.save(buf, 'png')
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@app.get("/api/utcnow")
def api_utcnow():
    img = get_utcnow_image()
    return serve_pil_image(img)
