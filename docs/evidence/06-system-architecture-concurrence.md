# **Assignment 3 — System Architecture Concurrence and Final Review Candidate**

&#x20;Source and authority verification passed

## **1. Verification and authority**

The new handoff's original documents were independently verified against their SHA-256 hashes, without replacing or modifying their contents.

| Evidence                            | SHA-256                           | Result |
| ----------------------------------- | --------------------------------- | ------ |
| Product Architecture Concurrence    | `07e391abd1c8…0a8e27bb3`          | PASS   |
| Original System Architecture        | `6137a0cee185…725d8e0f098`        | PASS   |
| Professor's original PDF            | `24dcd841cc12…249624830bbb`       | PASS   |
| Original requirements investigation | `f76c094ad188…22d94311afbcff5d3a` | PASS   |
| Independent requirements review     | `b49bc2b2636e…243b1b05bcf8abf88`  | PASS   |

The new handoff manifest agrees with the calculated hashes. The original assignment ZIP and previous Product Architecture follow-up were also rechecked against the earlier evidence manifest.

**Live repository verification:**

- Assignment `main`: `c31853dc398edc882c2448e2361ba66dce7087f5` — exact match.
- GitDrive `main`: `63175d7c52bd61b3888bbb6e0576102a87157d80`.
- Canonical governance marker: version `2`, activation PR `#64`.
- PR #64: merged.
- Operative role: `system-architect`, confirmed against the canonical role policy.

The governance role limits this work to technical architecture, interfaces, feasibility and verification criteria. Product semantics remain Product Architect-owned, and independent review remains a separate authority.

**Source precedence:** The professor's original five-page PDF remains the highest assignment authority. The Product Architect's conditional concurrence is authoritative for its own proposed behavioral direction, not proof of professor approval.

## **2. Overall technical determination**

The Product Architect's proposed contracts can be implemented as one coherent assignment-scale architecture.

I find **no fundamental technical incompatibility** between the three proposed ADRs and the selected positive-`fwrite()` counting, pathname identity, genuine-hash-or-`N/A`, and prescribed `LD_PRELOAD` monitoring policies.

However, three limitations remain material:

1. A valid digest of currently readable content does not necessarily represent the content resulting from a buffered write.
2. Lexically normalized pathnames do not always identify the same physical file, particularly where symbolic links and `..` interact.
3. A shared log can serve multiple ordinary UIDs only when its actual file permissions and ownership permit their operations. `/tmp` alone provides no such guarantee.

These limitations must be part of the architecture candidate, not left to the Developer to discover and resolve independently.

## **3. SA-C01–SA-C07 technical confirmations**

### **SA-C01 — Write-event qualification**

**Determination: Technically feasible. System concurrence granted to the proposed counting rule, subject to its stated meaning.**

The `fwrite()` wrapper can record the actual return value after delegating to libc. The standard return value is a count of complete elements, not necessarily bytes.&#x20;

Linux manual page



Define the qualifying predicate:

\\[ Q=(size>0)\land(nmemb>0)\land(returned>0) \\]

For every intercepted `fwrite()`:

| Event                                 | Qualified modifications |
| ------------------------------------- | ----------------------- |
| Requested 5 elements, returned 5      | 1                       |
| Requested 5 elements, returned 2      | 1                       |
| Requested 5 elements, returned 0      | 0                       |
| `size = 0` or `nmemb = 0`             | 0                       |
| Successfully writes identical content | 1                       |
| Successfully restores earlier content | 1                       |

Minimum useful record information is the originating UID, PID, file identity, operation `2`, element size, requested element count, actual returned element count and operation outcome.

The analyzer then calculates:

\\[ M(u,f)=\sum\_{\text{records for }u,f} \mathbf{1}[Q] \\]

\\[ M\_{\text{total}}(f)=\sum_u M(u,f) \\]

Each qualifying record represents one write invocation. Counting does not use SHA-256 deduplication. The aggregate count is also the proposed number of distinct qualifying write-event instances, provided each invocation produces one record.

**Limitation:** A positive `fwrite()` return establishes accepted complete elements according to the C stream interface, not necessarily a durable content change. Zero returned elements do not prove that no partial-element side effect occurred.

