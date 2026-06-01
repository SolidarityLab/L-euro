Security Policy
Supported Versions
DTEP-S is currently in specification phase (v0.1-draft). The reference implementation is not yet in production deployment.

Version	Supported
0.1-draft	Specification review only
Reporting a Vulnerability
CSDT takes security issues in DTEP-S seriously. We appreciate responsible disclosure.

Private reporting channel: security@solidaritylab.eu

Alternatively, use GitHub Security Advisories: https://github.com/SolidarityLab/dtep-f/security/advisories/new

Expected response time: 72 hours for initial acknowledgement.

What to include:

Description of the vulnerability
Steps to reproduce
Affected component (see Scope below)
Potential impact assessment
Coordinated Disclosure Process
Reporter submits vulnerability privately via email or GitHub Security Advisory
CSDT acknowledges within 72 hours
CSDT assesses severity and scope within 7 days
Fix or mitigation developed in coordination with reporter
Public disclosure after fix is available — typically within 90 days of initial report
Reporter credited in the security advisory unless anonymity is requested
Scope
The following components are in scope for security review:

Corner 5 Middleware — EN 16931 XML processing pipeline
DRRDB API — public and protected level endpoints
Taler Exchange integration — DD-18 scrubbing, coin commitment binding, Ed25519 signing
JSON Schema validation — dtep-public.json, dtep-encrypted.json, taler-invoice-ref.json
Analytical layer — τ(H) acyclicity verification, δ(e) computation
Out of Scope
The following are explicitly outside DTEP-F scope and should be reported directly to the respective projects:

Peppol Corner 1–4 transport security — report to OpenPeppol
Taler Exchange internals — report to GNU Taler (https://taler.net/en/contact.html)
Central VIES infrastructure — report to EC DG TAXUD
eIDAS 2.0 / EUDIW — report to the relevant national authority
See docs/threat-model.md Section 6 for the full out-of-scope definition.
