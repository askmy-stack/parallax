# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | Yes       |
| < 0.1   | No        |

This repository is an early research codebase. Security support focuses on
preventing credential leakage, unsafe recovery actions, and malicious benchmark
or example code.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead:

1. Email the maintainer via the address listed on the
   [askmy-stack GitHub profile](https://github.com/askmy-stack), **or**
2. Use GitHub's private vulnerability reporting for this repository (Security →
   Report a vulnerability), if enabled.

Include:

- a description of the issue and impact
- steps to reproduce
- affected files / versions if known

You should receive an acknowledgement within 7 days. We will coordinate a fix
and disclosure timeline after triage.

## Scope notes for this research project

- Benchmark failure injectors must not execute arbitrary remote code by default.
- Examples must not ship live credentials or private API keys.
- Recovery actions that mutate external state should be sandboxed or clearly
  marked as unsafe for production use.
- LLM-based judges and detectors should avoid sending secrets in prompts.
