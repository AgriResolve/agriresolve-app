# Security Policy

The AgriResolve Protocol team takes the security of our smart contracts, SDK, and oracle backend seriously.

## Supported Versions

| Member | Version | Supported |
|---|---|---|
| `@agriresolve/sdk` | 0.1.x | Yes |
| `agriresolve-web` | 0.1.x | Yes |
| `@agriresolve/indexer` | 0.1.x | Yes |

## Reporting a Vulnerability

If you discover a security vulnerability or exploit risk within `AgriResolve-app`:

1. **Do NOT report security vulnerabilities through public GitHub issues.**
2. Send a detailed report to the protocol maintainers:
   - Email: `edunhassan1006@gmail.com`
   - Telegram: [@HassanKorey](https://t.me/HassanKorey)
3. Please provide:
   - Description of the vulnerability and its potential impact.
   - Proof of concept or reproduction steps.
   - Recommended mitigations if known.

## Sensitive Key Hygiene

- NEVER commit real private keys or seed phrases (`AI_ARBITER_SECRET_KEY`, Stellar accounts).
- Use `.env.example` templates with sanitized placeholders only.
- In production, configure environment variables via secure secret management.
