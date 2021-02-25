from finwiz.extras import applenv
from finwiz.storage.providers import gcloud_storage


def upload_blob(filename, blob, bucket=None, project=None, provider=None):
    provider = provider or applenv.FILE_STORAGE_PROVIDER

    if provider == 'gcloud_storage':
        return gcloud_storage.gcs_upload(
            filename,
            blob,
            bucket=bucket,
            project=(project or applenv.FILE_STORAGE_APP_ID))
