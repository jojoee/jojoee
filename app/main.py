from fastapi import FastAPI, Request
from io import BytesIO
from starlette.responses import StreamingResponse
from module.image import get_image_from_utcnow, get_gifpath_from_utcnow, \
    remove_old_image_files, remove_old_gif_files
from fastapi_utils.tasks import repeat_every
from fastapi.responses import RedirectResponse

app = FastAPI()


# unused
def is_image_request(request: Request) -> bool:
    headers = request.headers
    header_sec_fetch_dest = headers["sec-fetch-dest"] if "sec-fetch-dest" in headers else ""
    header_accept = headers["accept"] if "accept" in headers else ""
    result = header_sec_fetch_dest == "image" or "text/html" not in header_accept

    return result


@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/api/utcnow")
@app.get("/api/utcnowimage")
def api_utcnowimage(request: Request):
    # guard
    # return an image when it's requested from a <img> html element
    if not is_image_request(request=request):
        return Response(status_code=status.HTTP_200_OK)

    # proceed
    img = get_image_from_utcnow()

    # returns
    buf = BytesIO()
    img.save(buf, "png")
    buf.seek(0)
    headers = {"Cache-Control": "max-age=0, no-cache, no-store, must-revalidate"}
    return StreamingResponse(buf, headers=headers, media_type="image/png")


@app.get("/api/utcnowgif")
def api_utcnowgif(request: Request):
    # guard
    # return an image when it's requested from a <img> html element
    if not is_image_request(request=request):
        return Response(status_code=status.HTTP_200_OK)

    # proceed
    gif_path = get_gifpath_from_utcnow()
    with open(gif_path, 'rb') as f:
        img_raw = f.read()
    byte_io = BytesIO(img_raw)
    headers = {"Cache-Control": "max-age=0, no-cache, no-store, must-revalidate"}
    return StreamingResponse(byte_io, headers=headers, media_type='image/gif')


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


# https://fastapi.tiangolo.com/tutorial/handling-errors/
# https://stackoverflow.com/questions/62986778/fastapi-handling-and-redirecting-404
@app.exception_handler(404)
async def custom_404_handler(_, __):
    return RedirectResponse("/")
