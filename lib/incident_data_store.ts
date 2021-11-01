import * as core from "@aws-cdk/core";
import * as s3 from "@aws-cdk/aws-s3";

export interface IncidentDataStoreProps {
    readonly bucketName: string
}

export class IncidentDataStore extends core.Construct {
  constructor(scope: core.Construct, id: string, props: IncidentDataStoreProps) {
    super(scope, id);

    const bucket = new s3.Bucket(this, props.bucketName);
  }
}
