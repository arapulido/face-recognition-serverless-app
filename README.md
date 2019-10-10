# Sample serverless application

This is a sample application to demonstrate Datadog serverless observability features. It is based out of the [Image Processing AWS Serverless Workshop](https://github.com/aws-samples/aws-serverless-workshops/tree/master/ImageProcessing) but with the following differences:

* Python, instead of Node.js
* It uses the [Serverless Framework](https://serverless.com/) for deployment
* It uses HTTP calls and SNS messages for coordination, instead of Step Functions

## Deployment

The application requires an [AWS Rekognition Collection](https://aws.amazon.com/rekognition/). You can create one with the `aws-cli` tool:

```aws rekognition create-collection --collection-id <your-rekognition-collection-id>```

The rest of the application is deployed using the Serverless Framework. Follow [their instructions](https://serverless.com/framework/docs/getting-started/) to install it.

Once you have the Serverless framework installed, you can deploy the application following these commands:

```
git clone https://github.com/arapulido/face-recognition-serverless-app
cd face-recognition-serverless-app
npm install
serverless deploy --ddApiKey <datadog_api> --owner <yourname> --rekognition-collection-id <your-rekognition-collection-id>
```

Once it has been deployed, get the HTTP endpoint for the `face-search` function and redeploy it with the correct endpoint option:

```
serverless deploy --ddApiKey <datadog_api> --owner <yourname> --rekognition-collection-id <your-rekognition-collection-id> --face-search-endpoint <face-search-function-endpoint>
```
