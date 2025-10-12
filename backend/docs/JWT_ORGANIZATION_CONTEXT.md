# JWT with Organization Context

Guide for using JWT tokens with organization context in DentaFlow.

## Token Structure

### Access Token Claims
- `sub`: User ID
- `email`: User email
- `organization_id`: Current organization UUID
- `organization_role`: Role in organization
- `functional_role`: Functional role
- `exp`: Expiration timestamp
- `type`: Token type

### Usage

```python
from app.core.jwt_utils import create_token_pair

tokens = create_token_pair(
    subject=user.id,
    email=user.email,
    organization_id=membership.organization_id,
    organization_role=membership.organization_role,
    functional_role=membership.functional_role
)
```

See full documentation in codebase.
