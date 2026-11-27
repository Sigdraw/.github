# Security policy

## Reporting a vulnerability

Please report security vulnerabilities privately by email to
[hello@sigdraw.com](mailto:hello@sigdraw.com) with "Security" in the subject
line.

Do not report security vulnerabilities through public GitHub issues, pull
requests, or discussions.

Please include as much of the following as you can:

- The affected project (Redstone, Rainglass, or the Sigdraw app) and the
  version, release, or commit hash.
- Your operating system and, for Rust projects, the Rust toolchain version.
- A description of the issue and its potential impact.
- Step-by-step instructions to reproduce it, including any proof-of-concept
  code, input files, or configuration.
- Whether the issue is already public or known to others.

## What to expect

We aim to acknowledge reports within 3 business days. After that, we will
investigate, keep you informed of our progress, and may ask for additional
information. Once the issue is confirmed, we will work on a fix and agree on a
disclosure timeline with you.

## Scope

This policy covers:

- Redstone, the SystemVerilog simulator.
- Rainglass, the Rust UI framework.
- The Sigdraw desktop app.

Vulnerabilities in third-party dependencies should be reported to the
upstream project. If a dependency issue affects one of our projects in a
specific way, we would also like to hear about it.

## Supported versions

Our open-source projects are pre-1.0. Security fixes are applied only to the
latest `main` branch and the latest release. For the Sigdraw app, fixes ship in
the latest release.

## Coordinated disclosure

We follow coordinated disclosure. Please give us a reasonable amount of time to
investigate and release a fix before disclosing the issue publicly. When a fix
is released, we will publish an advisory where appropriate and, with your
permission, credit you for the report.
