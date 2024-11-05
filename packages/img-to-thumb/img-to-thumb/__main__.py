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
    # Get track ID and cover image key from the request
    track_id = event.get('trackId')
    cover_image_key = event.get('coverImageKey')
    
    if not track_id or not cover_image_key:
        return {"statusCode": 400, "body": "trackId and coverImageKey are required"}
    
    # Set paths and file keys
    bucket_name = os.getenv('DO_SPACES_BUCKET')
    thumbnail_key = f"thumbnails/{os.path.splitext(cover_image_key)[0]}_thumbnail.webp"
    
    try:
        # Download image file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False) as image_file:
            s3.download_fileobj(bucket_name, cover_image_key, image_file)
            image_path = image_file.name

        # Open image and create thumbnail
        with Image.open(image_path) as img:
            # Ensure the image is in RGB mode
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Resize image to 150x150 pixels
            img.thumbnail((150, 150), Image.ANTIALIAS)
            
            # Save as WEBP format
            thumbnail_path = tempfile.mktemp(suffix=".webp")
            img.save(thumbnail_path, 'WEBP', quality=80)

        # Upload thumbnail image back to DigitalOcean Spaces
        with open(thumbnail_path, "rb") as thumbnail_data:
            s3.upload_fileobj(
                thumbnail_data,
                bucket_name,
                thumbnail_key,
                ExtraArgs={"ContentType": "image/webp", "ACL": "public-read"}
            )
        
        # Cleanup temp files
        os.remove(image_path)
        os.remove(thumbnail_path)
        
        # POST the thumbnail key to config-proxy
        post_url = "http://media.maar.world:3001/api/tracks/update-thumbnail"
        response = requests.put(post_url, json={"trackId": track_id, "thumbnailKey": thumbnail_key})
        
        if response.status_code == 200:
            return {"statusCode": 200, "body": {"message": "Thumbnail creation successful", "thumbnailKey": thumbnail_key}}
        else:
            raise Exception(f"Failed to notify config-proxy. Status: {response.status_code}, Response: {response.text}")
        
    except Exception as e:
        # Ensure cleanup on failure
        if 'image_path' in locals() and os.path.exists(image_path):
            os.remove(image_path)
        if 'thumbnail_path' in locals() and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        return {"statusCode": 500, "body": str(e)}
