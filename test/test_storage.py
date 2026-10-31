
from io import BytesIO

from storage import s3, BUCKET_NAME

test_key = "test-uploads/test.txt"
test_content = b"Backblaze B2 connection test"

try:
    # Upload
    s3.upload_fileobj(
        BytesIO(test_content),
        BUCKET_NAME,
        test_key,
        ExtraArgs={"ContentType": "text/plain"}
    )
    print("Upload successful")

    # Verify
    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key=test_key
    )

    downloaded_content = response["Body"].read()

    assert downloaded_content == test_content
    print("Download and verification successful")

    # Delete
    s3.delete_object(
        Bucket=BUCKET_NAME,
        Key=test_key
    )
    print("Delete successful")

except Exception as e:
    print(f"B2 test failed: {e}")
