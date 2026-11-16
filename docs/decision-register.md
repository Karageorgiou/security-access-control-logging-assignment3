# Assignment 3 — Architecture decision register

**Status:** factual tracking index only · **Owner of decisions:** Product Architect (P-ADR), System Architect (S-ADR), with explicit concurrence where their respective dimensions intersect · **Implementation:** not authorized by this register.

This register traces seven **proposed**, unaccepted decision candidates to their unchanged source reports in [`docs/evidence/`](evidence/README.md). Status reflects the documents' latest stated review position at the preserved handoff. A conditional concurrence is not final architecture acceptance; readiness for independent review is not a passing independent review. This index cannot settle professor-level ambiguities or approve an ADR.

## Product Architecture candidates

### P-ADR-01 — Audit Event and Outcome Semantics

- **Owning authority:** Product Architect; technical observation and interception lifecycle require System Architect concurrence.
- **Current status:** **PROPOSED — CONDITIONAL CONCURRENCE**, **not accepted**.
- **Source:** [`03-product-architecture-followup.md`](evidence/03-product-architecture-followup.md), §§ 6 (PC-01), 7 (ADR candidate inventory); [`05-product-architecture-concurrence.txt`](evidence/05-product-architecture-concurrence.txt), §§ 6–8 (PC-01); [`06-system-architecture-concurrence.md`](evidence/06-system-architecture-concurrence.md), §§ 3 SA-C06, 4 (record interface), 6–7.
- **Concurrence:** Product supports separate attempted/completed outcomes, genuine permission-denial evidence, preservation of original libc results, and technical pre/post observation subject to conditions. System reports technical feasibility.
- **Open conditions and risks:** Product must decide what happens when audit persistence fails (PC-01/PC-07); Product must approve operation-code classification for failed creation attempts. Broader interception and pre-delegation wording still require appropriately scoped validation/clarification.
- **Next authority / gate:** Targeted Product Architect decision and required System/Product concurrence; independent architecture review and Supervisor-controlled authorization remain pending.

### P-ADR-02 — File Identity and Query Matching

- **Owning authority:** Product Architect; normalization implementation and observation feasibility belong to System Architect.
- **Current status:** **PROPOSED — CONDITIONAL CONCURRENCE**, **not accepted**.
- **Source:** report 03, §§ 6 (PC-03), 7; report 05, § 4; report 06, §§ 3 SA-C04, 5 S-ADR-02, 6–7.
- **Concurrence:** Product conditionally supports pathname-string identity. System concurs with a shared case-sensitive, lexically normalized absolute-path key for the producer and `audit_monitor -i`, while retaining original paths for actual file operations.
- **Open conditions and risks:** Path aliases, symlinks plus `..`, hard links, and lexical versus physical file equivalence may make distinct-file counts disagree with professor expectations; no inode/`realpath()` equivalence is authorized by these proposals.
- **Next authority / gate:** Product Architect/professor for meaning of distinct files if grading-sensitive; independent architecture review of the disclosed limitation.

### P-ADR-03 — Hash Evidence and Observation Semantics

- **Owning authority:** Product Architect for evidence meaning; System Architect for content observation method and timing.
- **Current status:** **PROPOSED — CONDITIONAL CONCURRENCE**, **not accepted**.
- **Source:** report 03, §§ 6 (PC-04), 7; report 05, § 3; report 06, §§ 3 SA-C02–SA-C03, 5 S-ADR-03, 7.
- **Concurrence:** Both architects support genuine SHA-256 of independently observable content or literal `N/A` when unavailable; System specifies observation stages and no forced stream flush.
- **Open conditions and risks:** The professor's PDF requires a SHA-256 field and does **not** explicitly permit `N/A`. Buffered writes and competing writers limit the conclusion a snapshot supports. Human preference for `N/A` is not professor approval.
- **Next authority / gate:** Professor clarification or explicit human risk acceptance as needed, plus independent architecture review; no claim of full compliance.

### P-ADR-04 — Modification Metrics and Attribution

- **Owning authority:** Product Architect for counting meaning; System Architect for return-value evidence and event recording.
- **Current status:** **PROPOSED — CONDITIONAL CONCURRENCE**, **not accepted**.
- **Source:** report 03, §§ 6 (PC-05), 7; report 05, § 2; report 06, §§ 3 SA-C01, 5 S-ADR-01, 6–7.
- **Concurrence:** Product proposes counting one event for each intercepted positive-return `fwrite()` (`size > 0`, `nmemb > 0`, `returned > 0`) per UID and file, including partial successful returns and writes restoring an earlier state; total is the sum across UIDs. System confirms the return-value evidence is feasible. Hash equivalence is not used for deduplication.
- **Open conditions and risks:** The professor's phrase *unique modifications* may instead mean content changes; positive stream return is not proof of durable content changes. Zero-return is not guaranteed absence of all side effects.
- **Next authority / gate:** Professor clarification for counting meaning if necessary, independent architecture review, then proper acceptance and implementation authorization.

