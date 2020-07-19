from fastapi import FastAPI, Request, Response, status
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
    W, H = (140, 20)
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
    img.save(buf, "png")
    buf.seek(0)

    headers = {"Cache-Control": "max-age=0, no-cache, no-store, must-revalidate"}

    return StreamingResponse(buf, headers=headers, media_type="image/png")


def is_image_request(request: Request) -> bool:
    header_sec_fetch_dest = request.headers["sec-fetch-dest"]
    header_accept = request.headers["accept"]
    result = (
        True if header_sec_fetch_dest == "image" else "text/html" not in header_accept
    )

    return result


@app.get("/api/utcnow")
def api_utcnow(request: Request):
    # return an image when it's requested from a <img> html element
    if is_image_request(request=request):
        img = get_utcnow_image()
        return serve_pil_image(img)
    else:
        return Response(status_code=status.HTTP_200_OK)

