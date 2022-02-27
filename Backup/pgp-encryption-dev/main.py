import urllib.parse
import boto3
import gnupg
import os
import shutil

src_bucket = os.environ.get('SRC_BUCKET')
dest_bucket = os.environ.get('DEST_BUCKET')
recipients = os.environ.get('RECIPIENTS')


s3_client = boto3.client("s3")


def lambda_handler(event, context):
    # src_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    # file_loc = urllib.parse.unquote_plus(
    #     event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    # )

    file_loc = 'pgp/new_decrypted/test1.txt'
    file_name = file_loc.split('/')[-1]

    bucket = "freshers-training"
    key_recipients = "dcube_latest@dcube.com"

    gpg = gnupg.GPG(gnupghome="/tmp", gpgbinary="/opt/bin/gpg")
    # gpg.encoding = 'utf-8'

    # for i in ['pub_1.key', 'pub.key']:
    for i in ['pub_1.key']:
        secret_key = f"pgp/private-key/gpg_keys/{i}"
        s3_client.download_file(bucket, secret_key, f"/tmp/{i}")
        with open(f"/tmp/{i}", "rb") as f:
            priv_key = gpg.import_keys(f.read())
            gpg.trust_keys(priv_key.fingerprints, "TRUST_ULTIMATE")

    try:
        response = s3_client.get_object(Bucket=bucket, Key=file_loc)
        body = response["Body"].read()
        encrypted_data = gpg.encrypt(
            body,
            recipients=key_recipients,
            output="/tmp/" + file_name + ".gpg",
        )
        print("ok: ", encrypted_data.ok)
        print("status: ", encrypted_data.status)
        print("stderr: ", encrypted_data.stderr)

        s3_client.upload_file(
            "/tmp/" + file_name + ".gpg",
            bucket,
            "pgp/encrypted/" + file_name + ".gpg",
        )
        return True

    except Exception as e:
        print(e)
        raise e
