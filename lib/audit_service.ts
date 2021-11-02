// Adapted from starter-kit: https://docs.aws.amazon.com/cdk/latest/guide/serverless_example.html

import * as core from "@aws-cdk/core";
import * as apigateway from "@aws-cdk/aws-apigateway";
import * as lambda from "@aws-cdk/aws-lambda";
import * as s3 from "@aws-cdk/aws-s3";
import * as secretsManager from "@aws-cdk/aws-secretsmanager";

const IncidentBucketRootName = "incidents"
const CACHE_FILE_NAME = "audit_report"

export class AuditService extends core.Construct {
  constructor(scope: core.Construct, id: string) {
    super(scope, id);

    const bucket = new s3.Bucket(this, IncidentBucketRootName);
    const elevateCredentials = new secretsManager.Secret(this, 'ElevateSecretCredentials');

    const handler = new lambda.Function(this, 'requestHandler', {
      handler: 'activity.handler',
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset('resources'),
      timeout: core.Duration.seconds(10),
      environment: {
        "DATA_BUCKET": bucket.bucketName,
        "CREDENTIALS_ARN": elevateCredentials.secretArn,
        "CACHE_FILE_NAME": CACHE_FILE_NAME
      },
    });

    const api = new apigateway.RestApi(this, "SecurityAuditAPIGateway", {
      restApiName: "Elevate Security Audit API",
      description: "This service provides some audit information on user access telemetry."
    });

    const getHandler = new apigateway.LambdaIntegration(handler, {
      requestTemplates: { "application/json": '{ "statusCode": "200" }' }
    });

    api.root.addMethod("GET", getHandler);

    // Give permission to lambda to read credentials stored in Secret Manager
    elevateCredentials.grantRead(handler.role!);
    bucket.grantRead(handler.role!);
    bucket.grantWrite(handler.role!);
  }
}
