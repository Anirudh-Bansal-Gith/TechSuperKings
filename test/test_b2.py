from storage import s3, BUCKET_NAME

try:
    response = s3.head_bucket(Bucket=BUCKET_NAME)
    print("B2 connection successful!")
    print(response)

except Exception as e:
    print(type(e).__name__, e)