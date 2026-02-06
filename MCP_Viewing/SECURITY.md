# Security Documentation

## Overview

This document outlines the security measures implemented in the MCP_Viewing Spring Boot application.

## Security Features

### 1. Input Validation

- **Base64 Validation**: All PLMXML data must be valid Base64 encoded. Invalid Base64 throws a clear error message.
- **zlib Compression**: PLMXML data is automatically compressed using zlib before database storage, reducing storage requirements and improving performance.
- **Decompression Validation**: Proper error handling for corrupted or invalid compressed data.
- **Field Validation**: Required fields (SNR, PLMXML) are validated using Jakarta Bean Validation annotations.
- **Global Exception Handling**: Centralized error handling ensures consistent error responses and prevents information leakage.

### 2. Actuator Security

The Spring Boot Actuator is configured with minimal exposure:

```properties
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=never
```

**Only non-sensitive endpoints are exposed:**
- `/actuator/health` - Basic health check (no details)
- `/actuator/info` - Application information

**Sensitive endpoints are NOT exposed:**
- `/actuator/env` - Environment properties
- `/actuator/beans` - Bean information
- `/actuator/metrics` - Metrics
- `/actuator/mappings` - Request mappings
- `/actuator/threaddump` - Thread dump
- And all other sensitive endpoints

### 3. CI/CD Security

#### GitHub Actions Permissions

All workflow jobs follow the principle of least privilege:

```yaml
permissions:
  contents: read  # Read repository content
  checks: write   # Write test results
  packages: write # Push Docker images (docker-build job only)
```

- **No** write access to code
- **No** access to secrets beyond what's needed
- **No** broad permissions

### 4. Database Security

- **Embedded Derby Database**: Runs in-memory or locally, not exposed to network
- **No Default Credentials**: Username and password are empty for development
- **SQL Injection Protection**: JPA/Hibernate uses parameterized queries

### 5. Dependency Security

All dependencies are from trusted sources:
- Spring Boot official starters
- Apache Derby (Apache Software Foundation)
- Lombok (maintained project)
- SpringDoc OpenAPI (official Spring documentation project)

### 6. Docker Security

The Dockerfile follows security best practices:
- Multi-stage build to minimize final image size
- Non-root user for running the application
- Minimal base image (eclipse-temurin:17-jre-alpine)
- No unnecessary tools in the runtime image

## Security Considerations for Production

### 1. Database Configuration

For production deployment, consider:
- Use a production-grade database (PostgreSQL, MySQL, etc.)
- Configure proper authentication credentials
- Enable SSL/TLS for database connections
- Implement database access controls

### 2. API Security

Consider adding:
- Authentication (OAuth2, JWT, etc.)
- Authorization (role-based access control)
- Rate limiting to prevent abuse
- CORS configuration for web clients

### 3. HTTPS/TLS

- Deploy behind a reverse proxy (nginx, Apache)
- Configure TLS certificates
- Enforce HTTPS only

### 4. Logging and Monitoring

- Configure log levels appropriately (reduce DEBUG in production)
- Implement audit logging for sensitive operations
- Set up monitoring and alerting
- Never log sensitive data (passwords, tokens, PII)

### 5. Environment-Specific Configuration

- Use Spring profiles (dev, test, prod)
- Store secrets in secure vaults (not in properties files)
- Use environment variables for sensitive configuration

## Vulnerability Reporting

If you discover a security vulnerability, please:
1. **Do NOT** open a public issue
2. Contact the maintainers directly
3. Provide details about the vulnerability
4. Allow time for a fix before public disclosure

## Security Scanning

This project uses:
- **CodeQL**: Automated code security scanning
- **Maven dependency check**: (can be added for production)
- **GitHub Actions**: Secure CI/CD pipelines

## Compliance Notes

### False Positives

**CodeQL Alert: spring-boot-exposed-actuators-config**
- **Status**: False Positive
- **Reason**: Only non-sensitive endpoints (health, info) are exposed
- **Evidence**: See `application.properties` configuration
- **Mitigation**: Actuator is properly configured with minimal exposure

## Updates and Patching

- Keep dependencies up to date
- Monitor security advisories for Spring Boot and other dependencies
- Test updates in a non-production environment first
- Follow semantic versioning for updates

## Resources

- [Spring Boot Security Documentation](https://spring.io/guides/topicals/spring-security-architecture/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Spring Boot Actuator Security](https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html#actuator.endpoints.security)
