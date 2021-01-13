import boto3

s3 = boto3.resource('s3')
client = boto3.client('s3')

for bucket in s3.buckets.all():
    print(bucket.name)

# Upload a new file
def upload_file(file_name, bucket, object_name=None, args=None):
    """
    file_name: local file name
    bucket: bucket name
    object_name: name of file on s3
    args: custom
    """

    if object_name is None:
            object_name = file_name
    client.upload_file(file_name,bucket,object_name)
    data = open('test.jpg', 'rb')
    s3.Bucket('my-bucket').put_object(Key='test.jpg', Body=data)

