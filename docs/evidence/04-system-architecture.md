# **Assignment 3 — System Architecture and Implementation Readiness**

&#x20;Mandatory identity and governance checks passed

## **1. Verification and authority record**

The initial preflight establishes the following:

| Check                                   | Result                                                      |
| --------------------------------------- | ----------------------------------------------------------- |
| Assignment repository `main`            | &#x20;Exact SHA `c31853dc398edc882c2448e2361ba66dce7087f5`  |
| GitDrive Governance v2                  | &#x20;Active, canonical version `2`                         |
| Activation PR #64                       | &#x20;Merged                                                |
| Appointed role                          | &#x20;`system-architect` is an operative Governance v2 role |
| Handoff archive SHA-256                 | &#x20;Exact match                                           |
| Original investigation SHA-256          | &#x20;Exact match                                           |
| Independent requirements review SHA-256 | &#x20;Exact match                                           |
| Latest Product Architect report SHA-256 | &#x20;Exact match                                           |
| Professor's PDF                         | &#x20;Present, matching the supplied manifest hash          |
| Starter corpus                          | &#x20;Extracted and inspected                               |

### **Authority boundary**

GitDrive's operative role catalog assigns technical-system architecture to the System Architect. The supplied appointment is consistent with that authority.

This report may propose component interfaces, interception design, logging, hashing, verification architecture, and technical ADRs. It may not unilaterally establish product semantics, implement code, modify repositories, or approve its own design.

The assignment's own requirements remain authoritative. The Product Architect's latest follow-up is treated as **provisional rather than independently accepted**.

