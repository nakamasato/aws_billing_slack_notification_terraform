# AWS billing notification lambda

## Create Bucket

### bucket-for-lambda

```
aws s3api create-bucket --bucket=<bucket-for-lambda> --region=ap-northeast-1 --create-bucket-configuration LocationConstraint=ap-northeast-1
```

### bucket-for-terraform

```
aws s3api create-bucket --bucket=<bucket-for-terraform> --region=ap-northeast-1 --create-bucket-configuration LocationConstraint=ap-northeast-1
```

## Change backend.tf & variables.tf & update_lambda.sh

write your own s3 bucket (<bucket-for-lambda> and <bucket-for-terraform>)

## Upload lambda function to s3

```
cd lambda-code
./update_lambda.sh
```

## Create lambda & cloudwatch rule by terraform

```
terraform init
terraform apply -var="slack_url=https://hooks.slack.com/services/<hash>"
```

```
terraform destroy
```