**Acceptance tests:** Full success, controlled partial success, zero return, zero-sized requests, repeated identical writes, `A → B → A` and events from distinct UIDs.

No technical disagreement with the Product Architect's chosen counting rule remains. The professor's interpretation of *unique modifications* remains unconfirmed.

### **SA-C02 — Genuine SHA-256 versus&#x20;**`N/A`

**Determination: Technically feasible. System concurrence granted to the representation, not to an assertion of professor compliance.**

Define the hash field as a tagged value with exactly two valid forms:

| Value                                   | Meaning                                   |
| --------------------------------------- | ----------------------------------------- |
| `[0-9a-fA-F]` repeated exactly 64 times | Valid SHA-256 digest of observed contents |
| `N/A`                                   | No valid content digest obtained          |

The parser must distinguish these forms before any analysis.

`N/A` must never be converted to zero, counted as a hash, compared as a content state, or interpreted as evidence of a modification.

I recommend adding a small observation-status field to clarify whether the digest represents an independently visible post-call snapshot, a post-close snapshot, or unavailable evidence. This is a technical evidence label, not a new content-equivalence rule.

The original mandatory hash field remains present.

**Compliance limitation:** The professor explicitly asks for a SHA-256 file-content hash in each log entry. Nothing in the verified PDF authorizes a non-hash placeholder. The human-selected `N/A` policy remains a disclosed specification exception.

### **SA-C03 — Hash observation lifecycle**

**Determination: Feasible with clear observation-point limitations.**

The implementation should distinguish these stages.

| Observation                                  | Contract                                                                                  |
| -------------------------------------------- | ----------------------------------------------------------------------------------------- |
| After `fopen()`                              | Hash independently readable file contents at that moment                                  |
| After `fwrite()`                             | Hash independently readable contents currently visible, which may exclude buffered writes |
| After successful `fclose()`                  | Hash the independently observable post-close contents                                     |
| Unreadable, missing or unobservable contents | Record `N/A`                                                                              |
| Failed close                                 | Do not claim a successful final-state observation                                         |

For all successful hash calculations, the bytes supplied to OpenSSL EVP must actually come from the file contents being observed.

The hash helper should use a separate low-level read-only descriptor, avoiding changes to the application's stream position or buffering.

On close, stream identity must be captured before the real `fclose()` invalidates the stream. Reopening the recorded pathname afterward may observe a different object if it was renamed or replaced, so the architecture must not guarantee exact physical-object identity in that case.

The observation timestamp should be captured separately from potentially expensive hashing work.

**Technical choice:** Do not force `fflush()`, do not retroactively replace earlier hashes with close-time values, and do not implement historical-write reconstruction in the base version.

This meets the Product Architect's technical conditions while preserving the known limitation.

### **SA-C04 — Exact pathname-normalization strategy**

**Determination: Implementable. System concurrence granted to pathname-based identity with the following explicit limitation.**

The proposed strategy separates the actual pathname used for the operation from the pathname comparison key.

1. For an absolute `fopen()` argument, retain the absolute path as requested.
2. For a relative argument, capture the caller's current working directory and join it with the original pathname before the operation can change the relevant context.
3. Preserve that resulting absolute pathname for logging and for referring back to the originally requested file.
4. For analyzer comparison, construct a lexical key by collapsing repeated separators, removing `.` and resolving `..` against preceding components without crossing above the root.
5. Compare keys as case-sensitive strings.
6. Apply the identical algorithm to `audit_monitor -i <filename>`, using the analyzer's own current working directory for relative arguments.

This does not require the target to exist or be readable. In particular, failed access attempts can still receive a pathname-derived identity.

The absolute pathname retained for the event must be used when attempting to observe actual contents. The lexically simplified identity key must not replace the original path for file operations.

**Symlink limitation:** Suppose `/tmp/link` points to `/var/data/subdir`. The path `/tmp/link/../item` can resolve through the symlink into `/var/data/item`. Pure lexical cancellation would instead produce `/tmp/item`.

Therefore, lexical normalization is **not filesystem canonicalization** and can equate pathnames that the kernel resolves to different files.

The Product Architect explicitly acknowledged this issue. I concur with the proposed lexical-key model only as pathname-string identity, with that limitation retained. No inode-equivalence or `realpath()` dependency is introduced.

