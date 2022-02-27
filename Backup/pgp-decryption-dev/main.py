import boto3
import gnupg
import os
import shutil
from utils import *
import tempfile
from pathlib import Path


s3_client = boto3.client("s3")

def lambda_handler(event, context):
    print("Entering to Decryption")

    tmp_dir = tempfile.TemporaryDirectory()
    print(tmp_dir)
    temp_dir_path = Path(tmp_dir.name)
    gnupg_home_path = temp_dir_path.joinpath(".gnupg")
    if not gnupg_home_path.exists():
        gnupg_home_path.mkdir(mode=0o777, parents=True)
        
    gnupg_home = gnupg_home_path.__str__()
    run_gpg_agent(gnupg_home)


    bucket = "freshers-training"
    loc = "pgp/encrypted/"
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=loc, MaxKeys=1000)
    files_to_enc = []
    for obj in response.get("Contents"):
        if obj.get("Size") != 0:
            files_to_enc.append(obj.get("Key"))

    gpg = gnupg.GPG(gnupghome=gnupg_home, gpgbinary="/opt/bin/gpg")


    for i in ['sec_1.key']:
        secret_key = f"pgp/private-key/gpg_keys/{i}"
        s3_client.download_file(bucket, secret_key, f"/tmp/{i}")
        with open(f"/tmp/{i}", "rb") as f:
            priv_key = gpg.import_keys(f.read())
            gpg.trust_keys(priv_key.fingerprints, "TRUST_ULTIMATE")

    for file in files_to_enc:
        local_file_name = "/tmp/" + file.rsplit("/")[-1]
        s3_file_name = file.rsplit("/")[-1].rsplit(".", 1)[0]
        print(local_file_name, s3_file_name)
        s3_client.download_file(bucket, file, local_file_name)

        with open(local_file_name, 'rb') as a_file:
            decrypted_data = gpg.decrypt_file(
                a_file,
                always_trust=True,
                passphrase="dcube@2022",
                output=f'/tmp/{s3_file_name}'
                )

        # print("Decrypted_Data\n", decrypted_data)
        print("ok: ", decrypted_data.ok)
        print("status: ", decrypted_data.status)
        print("stderr: ", decrypted_data.stderr)

        s3_client.upload_file(
            f'/tmp/{s3_file_name}',
            bucket,
            "pgp/new_decrypted/decrypt_" + s3_file_name,
        )
    
    print("TemporaryDirectoryCheck:", gnupg_home_path.exists)
    tmp_dir.cleanup()
    print("TemporaryDirectoryCheck:", gnupg_home_path.exists)
    
    
    return True
