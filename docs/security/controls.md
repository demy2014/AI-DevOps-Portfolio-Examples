# Security controls and production gap list

Implemented in this demo: input validation, bounded text fields, webhook token option, no execution of remediation, explicit human review, audit records for incident decisions, duplicate lead-email check, bounded CSV upload, and no automated outbound messaging.

Before production: OIDC/SSO and role-based access control; server-side authorization on every action; managed secrets and rotation; TLS; private subnets and security groups; WAF/rate limits; database encryption and backups; migration tooling; structured redacted logs; retention/deletion policy; dependency and image scanning; SBOM; threat modeling; privacy/legal review; CRM OAuth and least privilege; approval identity binding; immutable audit export; incident response and recovery tests.

Do not treat demo headers such as `X-Actor` as authentication. Do not expose unauthenticated APIs to the public internet.
