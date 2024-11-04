Sample Function: WAV to MP3 Converter
Introduction
This repository contains a sample serverless function written in Python that converts a WAV audio file to MP3 format. The function performs the following actions:

Downloads a WAV file from a specified DigitalOcean Spaces bucket.
Converts the WAV file to MP3 format using audioread and lameenc.
Uploads the converted MP3 file back to the Spaces bucket.
Sends a notification to a specified endpoint (config-proxy) with details of the converted file.
You can deploy this function on DigitalOcean's App Platform as a Serverless Function component. For more information, refer to the DigitalOcean Functions Documentation.

Requirements
A DigitalOcean account.
The DigitalOcean doctl CLI installed on your local machine.
Access to a DigitalOcean Spaces bucket.
The following environment variables set up:
DO_SPACES_REGION: Your Spaces region (e.g., nyc3, ams3).
DO_SPACES_BUCKET: Your Spaces bucket name.
DO_ACCESS_KEY: Your Spaces access key ID.
DO_SECRET_KEY: Your Spaces secret access key.
Optional: Any additional environment variables required by your config-proxy endpoint.
Deploying the Function
Clone the Repository
bash
Copy code
# Clone this repository
git clone <your-repo-url>
cd <your-repo-directory>
Install Dependencies
Ensure that your requirements.txt file includes the necessary dependencies:

plaintext
Copy code
audioread==2.1.9
boto3==1.26.60
lameenc==1.7.0
requests==2.28.2
Deploy the Function
Use the doctl CLI to deploy your function. The --remote-build flag ensures that the build and runtime environments match.

bash
Copy code
doctl serverless deploy <your-directory> --remote-build
Example:

bash
Copy code
doctl serverless deploy wav-to-mp3-converter --remote-build
Deployment Output:

vbnet
Copy code
Deploying 'wav-to-mp3-converter'
  to namespace 'fn-...'
  on host 'https://faas-...'
Submitted action 'convert' for remote building and deployment in runtime python:default
Processing of 'convert' is still running remotely ...
...
Deployed functions ('doctl sbx fn get <funcName> --url' for URL):
  - convert
Using the Function
Invoke the Function via HTTP Request
You can invoke the function by sending an HTTP POST request. Replace <FUNCTION_URL> with the URL of your deployed function. You can obtain the function URL using the doctl command:

bash
Copy code
doctl serverless functions get convert --url
Sample curl Command:

bash
Copy code
curl -X POST "<FUNCTION_URL>" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic <YOUR_BASE64_ENCODED_CREDENTIALS>" \
  -d '{
        "trackId": "your-track-id",
        "audioFileWAVKey": "path/to/your/audio.wav"
      }'
Parameters
trackId: (string, required) The unique identifier for the track.
audioFileWAVKey: (string, required) The key (path) to the WAV file in your Spaces bucket.
Response
On successful execution, the function will:

Convert the WAV file to MP3 format.
Upload the MP3 file to your Spaces bucket.
Notify the config-proxy endpoint with the trackId and mp3Key.
Sample Successful Response:

json
Copy code
{
  "statusCode": 200,
  "body": {
    "message": "Conversion successful",
    "mp3Key": "path/to/your/audio.mp3"
  }
}
Error Handling
If an error occurs during execution, the function will return a 500 status code with an error message.

Sample Error Response:

json
Copy code
{
  "statusCode": 500,
  "body": "Error message detailing what went wrong"
}
Function Details
Code Breakdown
The function performs the following steps:

Input Validation: Checks for the required trackId and audioFileWAVKey parameters.
Download WAV File: Uses boto3 to download the WAV file from your Spaces bucket to a temporary location.
Convert to MP3: Utilizes audioread and lameenc to convert the WAV file to MP3 format.
Upload MP3 File: Uploads the converted MP3 file back to the Spaces bucket.
Cleanup: Deletes temporary files to free up resources.
Notify config-proxy: Sends a PUT request to the specified endpoint with the trackId and mp3Key.
Environment Variables
Ensure the following environment variables are set in your project.yml or function configuration:

yaml
Copy code
environment:
  DO_SPACES_REGION: <your-spaces-region>
  DO_SPACES_BUCKET: <your-spaces-bucket-name>
  DO_ACCESS_KEY: <your-spaces-access-key>
  DO_SECRET_KEY: <your-spaces-secret-key>
Dependencies
List the dependencies in your requirements.txt file:

plaintext
Copy code
audioread==2.1.9
boto3==1.26.60
lameenc==1.7.0
requests==2.28.2
project.yml Configuration
Your project.yml should define the function and its runtime:

yaml
Copy code
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
build.sh Script
Include a build.sh script if you need to handle any build steps, especially for dependencies that require compilation:

bash
Copy code
#!/bin/bash

set -e

virtualenv --without-pip virtualenv
pip install -r requirements.txt --target virtualenv/lib/python3.9/site-packages
Testing the Function
Using doctl CLI
Invoke the function with test parameters:

bash
Copy code
doctl serverless functions invoke convert \
  --param trackId=your-track-id \
  --param audioFileWAVKey=path/to/your/audio.wav
Using Postman
Create a new POST request to <FUNCTION_URL>.
Headers:
Content-Type: application/json
Authorization: Basic <YOUR_BASE64_ENCODED_CREDENTIALS>
Body:
json
Copy code
{
  "trackId": "your-track-id",
  "audioFileWAVKey": "path/to/your/audio.wav"
}
Send the request and verify the response.
Notes
Authentication: The function requires Basic Authentication using credentials provided by DigitalOcean. Ensure you include the correct Authorization header in your requests.
Timeouts: If processing large audio files, be mindful of function execution time limits. Optimize your code or adjust timeout settings as needed.
Error Logging: Use print statements or logging to output debug information during development.
Learn More
DigitalOcean Functions Documentation
DigitalOcean Spaces Documentation
doctl Serverless Reference
Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss improvements or bug fixes.