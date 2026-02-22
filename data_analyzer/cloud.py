from __future__ import annotations

import io

import boto3


def upload_bytes_to_s3(
    data: bytes,
    bucket: str,
    key: str,
    region: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
) -> str:
    session = boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region,
    )
    client = session.client("s3")

    client.upload_fileobj(io.BytesIO(data), bucket, key)
    return f"s3://{bucket}/{key}"
