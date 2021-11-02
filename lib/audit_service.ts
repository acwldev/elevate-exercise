// Adapted from starter-kit: https://docs.aws.amazon.com/cdk/latest/guide/serverless_example.html

import * as core from "@aws-cdk/core";
import * as apigateway from "@aws-cdk/aws-apigateway";
import * as lambda from "@aws-cdk/aws-lambda";
import * as s3 from "@aws-cdk/aws-s3";
import * as secretsManager from "@aws-cdk/aws-secretsmanager";
import * as aws_events from "@aws-cdk/aws-events";
import * as aws_events_targets from "@aws-cdk/aws-events-targets";

const IncidentBucketRootName = "incidents"
const CACHE_FILE_NAME = "audit_report"

export class AuditService extends core.Construct {
  constructor(scope: core.Construct, id: string) {
    super(scope, id);

    // S3 Bucket to store snapshot of audit report
    const bucket = new s3.Bucket(this, IncidentBucketRootName);

    // Store credentials to access the mock service
    const elevateCredentials = new secretsManager.Secret(this, 'ElevateSecretCredentials');

    // Lambda handler that serves the API logic
    const apiGatewayHandler = new lambda.Function(this, 'requestHandler', {
      handler: 'activity.handler',
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset('resources'),
      timeout: core.Duration.seconds(3),
      environment: {
        "DATA_BUCKET": bucket.bucketName,
        "CACHE_FILE_NAME": CACHE_FILE_NAME
      },
    });

    // API gateway that serves the API
    const api = new apigateway.RestApi(this, "SecurityAuditAPIGateway", {
      restApiName: "Elevate Security Audit API",
      description: "This service provides some audit information on user access telemetry."
    });

    const getHandler = new apigateway.LambdaIntegration(apiGatewayHandler, {
      requestTemplates: { "application/json": '{ "statusCode": "200" }' }
    });

    api.root.addMethod("GET", getHandler);

    // Lambda that serves business logic of a daemon that periodically uploads a snapshot of
    // audit report to S3
    const dataDaemon = new lambda.Function(this, 'dataDaemon', {
      handler: 'data_daemon.handler',
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset('resources'),
      timeout: core.Duration.seconds(60),
      environment: {
        "DATA_BUCKET": bucket.bucketName,
        "CREDENTIALS_ARN": elevateCredentials.secretArn,
        "CACHE_FILE_NAME": CACHE_FILE_NAME
      },
    });

    // Scheduler resources that trigger the data daemon's lambda to fire periodically
    const dataDaemonEventTarget = new aws_events_targets.LambdaFunction(dataDaemon)

    new aws_events.Rule(this, 'ScheduleRule', {
      schedule: aws_events.Schedule.cron({ minute: '20'}),
      targets: [dataDaemonEventTarget],
    });

    // Give permission to lambda to read credentials stored in Secret Manager
    elevateCredentials.grantRead(dataDaemon.role!);

    // Grant S3 read permission to API Gateway's lambda and write permission to data daemon
    // The former pulls snapshot of audit report from from S3 and the latter periodically updates
    // the snapshot in S3
    bucket.grantRead(apiGatewayHandler.role!);
    bucket.grantWrite(dataDaemon.role!);
  }
}
