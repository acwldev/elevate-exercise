#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { AuditServiceStack } from '../lib/audit_service_stack';

const app = new cdk.App();
new AuditServiceStack(app, 'AuditServiceStack', {});
