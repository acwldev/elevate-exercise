import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import * as IncidentApi2 from '../lib/incident-api2-stack';

test('Empty Stack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new IncidentApi2.IncidentApi2Stack(app, 'MyTestStack');
    // THEN
    expectCDK(stack).to(matchTemplate({
      "Resources": {}
    }, MatchStyle.EXACT));
});
