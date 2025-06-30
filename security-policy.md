# Security Policy

## Supported Versions

We actively support the following versions of EPR Co-Pilot:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do NOT create a public GitHub issue

Security vulnerabilities should not be reported through public GitHub issues.

### 2. Report privately

Send an email to security@epr-copilot.com with:
- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Any suggested fixes (if available)

### 3. Response timeline

- **Initial response**: Within 24 hours
- **Status update**: Within 72 hours
- **Resolution timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-14 days
  - Medium: 14-30 days
  - Low: 30-90 days

## Security Measures

### Automated Security Scanning

Our CI/CD pipeline includes:

- **Dependency scanning**: npm audit, pip-audit
- **Static code analysis**: Bandit, ESLint security rules
- **Container scanning**: Trivy
- **Secrets detection**: TruffleHog
- **Infrastructure scanning**: Terraform security checks

### Security Best Practices

#### Backend Security
- JWT token authentication
- Rate limiting on all endpoints
- Input validation and sanitization
- SQL injection prevention via SQLAlchemy ORM
- CORS configuration
- Security headers middleware
- Audit logging for sensitive operations
- Data encryption at rest and in transit

#### Frontend Security
- Content Security Policy (CSP)
- XSS protection
- Secure cookie handling
- Input sanitization
- Dependency vulnerability monitoring

#### Infrastructure Security
- HTTPS enforcement
- Database encryption
- Secure environment variable handling
- Regular security updates
- Access control and monitoring

## Vulnerability Disclosure

When a vulnerability is confirmed:

1. We will work on a fix immediately
2. A security advisory will be published
3. Affected users will be notified
4. A patch release will be issued
5. The vulnerability will be disclosed publicly after users have had time to update

## Security Contact

For security-related questions or concerns:
- Email: security@epr-copilot.com
- PGP Key: [Available on request]

## Acknowledgments

We appreciate security researchers who responsibly disclose vulnerabilities. Contributors will be acknowledged in our security advisories (unless they prefer to remain anonymous).