If the professor expects exact physical-file equivalence, this contract is insufficient. That is an outstanding compliance interpretation, not a problem the Developer should silently repair by changing identity semantics.

The shared test suite must cover relative/absolute equivalence, `./`, repeated separators, `../`, nonexistent targets, inaccessible targets, hard links, and a symlink-plus-`..` counterexample.

### **SA-C05 — Multi-user shared audit log**

**Determination: Technically feasible with an explicit deployment permission contract.**

Use a local Linux filesystem and a single pre-provisioned regular file at `/tmp/access_audit.log`.

The simplest assignment-scale permission policy for unrelated ordinary UIDs is a file mode of `0666`, allowing reading and writing by all participating users. This mode is deliberately not a security-hardening recommendation.

The file should be provisioned before the multi-user demonstration. Merely creating it with `open(..., 0666)` is insufficient because `umask` restricts the resulting permissions. For example, an ordinary `022` mask generally produces `0644`, preventing another UID from appending.&#x20;

Linux manual page



For persistence, the logger should:

- Use `O_WRONLY | O_APPEND | O_CREAT` and non-intercepted descriptor I/O.
- Check that the opened object is a regular file.
- Take a cooperative exclusive `flock()` before writing a complete serialized record.
- Handle interrupted and short writes, and release the lock afterward.
- Avoid changing another user's existing file permissions automatically.
- Reject/report an existing log that cannot be opened for append.

The analyzer should read the same absolute file and cooperate with writer locking when parsing records.

`O_APPEND` supplies atomic end-of-file positioning on the intended local filesystem, while `flock()` provides cooperating-process serialization. Locks are advisory; they do not protect the log from processes deliberately ignoring them.&#x20;

Linux manual page+1



Executable multi-user acceptance procedure

In a disposable Linux test environment with two ordinary accounts, `audit_a` and `audit_b`, and the compiled programs in a directory executable by both:

```
# Run only in a controlled, disposable test environment.
# The first user creates the empty shared log.
sudo -u audit_a touch /tmp/access_audit.log
sudo -u audit_a chmod 0666 /tmp/access_audit.log

# Confirm first ownership and actual permissions.
stat -c '%U %a %n' /tmp/access_audit.log

# Run the preloaded test binary from each user's writable home.
# LIB and TEST must be absolute paths accessible to both users.
sudo -u audit_a sh -c \
  'cd "$HOME" && LD_PRELOAD="$1" "$2"' sh "$LIB" "$TEST"

before=$(wc -c < /tmp/access_audit.log)

sudo -u audit_b sh -c \
  'cd "$HOME" && LD_PRELOAD="$1" "$2"' sh "$LIB" "$TEST"

after=$(wc -c < /tmp/access_audit.log)
test "$after" -gt "$before"

# MONITOR must be the absolute path of the built analyzer.
sudo -u audit_b "$MONITOR" -s
```

The verification must additionally check that the file remains owned by `audit_a`, both UIDs appear in valid appended event records, and the records from the first run remain intact. An `-i` query should be checked against a deliberate common-file test case where both users can access the target.

A second negative test should create a log owned by `audit_a` with mode `0600` and confirm that `audit_b` cannot append. That failure must not be mislabeled as successful logging or permission denial on the application's target file.

**Security limitation:** Mode `0666` permits tampering and truncation by users who can open the file. A group-restricted or privileged logging mechanism would improve integrity, but would add administration or infrastructure. Neither is a prerequisite for this assignment-scale proposal.

### **SA-C06 — Audit persistence failure**

**Determination: The failure is observable, but the application response remains a joint product/system decision.**

The logger can detect failed log opens, lock acquisitions, record writes and closes. It cannot truthfully claim persistence when one of those operations fails.

My technical recommendation is:

- Preserve the intercepted application's original return value and saved `errno`.
- Record the audit-subsystem failure separately through a nonrecursive diagnostic mechanism such as a low-level write to standard error.
- Do not convert a log-write failure into a false target-file denial.
- Do not retry without bound or introduce forced application-level file flushing.

A diagnostic may itself fail or be unobserved, so it is not a guarantee of durable error reporting.

