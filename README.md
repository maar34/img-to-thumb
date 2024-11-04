# Sample Function: WAV to MP3 Converter

## Introduction

This repository contains a sample serverless function written in Python that converts a WAV audio file to MP3 format. The function performs the following actions:

1. Downloads a WAV file from a specified DigitalOcean Spaces bucket.
2. Converts the WAV file to MP3 format using `audioread` and `lameenc`.
3. Uploads the converted MP3 file back to the Spaces bucket.
4. Sends a notification to a specified endpoint (`config-proxy`) with details of the converted file.

You can deploy this function on DigitalOcean's App Platform as a Serverless Function component. For more information, refer to the [DigitalOcean Functions Documentation](https://docs.digitalocean.com/products/functions/).

### Requirements

- A [DigitalOcean account](https://cloud.digitalocean.com/registrations/new).
- The [DigitalOcean `doctl` CLI](https://github.com/digitalocean/doctl/releases) installed on your local machine.
- Access to a DigitalOcean Spaces bucket.
- The following environment variables set up:
  - `DO_SPACES_REGION`: Your Spaces region (e.g., `nyc3`, `ams3`).
  - `DO_SPACES_BUCKET`: Your Spaces bucket name.
  - `DO_ACCESS_KEY`: Your Spaces access key ID.
  - `DO_SECRET_KEY`: Your Spaces secret access key.
  - **Optional**: Any additional environment variables required by your `config-proxy` endpoint.

## Deploying the Function

### Clone the Repository

```bash
# Clone this repository
git clone <your-repo-url>
cd <your-repo-directory>
```

### Install Dependencies

Ensure that your `requirements.txt` file includes the necessary dependencies:

```plaintext
audioread==2.1.9
boto3==1.26.60
lameenc==1.7.0
requests==2.28.2
```

### Deploy the Function

Use the `doctl` CLI to deploy your function. The `--remote-build` flag ensures that the build and runtime environments match.

```bash
doctl serverless deploy <your-directory> --remote-build
```

**Example:**

```bash
doctl serverless deploy wav-to-mp3-converter --remote-build
```

**Deployment Output:**

```
Deploying 'wav-to-mp3-converter'
  to namespace 'fn-...'
  on host 'https://faas-...'
Submitted action 'convert' for remote building and deployment in runtime python:default
Processing of 'convert' is still running remotely ...
...
Deployed functions ('doctl sbx fn get <funcName> --url' for URL):
  - convert
```

## Using the Function

### Invoke the Function via HTTP Request

You can invoke the function by sending an HTTP `POST` request. Replace `<FUNCTION_URL>` with the URL of your deployed function. You can obtain the function URL using the `doctl` command:

```bash
doctl serverless functions get convert --url
```

**Sample `curl` Command:**

```bash
curl -X POST "<FUNCTION_URL>" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic <YOUR_BASE64_ENCODED_CREDENTIALS>" \
  -d '{
        "trackId": "your-track-id",
        "audioFileWAVKey": "path/to/your/audio.wav"
      }'
```

### Parameters

- **`trackId`**: *(string, required)* The unique identifier for the track.
- **`audioFileWAVKey`**: *(string, required)* The key (path) to the WAV file in your Spaces bucket.

### Response

On successful execution, the function will:

- Convert the WAV file to MP3 format.
- Upload the MP3 file to your Spaces bucket.
- Notify the `config-proxy` endpoint with the `trackId` and `mp3Key`.

**Sample Successful Response:**

```json
{
  "statusCode": 200,
  "body": {
    "message": "Conversion successful",
    "mp3Key": "path/to/your/audio.mp3"
  }
}
```

### Error Handling

If an error occurs during execution, the function will return a `500` status code with an error message.

**Sample Error Response:**

```json
{
  "statusCode": 500,
  "body": "Error message detailing what went wrong"
}
```

## Function Details

### Code Breakdown

The function performs the following steps:

1. **Input Validation**: Checks for the required `trackId` and `audioFileWAVKey` parameters.
2. **Download WAV File**: Uses `boto3` to download the WAV file from your Spaces bucket to a temporary location.
3. **Convert to MP3**: Utilizes `audioread` and `lameenc` to convert the WAV file to MP3 format.
4. **Upload MP3 File**: Uploads the converted MP3 file back to the Spaces bucket.
5. **Cleanup**: Deletes temporary files to free up resources.
6. **Notify `config-proxy`**: Sends a `PUT` request to the specified endpoint with the `trackId` and `mp3Key`.

### Environment Variables

Ensure the following environment variables are set in your `project.yml` or function configuration:

```yaml
environment:
  DO_SPACES_REGION: <your-spaces-region>
  DO_SPACES_BUCKET: <your-spaces-bucket-name>
  DO_ACCESS_KEY: <your-spaces-access-key>
  DO_SECRET_KEY: <your-spaces-secret-key>
```

### Dependencies

List the dependencies in your `requirements.txt` file:

```plaintext
audioread==2.1.9
boto3==1.26.60
lameenc==1.7.0
requests==2.28.2
```

### project.yml Configuration

Your `project.yml` should define the function and its runtime:

```yaml
packages:
  - name: wav-to-mp3
    actions:
      - name: convert
        runtime: 'python:3.9'
        main: __main__.main
    environment:
      DO_SPACES_REGION: ${DO_SPACES_REGION}
      DO_SPACES_BUCKET: ${DO_SPACES_BUCKET}
      DO_ACCESS_KEY: ${DO_ACCESS_KEY}
      DO_SECRET_KEY: ${DO_SECRET_KEY}
```

### build.sh Script

Include a `build.sh` script if you need to handle any build steps, especially for dependencies that require compilation:

```bash
#!/bin/bash

set -e

virtualenv --without-pip virtualenv
pip install -r requirements.txt --target virtualenv/lib/python3.9/site-packages
```

## Testing the Function

### Using `doctl` CLI

Invoke the function with test parameters:

```bash
doctl serverless functions invoke convert \
  --param trackId=your-track-id \
  --param audioFileWAVKey=path/to/your/audio.wav
```

### Using Postman

1. **Create a new POST request** to `<FUNCTION_URL>`.
2. **Headers**:
   - `Content-Type`: `application/json`
   - `Authorization`: `Basic <YOUR_BASE64_ENCODED_CREDENTIALS>`
3. **Body**:
   ```json
   {
     "trackId": "your-track-id",
     "audioFileWAVKey": "path/to/your/audio.wav"
   }
   ```
4. **Send the request** and verify the response.

## Notes

- **Authentication**: The function requires Basic Authentication using credentials provided by DigitalOcean. Ensure you include the correct `Authorization` header in your requests.
- **Timeouts**: If processing large audio files, be mindful of function execution time limits. Optimize your code or adjust timeout settings as needed.
- **Error Logging**: Use `print` statements or logging to output debug information during development.

## Learn More

- [DigitalOcean Functions Documentation](https://docs.digitalocean.com/products/functions/)
- [DigitalOcean Spaces Documentation](https://docs.digitalocean.com/products/spaces/)
- [doctl Serverless Reference](https://docs.digitalocean.com/reference/doctl/reference/functions/)

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss improvements or bug fixes.

---

Feel free to customize this README to suit your specific repository details, such as adding a link to your repository, adjusting the function name, or including additional information relevant to your use case.