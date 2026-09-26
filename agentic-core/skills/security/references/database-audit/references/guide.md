# Database Audit Guide

Use this guide when the workflow needs a reminder of the legacy database-audit responsibilities.

- Check parameterization, constraints, and index coverage first.
- Review transaction boundaries and operational safety, not only query syntax.
- Watch for tenant-isolation and privilege issues in multi-tenant access.
- Treat irreversible or lock-heavy migrations as high risk.
- Report findings with impact and remediation direction, not broad rewrites.