**Remaining concurrence:** PC-01 and PC-07 must explicitly accept best-effort audit persistence that preserves the underlying operation. This policy avoids changing libc behavior but necessarily allows an event to be absent if the shared log cannot be written.

A policy that instead makes the original application operation fail would be a materially different behavioral decision. I do not authorize that change.

### **SA-C07 — Coherence of the three ADRs**

**Determination: Coherent and suitable for independent architecture review, with the declared contractual conditions.**

The three ADRs are compatible:

- S-ADR-01 provides attempted/completed events, UID attribution, stream context and actual `fwrite()` return evidence.
- S-ADR-02 defines consistent producer/analyzer records, multi-user append persistence and pathname comparison.
- S-ADR-03 supplies genuine observed-content hashes or explicit unavailable evidence without changing application stream buffering.

Their interfaces support the selected operation-based modification counts independently of hash availability.

No fourth technical ADR is needed.

The remaining issues are not internal contradictions between the ADRs. They are contractual acceptance of the audit-failure policy, acknowledged professor ambiguities, and the real limits of filesystem observation.

## **4. Final proposed technical architecture**

**C application**

Calls fopen(), fwrite(), fclose()

audit_logger.so — LD_PRELOAD

Interception

Real libc results

Stream registry

FILE \* → pathname

EVP hashing

SHA-256 or N/A

Record writer

Append + flock

**/tmp/access_audit.log**

Versioned, escaped, append-only audit records

**audit_monitor**

-s → distinct denied pathnames per UID

-i → successful-access UIDs and qualifying write counts

### **Final proposed record interface**

Use a versioned tab-delimited record with reversible encoding of filename bytes, including tabs, newlines and separators.

| Field             | Contract                                                        |
| ----------------- | --------------------------------------------------------------- |
| Version           | `v1`                                                            |
| UID / PID         | Decimal values from `getuid()` / `getpid()`                     |
| Absolute filename | Original absolute pathname representation                       |
| UTC date / time   | Separate fields with explicit UTC convention                    |
| Operation         | `0`, `1`, `2`, `3`                                              |
| Denied            | `0` or `1`, based on privilege-denial evidence                  |
| Hash              | Genuine 64-character hexadecimal SHA-256 or `N/A`               |
| Operation outcome | Success, failure or partial completion as observable            |
| Write evidence    | Element size, requested count and returned count for `fwrite()` |
| Hash observation  | Visible snapshot, post-close snapshot or unavailable            |
| Error evidence    | Saved original error information when meaningful                |

For non-write events, write-specific fields have an explicitly defined non-applicable encoding.

Each event is serialized once. The monitor counts one qualifying record per qualifying write invocation. It does not infer modification counts from hashes.

A single agreed parser/serializer specification and golden-record fixtures should be part of the implementation handoff. An additional submitted header file is not necessary.

**One residual event-label decision:** Failed `fopen()` attempts require a consistent operation-code policy where creation was attempted but did not occur. The record can preserve attempted mode, prior existence and failure evidence, but the Product Architect must approve the final mapping of unsuccessful creation attempts to the professor's operation codes.

## **5. S-ADR-01 through S-ADR-03 dispositions**

### **S-ADR-01 — Interception Lifecycle and Stream State**

Proposed · Review-ready

**Final technical choice:** Combined pre/post observation, original libc delegation, preserved results and `errno`, synchronized process-local stream registry, actual `fwrite()` return evidence.

**Product conditions incorporated:** Attempt versus outcome, permission-denial distinction, UID attribution, and one accepted write invocation counted once.

**Alternatives rejected:** Pre-call-only recording cannot confirm outcomes; post-call-only recording loses preexisting-file and pre-close information.

**Acceptance:** Verify all three hooks, full/partial/zero writes, correct stream association, original error preservation and reentrancy avoidance.

**Residual risk:** Incomplete coverage of other I/O interfaces, time-of-check/time-of-use creation races, and the failed-creation operation-code decision.

**Disposition:** Ready for independent architecture review; not binding until approved.

### **S-ADR-02 — Shared Record and Append Persistence**

Proposed · Review-ready

**Final technical choice:** One absolute log, versioned text records, pathname-based identity, cooperative locking, append-only descriptor writes, explicitly provisioned multi-user permissions and strict parsing.

