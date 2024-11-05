# Sample Function: Image Thumbnail Creator

## Introduction

This repository contains a sample serverless function written in Python that creates a thumbnail image from an uploaded image file. The function performs the following actions:

1. **Downloads** an image file from a specified DigitalOcean Spaces bucket.
2. **Creates a thumbnail** in WEBP format (150 x 150 pixels, 1:1 aspect ratio) using the `Pillow` library.
3. **Uploads** the thumbnail image back to the Spaces bucket under a `thumbnails/` directory.
4. **Sends a notification** to a specified endpoint (`config-proxy`) with details of the thumbnail image.

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
git clone https://github.com/maar34/img-to-thumb.git
cd img-to-thumb
```

### Install Dependencies

Ensure that your `requirements.txt` file includes the necessary dependencies:

```plaintext
boto3==1.26.60
requests==2.31.0
Pillow==9.2.0
```

### Deploy the Function

Use the `doctl` CLI to deploy your function. The `--remote-build` flag ensures that the build and runtime environments match.

```bash
doctl serverless deploy img-to-thumb --remote-build
```

**Deployment Output:**

```
Deploying 'img-to-thumb'
  to namespace 'fn-...'
  on host 'https://faas-...'
Submitted action 'imgToThumb' for remote building and deployment in runtime python:default
Processing of 'imgToThumb' is still running remotely ...
...
Deployed functions ('doctl sbx fn get <funcName> --url' for URL):
  - imgToThumb
```

## Using the Function

### Invoke the Function via HTTP Request

You can invoke the function by sending an HTTP `POST` request. Replace `<FUNCTION_URL>` with the URL of your deployed function. You can obtain the function URL using the `doctl` command:

```bash
doctl serverless functions get img-to-thumb/imgToThumb --url
```

**Sample `curl` Command:**

```bash
curl -X POST "<FUNCTION_URL>" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic <YOUR_BASE64_ENCODED_CREDENTIALS>" \
  -d '{
        "trackId": "your-track-id",
        "coverImageKey": "path/to/your/image.jpg"
      }'
```

### Parameters

- **`trackId`**: *(string, required)* The unique identifier for the track or item associated with the image.
- **`coverImageKey`**: *(string, required)* The key (path) to the image file in your Spaces bucket.

### Response

On successful execution, the function will:

- Create a thumbnail image in WEBP format.
- Upload the thumbnail image to your Spaces bucket under the `thumbnails/` directory.
- Notify the `config-proxy` endpoint with the `trackId` and `thumbnailKey`.

**Sample Successful Response:**

```json
{
  "statusCode": 200,
  "body": {
    "message": "Thumbnail creation successful",
    "thumbnailKey": "thumbnails/path/to/your/image_thumbnail.webp"
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

1. **Input Validation**: Checks for the required `trackId` and `coverImageKey` parameters.
2. **Download Image File**: Uses `boto3` to download the image file from your Spaces bucket to a temporary location.
3. **Create Thumbnail**:
   - Opens the image using `Pillow`.
   - Converts the image to RGB mode if necessary.
   - Resizes the image to 150 x 150 pixels while maintaining aspect ratio.
   - Saves the thumbnail in WEBP format with a quality setting that balances size and quality.
4. **Upload Thumbnail Image**: Uploads the thumbnail image back to the Spaces bucket under a `thumbnails/` directory.
5. **Cleanup**: Deletes temporary files to free up resources.
6. **Notify `config-proxy`**: Sends a `PUT` request to the specified endpoint with the `trackId` and `thumbnailKey`.

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
boto3==1.26.60
requests==2.31.0
Pillow==9.2.0
```

### `serverless.yml` Configuration

Your `serverless.yml` file should define the function and its runtime:

```yaml
service: img-to-thumb

provider:
  name: openfaas
  gateway: https://faas-nyc1-<your-namespace>.functions.digitalocean.com

functions:
  imgToThumb:
    handler: main.main
    image: docker.io/<your-dockerhub-username>/img-to-thumb
    environment:
      DO_SPACES_REGION: ${env:DO_SPACES_REGION}
      DO_SPACES_BUCKET: ${env:DO_SPACES_BUCKET}
      DO_ACCESS_KEY: ${env:DO_ACCESS_KEY}
      DO_SECRET_KEY: ${env:DO_SECRET_KEY}
```

### `build.sh` Script

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
doctl serverless functions invoke img-to-thumb/imgToThumb \
  --param trackId=your-track-id \
  --param coverImageKey=path/to/your/image.jpg
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
     "coverImageKey": "path/to/your/image.jpg"
   }
   ```

4. **Send the request** and verify the response.

## Notes

- **Authentication**: Ensure you include the correct `Authorization` header in your requests if your function is secured.
- **Timeouts**: Be mindful of function execution time limits. Optimize your code or adjust timeout settings as needed.
- **Error Logging**: Use logging to output debug information during development.

## Learn More

- [DigitalOcean Functions Documentation](https://docs.digitalocean.com/products/functions/)
- [DigitalOcean Spaces Documentation](https://docs.digitalocean.com/products/spaces/)
- [doctl Serverless Reference](https://docs.digitalocean.com/reference/doctl/reference/functions/)
- [Pillow Documentation](https://pillow.readthedocs.io/en/stable/)

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss improvements or bug fixes.
