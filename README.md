## Project 用途
-  使用 aws api 獲取特定帳號的一日花費

## python version && package version
- python version (3.11.4)
- boto3 (1.28.15)
- python-dotenv (1.0.0)

## .env file 所需環境變數如下
- region_name (example: ap-northeast-1)
- aws_access_key_id
- aws_secret_access_key
- aws_account_id (可於 aws 帳號中獲取)
- telegram_token (自行於 telegram bot father 中建立)
- chat_id (於 telegram bot api request 中可以獲取)
- (aws access_key, secret_access_key 都可以透過 aws 生成 請記得給予查詢帳單的相關權限)

## Reference
- [aws boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html) 
- [aws cost api doc](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_Operations_AWS_Cost_Explorer_Service.html)
- [telegram api](https://docs.python-telegram-bot.org/en/v20.5/index.html)