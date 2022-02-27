# PGPEncryptDecryptForS3File
GnuPG with AWS Lambda - To Encrypt and Decrypt S3 File 

### Build SAM Package and Upload to S3 
```bash
$ sam package --template-file template.yaml --output-template-file deploy.yaml --s3-bucket freshers-training --s3-prefix lambda-layer-code --force-upload
```

### Deploy the Code to CloudFormation
```bash
$ sam deploy --template-file deploy.yaml --stack-name PGPEncryptDecryptForS3File
```