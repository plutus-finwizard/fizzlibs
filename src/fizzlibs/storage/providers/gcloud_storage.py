from google.cloud import storage
from finwiz.storage.blob import FinwizBlob


def gcs_upload(filname, blob, bucket, project):
    client = storage.Client(project=project)
    bucket = client.get_bucket(bucket)

    gcs_blob = bucket.blob(filname)
    gcs_blob.upload_from_file(blob)

    return gcs_blob.id


def gcs_fileserving_url(blob_id):
    client = storage.Client(project=project)
    bucket = client.get_bucket(bucket)
