import os
from urllib.parse import unquote_plus


def parse_s3_uri_to_bucket_prefix(s3_path):
    """
    # Parse s3 Path URI to Bucket and Prefix
    """
    s3_path = unquote_plus(s3_path).split('/', 3)
    return s3_path[-2], s3_path[-1]


def parse_event_to_bucket_obj(event):
    """
    # Parse Lambda Event Object
    """
    s3_obj = event['Records'][0]['s3']

    _bucket = unquote_plus(s3_obj['bucket']['name'])
    _file = unquote_plus(s3_obj['object']['key']).rsplit('/', 1)
    _prefix = _file[0] if len(_file) > 1 else None
    _file_name = _file[-1]
    _file_size = s3_obj['object']['size']
    return _bucket, _prefix, _file_name, _file_size
