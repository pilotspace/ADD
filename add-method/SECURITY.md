# Security Policy

ADD (AI-Driven Development) ships as [`@pilotspace/add`](https://www.npmjs.com/package/@pilotspace/add)
on npm and [`pilotspace-add`](https://pypi.org/project/pilotspace-add/) on PyPI. This policy
covers both distributions, their installers, and the skill in this repository.

## Supported Versions

Security fixes land on the latest minor release line. Older lines are not
back-patched — upgrade to the latest `4.0.x` to receive fixes. 3.7.0 was the last release
that shipped the Python engine; it receives no further fixes.

| Version | Supported          |
| ------- | ------------------ |
| 4.0.x   | :white_check_mark: |
| < 4.0   | :x:                |

To check your installed version: the `version:` in `.claude/skills/add/SKILL.md` (project),
`pip show pilotspace-add`, or `npm ls @pilotspace/add`.

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security reports.**

Report privately through one of:

- **GitHub Security Advisories** (preferred) — open a private report via the
  repository's **Security → Report a vulnerability** tab. This keeps the details
  confidential until a fix ships.
- **Email** — `tindang.ht97@gmail.com` with subject `SECURITY: <short summary>`.

Please include:

- the affected version, platform, and install channel (npm / PyPI / source);
- a description of the issue and its impact;
- reproduction steps or a proof of concept, if available.

### What to expect

- **Acknowledgement** within **3 business days** of your report.
- **Triage assessment** (accepted / needs-info / declined, with rationale)
  within **10 business days**.
- For **accepted** reports: a coordinated fix and release, with credit to you in
  the release notes unless you prefer to remain anonymous. We will keep you
  updated on remediation progress.
- For **declined** reports: an explanation of why the issue falls outside the
  project's threat model.

Please give us a reasonable window to release a fix before any public disclosure.
