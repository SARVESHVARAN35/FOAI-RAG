# KB-005: Redis Connection Failure

Document Type: Troubleshooting Guide
Service: Redis Cache
Severity: High

## Symptoms

The application reports that it cannot connect to the Redis cache.
Features depending on caching or session storage may fail or become
slow.

## Error

Redis connection refused

## Root Cause

The Redis service may be unavailable, the application may be using
an incorrect Redis hostname or port, network connectivity may be
blocked, or Redis may have reached a resource or connection limit.

## Troubleshooting Steps

1. Verify that the Redis service is running.
2. Check the Redis hostname and port configuration.
3. Test network connectivity between the application and Redis.
4. Review Redis server logs.
5. Check Redis connection and resource usage.
6. Verify that firewall or network rules allow the connection.

## Resolution

Restore the Redis service or correct the application connection
configuration. Verify connectivity from the application after making
the change.

## Prevention

Monitor Redis availability, connection failures, resource usage,
and service health.