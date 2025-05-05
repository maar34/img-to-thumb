import os
import tempfile
import boto3
import requests
from PIL import Image

# Initialize DigitalOcean Spaces client
s3 = boto3.client(
    's3',
    endpoint_url=f"https://{os.getenv('DO_SPACES_REGION')}.digitaloceanspaces.com",
    aws_access_key_id=os.getenv('DO_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('DO_SECRET_KEY')
)

def main(event, context):
    entity_id = event.get('entityId')
    entity_type = event.get('entityType')
    cover_image_key = event.get('coverImageKey')
    
    if not entity_id or not cover_image_key or not entity_type:
        return {"statusCode": 400, "body": "entityId, entityType, and coverImageKey are required"}
    
    entity_api_endpoints = {
        'orbiter': 'orbiters',
        'interplanetaryPlayer': 'interplanetaryplayers',
        'track': 'tracks',
        'user': 'users',
        'collection': 'collections'
    }
    
    if entity_type not in entity_api_endpoints:
        return {
            "statusCode": 400,
            "body": f"Invalid entityType. Must be one of {list(entity_api_endpoints.keys())}."
        }
    
    bucket_name = os.getenv('DO_SPACES_BUCKET')
    cover_image_dir = os.path.dirname(cover_image_key)
    original_filename = os.path.basename(cover_image_key)
    name_without_ext, _ = os.path.splitext(original_filename)
    
    thumbnail_filenames = {
        'small': f"{name_without_ext}_thumbnail_small.webp",
        'mid': f"{name_without_ext}_thumbnail_mid.webp"
    }
    
    thumbnail_keys = {
        size: f"{cover_image_dir}/{filename}"
        for size, filename in thumbnail_filenames.items()
    }
    
    try:
        with tempfile.NamedTemporaryFile(delete=False) as image_file:
            s3.download_fileobj(bucket_name, cover_image_key, image_file)
            image_path = image_file.name

        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            sizes = {
                'small': (150, 150),
                'mid': (1024, 1024)
            }
            
            for size_label, dimensions in sizes.items():
                img_copy = img.copy()
                img_copy.thumbnail(dimensions)
                
                thumbnail_path = tempfile.mktemp(suffix=".webp")
                img_copy.save(thumbnail_path, 'WEBP', quality=80)
                
                with open(thumbnail_path, "rb") as thumbnail_data:
                    try:
                        s3.upload_fileobj(
                            thumbnail_data,
                            bucket_name,
                            thumbnail_keys[size_label],
                            ExtraArgs={"ContentType": "image/webp", "ACL": "public-read"}
                        )
                        print(f"Thumbnail '{thumbnail_keys[size_label]}' uploaded successfully.")
                    except Exception as upload_error:
                        print(f"Error uploading thumbnail '{thumbnail_keys[size_label]}': {upload_error}")
                        raise upload_error
                
                os.remove(thumbnail_path)
        
        os.remove(image_path)
        
        base_url = "http://media.maar.world:3001"
        api_endpoint = entity_api_endpoints[entity_type]
        post_url = f"{base_url}/api/{api_endpoint}/update-thumbnail"
        
        payload = {
            f"{entity_type}Id": entity_id,
            "thumbnailKeySmall": thumbnail_keys['small'],
            "thumbnailKeyMid": thumbnail_keys['mid']
        }
        
        response = requests.put(post_url, json=payload)
        
        if response.status_code == 200:
            return {
                "statusCode": 200,
                "body": {
                    "message": "Thumbnail creation successful",
                    "thumbnailKeySmall": thumbnail_keys['small'],
                    "thumbnailKeyMid": thumbnail_keys['mid']
                }
            }
        else:
            return {
                "statusCode": response.status_code,
                "body": f"Failed to notify API. Status: {response.status_code}, Response: {response.text}"
            }
        
    except Exception as e:
        if 'image_path' in locals() and os.path.exists(image_path):
            os.remove(image_path)
        return {"statusCode": 500, "body": str(e)}
