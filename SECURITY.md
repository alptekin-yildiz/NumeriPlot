# Security Policy

## Supported versions

Security fixes target the latest published NumeriPlot 0.2.x Public Beta
release unless a release note states otherwise. Version 0.2.0 is distributed as
a Mac app for Apple Silicon (macOS 14 or later); other computers can run it from
source.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability, a privacy problem, or
a report containing sensitive data. Send a concise private report to
[alptekin.yildiz@itu.edu.tr](mailto:alptekin.yildiz@itu.edu.tr) with the subject
`NumeriPlot security report`.

Include, when possible:

- the affected NumeriPlot version or commit;
- the macOS version, and whether you use the Mac app or run from source; for
  source, also the Python version;
- reproduction steps and expected impact;
- whether private data may have been exposed; and
- a minimal synthetic reproducer.

Do not send real research data, credentials, student information, or an
unredacted log unless the maintainer explicitly requests a secure transfer
method. macOS logs may contain local paths and are stored at
`~/Library/Logs/NumeriPlot/numeriplot.log`.

The maintainer will acknowledge reports as capacity allows, investigate, and
coordinate disclosure and a fix when warranted. This project does not provide
a guaranteed response or remediation time. Please avoid public disclosure
until a reasonable coordination attempt has been made.

For ordinary bugs and support questions that contain no sensitive information,
use the public issue tracker.