**Product conditions incorporated:** `N/A` as an unavailable hash token, pathname comparison, UID reporting, preservation of prior records, and access by participating users.

**Alternatives rejected:** Database or logging daemon as unnecessarily complex; implicit `/tmp` permissions as unreliable; uncoordinated multiple writes as vulnerable to record interleaving.

**Acceptance:** Two unrelated ordinary UIDs can append and read records, including where another UID created the file first. Parser rejects malformed rows and handles missing/unwritable logs explicitly.

**Residual risk:** World-writable-log integrity, lexical pathname aliases, noncooperating writers and persistence-failure behavior awaiting product concurrence.

**Disposition:** Ready for independent architecture review; acceptance of the audit-failure policy remains a joint gate.

### **S-ADR-03 — File-Content Hash Observation Strategy**

Proposed · Review-ready

**Final technical choice:** OpenSSL EVP SHA-256 of independently observable contents, literal `N/A` when unavailable, explicit observation stage, no forced `fflush()`, no general reconstruction.

**Product conditions incorporated:** Human-selected unavailable-hash handling, no fabricated digests, no claim that a write-time snapshot necessarily includes buffered data.

**Alternatives rejected:** Forced flushing changes application behavior; metadata-derived hashes are not content hashes; general reconstruction exceeds the minimal architecture and cannot cover unobserved writes.

**Acceptance:** Digest comparisons with independent hashing, buffered-write tests, close-time tests, unreadable-file tests and strict treatment of `N/A` in the analyzer.

**Residual risk:** The professor does not permit `N/A` explicitly; post-close snapshots are not automatically race-free or durable.

**Disposition:** Ready for independent architecture review, with unresolved full-specification compliance expressly declared.

No new ADR is necessary. None of these three is published or accepted solely through this report.

## **6. Product/System concurrence matrix**

| Contract              | Product position        | System position                                              | Remaining gate                                                 |
| --------------------- | ----------------------- | ------------------------------------------------------------ | -------------------------------------------------------------- |
| PC-01 Events/outcomes | Conditional concurrence | Technically feasible; concurs with pre/post observation      | Audit-failure policy and failed-creation labeling              |
| PC-02 Coverage        | Concur                  | Concur with prescribed three wrappers                        | Broader professor wording remains ambiguous                    |
| PC-03 File identity   | Conditional concurrence | Concur with lexical pathname keys and documented limitations | Professor's interpretation of distinct files                   |
| PC-04 Hashes          | Conditional concurrence | Concur technically with digest/`N/A` contract                | Explicit professor-compliance risk                             |
| PC-05 Modifications   | Conditional concurrence | Concur with positive-return event counting                   | Professor's meaning of unique modifications                    |
| PC-06 Analyzer users  | Conditional concurrence | Feasible: confirmed successful accesses define membership    | Product decision remains provisional against professor wording |
| PC-07 Records         | Conditional concurrence | Concur with versioned structured interface                   | Final failure policy and implementation validation             |

**Concurrence result:** The selected behavioral directions are technically supportable, and the technical proposal now incorporates them. Conditional concurrence is not equivalent to final architecture acceptance.

The outstanding PC-01/PC-07 audit-failure policy should be returned to the Product Architect as a targeted decision. The recommendation is to preserve underlying operation outcomes and provide a separate audit diagnostic.

## **7. Remaining compliance risks and authorities**

| Risk                                         | Consequence                                                           | Responsible authority                             |
| -------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------- |
| `N/A` instead of mandatory SHA-256           | Potential direct deviation from PDF                                   | Professor clarification; human risk acceptance    |
| Unique modifications defined as write events | May differ from intended content-state uniqueness                     | Professor / Product Architect                     |
| Pathname equality versus physical files      | Aliases and symlink paths may affect distinct-file counts             | Product Architect; professor if grading-sensitive |
| `LD_PRELOAD` coverage                        | Not truly system-wide across arbitrary processes                      | Professor scope clarification                     |
| Audit persistence failure                    | Some events may not reach the log                                     | Product Architect concurrence                     |
| Failed creation attempt classification       | May affect operation-code correctness                                 | Product Architect                                 |
| Existing restrictive log permissions         | Another UID cannot append until the deployment condition is corrected | System deployment/verification                    |

