# KB-002: Database Connection Timeout

Document Type: Troubleshooting Guide
Service: Application Database
Severity: High

## Symptoms

The application is unable to establish a connection to the database.
Requests may fail after waiting for the configured connection timeout.

## Error

Database connection timeout

## Root Cause

The application could not establish a database connection within the
configured timeout period. Possible causes include incorrect database
configuration, network connectivity problems, unavailable database
service, or exhausted connection capacity.

## Troubleshooting Steps

1. Verify that the database service is running.
2. Check the database hostname and port configuration.
3. Verify that the application can reach the database server.
4. Check database authentication configuration.
5. Review the application logs for connection errors.
6. Check whether the database connection pool has reached its limit.

## Resolution

Identify the failed connection component and correct the configuration
or connectivity issue. Restart the affected service if required and
verify that new database connections can be established.

## Prevention

Monitor database availability, connection pool usage, and connection
failures. Validate database connectivity during deployment checks.