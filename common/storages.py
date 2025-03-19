from storages.backends.s3 import S3ManifestStaticStorage, S3Storage
from core_app.settings import DEBUG


class StaticFilesStorage(S3ManifestStaticStorage):
    """Storage class for static files."""

    #location = "static"
    custom_domain = '127.0.0.1:9000/static'
    if DEBUG:
        url_protocol = 'http:'

class UploadedFilesStorage(S3Storage):
    """Storage class for media files."""

    #location = "media"
    custom_domain = '127.0.0.1:9000/media'
    if DEBUG:
        url_protocol = 'http:'