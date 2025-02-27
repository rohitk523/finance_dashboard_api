# app/services/storage.py
import os
import shutil
from typing import Optional
import uuid
from datetime import datetime

from fastapi import UploadFile
import boto3
from botocore.exceptions import NoCredentialsError

from app.config import settings

def store_file(file: UploadFile, directory: str = None) -> str:
    """
    Store a file and return the file path or URL.
    Supports local file storage or S3 based on configuration.
    """
    if settings.STORAGE_TYPE == "s3":
        return store_file_s3(file, directory)
    else:
        return store_file_local(file, directory)

def store_file_local(file: UploadFile, directory: str = None) -> str:
    """
    Store a file in the local file system.
    """
    # Create a unique filename
    filename = generate_unique_filename(file.filename)
    
    # Create the directory if it doesn't exist
    base_dir = settings.LOCAL_STORAGE_PATH
    if directory:
        storage_dir = os.path.join(base_dir, directory)
    else:
        storage_dir = base_dir
        
    os.makedirs(storage_dir, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(storage_dir, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Return relative path from base directory
    relative_path = os.path.join(directory if directory else "", filename) if directory else filename
    return relative_path

def store_file_s3(file: UploadFile, directory: str = None) -> Optional[str]:
    """
    Store a file in an S3 bucket.
    """
    try:
        # Create S3 client
        s3 = boto3.client('s3')
        
        # Create a unique filename
        filename = generate_unique_filename(file.filename)
        
        # Create S3 key with directory if provided
        key = f"{directory}/{filename}" if directory else filename
        
        # Upload the file
        s3.upload_fileobj(
            file.file,
            settings.S3_BUCKET_NAME,
            key,
            ExtraArgs={"ContentType": file.content_type}
        )
        
        # Return the S3 URL
        return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.S3_REGION}.amazonaws.com/{key}"
    except NoCredentialsError:
        print("AWS credentials not available")
        return None
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return None

def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename to prevent collisions.
    """
    # Extract file extension
    if "." in original_filename:
        ext = original_filename.rsplit(".", 1)[1]
    else:
        ext = ""
    
    # Create a unique name using timestamp and UUID
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    if ext:
        return f"{timestamp}_{unique_id}.{ext}"
    else:
        return f"{timestamp}_{unique_id}"

def delete_file(file_path: str) -> bool:
    """
    Delete a file from storage.
    """
    if settings.STORAGE_TYPE == "s3":
        return delete_file_s3(file_path)
    else:
        return delete_file_local(file_path)

def delete_file_local(file_path: str) -> bool:
    """
    Delete a file from local storage.
    """
    try:
        full_path = os.path.join(settings.LOCAL_STORAGE_PATH, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

def delete_file_s3(file_url: str) -> bool:
    """
    Delete a file from S3 storage.
    """
    try:
        # Extract key from URL
        s3_prefix = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.S3_REGION}.amazonaws.com/"
        if file_url.startswith(s3_prefix):
            key = file_url[len(s3_prefix):]
            
            # Create S3 client
            s3 = boto3.client('s3')
            
            # Delete the file
            s3.delete_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=key
            )
            return True
        return False
    except Exception as e:
        print(f"Error deleting file from S3: {e}")
        return False