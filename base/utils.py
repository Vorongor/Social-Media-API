import os
import pathlib
import uuid
from django.utils.text import slugify


def get_path_for_image(instance, filename):
    ext = pathlib.Path(filename).suffix

    if hasattr(instance, 'get_image_name'):
        new_name = instance.get_image_name
    elif hasattr(instance, 'full_name') and instance.full_name.strip():
        new_name = instance.full_name
    else:
        new_name = pathlib.Path(filename).stem

    new_filename = f"{slugify(new_name)}-{uuid.uuid4()}{ext}"

    return os.path.join(instance.get_dir_path(), new_filename)