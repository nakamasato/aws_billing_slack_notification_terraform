#!/bin/bash

set -eu

rm function.zip
rm -rf package
mkdir -p package
pip install --target ./package requests
cd package
zip -r9 ${OLDPWD}/function.zip .
cd $OLDPWD
zip -g function.zip app.py

aws s3 cp function.zip s3://<bucket-for-lambda>/billing-notification/function.zip
