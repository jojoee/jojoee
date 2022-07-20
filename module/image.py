from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from typing import Dict
import os
import imageio
import time

IMAGE_DIR_PATH = os.path.join(os.getcwd(), 'precompute/image')
GIF_DIR_PATH = os.path.join(os.getcwd(), 'precompute/gif')
KEEP_FILE_NAMES = [
    '.gitkeep',
]
KEEP_FILE_NAMES_KEY: Dict[str, int] = dict(zip(
    KEEP_FILE_NAMES,
    list(range(1, len(KEEP_FILE_NAMES) + 1))
))

print(IMAGE_DIR_PATH)
print(GIF_DIR_PATH)
print(KEEP_FILE_NAMES_KEY)


# TODO remove it cause it is unused
def get_image_from_utcnow() -> Image:
    text = datetime.utcnow().replace(microsecond=0).isoformat()

    return get_image_from_text(text)


def get_image_file_name(image_text: str) -> str:
    """
    Replace ":" with "-"

    :param image_text:
    :return:
    """
    return image_text.replace(':', '-')


def get_image_from_text(text: str) -> Image:
    """
    generate image

    :param text: in ISO format e.g. "2022-07-20T03:59:24"
    :return:
    """

    file_name = '%s.png' % get_image_file_name(text)
    file_path = os.path.join(IMAGE_DIR_PATH, file_name)

    image: Image = None
    if os.path.isfile(file_path):
        print("Found image at %s then load it" % file_path)
        image = Image.open(file_path)
    else:
        print("Not found image at %s then create it" % file_path)

        # generate image
        image_width, image_height = (140, 20)
        github_bgcolor_code = (36, 41, 46)
        github_textcolor_code = (255, 255, 255)
        image = Image.new("RGB", (image_width, image_height), color=github_bgcolor_code)
        draw = ImageDraw.Draw(image)
        w, h = draw.textsize(text)
        draw.text(((image_width - w) / 2, (image_height - h) / 2), text, fill=github_textcolor_code)

        # save
        print("Saving newly created image to %s" % file_path)
        image.save(file_path)

    return image


def get_gifpath_from_utcnow(n_seconds: int = 10) -> str:
    global IMAGE_DIR_PATH

    start_time = datetime.utcnow().replace(microsecond=0)
    start_time_text = start_time.isoformat()

    # if we already have file then returns
    gif_file_name = "%s-%d.gif" % (get_image_file_name(start_time_text), n_seconds)
    gif_file_path = os.path.join(GIF_DIR_PATH, gif_file_name)

    if not os.path.isfile(gif_file_path):
        # generate new gif file
        images = []
        for i in range(n_seconds):
            this_time = start_time + timedelta(seconds=i)
            text = this_time.isoformat()
            image = get_image_from_text(text)
            images.append(image)

        print("Saving newly created gif to %s" % gif_file_path)
        imageio.mimsave(gif_file_path, images, duration=1)

    return gif_file_path


def remove_old_image_files():
    global IMAGE_DIR_PATH
    global KEEP_FILE_NAMES_KEY

    remove_old_files(
        IMAGE_DIR_PATH,
        5 * 60,
        KEEP_FILE_NAMES_KEY
    )


def remove_old_gif_files():
    global GIF_DIR_PATH
    global KEEP_FILE_NAMES_KEY

    remove_old_files(
        GIF_DIR_PATH,
        5 * 60,
        KEEP_FILE_NAMES_KEY
    )


def remove_old_files(dir_path: str = IMAGE_DIR_PATH, n_seconds: int = 5 * 60, keep_file_names_key: Dict[str, int] = {}):
    """

    :param dir_path: directory of files
    :param n_seconds: remove files that older than "seconds" seconds
    :param keep_file_names_key: e.g. {".gitkeep": 1}
    :return:
    """
    now = time.time()
    n_files = 0
    time_str = str(timedelta(seconds=n_seconds))
    print("Remove files that older than %s hh:mm:ss" % time_str)

    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        is_keep_file = file_name in keep_file_names_key
        is_old_file = os.stat(file_path).st_mtime < now - n_seconds
        is_file = os.path.isfile(file_path)

        if not is_keep_file and is_old_file and is_file:
            print("Remove file %s" % file_path)
            n_files = n_files + 1
            os.remove(file_path)

    print("Remove %d files from %s" % (n_files, dir_path))
