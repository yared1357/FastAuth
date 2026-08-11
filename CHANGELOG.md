# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-08-10

### Added

- 🎉 Initial release of FastAuth
- Core `FastAuth` class with dependency injection support
- JWT authentication strategy with access/refresh tokens
- Bearer token transport (Authorization header)
- Cookie transport (HttpOnly secure cookies)
- `AuthenticationBackend` combining strategy + transport
- `UserManager` with full user lifecycle management
  - Registration with email verification
  - Login / logout
  - Password reset flow
  - User profile management
- Async SQLAlchemy database adapter
- Pydantic v2 user schemas (extensible via mixins)
- Password hashing with Bcrypt (default) and Argon2 (optional)
- Pre-built FastAPI routers:
  - `/auth/login`, `/auth/logout`, `/auth/refresh`
  - `/auth/register`
  - `/auth/verify`, `/auth/request-verify-token`
  - `/auth/forgot-password`, `/auth/reset-password`
  - `/users/me`, `/users/{id}`
- Custom exception hierarchy with auto-registered handlers
- Full type annotations (PEP 484)
- Comprehensive test suite with pytest-asyncio
- GitHub Actions CI/CD pipeline
- Contributing guide, issue templates, and PR template

[Unreleased]: https://github.com/fastauth/fastauth/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fastauth/fastauth/releases/tag/v0.1.0