These risks are visible requirements questions, not hidden implementation tasks.

The human has selected the `N/A` strategy despite its acknowledged risk. That establishes a preferred design direction, not an exception granted by the professor.

## **8. Developer milestones and objective acceptance gates**

After the required review and authorization, the Developer can implement the following bounded sequence.

| Milestone | Deliverable                   | Objective acceptance                                                              |
| --------- | ----------------------------- | --------------------------------------------------------------------------------- |
| M1        | Interception and stream state | Three hooks work; libc returns and errors preserved                               |
| M2        | Path and event representation | Correct absolute paths, UID/PID, UTC, operation and outcome                       |
| M3        | Shared logging and parser     | Multi-UID append, complete parseable records, no loss of prior successful entries |
| M4        | Hash observation              | Real EVP digests match reference outputs; `N/A` recognized correctly              |
| M5        | Analyzer `-s` / `-i`          | Five vs six denied identities; per-UID write counts; aggregate counts             |
| M6        | Integration and packaging     | Required tests and exact six-file submission contract verified                    |

### **Mandatory acceptance examples**

For `-i`, the golden fixtures must establish that two successful writes changing `A → B → A` produce two qualifying modification events. Repeating an identical successful write also adds one event. Partial positive-return writes count once, and zero-return writes count zero.

For `-s`, five distinct denied pathname identities must not qualify a UID, while six must. Repeated attempts against one identical identity count once.

For logging, the fixture must demonstrate that `audit_b` can append to a mode-`0666` log created by `audit_a`, that existing records remain readable, and that restrictive permissions produce an explicit audit failure without corrupting the original file-operation result.

For hashing, a write-time digest may match the independently readable old contents while data remains buffered. The test must not misclassify that snapshot as proof of the write's final state.

These acceptance conditions describe the test oracles. No implementation or runtime test has been executed during this work unit.

## **9. Exact candidate and independent-review handoff**

Architecture candidate

Review-ready

## **A3-SA-CONCURRENCE-01**

Assignment 3 · November 16, 2026 · System Architect

**Candidate content:** The SA-C01–SA-C07 determinations, record interface, three ADR dispositions, concurrence matrix, risks and acceptance gates in this report.

**Repository baseline:** `c31853dc398edc882c2448e2361ba66dce7087f5`

**Product input identity:** `07e391abd1c8c4640790764b38828b523b60a63b063ed38cb78239b0a8e27bb3`

**Original System report identity:** `6137a0cee185330b274323a7969889e58af0c91ddd0c77c855972d1dd8e0f098`

**Professor PDF identity:** `24dcd841cc12a90bd7304d35e40d6d4099b12b2e5140eb3f0f7d249624830bbb`

**Governance:** GitDrive v2, activation PR #64, `main` `63175d7c52bd61b3888bbb6e0576102a87157d80`

This candidate ID identifies the report and its declared source baseline. It is not a cryptographic hash of this newly authored report. Before exact-byte independent review, the Supervisor should preserve the report unchanged, calculate its SHA-256 and provide that frozen artifact to the reviewer.

The reviewer should concentrate on the correctness of the write-event counting rule, the symlink normalization limitation, practical multi-user log permissions, audit-failure preservation, and the evidentiary meaning of SHA-256/`N/A`.

## **10. Final readiness verdict**

## **&#x20;READY FOR INDEPENDENT ARCHITECTURE REVIEW**

The proposed System Architecture and Product Architect's conditional contracts form a coherent, implementable technical candidate. Its limitations are explicit, and no further broad architecture investigation is necessary before independent review.

**This is not authorization to develop or claim complete professor compliance.** The audit-failure response needs targeted Product Architect concurrence, and professor-sensitive ambiguities remain disclosed. The relevant approval and review gates must still be satisfied.

**Recommended next authorized step:** Supervisor freezes the exact architecture report, routes it to an independent adversarial reviewer alongside the verified original evidence, and coordinates the remaining targeted concurrence before authorizing implementation.

**Role-compliance record:** No source modification, code implementation, repository mutation, ADR publication, independent self-approval, or development authorization occurred.

**System Architect concurrence work unit complete — REPORT AND STOP.**