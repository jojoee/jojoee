from fastapi import FastAPI, Request, Response, status
from PIL import Image
from io import BytesIO
from starlette.responses import StreamingResponse
from module.image import get_image_from_utcnow, get_gifpath_from_utcnow, remove_old_image_files, remove_old_gif_files
from fastapi_utils.tasks import repeat_every

app = FastAPI()


def serve_image(img: Image) -> StreamingResponse:
    buf = BytesIO()
    img.save(buf, "png")
    buf.seek(0)

    headers = {"Cache-Control": "max-age=0, no-cache, no-store, must-revalidate"}

    return StreamingResponse(buf, headers=headers, media_type="image/png")


def serve_gif(img) -> StreamingResponse:
    buf = BytesIO()
    img.save(buf, "gif")
    buf.seek(0)
    headers = {"Cache-Control": "max-age=0, no-cache, no-store, must-revalidate"}

    return StreamingResponse(buf, headers=headers, media_type="image/gif")


def is_image_request(request: Request) -> bool:
    headers = request.headers
    header_sec_fetch_dest = headers["sec-fetch-dest"] if "sec-fetch-dest" in headers else ""
    header_accept = headers["accept"] if "accept" in headers else ""
    result = True if header_sec_fetch_dest == "image" else "text/html" not in header_accept

    return result


def image_request_guard(request: Request):
    # return an image when it's requested from a <img> html element
    if not is_image_request(request=request):
        return Response(status_code=status.HTTP_200_OK)


@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/api/utcnow")
def api_utcnow(request: Request):
    # guard
    image_request_guard(request)

    # proceed
    img = get_image_from_utcnow()
    return serve_image(img)


# TODO: remove it
# debug route
@app.get("/api/utcnowimage")
def api_utcnowimage(request: Request):
    # guard
    image_request_guard(request)

    # proceed
    img = get_image_from_utcnow()
    return serve_image(img)


# TODO: remove it
# debug route
@app.get("/api/utcnowgif")
def api_utcnowgif(request: Request):
    # guard
    image_request_guard(request)

    # proceed
    gif_path = get_gifpath_from_utcnow()
    with open(gif_path, 'rb') as f:
        img_raw = f.read()
    byte_io = BytesIO(img_raw)
    return StreamingResponse(byte_io, media_type='image/gif')


@app.on_event("startup")
@repeat_every(seconds=60)
def minutes_tick() -> None:
    print("Tick 1 minute")


@app.on_event("startup")
@repeat_every(seconds=5 * 60)  # 5 minutes
def remove_old_images() -> None:
    print("Remove old images")
    remove_old_image_files()


@app.on_event("startup")
@repeat_every(seconds=5 * 60)  # 5 minutes
def remove_old_gifs() -> None:
    print("Remove old gifs")
    remove_old_gif_files()
