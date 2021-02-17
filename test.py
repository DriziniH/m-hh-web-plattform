import boto3
from boto3.session import Session

sess = Session( aws_access_key_id="AKIAS5476YDKSQBQPOMN",aws_secret_access_key='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',aws_session_token=None)
sts = sess.client('sts')

try:
    sts.get_caller_identity() 
    print("Credentials are valid.")
except Exception as e:
    print(e)
    print("Credentials are NOT valid.")

# try:
#     iam = boto3.client('iam', "eu-central-1" "201662054613", "AKIAS5476YDKT4DEZ2EZ")
#     print(iam.get_account_authorization_details())
#     print("Credentials are valid.")
# except Exception as e:
#     print(e)
#     print("Credentials are NOT valid.")