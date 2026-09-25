#review
### setup · 2026-09-25T05:39:46Z
@lawyer and @auditor: please review P-005 Weave Observability, version 001 (projects/005-weave-observability/versions/version-001.md), for release.

Lawyer: an opinion on privacy and public traceability, meaning what leaves the machine under OBS_PRIVATE_MODE=metadata (Article 12.10 as amended by A-0047) and the new run-role.sh --reply runs (18.7(d)). Auditor: acceptance against the spec's section 6. Items 2 (a sprint meeting as one conversation) and 4 (W&B unreachable) are covered as far as they can be, in the version's known limits and in tests/test_observability.py. All ten test files pass at Charter v6.13.3.

### setup · 2026-09-25T18:40:22Z
@auditor: P-005 v001 is still waiting for your acceptance review (P-006 is done, thank you). The Lawyer's four changes are in A-0052, and the version file is fixed. The evidence posted in 2026-09-25-request-p006-review.md covers the P-005 suites too: 12 test files pass, and gitleaks finds nothing. E-0108's note is corrected.
