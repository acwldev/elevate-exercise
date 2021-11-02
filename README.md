### Foreword
I wanted to do something with CDK and Lambda and I took this as an opportunity for some practice. Apparently, the solution is never meant to be hosted despite a very specific request for it to be listening on port 9000.

### Instructions on how to run
GET from this endpoint and take data from body: https://mx79hbladf.execute-api.us-east-1.amazonaws.com/prod
No port restrictions are configured

Note: This endpoint will stop working in a week or so, since it's hosted on a temporary AWS account

### Overall strategy
Configure a daemon to pull from 3P data sources and construct a report every 20 minutes. (SLA to meet is 1hr staleness)
This report is cached on cloud
The API itself would then pull the report from cloud.

As an exercise, this is done using serverless AWS. The API is provided via API Gateway backed by a Lamnda handler. The daemon is another Lambda scheduled to run periodically via Cloudwatch Events. The report cache is hosted on S3. Secrets manager is used to securely store and provide credentials used for basic auth.

These infrastructures are managed via AWS CDK, which is an infrastructure-as-code framework built on top of CloudFormation.

### Enhancements to consider
1. Automated tests
Testing are manual in this case (test cases are run via Lambda console). Automated test cases are always welcomed

2. Retries and failovers
Exponential retries on 3P endpoints

3. Performance
Pagination of API, pandas, parallelization

4. Monitoring
Metrics, dashboards, and alarms on faults and traffic of lambdas and dependency calls

5. Auth
Not everyone should necessarily be able to call the API

6. Code organization
Better adoption of OOP, modularization of the infra definitions

### Potential oversights
1. Heterogeneity of data
The data do not appear to follow a consistent format. Some of the data do not seem to map to any known entities. I am not sure if that's intended. For simplicity, unresolvable entities have incident data grouped under "unknown"

2. Data reporting
The 3P data sources appear to return different data over time and may not serve data returned previously. This raises questions on the requirements. Should the API be regularly collecting data and include new and old data into the output? But then the report would quickly bloat. It'd seem like there should be some sort of drop off in that case but that does not appear to be clearly specified in the requirements.

### How to deploy
1. Provision an AWS account with proper access credentials
2. Setup workspace and pull from remote
3. Run `aws configure` and enter the access credentials for the AWS account
4. `cdk synth`
5. `cdk deploy`
