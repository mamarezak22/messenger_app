import os

def get_upload_path_for_profile_image(instance, filename):
    # نام فایل اصلی را می‌گیرد و در مسیر دلخواه قرار می‌دهد
    return os.path.join('uploads', 'images', filename)
