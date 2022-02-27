import json
from urllib.parse import unquote_plus

with open(r"Backup\event-copy.json", 'r') as fp:
    event = json.load(fp)


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


(bucket,
 prefix,
 file_name,
 file_size) = parse_event_to_bucket_obj(event)

print(bucket, prefix, file_name, file_size)

if file_size:
    print(f"File Size is {file_size}")
else:
    print(f"Zero File Size is {file_size}")

