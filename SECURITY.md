# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | ✅ Yes             |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them responsibly by emailing the maintainers or using [GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability).

### What to include

- Type of vulnerability (e.g., token forgery, privilege escalation, SQL injection)
- Full path of the affected source file(s)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact assessment

### What to expect

- **Acknowledgment** within 48 hours
- **Status update** within 5 business days
- **Fix timeline** based on severity:
  - 🔴 Critical: Patch within 24-48 hours
  - 🟠 High: Patch within 1 week
  - 🟡 Medium: Patch in next release
  - 🟢 Low: Scheduled for future release

We will credit you in the security advisory (unless you prefer to remain anonymous).

## Best Practices for Users

- Always use a **strong, unique secret key** for JWT signing
- Enable **HTTPS** in production
- Use **HttpOnly cookies** for browser-based auth
- Keep FastAuth and its dependencies **up to date**
- Set appropriate **token lifetimes** (short-lived access tokens, longer-lived refresh tokens)
