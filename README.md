# PGP Encrypt Decrypt For S3 File with Lambda
GnuPG with AWS Lambda - To Encrypt and Decrypt S3 File 

## Gnup Setup

1. Install Gnupg and Python package, Run below command to install gpg and python wrapper package.

    ```sh
    # Debian/Ubuntu Installation
    sudo apt-get update
    sudo apt-get install gnupg

    # Python Package Installation
    pip install python-gnupg
    ```

2. Create GPG Profile and Generate Public and Secret Keys for Encryption and Decryption respectively.
    ```sh
    gpg --full-generate-key
    # Enter 1 for RSA key
    # Enter the bits value between 1024 and 4096 for RSA
    # Enter 0 for non expirable key or enter no.of days to set expiration
    # Enter the unique Name and email for key identificatoion
    # Enter passphrase for your key which will be used whilw decryption
    # Then, Finally Type O and Enter to complete.
    ```

3. Generate Public and Secret Key for Encryption and Decryption respectively
    ```sh
    gpg --output <path-to-public-key> --export --armor  <email-provide-for-gpg-profile>
    gpg --output <path-to-secret-key> --export-secret-keys --armor  <email-provide-for-gpg-profile>

    # Ignore Sub-Secret-Key, Only Pub adn Sec keys are important.
    gpg --output <path-to-sub-secret-key> --export-secret-subkeys --armor  <email-provide-for-gpg-profile>
    ```

4. Copy Public and Secret Key to S3
    ```sh
    aws s3 cp  /home/ubuntu/hari/gpg_key/pub_1.key  s3://freshers-training/pgp/private-key/gpg_keys/pub_1.key
    aws s3 cp  /home/ubuntu/hari/gpg_key/sec_1.key  s3://freshers-training/pgp/private-key/gpg_keys/sec_1.key
    ```

5. Build and Deploy Code to CloudFormation
    ##### Build SAM Package and Upload to S3 
    ```bash
    sam package --template-file template.yaml --output-template-file deploy.yaml --s3-bucket freshers-training --s3-prefix lambda-layer-code --force-upload
    ```

    ##### Deploy the Code to CloudFormation
    ```bash
    sam deploy --template-file deploy.yaml --stack-name PGPEncryptDecryptForS3File
    ```
