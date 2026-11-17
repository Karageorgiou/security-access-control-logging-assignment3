# Assignment 3 — Current Architecture and Project Handoff
**Snapshot:** 2026-11-17 (Europe/Athens)  
**Purpose:** Factual coordination record, NOT a new architecture decision or implementation approval. The professor's original PDF at `raw/Assignment 3 2026.pdf` is authoritative. Older evidence reports remain unchanged under `docs/evidence/`.

## 1. Scope and accepted design baseline

The Product Architect's **Final R03 Scope Correction** expressly withdrew the earlier trusted cross-process log-identity distribution requirement. The System Architect's **Final Minimal Implementation Contract** expressly concurred. The independent adversarial review concluded **PASS WITH DISCLOSED RISKS**, with no identified architecture implementation blocker. This is readiness for development, **not** professor approval of all exceptions, code correctness, or merge approval.

**Explicit human priority:** Complete the professor's required university assignment first. Preserve correctness and professional C engineering; defer optional security features or infrastructure until after the required program works. No daemon, privileged service, extra interceptors, trusted log-identity distribution, tamper-resistant audit store or optional hardening is required.

### 1.1 Interception and events
- Build `audit_logger.so` for `LD_PRELOAD`. Intercept exactly `fopen()`, `fwrite()` and `fclose()` through `dlsym(RTLD_NEXT, ...)`.
- Record UID, PID, absolute pathname, UTC timestamp, operation integer **0 = created/creation attempt, 1 = opened/open attempt, 2 = written, 3 = closed**, denied flag, genuine SHA-256 digest when safely observable, and necessary outcome evidence. Use OpenSSL EVP for SHA-256.
- Preserve the original libc return values, `errno`, and observable operation. Prevent recursive logging. Do not claim complete system-wide file-access interception.

### 1.2 Product/System decisions and risk boundaries
- **R02 — stream provenance:** Track successful intercepted `fopen()` streams and validate their pathname association. If a `FILE *` is unregistered or its association is detectably stale, preserve the real operation and attempt a bounded, nonrecursive diagnostic. Do not invent a filename or count the unsupported operation in pathname-based statistics. `fdopen()`, inherited streams and certain unobserved `freopen()` reassociations cannot be universally attributed under only the three specified wrappers.
- **R03 — shared audit log:** Use one explicitly provisioned `/tmp/access_audit.log`, accessible for ordinary multi-user append **and** analyzer read. Open the existing log for append with `O_APPEND`, `O_NOFOLLOW`, appropriate nonblocking precautions and `fstat()` regular-file validation; coordinate complete records with cooperative `flock()`. Reject missing, symlinked, inaccessible or unsuitable log targets; do not silently recreate the file during interception. Processes may independently validate/adopt the existing log. The deliberately sacrificed protection is trusted cross-process identity agreement and comprehensive detection of hostile replacement/tampering; document the limitation.
- **R04 — audit persistence failure:** A failed append must not alter the application's original libc result or `errno`. Attempt a bounded best-effort diagnostic, do not fabricate a successful audit record, and acknowledge lost audit coverage.
- **R05 — attempted creation:** For a creation-capable `fopen()` mode (`w` or `a` family), use operation **0** when prior absence was observed, including a failed creation attempt; retain separate success/failure evidence. Otherwise classify as opening (**1**) while retaining creation intent and prior-state evidence. Denied flag follows genuine permission-denial evidence, not any arbitrary failure.
- **R09 — hash observation:** Hash safely readable ordinary regular-file contents with OpenSSL EVP, including empty-file SHA-256. Use literal `N/A` only when genuinely unobservable or unsafe (read-inaccessible targets, FIFO/socket/device, unsupported virtual file, unsafe identity); do not fabricate a hash, consume special streams or force `fflush()`. **This is an explicit professor-compliance risk** because the PDF literally calls for SHA-256 in each record.
- **File identity:** Producer and analyzer use the same **case-sensitive, lexically normalized absolute pathname** key. Relative paths such as `Downloads/file.txt` resolve against the current working directory. A distinct hard-link alias may remain a distinct pathname; no general inode or `realpath()` equivalence is promised.
- **Modification count:** Count **one event per intercepted positive-return `fwrite()`** with positive `size` and `nmemb`, including partial successful returns, for a trustworthy path and UID. Identical final hashes are not deduplicated. Zero-return calls do not qualify.
- **Analyzer:** `audit_monitor -s` reports UIDs denied access to **more than five distinct pathnames**; `audit_monitor -i <filename>` reports users who successfully accessed the pathname, per-UID qualifying modification-event counts, and their aggregate total. Persisted, attributable records form the analyzer's evidence.
- **Professor submission files (exactly six):** `README`, `Makefile`, `audit_logger.c`, `audit_logger.so`, `audit_monitor.c`, `test_audit.c`. Development-only GitHub Actions workflows and test fixtures are not extra submitted files.

