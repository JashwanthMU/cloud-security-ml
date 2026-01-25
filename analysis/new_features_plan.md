# New Features for Week 2

## Current Features (6):
1. public_access
2. encryption_enabled
3. versioning_enabled
4. logging_enabled
5. sensitive_naming
6. has_tags

## New Features (4):

### 7. MFA Delete Protection
- **What**: Requires MFA to delete object versions
- **Why Important**: Prevents accidental/malicious deletion
- **How to Extract**: Check `versioning.mfa_delete`

### 8. Lifecycle Policy
- **What**: Automatic data expiration/archival
- **Why Important**: Shows resource is maintained
- **How to Extract**: Check for `lifecycle_rule`

### 9. Risky CORS
- **What**: Cross-Origin Resource Sharing config
- **Why Important**: Wide-open CORS = security risk
- **How to Extract**: Check if `cors_rule` allows `*`

### 10. Tag Quality Score
- **What**: How well-tagged is the resource?
- **Why Important**: Well-tagged = better maintained
- **How to Extract**: Count required tags (Environment, Owner, Purpose)