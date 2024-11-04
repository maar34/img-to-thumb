import os
import tempfile
import boto3
import audioread
import lameenc
import requests

# Initialize DigitalOcean Spaces client
s3 = boto3.client(
    's3',
    endpoint_url=f"https://{os.getenv('DO_SPACES_REGION')}.digitaloceanspaces.com",
    aws_access_key_id=os.getenv('DO_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('DO_SECRET_KEY')
)

def main(event, context):
    # Get track ID and WAV file key from the request
    track_id = event.get('trackId')
    audio_file_wav_key = event.get('audioFileWAVKey')
    
    if not track_id or not audio_file_wav_key:
        return {"statusCode": 400, "body": "trackId and audioFileWAVKey are required"}

    # Set paths and file keys
    bucket_name = os.getenv('DO_SPACES_BUCKET')
    mp3_key = audio_file_wav_key.replace('.wav', '.mp3')

    try:
        # Download WAV file to a temporary location
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            s3.download_fileobj(bucket_name, audio_file_wav_key, wav_file)
            wav_path = wav_file.name

        # Convert WAV to MP3 using audioread and lameenc
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as mp3_file:
            encoder = lameenc.Encoder()
            encoder.set_bit_rate(128)
            encoder.set_in_sample_rate(44100)
            encoder.set_channels(2)
            encoder.set_quality(2)

            with audioread.audio_open(wav_path) as input_file:
                for buf in input_file:
                    mp3_data = encoder.encode(buf)
                    mp3_file.write(mp3_data)
                mp3_file.write(encoder.flush())

            mp3_path = mp3_file.name

        # Upload MP3 file back to DigitalOcean Spaces
        with open(mp3_path, "rb") as mp3_data:
            s3.upload_fileobj(mp3_data, bucket_name, mp3_key, ExtraArgs={"ContentType": "audio/mpeg"})

        # Cleanup temp files
        os.remove(wav_path)
        os.remove(mp3_path)

        # POST the MP3 key to config-proxy
        post_url = "http://media.maar.world:3001/api/tracks/update-mp3"
        response = requests.put(post_url, json={"trackId": track_id, "mp3Key": mp3_key})

        # Check for response status and return accordingly
        if response.status_code == 200:
            return {"statusCode": 200, "body": {"message": "Conversion successful", "mp3Key": mp3_key}}
        else:
            raise Exception(f"Failed to notify config-proxy. Status: {response.status_code}, Response: {response.text}")

    except Exception as e:
        # Ensure cleanup on failure
        if os.path.exists(wav_path):
            os.remove(wav_path)
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
        return {"statusCode": 500, "body": str(e)}