## System Architecture candidates

### S-ADR-01 — Interception Lifecycle and Stream State

- **Owning authority:** System Architect; Product Architect owns associated event/outcome semantics.
- **Current status:** **PROPOSED — READY FOR INDEPENDENT REVIEW**, **not accepted**.
- **Source:** [`04-system-architecture.md`](evidence/04-system-architecture.md), § 8 S-ADR-01; report 05, § 6; report 06, §§ 3 SA-C01, 5 S-ADR-01, 7–9.
- **Concurrence:** Product Architect **CONCUR WITH CONDITIONS**; System Architect confirms pre/post interception, original results and `errno`, a synchronized process-local stream registry, and positive-return write accounting.
- **Open conditions and risks:** Coverage is limited to specified `fopen()`, `fwrite()`, `fclose()` hooks under `LD_PRELOAD`, not system-wide or kernel-wide interception; creation races and failed-attempt operation labeling remain. A targeted Product Architect decision is outstanding.
- **Next authority / gate:** Product Architect on failed-creation code mapping and PC-01/PC-07 persistence policy; independent architecture review and Supervisor-controlled implementation authorization.

### S-ADR-02 — Shared Record and Append Persistence

- **Owning authority:** System Architect; Product Architect owns record meanings, file-identity and audit-failure semantics.
- **Current status:** **PROPOSED — READY FOR INDEPENDENT REVIEW**, **not accepted**.
- **Source:** report 04, § 8 S-ADR-02; report 05, §§ 4–6; report 06, §§ 3 SA-C04–SA-C06, 4 (record interface), 5 S-ADR-02, 7–9.
- **Concurrence:** Product Architect **CONCUR WITH CONDITIONS**; System Architect proposes one log at `/tmp/access_audit.log`, versioned and escaped records, cooperative `flock()`, `O_APPEND`, and explicit permissions for ordinary-user append and read access.
- **Open conditions and risks:** Directory accessibility does not guarantee multi-user file permissions. The demonstrated proposal requires explicit pre-provisioning or verified `0666` mode; world-writable logs permit tampering, and advisory locking does not prevent noncooperating writes. PC-01/PC-07 best-effort audit persistence still needs Product Architect concurrence.
- **Next authority / gate:** Targeted Product Architect decision on logging failure policy; independent architecture review, then multi-UID deployment and parser verification at implementation validation.

### S-ADR-03 — File-Content Hash Observation Strategy

- **Owning authority:** System Architect; Product Architect owns the semantics and proposed `N/A` exception.
- **Current status:** **PROPOSED — READY FOR INDEPENDENT REVIEW**, **not accepted**.
- **Source:** report 04, § 8 S-ADR-03; report 05, §§ 3 and 6; report 06, §§ 3 SA-C02–SA-C03, 5 S-ADR-03, 7–9.
- **Concurrence:** Product Architect **CONCUR WITH CONDITIONS**; System Architect proposes OpenSSL EVP SHA-256 of independently visible contents, explicit observation stage, literal `N/A` when unavailable, no forced `fflush()`, and no general file reconstruction.
- **Open conditions and risks:** `N/A` is an explicit, unapproved departure from the professor's mandatory SHA-256 requirement. Buffered content and races limit snapshot meaning; no full professor-compliance determination exists.
- **Next authority / gate:** Professor-compliance clarification or human risk acceptance where appropriate, independent architecture review and required acceptance by the owning authorities.

## Outstanding issues and gates — not settled by this register

| Issue | Recorded state | Responsible next authority or gate |
| --- | --- | --- |
| SHA-256 unavailable | `N/A` selected as a human-preferred representation but not confirmed by the professor | Professor clarification / human risk decision; architecture reviewer evaluates compliance gap |
| Modification meaning | Per-UID qualifying positive-return `fwrite()` events and total proposed, regardless of resulting hash; professor's "unique" term remains ambiguous | Professor / Product Architect; independent reviewer |
| File aliases | Lexical absolute pathname identity is not physical-file equivalence | Product Architect / professor interpretation; independent reviewer |
| Interception scope | `LD_PRELOAD` wrappers do not observe arbitrary system-wide file activity | Professor scope clarification / independent reviewer |
| Multi-user log integrity | `0666` provisioning can enable multi-UID access but also tampering, and `flock()` is advisory | System Architect deployment contract and independent reviewer |
| Audit persistence failure | System proposes preserving libc result and reporting audit failure separately, but Product contract not yet concurred | **Product Architect (PC-01/PC-07)**, then System/Product concurrence |
| Failed creation-attempt classification | `fopen()` failed-creation attempts require final mapping to operation codes | **Product Architect**, then System/Product concurrence |
| Independent architecture review | Final candidate A3-SA-CONCURRENCE-01 is ready but has **not** passed independent review | Supervisor routes exact frozen evidence to Independent Adversarial Reviewer |

**No accepted ADRs; no application implementation or testing is established by these reports.** Architecture acceptance and implementation authorization remain outside this documentation-only work unit.
