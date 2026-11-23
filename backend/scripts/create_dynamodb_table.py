"""Create the development DynamoDB table if it does not already exist."""

from botocore.exceptions import ClientError

import boto3

from app.core.config import get_settings


def main() -> None:
    settings = get_settings()
    dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
    table = dynamodb.Table(settings.dynamodb_table_name)

    try:
        table.load()
    except ClientError as error:
        if error.response["Error"]["Code"] != "ResourceNotFoundException":
            raise
    else:
        print(
            f"Table {settings.dynamodb_table_name!r} already exists "
            f"in {settings.aws_region}."
        )
        return

    table = dynamodb.create_table(
        TableName=settings.dynamodb_table_name,
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
        Tags=[
            {"Key": "Project", "Value": "etf-portfolio-dashboard"},
            {"Key": "Environment", "Value": "development"},
        ],
    )
    print(f"Creating table {settings.dynamodb_table_name!r}...")
    table.wait_until_exists()
    print(f"Table is active in {settings.aws_region}.")


if __name__ == "__main__":
    main()

