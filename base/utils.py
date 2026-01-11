import os
import pathlib
import uuid

from django.conf import settings
from django.utils.text import slugify


user_model = settings.AUTH_USER_MODEL


def get_path_for_image(
        model: user_model,
        filename: str,

) -> str:
    ext = pathlib.Path(filename).suffix

    new_name = model.full_name if model.full_name else pathlib.Path(
        filename
    ).stem

    new_filename = f"{slugify(new_name)}-{uuid.uuid4()}{ext}"
    return os.path.join("media/", model.get_dir_path(), new_filename)
