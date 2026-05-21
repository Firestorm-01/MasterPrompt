"""
AWS S3 tool - upload/download objects, list buckets.
"""
import os
from tools.base import BaseTool
class S3Tool(BaseTool):
    name = "s3"
    description = """Manage AWS S3 buckets and objects.
    Actions: 'list_buckets' (), 'list_objects' (bucket), 'upload' (file_path, bucket, key), 'download' (bucket, key, local_path)"""
    category = "Files & Storage"
    required_env_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))
    def _run(self, action: str, bucket: str = None, key: str = None, file_path: str = None, local_path: str = None, **kwargs) -> str:
        import boto3
        s3 = boto3.client("s3", aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), region_name=os.getenv("AWS_REGION", "us-east-1"))
        if action == "list_buckets":
            return "Buckets:\n" + "\n".join(f"- {b['Name']}" for b in s3.list_buckets().get("Buckets", []))
        elif action == "list_objects":
            if not bucket:
                return "Error: 'list_objects' requires 'bucket'"
            objs = s3.list_objects_v2(Bucket=bucket, MaxKeys=50).get("Contents", [])
            return "Objects:\n" + "\n".join(f"- {o['Key']} ({o['Size']} bytes)" for o in objs)
        elif action == "upload":
            if not all([file_path, bucket, key]):
                return "Error: 'upload' requires 'file_path', 'bucket', 'key'"
            s3.upload_file(file_path, bucket, key)
            return f"Uploaded to s3://{bucket}/{key}"
        return f"Error: Unknown action '{action}'"
