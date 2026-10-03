# KB-004: VPN Authentication Failure

Document Type: Troubleshooting Guide
Service: Corporate VPN
Severity: Medium

## Symptoms

A user is unable to authenticate to the corporate VPN. The VPN client
rejects the login even though the user believes the credentials are
correct.

## Error

VPN authentication failed

## Root Cause

Authentication failures may result from incorrect credentials,
expired passwords, account restrictions, multi-factor authentication
issues, VPN client configuration problems, or authentication service
availability.

## Troubleshooting Steps

1. Verify the username and password.
2. Check whether the user's password has expired.
3. Verify that the user account is active.
4. Check whether multi-factor authentication is completing correctly.
5. Verify the VPN server and client configuration.
6. Check authentication service availability.
7. Review VPN client logs for authentication errors.

## Resolution

Correct the identified authentication or configuration problem.
If the account is restricted or the authentication service is
unavailable, escalate the issue to the appropriate IT administrator.

## Prevention

Monitor authentication service availability and maintain documented
VPN configuration and account-management procedures.