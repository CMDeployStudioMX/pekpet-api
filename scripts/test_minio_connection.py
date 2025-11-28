import boto3
from botocore.client import Config
import os

def load_env_file(filepath):
    """Simple parser for .env files since python-dotenv might not be installed"""
    env_vars = {}
    if os.path.exists(filepath):
        print(f"Loading credentials from {filepath}")
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip("'\"")
                env_vars[key.strip()] = value
    return env_vars

# Try to load from .env.local
env_vars = load_env_file('.env.local')

# Get credentials from loaded env vars or os.environ, fallback to hardcoded (or empty)
endpoint = env_vars.get('AWS_S3_ENDPOINT_URL') or os.environ.get('AWS_S3_ENDPOINT_URL') or "https://s3.pek-pet.com"
access_key = env_vars.get('AWS_ACCESS_KEY_ID') or os.environ.get('AWS_ACCESS_KEY_ID') or "djcrespo"
# FORCE CORRECT PASSWORD FROM DOCKER COMPOSE FOR TESTING
secret_key = "Didier1998" 
region = env_vars.get('AWS_S3_REGION_NAME') or os.environ.get('AWS_S3_REGION_NAME') or 'us-east-1'

print(f"Testing connection to {endpoint}")
print(f"User: {access_key}")
print(f"Region: {region}")
# Mask secret key for display
masked_secret = secret_key[:4] + '*' * (len(secret_key) - 4) if secret_key and len(secret_key) > 4 else "****"

print(f"Testing connection to {endpoint}")
print(f"User: {access_key!r} (Length: {len(access_key)})")
print(f"Secret: {masked_secret} (Length: {len(secret_key)})")
print(f"Region: {region!r}")

s3 = boto3.client('s3',
    endpoint_url=endpoint,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    config=Config(
        signature_version='s3v4',
        retries={'max_attempts': 1}
    ),
    region_name=region
)

try:
    print("\nAttempting to list buckets...")
    response = s3.list_buckets()
    print("\nConnection Successful! List buckets worked.")
    print("Buckets:")
    for bucket in response.get('Buckets', []):
        print(f"- {bucket['Name']}")
except Exception as e:
    print(f"\nConnection Failed: {e}")
    print("\nPOSSIBLE CAUSES:")
    print("1. Incorrect Access Key or Secret Key (Check for typos or extra spaces).")
    print("2. Region Mismatch (Server configured with a different region than 'us-east-1').")
    print("3. System Time Skew (Ensure your local clock is synchronized).")
    print("4. Server-side configuration (Nginx proxy headers, MinIO policy).")
