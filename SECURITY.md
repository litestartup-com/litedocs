# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.4.x   | :white_check_mark: |
| < 0.4   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in LiteDocs, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please email us at **young@litestartup.com** with:

- A description of the vulnerability
- Steps to reproduce the issue
- The potential impact
- Any suggested fixes (optional)

We will acknowledge your report within **48 hours** and aim to provide a fix or mitigation within **7 days** for critical issues.

## Security Considerations

LiteDocs is a documentation rendering tool. When deploying in production, please consider:

1. **Network exposure** — By default, LiteDocs binds to `127.0.0.1`. Only bind to `0.0.0.0` if you intend to expose the server externally, and use a reverse proxy (Nginx) with HTTPS.
2. **File access** — LiteDocs reads Markdown files from the directories you specify. Ensure these directories do not contain sensitive files.
3. **Daemon mode** — PID files and logs are stored in `.litedocs/` in the working directory. Ensure appropriate file permissions.
4. **Dependencies** — Keep dependencies up to date. Run `pip install --upgrade` periodically.

## Disclosure Policy

We follow a coordinated disclosure process. We will credit reporters in the release notes (unless anonymity is requested).