Governance references: [Roles](https://github.com/Karageorgiou/GitDrive/blob/main/docs/GITDRIVE_ROLES.md?utm_source=chatgpt.com) · [Engineering process](https://github.com/Karageorgiou/GitDrive/blob/main/docs/GITDRIVE_ENGINEERING_PROCESS.md?utm_source=chatgpt.com) · [Activation PR #64](https://github.com/Karageorgiou/GitDrive/pull/64?utm_source=chatgpt.com)

## **2. Executive technical recommendation**

**Recommendation:** Build a small, synchronous, process-local audit library with one shared append-only log, one analyzer, and a deterministic test program.

Proposed assignment-scale architecture. The analyzer reads records; it does not reconstruct the application's execution.

The architecture should have the following properties:

1. Preserve the three mandated C function signatures and delegate to the real libc functions.
2. Track a minimal `FILE *`-to-file-context association within each process.
3. Preserve the underlying operation's result and `errno`, even when audit-record generation encounters errors.
4. Use OpenSSL EVP to calculate genuine SHA-256 digests of readable file contents.
5. Record available content evidence without confusing buffered writes with committed file states.
6. Serialize complete records through one shared absolute log path.
7. Let the analyzer implement the professor's two required modes using a common record parser.

**Critical qualification:** This architecture can satisfy the straightforward file-access demonstrations, but cannot guarantee a valid file-content SHA-256 at every possible observation point for every event. Inaccessible files, pending buffered writes, and concurrent mutations create genuine limits. These must remain visible rather than being disguised as solved.

## **3. Component architecture**

| Component                            | Responsibilities                                                                                        | Recommended interface                                    |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `audit_logger.c` / `audit_logger.so` | Intercept, delegate, observe outcomes, track streams, hash contents, append records                     | Exact libc signatures; internal stream and event helpers |
| Stream registry                      | Retain filename, initial existence classification, access mode, and optionally device/inode information | Process-local keyed association by `FILE *`              |
| SHA-256 helper                       | Read an observable regular-file state and return valid digest or explicit failure internally            | Digest plus observation status                           |
| Shared log                           | Exchange event evidence between producer and analyzer                                                   | Versioned textual record format                          |
| `audit_monitor.c`                    | Parse, validate, aggregate and report                                                                   | `-s`, `-i <filename>`, `-h`                              |
| `test_audit.c`                       | Produce required access, modification, close and denial scenarios                                       | Ordinary stdio calls                                     |
| `Makefile`                           | Compile library and programs; support clean/test invocation                                             | GCC, OpenSSL development headers, `-lcrypto`, `-ldl`     |

No daemon, database, kernel module, background worker, or external logging service is justified by the professor's specification.

### **Minimal state**

A stream-context structure needs only the association between a `FILE *` and its path, opening mode, and relevant identity metadata. It may also retain a prior valid digest and an optional write-event counter.

The logger should not cache entire file contents or retain historical write payloads as part of the base design. Those are materially more complex reconstruction mechanisms.

The record format should be implemented by one explicitly agreed producer/parser contract. Because the professor specifies exactly six submission files, shared format definitions may remain in the two C components without introducing an additional required submission file.

## **4. Event lifecycle and interception**

### **4.1 Observable operation lifecycle**

| Stage             | What is observable                                                                       | What cannot generally be established                           |
| ----------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Before `fopen()`  | Requested pathname and mode, current identity, pre-call filesystem metadata              | Whether the requested operation will succeed                   |
| After `fopen()`   | Returned stream or failure, saved `errno`, potential new stream identity                 | Race-free proof of actual creation from a prior `stat()` alone |
| Before `fwrite()` | Requested data, element size/count, registered stream identity                           | How many elements will be accepted                             |
| After `fwrite()`  | Returned completed-element count, stream error indicators, current observable file state | Guaranteed persistence or visibility of buffered data          |
| Before `fclose()` | Stream association and descriptor metadata                                               | Whether the close and pending flush will succeed               |
| After `fclose()`  | Return status, saved `errno`, independently observable final pathname state              | Further safe access to the closed `FILE *`                     |

The technical evidence favors gathering relevant facts both before and after delegation.

The professor's wording about adding auditing capabilities *before delegating* remains a semantic ambiguity. Literal pre-delegation-only recording would prevent the logger from reliably reporting actual outcomes. Therefore, the recommended before/after lifecycle is a **technical proposal awaiting joint Product/System concurrence**, not an accepted reinterpretation of the assignment.

### **4.2 Interception method**

Use `dlsym(RTLD_NEXT, ...)` to resolve the original `fopen()`, `fwrite()`, and `fclose()` entry points. Resolve them reliably without reentering the interception logic, preserve exact arguments and return values, and save the original operation's `errno` before any additional library activity.

Record construction should use non-intercepted low-level file-descriptor operations. A thread-local reentrancy guard provides additional protection where helper functions might indirectly invoke intercepted stdio functions. The stream registry requires synchronization if multiple threads share the process.

Failure of audit logging must not be passed off as a permission denial by the original file operation. It should instead be observable through a diagnostic/error mechanism. Whether a logging failure may influence application execution is an outstanding product-owned failure-policy decision.

### **4.3 Coverage limitations**

`LD_PRELOAD` is a dynamic-linker interception mechanism, not a kernel-wide file-event monitor. It does not automatically observe:

- Other processes that were not loaded with the library.
- Statically linked programs or restricted secure-execution contexts.
- File operations performed through `open()`, `write()`, `pwrite()`, `mmap()`, or other interfaces that bypass the three wrapped functions.
- Some alternate stdio symbols, including `fopen64()` or unlocked variants.
- Changes from other machines or unmonitored writers.

These limitations follow from the prescribed interception mechanism.&#x20;

Linux manual page+1



**System conclusion for PC-02:** Complete system-wide file monitoring is not achievable through the three prescribed wrappers alone. The professor's intended coverage scope requires reconciliation. Expanding to kernel monitoring would materially change the method and is not authorized in this work unit.

## **5. Hashing feasibility — priority investigation**

### **5.1 After&#x20;**`fwrite()`

The distinction that governs this design is:

**Successfully writing to a C stream is not equivalent to making the resulting bytes immediately readable from the filesystem.**

Normal file streams may buffer writes. `fflush()` forces user-space buffered output toward the underlying file, and `fclose()` performs a flush before closing.&#x20;

Linux manual page+2



Example:

Application writes `"ABC"`

`fwrite()` returns success

stdio buffer

## **ABC**

new bytes may be here

File on filesystem

## **OLD**

still independently readable

An independent SHA-256 reader can hash `OLD` rather than the intended `ABC` state. This is a valid observation of old content, not proof of the completed modification's resulting content.

If the underlying file already reflects the written data, a post-`fwrite()` digest can be genuine. However, ordinary stream semantics do not provide a universal guarantee of that visibility.

Forcing `fflush()` after every intercepted write is not recommended. It changes buffering, error timing, and application-visible behavior. It is not an observationally neutral audit operation.

### **5.2 At&#x20;**`fclose()`

`fclose()` is the preferable point for observing the contents after a stream's pending output has been flushed.

A successful `fclose()` supports a stronger final-state observation than an immediately preceding `fwrite()`. However:

- The `FILE *` is unusable after the close, whether or not the close succeeds.
- An independent reader still needs permission to read the file.
- A renamed or deleted pathname may no longer identify the original file.
- Other writers may modify the content between close and hash calculation.
- A successful close does not guarantee crash-durable storage without additional synchronization.

The close-time digest can be associated with the stream's earlier write events through its recorded identity and lifecycle, but it **cannot retroactively transform earlier buffered-write observations into genuine post-write content hashes**.

Delaying all write-event records until close, or rewriting previously appended records, would introduce different behavior and substantial failure cases. Neither should be assumed acceptable.

### **5.3 Unreadable files**

A normal process may be allowed to write a file while being unable to read it. For example, it may successfully open a write-only file whose permission bits prohibit reading.

The logger inherits the process's privileges. Neither OpenSSL nor a separately opened descriptor can produce the SHA-256 of content the logger cannot obtain.

This also applies to denied access attempts: the failure itself may establish that no accessible file contents are available to hash.

The following ideas are not sound general solutions:

- Reverse the previous SHA-256 to recover the content.
- Combine the previous hash with newly written data.
- Hash metadata or the filename as a substitute for contents.
- Assume a write-only stream can be read merely because the process possesses it.

OpenSSL's incremental digest API can accumulate *known bytes in order*, but an already finalized SHA-256 value is not a reversible representation of the file.&#x20;

OpenSSL Documentation



The user's previously established development priority—implement ordinary readable-file cases first—is technically reasonable as a development sequence. It does **not** resolve the mandatory hash-field compliance question.

### **5.4 Reconstruction of newly created files**

Reconstruction is technically possible only when the initial content is known and all relevant changes are captured with their actual order, offsets, and effects.

A newly created, empty file with strictly sequential, fully observed writes is a favorable case. General reconstruction must additionally address truncation, seeking, append semantics, multiple streams, partial writes, concurrent modifications, and unmonitored I/O.

If operations occur at arbitrary offsets, simply hashing the concatenation of `fwrite()` arguments is incorrect.

A complete reconstruction engine therefore does not belong in the base architecture. It remains a deferred technical enhancement, not an established solution for arbitrary write-only files.

### **5.5 Hashing feasibility matrix**

| Case                                                    | Assessment                                         | Recommended observation                                      |
| ------------------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------ |
| Stable readable file after successful `fopen()`         | Reliable under a stable-file assumption            | Real contents via EVP                                        |
| Readable file after successful `fclose()`               | Reliable under stable identity/content assumptions | Post-close contents                                          |
| Readable file immediately after buffered `fwrite()`     | Conditional                                        | Current visible contents, not necessarily new buffered state |
| Unbuffered write, content accessible                    | Conditional                                        | Verify actual resulting state and file identity              |
| Write-only file without read permission                 | Generally unavailable                              | Do not fabricate a digest                                    |
| Denied file without readable contents                   | Generally unavailable                              | Requires professor-approved handling                         |
| File modified concurrently                              | Conditional                                        | Snapshot consistency cannot be assumed                       |
| Newly created, sequentially tracked file                | Reconstructable under restrictions                 | Deferred enhancement                                         |
| General seek/overwrite/concurrent reconstruction        | Material complexity                                | Do not include in initial design                             |
| File closed after process crash or abnormal termination | No guaranteed close event                          | Earlier records may be incomplete                            |

**Hashing recommendation:** Implement a genuine, read-only EVP hashing helper with explicit internal success/failure status. Prefer an independently observable final state at close for post-write content evidence. Permit immediate snapshots at write time only with their actual observation meaning, and never force a flush merely to manufacture a stronger claim.

The final record policy for unavailable or temporally ambiguous hashes remains blocked on PC-04 and professor clarification.

## **6. Shared log and file identity**

### **6.1 Log location and persistence**

The recommended assignment-scale path is:

`/tmp/access_audit.log`

This is a **proposed location**, not a professor-mandated path. Both programs must use exactly the same absolute location regardless of their working directories.

The proposed persistence mechanism is:

- Open the log using low-level file-descriptor operations with `O_APPEND | O_CREAT | O_WRONLY`.
- Serialize each event into a complete record before writing.
- Use a cooperative exclusive `flock()` around record writes, including partial-write handling, to prevent cooperating logger instances from mixing records.
- Preserve the application's original operation outcome if audit persistence fails, subject to the agreed failure policy.

`O_APPEND` atomically positions each write at the end of the file on supported local filesystems. `flock()` supplies advisory coordination between cooperating processes but does not prevent external modification of the file.&#x20;

Linux manual page+1



**Important multi-user limitation:** A directory being accessible to every user does not make its files automatically writable or readable by every user. The log's permissions, ownership and `umask` must be explicitly considered.

A world-writable log is convenient for the assignment but can be altered or truncated by users with sufficient access. Consequently, `/tmp/access_audit.log` cannot be presented as tamper-proof audit infrastructure.

A more secure, privileged collector would require additional infrastructure and authorization. It is not part of this recommendation.

### **6.2 Proposed record contract**

I recommend one versioned, newline-delimited textual format.

| Field          | Suggested representation                      |
| -------------- | --------------------------------------------- |
| Format version | `v1`                                          |
| UID            | Decimal integer                               |
| PID            | Decimal integer                               |
| Filename       | Escaped absolute pathname                     |
| Date           | `YYYY-MM-DD`                                  |
| Time           | `HH:MM:SS.ffffffZ`                            |
| Operation      | Integer `0`, `1`, `2`, `3`                    |
| Denied         | Integer `0` or `1`                            |
| Hash           | 64 hexadecimal characters for a valid SHA-256 |

Optional fields such as operation outcome, original `errno`, event identifier and hash-observation status could strengthen the interface, but their inclusion must not silently alter the agreed semantic contract.

A field containing a filename should be escaped before serialization, preventing embedded tabs or newlines from corrupting record boundaries. The analyzer must decode exactly the same format.

For unavailable hashes, the final representation remains **unapproved**. An explicit status could be technically implemented, but it must not be treated as professor-compliant without the appropriate clarification and concurrence.

### **6.3 File identity strategy**

The professor requires absolute filenames but does not require canonicalized or physical-file identity.

Three principal technical options exist:

| Option                    | Advantages                                                        | Limitations                                                                                  |
| ------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Absolute pathname strings | Simple; directly matches the required log field                   | Aliases may count separately                                                                 |
| Canonicalized paths       | Resolves some relative and symbolic-link differences              | May fail for nonexistent or inaccessible paths                                               |
| Device/inode identity     | Better reflects physical-file identity while inode remains stable | Not meaningful for all denied accesses; rename and inode reuse complicate historical records |

**Recommended implementation starting point:** Record absolute pathname strings, together with optional device/inode evidence when the file is accessible.

For relative paths, the logger must resolve the pathname against the process's working directory at interception time. The analyzer should apply the same accepted normalization policy to its `-i` argument.

The System Architect should not independently decide whether symbolic-link aliases, hard links or differently spelled paths count as the same file. That is PC-03.

### **6.4 Stream registry and lifecycle**

The `FILE *` registry should be updated only after a successful `fopen()` and should retain the associated filename until the intercepted `fclose()`.

For opening classification, the recommended sequence is to inspect existence before `fopen()`, then consider the actual return status and opening mode.

This follows the professor's `stat()` hint, but has a race: another process may create or delete the file between the initial check and `fopen()`. A prior `stat()` alone cannot prove that the current call actually created the file in all concurrent cases.

At `fclose()`, capture identity information before calling the real function and remove the registry entry regardless of the close result. Reusing the invalidated `FILE *` afterward would be incorrect.

## **7. Analyzer and verification design**

### **7.1 Shared parser**

The analyzer should parse each record into a validated internal structure before using it.

Validation includes correct field count, numeric ranges, permitted operation codes, UTC timestamp encoding, pathname escaping and valid hash representation.

Malformed records should be reported or skipped without crashing. A malformed record must never contribute to suspicious-user counts or modification statistics.

### **7.2 Suspicious users:&#x20;**`-s`

The fundamental structure is:

`UID → set of distinct qualifying denied-file identities`

For each valid qualifying denial, add the file identity to that UID's set. Print the UID only when the set contains more than five distinct files.

Five distinct files

# **5**

Does not qualify

Six distinct files

# **6**

Qualifies

Repeated denial attempts against the same accepted file identity contribute only once.

The technically defensible initial denial classifier is an underlying access failure with permission-related evidence such as `EACCES` or `EPERM`, rather than every nonzero `errno`. Not every failed operation represents insufficient privileges.

The Product Architect must still confirm which operation codes qualify as denied access attempts for the suspicious-user calculation.

### **7.3 File activity:&#x20;**`-i <filename>`

The analyzer needs two logical aggregations:

1. File-associated UIDs, based on the accepted definition of access.
2. Per-UID modification activity, plus the unique-modification statistic.

A per-UID successful-`fwrite()` counter is technically straightforward and directly supported by an intercepted operation and its UID.

Counting observed content changes is more complicated. It requires comparable content observations, an accepted time relationship and attribution evidence.

A hash difference between successive audit records does not establish that the UID attached to the second record caused that difference. An unmonitored process could have performed the intervening modification.

The professor explicitly permits modification counting based on `fwrite()` **or** differing hashes. Neither method is required to agree with the other under the existing evidence.

I recommend designing the parser and aggregation interface to support a selected method, rather than implementing all possible metric interpretations. The selection and the meaning of unique modifications remain PC-05 decisions.

### **7.4 Verification plan**

The subsequent Developer should produce test evidence for the following scenarios.

| Test                           | Expected verification                                   |
| ------------------------------ | ------------------------------------------------------- |
| Clean GCC build                | Shared library and both executables compile             |
| Basic preload                  | Calls to all three wrapped functions are observed       |
| New file                       | Creation event recorded with code `0`                   |
| Existing file                  | Opening event recorded with code `1`                    |
| Write                          | Code `2`, correct original return behavior              |
| Close                          | Code `3`, correct original return behavior              |
| Permission denial              | Denied flag set only for genuine privilege failures     |
| Non-permission failure         | Not incorrectly counted as a denial                     |
| Normal SHA-256                 | Matches independently calculated file-content digest    |
| Buffered write                 | Does not falsely claim an unobservable post-write state |
| Read-denied/write-allowed file | Demonstrates the missing-content limitation             |
| Repeated denial                | Same file identity not counted repeatedly               |
| Five distinct denials          | UID excluded from `-s` result                           |
| Six distinct denials           | UID included in `-s` result                             |
| Relative/absolute paths        | Match according to accepted PC-03 contract              |
| `-i` multi-user file           | UIDs and counts match accepted PC-05/PC-06              |
| Invalid options                | Appropriate help or error                               |
| Concurrent logger processes    | Records remain individually parseable                   |
| Log unwritable                 | Failure is handled under the accepted policy            |
| Final ZIP                      | Exact six submission files and required README details  |

Permission-denied tests must run in an environment that actually enforces the restriction. Testing as root is unsuitable for many conventional permission-bit scenarios because privileged processes may bypass those restrictions.

The test fixture should use an ordinary unprivileged Linux account, controlled ownership and permission bits, and isolated files. Multiple UIDs require separate process identities.

The Developer must also inspect the resulting audit records rather than merely checking that the demonstration program exited successfully.

**Evidence status:** These are proposed tests. No tests have been executed against a completed implementation, and no PASS claim is made for runtime behavior.

## **8. Technical ADR candidates**

Three technical decisions merit durable records. All are proposed and require the relevant approvals before being marked Accepted.

### **S-ADR-01 — Interception Lifecycle and Stream State**

Proposed · Technical ownership: System Architect

**Problem:** Accurate outcomes and stream identity require observations before and after the intercepted calls.

**Requirements:** Three overridden libc functions, creation/opening distinction, event codes, denied flag and graceful operation.

**Alternatives:** Pre-call-only recording; post-call-only recording; combined pre/post observation.

**Recommendation:** Combined observation, with a process-local stream registry and preservation of original results.

**Consequences:** Additional state and locking responsibilities; concurrent creation classification remains best-effort.

**Validation:** Confirm event ordering, function return preservation, `errno`, stream association and recursion prevention.

**Concurrence:** PC-01 and lifecycle-related PC-04 semantics require Product Architect agreement. Professor clarification may be needed regarding literal pre-delegation wording.

### **S-ADR-02 — Shared Record and Append Persistence**

Proposed · Technical ownership: System Architect

**Problem:** Several processes must write records that a separate analyzer can read consistently.

**Requirements:** Shared `access_audit.log`, append mode, all mandatory fields, consistent producer/consumer interpretation.

**Alternatives:** Text lines, binary records or externally managed storage.

**Recommendation:** A versioned, escaped, line-oriented textual format using one absolute log path and coordinated append operations.

**Consequences:** Human-readable records and simpler debugging, but pathname encoding, error handling and shared-file permission rules must be implemented correctly.

**Validation:** Round-trip parser tests, concurrency tests, malformed-record rejection and multi-user access checks.

**Concurrence:** PC-03 for identity, PC-07 for field meanings, and PC-01 for logging failures.

### **S-ADR-03 — File-Content Hash Observation Strategy**

Proposed · Blocked for final acceptance

**Problem:** The mandatory hash field cannot always be populated with a genuine digest of the intended file state.

**Requirements:** SHA-256 using OpenSSL EVP for file contents on every log entry.

**Alternatives:** Immediate post-call read, forced flush, post-close observation, delayed event persistence, content reconstruction.

**Recommendation:** Real content reads where possible, without forced flushing. Prefer close-time observation for the final visible state. Defer reconstruction.

**Consequences:** Some event-time hashes can be stale relative to buffered data, and some hashes are unavailable entirely.

**Validation:** Independent SHA-256 comparisons, buffered writes, denied reads, file replacement and concurrent changes.

**Concurrence:** PC-04 and PC-05. Professor clarification on inaccessible hashes and intended observation time is required before asserting full compliance.

These are technical ADR candidates, not permission to publish ADR files.

## **9. PC-01–PC-07 feasibility and concurrence matrix**

| Contract                            | System Architect assessment         | Required action                                                                              |
| ----------------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------- |
| **PC-01** Audit events and outcomes | Feasible with stated limitations    | Concur on pre/post lifecycle, denial classification and failure policy                       |
| **PC-02** Monitoring coverage       | Requires Product/System concurrence | Establish the intended scope; literal system-wide coverage is beyond the prescribed wrappers |
| **PC-03** File identity             | Requires Product/System concurrence | Choose path-equivalence rule before final `-s` and `-i` acceptance tests                     |
| **PC-04** Hash evidence             | Requires additional evidence        | Resolve unavailable hashes and observation timing with professor clarification               |
| **PC-05** Modification metrics      | Requires Product/System concurrence | Clarify uniqueness and attribution before fixing counting algorithms                         |
| **PC-06** Analyzer user reporting   | Feasible with stated limitations    | Product Architect resolves denied-only user membership                                       |
| **PC-07** Shared record meaning     | Requires Product/System concurrence | Agree on required semantics; System Architect owns encoding and persistence                  |

### **Technical concurrence recommendations**

For PC-01, distinguish attempted operations from their actual outcomes. A file-access failure should not be treated as permission-denied merely because it returned an error.

For PC-02, the most reliable technical scope is the set of intercepted calls in processes where the library actually loads. This does not settle whether that scope meets the professor's broader language.

For PC-03, pathname identity is the simplest proposal but cannot resolve every physical-file alias correctly.

For PC-04, do not claim that readable contents after `fwrite()` necessarily incorporate the write. Inaccessible contents remain a separate unresolved limitation.

For PC-05, prefer operation-based attribution if the approved definition permits it. A direct intercepted successful write is stronger causal evidence of that process's write activity than an unrelated pair of hash snapshots.

For PC-06, the parser can easily support either inclusion policy for denied-only users. This is principally a product semantics issue rather than an infrastructure obstacle.

For PC-07, the System Architect may select serialization, escaping and locking mechanisms. The interpretation of fields remains subject to the shared contract.

None of the seven contracts has been silently accepted or rewritten.

## **10. Implementation handoff**

The Developer should receive a bounded implementation plan after the Supervisor completes the applicable design gates.

1. **Milestone 1 — Build and interception foundation**

   Establish the shared library build, resolve original libc functions, preserve results and `errno`, and confirm all three hooks operate under `LD_PRELOAD`.

   *Acceptance:* Clean build, observed interception, no recursion and no alteration to the demonstrated original operation outcomes.
2. **Milestone 2 — Stream identity and basic events**

   Add stream association, absolute path representation, pre-call existence checks, successful opening classification and close cleanup.

   *Acceptance:* Creation, opening, write and close records contain correct UID, PID, pathname, timestamp and operation code.
3. **Milestone 3 — Shared logging**

   Implement the agreed record format, append persistence, synchronization, parser validation and error handling.

   *Acceptance:* Independent processes generate records that the analyzer can reliably parse without corrupting boundaries.
4. **Milestone 4 — Genuine content hashing**

   Implement OpenSSL EVP hashing for supported readable content states and establish tested handling of unavailable states.

   *Acceptance:* Recorded valid hashes match independently computed digests for the agreed observation point. Unavailable evidence is never presented as a valid digest.

   *Blocking dependency:* PC-04 and relevant professor clarification for full-compliance acceptance.
5. **Milestone 5 — Analyzer**

   Implement `-s` using distinct denied-file identities and `-i` using the accepted user membership, modification and uniqueness rules.

   *Acceptance:* Five-versus-six threshold tests, repeated denials, per-file user reporting and accepted modification scenarios all produce correct results.

   *Blocking dependency:* PC-03, PC-05 and any remaining PC-06 clarification.
6. **Milestone 6 — End-to-end verification and submission packaging**

   Extend `test_audit.c`, run the complete demonstration, verify malformed input and permission cases, and prepare the required deliverables.

   *Acceptance:* All professor-mandated functions and outputs are demonstrated, with separate documentation of limitations and exact runtime evidence.

### **Submission interface**

The professor requires exactly these six submitted files:

- `README`
- `Makefile`
- `audit_logger.c`
- `audit_logger.so`
- `audit_monitor.c`
- `test_audit.c`

The submission directory must be named `<AM1>_<AM2>_assign3` and compressed into the correspondingly named ZIP file.

The README must contain both full names, student IDs/logins and a short implementation description. The analyzer and demonstration executables should be buildable from the supplied source and Makefile.

This report does not authorize creating the submission package or modifying the repository.

## **11. Open issues and responsible authorities**

The material blockers are limited and identifiable.

| Priority | Issue                                                  | Responsible authority                            | Required next action                                    |
| -------- | ------------------------------------------------------ | ------------------------------------------------ | ------------------------------------------------------- |
| Critical | Meaning of unique modifications, Q11/Q22               | Professor → Product Architect                    | Resolve metric and aggregation                          |
| Critical | Hash unavailable for denied/unreadable content, Q08    | Professor → Product/System Architects            | Decide permitted representation or revised guarantee    |
| High     | Hash observation timing, Q07/Q21                       | Product/System Architects; potentially professor | Concur on what a digest represents                      |
| High     | Intended system-wide scope, Q01/Q19                    | Professor → Product/System Architects            | Reconcile prescribed mechanism and scope                |
| High     | Qualifying denied operations, Q04                      | Product Architect; potentially professor         | Establish `-s` event qualification                      |
| High     | File identity and aliases, Q05/Q13                     | Product/System Architects                        | Concur on matching and distinctness                     |
| Medium   | Shared-log access versus integrity, Q02/Q20            | Product/System Architects                        | Accept a practical permission and failure policy        |
| Medium   | Denied-only users in `-i`, Q12                         | Product Architect                                | Establish user membership rule                          |
| Process  | Product Architect follow-up not independently approved | Supervisor → Reviewer                            | Arrange exact-evidence review if required by governance |

The highest-risk unresolved issue is not the interception code itself. It is whether the required event-level SHA-256 field can be guaranteed for all cases while preserving the original program's behavior and permissions.

That is a specification-versus-observability limitation, not merely an unimplemented helper function.

## **12. Completion and role-compliance assessment**

| Completion criterion                                | Assessment                          |
| --------------------------------------------------- | ----------------------------------- |
| Source and governance preflight                     | PASS                                |
| Professor requirements and starter source inspected | PASS                                |
| Interception and event lifecycle investigated       | COMPLETE                            |
| Hash feasibility characterized                      | COMPLETE, with explicit limitations |
| Technical component and record proposals            | PREPARED                            |
| Analyzer and verification architecture              | PREPARED                            |
| Three bounded technical ADR candidates              | PREPARED                            |
| All seven PC contracts assessed                     | COMPLETE                            |
| Cross-role decisions independently accepted         | NOT YET                             |
| Professor clarifications obtained                   | NOT YET                             |
| Working implementation tested                       | NOT PERFORMED                       |
| Repository changes or implementation by this role   | NONE                                |

The local original five-page professor PDF was extracted and visually rendered. The external PDF screenshot service could not open the GitHub-hosted PDF, so no independent remote screenshot verification is claimed. The exact locally supplied document identity was verified against its manifest, and no reconstructed or substituted specification was used.

### **Final determinations**

**Recommended technical architecture:** A minimal C/Linux `LD_PRELOAD` interceptor, process-local stream tracking, genuine EVP content hashing, shared append-only text log, and a separate two-mode analyzer.

**Technical ADRs:** S-ADR-01 for interception lifecycle, S-ADR-02 for shared records and persistence, and S-ADR-03 for hash observation. All remain proposed.

**Material Product Architect concurrence:** Event lifecycle, monitoring scope, file identity, hash semantics, modification attribution, unique-modification metrics and shared-record guarantees.

**Remaining implementation blockers:** The unresolved semantics above, especially the hash-field limitation and unique-modification definition. These do not prevent bounded technical development once its applicable architecture is accepted, but they prevent an unconditional full-compliance claim.

**Development readiness:** Conditionally ready. The implementation approach is defined well enough to support bounded development after architectural concurrence. The complete solution is **not yet ready to be declared professor-compliant**.

**Independent architecture review readiness:** Ready for an independent adversarial review of this proposed technical architecture and its explicitly unresolved dependencies.

**Recommended next authorized step:** The Supervisor should coordinate Product/System concurrence on the material interfaces, obtain prioritized professor clarifications, and route the architecture through independent review before authorizing implementation against an accepted baseline.

**Work-unit boundary respected:** No implementation, repository mutation, ADR publication, independent approval or additional work unit has been performed.