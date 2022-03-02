
import os
import tempfile
from pathlib import Path

import boto3
import gnupg

from utils import (
    parse_s3_uri_to_bucket_prefix,
    parse_event_to_bucket_obj,
    run_gpg_agent
)

DEST_BUCKET = os.environ.get("DEST_BUCKET")
DEST_PREFIX = os.environ.get("DEST_PREFIX")
CRYPT_FILE_PREFIX = os.environ.get("CRYPT_FILE_PREFIX")
CRYPT_FILE_SUFFIX = os.environ.get("CRYPT_FILE_SUFFIX")
PASSPHRASE = os.environ.get("PASSPHRASE")
PROCESS_ZERO_FILE_SIZE = bool(os.environ.get("PROCESS_ZERO_FILE_SIZE"))
SEC_KEY_PATH = os.environ.get("SEC_KEY_PATH")
SEC_KEY_BUCKET, SEC_KEY_PREFIX = parse_s3_uri_to_bucket_prefix(SEC_KEY_PATH)

s3_client = boto3.client("s3")


def lambda_handler(event, context):
    """
    # GnuPG Decryption Code with AWS Lambda
    """

    # Create Temp Folder For GnuPG
    # TempFolder: /tmp/<temp_dir>/.gnupg
    tmp_dir = tempfile.TemporaryDirectory()
    temp_dir_path = Path(tmp_dir.name)
    gnupg_home_path = temp_dir_path.joinpath(".gnupg")
    gnupg_home_path.mkdir(mode=0o777, parents=True)
    gnupg_home = gnupg_home_path.__str__()
    run_gpg_agent(gnupg_home)

    src_bucket, src_prefix, src_file_name, src_file_size = parse_event_to_bucket_obj(
        event)
    dest_file_name = src_file_name.replace(CRYPT_FILE_SUFFIX, '')  # Replace Suffix for Deccrypted File
    tmp_decrypt_path = f'/tmp/{dest_file_name}'

    response_msg = ''

    # Init GPG with --gnupghome and --gpgbinary
    gpg = gnupg.GPG(gnupghome=gnupg_home, gpgbinary="/opt/bin/gpg")

    # Import Secret Key to GPG
    sec_key = s3_client.get_object(
        Bucket=SEC_KEY_BUCKET,
        Key=SEC_KEY_PREFIX)["Body"].read()
    sec_key = gpg.import_keys(sec_key)
    gpg.trust_keys(sec_key.fingerprints, "TRUST_ULTIMATE")

    if src_file_size or PROCESS_ZERO_FILE_SIZE:
        # Read Encrypted Data From S3
        encrypted_data = s3_client.get_object(
            Bucket=src_bucket,
            Key=f'{src_prefix}/{src_file_name}')["Body"].read()

        # Dencrypted Data
        decrypted_data = gpg.decrypt(
            encrypted_data,
            always_trust=True,
            passphrase=PASSPHRASE,
            output=tmp_decrypt_path
        )

        response_msg = decrypted_data.status

        # Upload Decrypted File to S3
        s3_client.upload_file(
            tmp_decrypt_path,
            DEST_BUCKET,
            f"{DEST_PREFIX}/{dest_file_name}"
        )
    else:
        response_msg = "No Action: Source File Size is Zero Bytes"

    # Clean Up Temp Directory
    tmp_dir.cleanup()

    return {
        'status': decrypted_data.ok,
        'msg': response_msg
    }