### 1.3 Disclosed residual risks (not professor-approved exceptions)
The literal SHA-256 requirement vs `N/A`; limited coverage of only three wrappers; unattributable streams and missing events; event-count vs content-change interpretation of “unique modifications”; pathname aliases; buffered write/hash observation timing; best-effort logging gaps; shared writable log not tamper-resistant. Do not silently redefine these as resolved.

## 2. Controlled staged development and test gates

**Human-directed current sequence:** implement each stage → **mandatory GitHub Actions CI and actual assertion checks** → Supervisor source/CI verification → next-stage authorization. A **cumulative independent adversarial code review** and **human WSL end-to-end tests** are deferred until implementation stages are complete and WSL access is available. Neither is waived or claimed already passed. **No PR merges without later authorization.**

1. **Stage 1 — `fopen()` logger.** Completed on `feature/a3-stage1-fopen`, PR [#2](https://github.com/Karageorgiou/security-access-control-logging-assignment3/pull/2), reviewed repository head `9d5baf98e94a3837e4625e7108e7b3d785803fdd`. GitHub Actions push run [44105170716](https://github.com/Karageorgiou/security-access-control-logging-assignment3/actions/runs/44105170716) and PR run [44105187254](https://github.com/Karageorgiou/security-access-control-logging-assignment3/actions/runs/44105187254) both succeeded on this head, including a real `LD_PRELOAD` probe and assertion-based tests. This establishes CI results, **not WSL results or independent code approval**.
2. **Stage 2 — `fwrite()`, `fclose()`, stream tracking.** Authorized and handed to existing Product Developer. Branch should start from the verified Stage 1 head and use a stacked PR targeting `feature/a3-stage1-fopen`; preserve Stage 1 regressions in CI. **Developer working; no Stage 2 CI result has yet been verified in this snapshot.**
3. **Stage 3 — analyzer `audit_monitor -s` and `-i`.** Not yet authorized/implemented at this snapshot.
4. **Stage 4 — `test_audit.c`, Makefile, README, multi-user integration, final professor submission ZIP and final checks.** Not yet authorized/implemented.

**Must still verify later:** end-to-end multi-user logging under two ordinary UIDs; logger and analyzer sharing records; exact denied-file threshold of five versus six; correct write counting and partial returns; permission and invalid-log cases; original results and errno; actual WSL build/test; cumulative independent code review; submission ZIP contents.

**Coding convention:** Use Assignment 2 C files (`ecdh_assign_2.c`, `rsa_assign_2.c`) as style references: PascalCase internal helpers, four-space indent, opening braces on new lines, concise purpose-driven comments, straightforward error handling, and no decorative tutorial scaffolding. Preserve the professor's prescribed external function signatures.

## 3. Repository and governance boundaries

- Assignment repository `Karageorgiou/security-access-control-logging-assignment3`. Initial `main` implementation baseline `c31853dc398edc882c2448e2361ba66dce7087f5` (verify live before acting).
- Documentation branch `docs/a3-evidence-archive`, PR [#1](https://github.com/Karageorgiou/security-access-control-logging-assignment3/pull/1), documentation-only and separate from implementation. Preserve the original six evidence files without rewriting history. This handoff supersedes their *old status annotations*, not their source contents.
- GitDrive Governance v2 activation PR #64; Supervisor routes work and tracks status, Product Architect owns product semantics, System Architect technical architecture, Product Developer implementation, Independent Adversarial Reviewer independent judgments. This handoff **does not publish new ADRs** or transfer those authorities.
- Professor source PDF SHA-256: `24dcd841cc12a90bd7304d35e40d6d4099b12b2e5140eb3f0f7d249624830bbb`.

## 4. Final handoff source identities

The final reports were authored as chat responses, later faithfully transcribed into `A3_Stage2_Authoritative_Handoff_20261117.zip`. These are SHA-256 identities of **the packaged transcriptions**, not independent signatures of original chat artifacts. The ZIP itself is SHA-256 `ec5009a87e034b0b144348d4b7098af980116cbfe60d04ec43658446ef7fd5f7`.

- Full Product R02/R03/R09 cross-concurrence: `d0ff5889b54266ed6b646be1f6098089e8c422c0b3cc91a1288bdc840cc9d6a7` (its earlier strong R03 choice is **superseded**).
- Product R03 final scope correction: `891e9bf86e2edbdf38e1aa1878bfaa70a34b01c9d87a3771034a9416e329d323`.
- System Final Minimal Implementation Contract: `79d17252f408cb43285305b4dda3d5e9fa36e2e8db5cc531a04766b62b31c986`.
- Independent Final Implementation-Readiness Review, `PASS WITH DISCLOSED RISKS`: `ca6690f34b8193a4882c3e600b08fd76c04fdfc94bcd56b1611c321f1c035e70`.
- Other supporting addenda and earlier review source hashes are in the handoff ZIP's `SHA256SUMS.txt`.

**Source hierarchy:** professor PDF → latest jointly concurred Product/System contract and explicit human scope choices → reviewed previous decisions where not superseded → older historical proposals. This handoff is a factual retrieval aid; do not treat its wording as a new independent authority or a substitute for checking the source reports when changing architecture.
