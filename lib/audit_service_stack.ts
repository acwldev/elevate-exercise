// Adapted from starter-kit: https://docs.aws.amazon.com/cdk/latest/guide/serverless_example.html

import * as cdk from '@aws-cdk/core';
import * as audit_service from '../lib/audit_service';

export class AuditServiceStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new audit_service.AuditService(this, 'AuditService');
  }
}
