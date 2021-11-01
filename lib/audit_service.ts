// Adapted from starter-kit: https://docs.aws.amazon.com/cdk/latest/guide/serverless_example.html

import * as core from "@aws-cdk/core";
import * as apigateway from "@aws-cdk/aws-apigateway";
import * as lambda from "@aws-cdk/aws-lambda";

export class AuditService extends core.Construct {
  constructor(scope: core.Construct, id: string) {
    super(scope, id);

    const handler = new lambda.Function(this, 'requestHandler', {
      handler: 'activity.handler',
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset('resources'),
    });

    const api = new apigateway.RestApi(this, "security-audit-api", {
      restApiName: "Elevate Security Audit API",
      description: "This service provides some audit information on user access telemetry."
    });

    const getHandler = new apigateway.LambdaIntegration(handler, {
      requestTemplates: { "application/json": '{ "statusCode": "200" }' }
    });

    api.root.addMethod("GET", getHandler);
  }
}
