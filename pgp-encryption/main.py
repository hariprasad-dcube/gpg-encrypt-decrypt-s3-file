
import os


import boto3
import gnupg

from utils import (
    parse_s3_uri_to_bucket_prefix,
    parse_event_to_bucket_obj
)

DEST_BUCKET = os.environ.get("DEST_BUCKET")
DEST_PREFIX = os.environ.get("DEST_PREFIX")
CRYPT_FILE_PREFIX = os.environ.get("CRYPT_FILE_PREFIX")
CRYPT_FILE_SUFFIX = os.environ.get("CRYPT_FILE_SUFFIX")
RECIPIENTS = os.environ.get("RECIPIENTS")
PROCESS_ZERO_FILE_SIZE = bool(os.environ.get("PROCESS_ZERO_FILE_SIZE"))
PUB_KEY_PATH = os.environ.get("PUB_KEY_PATH")
PUB_KEY_BUCKET, PUB_KEY_PREFIX = parse_s3_uri_to_bucket_prefix(PUB_KEY_PATH)


s3_client = boto3.client("s3")


def lambda_handler(event, context):
    """
    # GnuPG Encryption Code with AWS Lambda
    """

    src_bucket, src_prefix, src_file_name, src_file_size = parse_event_to_bucket_obj(
        event)
    dest_file_name = f'{src_file_name}{CRYPT_FILE_SUFFIX}' # Add Suffix for Encrypted File
    tmp_encrypt_path = f'/tmp/{dest_file_name}'

    response_msg = ''


    # Init GPG with --gnupghome and --gpgbinary
    gpg = gnupg.GPG(gnupghome="/tmp", gpgbinary="/opt/bin/gpg")


    # Import Secret Key to PGP
    pub_key = s3_client.get_object(
        Bucket=PUB_KEY_BUCKET,
        Key=PUB_KEY_PREFIX)["Body"].read()
    pub_key = gpg.import_keys(pub_key)
    gpg.trust_keys(pub_key.fingerprints, "TRUST_ULTIMATE")


    if src_file_size or PROCESS_ZERO_FILE_SIZE:
        # Read Encrypted Data From S3
        raw_data = s3_client.get_object(
            Bucket=src_bucket,
            Key=f'{src_prefix}/{src_file_name}')["Body"].read()
        encrypted_data = gpg.encrypt(
            raw_data,
            recipients=RECIPIENTS,
            output=tmp_encrypt_path,
        )
        print("ok: ", encrypted_data.ok)
        print("status: ", encrypted_data.status)
        print("stderr: ", encrypted_data.stderr)

        s3_client.upload_file(
            tmp_encrypt_path,
            DEST_BUCKET,
            f"{DEST_PREFIX}/{dest_file_name}",
        )
    else:
        response_msg = "No Action: Source File Size is Zero Bytes"

    return {
        'status': encrypted_data.ok,
        'msg': response_msg
    }
