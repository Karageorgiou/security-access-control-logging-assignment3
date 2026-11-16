# Assignment 3 — Product Architecture Requirements Investigation

Authority and repository baseline verified

## 1. Governance and role-compliance gate

Status: PASSED — read-only investigation authorized.

I independently checked the canonical GitDrive repository rather than relying on the supplied assignment prompt.

| Verification            | Result                                                     |
| ----------------------- | ---------------------------------------------------------- |
| Base role               | `product-architect`                                        |
| Operative governance    | GitDrive Governance v2                                     |
| Activation marker       | Version `2`, PR `#64`                                      |
| Governance `main`       | `63175d7c52bd61b3888bbb6e0576102a87157d80`                 |
| Assignment repository   | `Karageorgiou/security-access-control-logging-assignment3` |
| Assignment `main`       | `c31853dc398edc882c2448e2361ba66dce7087f5`                 |
| Expected baseline match | PASS                                                       |

The governance marker confirms that v2 is active, notwithstanding historical text in the architecture design document describing its pre-activation status.

### Authority established

Under the active role catalog, I may investigate domain requirements, identify semantic ambiguities, propose behavioral contracts and prepare product-architecture findings.

I may not select technical implementation mechanisms, make binding System Architect decisions, modify code, coordinate other work units, or independently approve my own conclusions.

Work-unit objective: Examine Assignment 3's specification and starter code exhaustively, identify the required observable behavior, and produce a traceable report suitable for independent review.

Evidence standard: The professor's original PDF is primary. The starter code is secondary. Explicit requirements, interpretations, and unresolved choices must remain distinguishable.

Completion boundary: Deliver the investigation report and stop. No implementation, repository mutation, technical ADR, or acceptance decision is authorized.

Governance sources: [Role catalog](https://github.com/Karageorgiou/GitDrive/blob/63175d7c52bd61b3888bbb6e0576102a87157d80/docs/GITDRIVE_ROLES.md?utm_source=chatgpt.com), [architecture authority design](https://github.com/Karageorgiou/GitDrive/blob/63175d7c52bd61b3888bbb6e0576102a87157d80/docs/GITDRIVE_GOVERNANCE_V2_ROLE_ARCHITECTURE_DESIGN.md?utm_source=chatgpt.com), [engineering process](https://github.com/Karageorgiou/GitDrive/blob/63175d7c52bd61b3888bbb6e0576102a87157d80/docs/GITDRIVE_ENGINEERING_PROCESS.md?utm_source=chatgpt.com).

## 2. Executive summary

PRODUCT ARCHITECT FINDINGS — PRE-REVIEW

ESTABLISHED: The professor requires a C-based audit system consisting of a preloaded logging library, a log analyzer, and a demonstration program.

The core functionality is:

1. Intercept `fopen()`, `fwrite()`, and `fclose()`.
2. Record file operations, identities, timestamps, outcomes, and SHA-256 content hashes in an append-only-by-mode shared log.
3. Identify users associated with denied operations on more than five distinct files.
4. Report the users and modification activity associated with a specified file.
5. Demonstrate the system and deliver the specified source, build files, library, and documentation.

INTERPRETED: This is primarily an audit and analysis exercise, not an implementation of permission enforcement. The specification requires reporting access denials, but does not authorize replacing the operating system's access-control decisions.

UNRESOLVED: The specification does not completely define the semantics necessary for consistent, independently testable implementation. Particularly consequential issues include:

- The meaning and limits of system-wide monitoring.
- Failed operations versus permission-denied operations.
- File identity and path equivalence.
- Counting writes versus actual content modifications.
- The meaning of unique modifications.
- The meaning and timing of file hashes.
- Ordering and formatting of audit records and analyzer output.

These are not all equally serious. Several admit reasonable domain interpretations, while others require technical feasibility investigation or clarification from the professor.

ESTABLISHED: The starter code is incomplete and not an implementation that can be accepted as conforming merely by compiling it. In fact, the supplied logger source appears syntactically incomplete.

Assessment: The problem is sufficiently specified to identify the principal features and interfaces, but not sufficiently precise to establish every acceptance criterion without additional decisions.

No semantic alternatives have been silently selected as binding requirements.

## 3. Verified evidence and source hierarchy

| Source                           | Verification                                                                              | Authority |
| -------------------------------- | ----------------------------------------------------------------------------------------- | --------- |
| `raw/Assignment 3 2026.pdf`      | Exact uploaded PDF matches repository Git blob `438410058b9d018979ef14c315fcd92c58ec60c5` | Primary   |
| `raw/src_corpus/audit_logger.c`  | Verified at pinned commit                                                                 | Secondary |
| `raw/src_corpus/audit_monitor.c` | Verified at pinned commit                                                                 | Secondary |
| `raw/src_corpus/test_audit.c`    | Verified at pinned commit                                                                 | Secondary |
| `raw/src_corpus/Makefile`        | Verified at pinned commit                                                                 | Secondary |

The repository contains identical copies of all four starter files at the root. Their Git blob identities match those under `raw/src_corpus/`.

This proves content identity at the verified revision, not a broader claim about every historical revision or the origin of files outside the repository.

The primary PDF consists of five pages, dated November 8, 2026, with submission due November 18, 2026, at 23:55 GMT+2. The document also specifies pair work and individual oral examination.&#x20;

Assignment 3 2026.pdf

Assignment 3 2026.pdf



Source hierarchy for this investigation:

- An explicit PDF requirement prevails over conflicting example code.
- PDF examples and hints are not binding requirements unless the document expressly makes them mandatory.
- Starter code is implementation evidence, not proof of intended behavior.
- Proposed behavioral interpretations remain provisional until accepted through the appropriate authority process.

## 4. Traceable requirements inventory

The following IDs are local to this investigation. They are not IDs supplied by the professor.

Classification legend: M mandatory, C conditional, I illustrative, P permitted, A materially ambiguous.

### 4.1 Audit logging library

Source: PDF pages 1–2, Overview, Step 1: Audit Logging Library, Events to Log, and Implementation Constraints.&#x20;

Assignment 3 2026.pdf



| ID  | Requirement and source                                                                             | Class | Observable acceptance / unresolved dependency                                                                                |
| --- | -------------------------------------------------------------------------------------------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------- |
| L01 | Provide `audit_logger.so` (p.1, Step 1).                                                           | M     | Named shared library exists and can be loaded.                                                                               |
| L02 | Use `LD_PRELOAD` to override `fopen()`, `fwrite()`, `fclose()` (p.1).                              | M     | Demonstrate interception of all three functions. Coverage is limited by the stated mechanism.                                |
| L03 | Delegate to the original C library functions (p.1).                                                | M     | Original operations execute with their intended return behavior. Error-preservation details require technical investigation. |
| L04 | Append records to `access_audit.log` (p.1).                                                        | M     | Events are written to the specified log.                                                                                     |
| L05 | Store the log in a directory accessible to all users (p.1).                                        | M     | Shared location is accessible in the test environment. Exact location is not mandated.                                       |
| L06 | Record UID using `getuid()` (p.1, field table).                                                    | M     | Logged UID matches the caller's real UID.                                                                                    |
| L07 | Record PID using `getpid()` (p.1).                                                                 | M     | Logged PID matches the originating process.                                                                                  |
| L08 | Record the absolute filename (p.1).                                                                | M     | File records contain absolute paths. Canonical identity remains unresolved.                                                  |
| L09 | Record the date in UTC (p.1).                                                                      | M     | Date is consistent with UTC event time.                                                                                      |
| L10 | Record the exact time in UTC (p.1).                                                                | M     | Time is consistent with UTC event time. Required precision is unspecified.                                                   |
| L11 | Encode operation as 0 created, 1 opened, 2 written, 3 closed (p.1).                                | M     | Event classifications use precisely these values.                                                                            |
| L12 | Record denied flag as 1 for operations denied due to missing access privileges, otherwise 0 (p.2). | M     | Permission denials are distinguishable from non-denials. Other failure types are not completely specified.                   |
| L13 | Record a SHA-256 content hash using OpenSSL EVP (p.2).                                             | M     | For readable, available content, digest equals independently computed SHA-256. Failure and timing semantics unresolved.      |
| L14 | Log creation of a previously nonexistent file (p.2, Events to Log).                                | M     | Successful qualifying creation produces operation 0.                                                                         |
| L15 | Log opening of an existing file (p.2).                                                             | M     | Successful opening produces operation 1.                                                                                     |
| L16 | Log file modification through `fwrite()` (p.2).                                                    | M/A   | Write operation produces operation 2; whether unsuccessful or zero-length writes constitute modifications is unresolved.     |
| L17 | Log file closing through `fclose()` (p.2).                                                         | M     | Closing a tracked file produces operation 3.                                                                                 |
| L18 | Open the audit log in append mode to prevent overwriting (p.2).                                    | M     | Existing records are preserved when later records are added.                                                                 |
| L19 | Record denied operations and continue execution gracefully (p.2).                                  | M     | Denial is logged without an audit-induced crash or bypass of access controls.                                                |
| L20 | Check prior file existence using `stat()` (p.2, Hint).                                             | I     | Illustrative method for L14/L15, not a separate required implementation.                                                     |
| L21 | Monitor file operations across the system (p.1, Overview).                                         | A     | Intended monitoring scope must be reconciled with L02.                                                                       |
| L22 | Preserve the three overridden function signatures (p.5, Implementation Notes).                     | M     | Signature-level compatibility is preserved.                                                                                  |

The dependency cluster is L08, L11–L17, and L19: these requirements jointly determine how event classification, failed operations, file identity, and hashes are interpreted. They cannot all be acceptance-tested precisely without additional contracts.

### 4.2 Audit analyzer

Source: PDF pages 2–3, Step 2: Audit Log Analyzer, with invalid-argument requirements on page 4.&#x20;

Assignment 3 2026.pdf

Assignment 3 2026.pdf



| ID  | Requirement and source                                                                        | Class | Observable acceptance / unresolved dependency                                                            |
| --- | --------------------------------------------------------------------------------------------- | ----- | -------------------------------------------------------------------------------------------------------- |
| A01 | Provide command-line analyzer `audit_monitor.c` (p.2).                                        | M     | Compilable executable supports required features.                                                        |
| A02 | Support `./audit_monitor -s` (p.2).                                                           | M     | Option initiates suspicious-user analysis.                                                               |
| A03 | Print UIDs with denied accesses to more than five distinct files (p.2).                       | M     | Five distinct denied files do not qualify; six do. Depends on A04.                                       |
| A04 | Count distinct files for denied attempts (p.2).                                               | M/A   | Repeated attempts against the same file are not automatically distinct. Identity equivalence unresolved. |
| A05 | Support `./audit_monitor -i <filename>` (p.3).                                                | M     | Option initiates analysis for the requested file.                                                        |
| A06 | Print all users who accessed the specified file (p.3).                                        | M/A   | User set is complete under the selected definition of access.                                            |
| A07 | Count modifications for each user, using `fwrite()` or differing hashes (p.3).                | M/A   | Per-user counts are correct under an accepted counting rule.                                             |
| A08 | Display the number of unique modifications (p.3).                                             | M/A   | Displayed count agrees with an accepted uniqueness rule, not yet defined.                                |
| A09 | Invalid options or incorrect arguments must produce appropriate help or error (p.4, Notes 3). | M     | Missing and malformed arguments produce an informative response.                                         |
| A10 | Support `-h` as shown in starter usage (starter source).                                      | I     | Not explicitly required by the PDF. It is only an example-supported behavior.                            |

The professor specifies the analyzer's two major functions, but not exact printed labels, row ordering, table structure, or numeric formatting.

### 4.3 Testing requirements

Source: PDF page 3, Step 3: Testing the Audit System.&#x20;

Assignment 3 2026.pdf



| ID  | Requirement                                                        | Class | Observable acceptance / unresolved dependency                                                                                     |
| --- | ------------------------------------------------------------------ | ----- | --------------------------------------------------------------------------------------------------------------------------------- |
| T01 | Create `test_audit.c`.                                             | M     | Source file exists and provides demonstration behavior.                                                                           |
| T02 | Create several files.                                              | M     | Demonstration actually creates multiple files.                                                                                    |
| T03 | Open and modify files under various conditions.                    | M     | Demonstrates different operations or conditions. Exact scenario inventory is unspecified.                                         |
| T04 | Attempt to open files without permissions.                         | M     | Demonstrates permission-denied attempts.                                                                                          |
| T05 | Run the test with `LD_PRELOAD=./audit_logger.so ./test_audit`.     | M     | Instrumented execution is demonstrated.                                                                                           |
| T06 | Produce a populated `access_audit.log`.                            | M     | Expected audit events appear after execution.                                                                                     |
| T07 | Demonstrate `audit_monitor -s` and `audit_monitor -i example.txt`. | C/I   | The two commands illustrate the expected workflow. `example.txt` is an example filename, not a mandatory generated test artifact. |

### 4.4 Build, documentation, and submission

Source: PDF pages 4–5, Tool Specifications, Notes, Submission Requirements, and Implementation Notes.&#x20;

Assignment 3 2026.pdf

Assignment 3 2026.pdf



| ID  | Requirement                                                                  | Class | Acceptance / clarification                                          |
| --- | ---------------------------------------------------------------------------- | ----- | ------------------------------------------------------------------- |
| B01 | Provide a Makefile.                                                          | M     | File exists.                                                        |
| B02 | Makefile compiles the shared library and programs.                           | M     | Required build products can be generated.                           |
| B03 | README contains both full names.                                             | M     | Both students identified.                                           |
| B04 | README contains both student IDs/logins.                                     | M     | Both identifiers present.                                           |
| B05 | README briefly describes the implementation approach.                        | M     | Accurate technical summary exists.                                  |
| B06 | Submit `README`.                                                             | M     | Required filename present.                                          |
| B07 | Submit `Makefile`.                                                           | M     | Required filename present.                                          |
| B08 | Submit `audit_logger.c`.                                                     | M     | Required source present.                                            |
| B09 | Submit `audit_logger.so`.                                                    | M     | Required binary library present.                                    |
| B10 | Submit `audit_monitor.c`.                                                    | M     | Required source present.                                            |
| B11 | Submit `test_audit.c`.                                                       | M     | Required source present.                                            |
| B12 | Place the six files together in `<AM1>_<AM2>_assign3/`.                      | M     | Folder matches both student IDs.                                    |
| B13 | Submit one ZIP named `<AM1>_<AM2>_assign3.zip`.                              | M     | Archive contains the prescribed folder.                             |
| B14 | Complete the assignment in pairs.                                            | M     | Pair membership established.                                        |
| B15 | Each student is orally examined.                                             | M     | Both must be prepared to explain their work.                        |
| B16 | Submit by November 18, 2026, 23:55 GMT+2.                                    | M     | Timely course submission.                                           |
| B17 | The starter corpus may be modified or replaced, with helper functions added. | P     | Freedom granted, subject to L22.                                    |
| B18 | Use the example Makefile, or create another.                                 | P     | No mandatory build recipe is imposed.                               |
| B19 | Missing or incomplete README incurs a one-point penalty.                     | M     | Explicit assessment consequence, not an additional runtime feature. |

Submission boundary: The PDF explicitly lists six deliverables, not eight. It requires `audit_logger.so` but does not list the compiled `audit_monitor` or `test_audit` executables among the six submission files.

Potentially important distinction: The README's contents are mandatory, and the PDF gives the submitted filename as `README`. The repository's existing `README.md` is an empty starter placeholder, not proof of README compliance.

## 5. Behavioral and semantic interpretation

This section separates what the professor states from reasonable interpretations and currently unspecified behavior.

### 5.1 Logging behavior

ESTABLISHED

The required event categories are:

| Code | Meaning | Explicit trigger                           |
| ---- | ------- | ------------------------------------------ |
| `0`  | Created | File creation through qualifying `fopen()` |
| `1`  | Opened  | Opening an existing file                   |
| `2`  | Written | File modification through `fwrite()`       |
| `3`  | Closed  | Closing through `fclose()`                 |

A successful file-creation event should be classified differently from an opening of a previously existing file. The creation examples include `w`, `w+`, and `a`, conditional on prior nonexistence.

For every log entry, the professor requires UID, PID, absolute path, UTC date/time, operation code, denied flag, and SHA-256 file-content hash.

INTERPRETED

The natural behavioral model is a sequence of observable operation events. For example, creating, writing, and closing one file can produce operations `0`, `2`, and `3`.

Subsequently opening that same existing file can produce operation `1`.

This model is compatible with the specification, but the PDF does not fully specify how unsuccessful operations, buffering, or other exceptional cases affect the event sequence.

UNRESOLVED

The specification does not establish:

- Whether every attempted `fwrite()` must generate an event, including zero-length or unsuccessful writes.
- Whether failed `fclose()` operations must be logged as close events.
- Whether opening an already existing file in a truncating mode is solely an opening event or also requires a modification event.
- Whether every intercepted stream, including non-file streams, belongs to the same logging contract.
- Whether a file hash represents content before the operation, immediately afterward, after flushing, or at a separate observation point.

Product consequence: An event cannot necessarily be equated with a confirmed change to persistent file content. Treating those concepts as identical would silently settle an ambiguity in the specification.

### 5.2 Identity, timestamps, and content hashes

ESTABLISHED: The UID must use `getuid()` and the PID must use `getpid()`. These identify the real user ID and process ID for the logging process, respectively.

The PDF specifies absolute filenames rather than arbitrary relative filenames. Both date and time must use UTC.

The SHA-256 field describes file contents rather than merely the bytes supplied to one `fwrite()` call.

INTERPRETED: A meaningful content-hash contract should identify which file state is represented by the digest. Otherwise, the analyzer cannot reliably interpret hash differences as modifications.

UNRESOLVED: There is no defined representation for a hash that cannot be obtained, such as after a denied opening. The document does not specify timestamp precision, path canonicalization, or how to distinguish a missing hash from the valid SHA-256 hash of empty content.

These semantic contracts must be established before tests can compare every audit field unambiguously.

### 5.3 Suspicious-user detection

ESTABLISHED: The threshold is strictly greater than five distinct denied files, grouped by UID.

The core predicate can be expressed as:

\\[ D(u)=\left|\left\\{f\mid\text{a denied access by UID }u\text{ concerns file }f\right\\}\right| \\]

A UID qualifies if:

\\[ D(u)>5 \\]

This is a representation of the professor's stated rule, not a new algorithmic requirement.

The expected boundary behavior follows directly:

| Denied events               | Distinct denied files | Qualifies? |
| --------------------------- | --------------------- | ---------- |
| 5 attempts against 5 files  | 5                     | No         |
| 6 attempts against 6 files  | 6                     | Yes        |
| 20 attempts against 1 file  | 1                     | No         |
| 10 attempts against 5 files | 5                     | No         |
| 8 attempts against 6 files  | 6                     | Yes        |

The unresolved variable is the definition of \\(f\\): pathname equivalence, physical-file identity, and aliases are not specified. Whether every denied operation code should contribute also requires clarification.

### 5.4 Per-file activity analysis

ESTABLISHED: For the selected file, the analyzer must display users who accessed it, modification counts per user, and the number of unique modifications.

INTERPRETED: The per-user count and the unique-modification count are distinct requested outputs. Their definitions must not be collapsed merely because a simple test happens to produce identical values.

Consider this illustrative sequence for one file:

| Event         | Resulting content |
| ------------- | ----------------- |
| Initial state | `A`               |
| Write 1       | `B`               |
| Write 2       | `B`               |
| Write 3       | `C`               |
| Write 4       | `B`               |

Depending on the counting contract, this could represent:

- Four successful write operations.
- Three content-changing transitions.
- Two distinct resulting content states, `B` and `C`.
- Three distinct observed hashes if the initial state `A` is included.

All are objectively definable measures, but they answer different questions.

The PDF does not establish which measure represents unique modifications. Nor does it establish whether a change from `B` back to `B` should count after an intervening different state.

Consequently, A07 and A08 have provisional acceptance semantics.

### 5.5 Analyzer command-line behavior

ESTABLISHED: `-s` and `-i <filename>` are the required user-facing operations. Missing or incorrect arguments must produce appropriate help or error messages.

UNRESOLVED: The professor does not define whether both options can be combined, what their ordering should be, whether extra positional arguments are invalid, or the precise output format.

These are secondary issues. They must not be allowed to obscure the much more consequential counting and identity semantics.

### 5.6 Testing and submission behavior

The test program must demonstrate file creation, opening, modification, and permission denial, with the logger preloaded. The analyzer must then operate on the generated log.

A meaningful demonstration of `-s` additionally depends on enough distinct denied files to cross the strict threshold. Although the PDF does not explicitly require the test program to generate six denied-file identities, that is a directly derived verification condition for demonstrating a positive suspicious-user detection.

The test must not assume that making a file read-only necessarily produces denial under every execution identity. A test that runs with privileges sufficient to bypass ordinary file restrictions would not establish the intended permission-denial behavior.

Actual execution and environment control belong to the implementation and verification work units, not to this architectural investigation.

## 6. Ambiguity and contradiction register

The following are material findings requiring explicit resolution or bounded uncertainty. An ambiguity is not automatically a defect in the assignment.

| ID  | Evidence and uncertainty                                                                                     | Plausible interpretations and behavioral consequences                                                                                                                                                                                       | Owner and required next action                                                                                    |
| --- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Q01 | p.1 Overview: system-wide monitoring, but interception is limited to three libc functions with `LD_PRELOAD`. | Literal system-wide coverage would include operations outside a preloaded process. Interposition-only coverage observes qualifying calls made through the preloaded environment. These are not equivalent guarantees.                       | Joint Product/System; professor clarification for intended scope. System Architect assesses feasibility.          |
| Q02 | p.1: shared `access_audit.log` accessible to all users.                                                      | Shared visibility, shared readability, shared append permission, and tamper resistance are different properties. The specification does not select all of them.                                                                             | Joint Product/System. Establish required access semantics, then investigate storage architecture.                 |
| Q03 | p.2: denied flag means missing access privileges.                                                            | A failed `fopen()` may be permission-denied, nonexistent, or fail for another reason. Treating all failures as denials produces false positives.                                                                                            | Product Architect, with professor clarification if necessary. Establish the denial taxonomy.                      |
| Q04 | p.2 and p.3: denied operations feed suspicious-user analysis.                                                | Count only denied opens or denied operations of any kind. Different rules can produce different suspicious-user sets.                                                                                                                       | Product Architect / professor. Define qualifying attempts.                                                        |
| Q05 | p.1: absolute filename; p.2: distinct files.                                                                 | Compare exact absolute strings, normalized paths, or physical-file identities. Symlinks, hard links, and renamed files may produce different counts.                                                                                        | Product Architect, with System Architect concurrence on feasibility and representation.                           |
| Q06 | p.2: creation versus opening based on prior existence.                                                       | Classify by successful creation, observed nonexistence, or requested mode. Failed creation and races produce different classifications.                                                                                                     | Joint Product/System. Clarify observable classification semantics before choosing mechanism.                      |
| Q07 | p.1–2: record SHA-256 of file contents.                                                                      | Hash before operation, after operation, or after data becomes visible in the file. This changes the meaning of recorded digests.                                                                                                            | Product Architect establishes meaning; System Architect assesses observation feasibility.                         |
| Q08 | p.2: hash required on every entry, including denied operations.                                              | Hash may be available from independent access, unavailable, or unknowable. The PDF supplies no missing-value representation.                                                                                                                | Joint Product/System; professor if strict all-entry hash requirement conflicts with denial semantics.             |
| Q09 | p.2: `fwrite()` is a modification event.                                                                     | Count calls, successful returns, accepted bytes, or actual content changes. These measures can differ.                                                                                                                                      | Product Architect / professor. Establish modification-event meaning.                                              |
| Q10 | p.3: count modifications based on `fwrite()` or differing hashes.                                            | Either method may be treated as sufficient, or they may be expected to agree. They do not necessarily agree because content can be rewritten unchanged.                                                                                     | Professor clarification recommended; Product Architect records candidate interpretations.                         |
| Q11 | p.3: unique modifications.                                                                                   | Unique write events, unique resulting states, unique hash values, or unique state transitions. All can produce different results.                                                                                                           | Professor clarification strongly recommended. Product Architect may subsequently formalize the accepted contract. |
| Q12 | p.3: all users who accessed a file.                                                                          | Include denied attempts, successful opens only, or any successful file operation. Each produces a different user set.                                                                                                                       | Product Architect / professor. Define access membership.                                                          |
| Q13 | p.3: `-i <filename>` versus absolute logged paths.                                                           | Relative query paths may be resolved against the analyzer's working directory, compared literally, or mapped to file identity.                                                                                                              | Joint Product/System. Define match semantics and feasible normalization.                                          |
| Q14 | p.1–2: structured shared log, append mode.                                                                   | Field order, record boundaries, encoding, concurrency behavior, and malformed-record policy are not specified. They affect analyzer interoperability.                                                                                       | Joint Product/System. Product owns field meanings; System owns serialization and consistency design.              |
| Q15 | p.1: UTC date and exact time.                                                                                | Seconds, microseconds, or other precision; distinct date/time fields or one underlying timestamp. Ordering guarantees are not defined.                                                                                                      | Product Architect defines required observation; System Architect determines representation.                       |
| Q16 | p.2: continue gracefully after denial.                                                                       | This may mean preserving the original denied result and allowing program execution to continue, or conceivably suppressing the failure. Suppression would change access-control behavior and is unsupported by the stated auditing purpose. | Product Architect. Propose preserving original operation outcome; seek clarification if challenged.               |
| Q17 | p.3: print users and counts; p.4: help/error.                                                                | Unordered UID list versus sorted output, numeric-only versus explanatory text, combined versus separate reports. No exact output schema.                                                                                                    | Product Architect, with professor clarification only if exact grading output matters.                             |
| Q18 | p.3–4: test denied actions under various conditions.                                                         | Static permission bits alone may not reliably generate failure for privileged test users. The necessary test identity and environment are unspecified.                                                                                      | System Architect investigates test feasibility and environment requirements.                                      |
| Q19 | p.1: every open, write, close; p.2: explicit intercepted functions.                                          | File descriptor functions, alternate libc functions, and operations outside the preload scope might be included in the broad claim but excluded by the explicit interface.                                                                  | Joint Product/System; professor for coverage boundary.                                                            |
| Q20 | p.1–2: shared log persistence and graceful handling.                                                         | If the audit log cannot be written, fail the original operation, continue without an audit record, or produce some other observable failure. No general audit-failure policy is specified.                                                  | Joint Product/System, with risk acceptance through human authorization where needed.                              |
| Q21 | p.1–2: close events and content hashes.                                                                      | Closing a stream may make buffered data observable, while the earlier write event may not correspond to that same file state. This affects content-change comparisons.                                                                      | Joint Product/System. Investigate the observable event/state relationship.                                        |
| Q22 | p.3: aggregate unique modifications for a queried file.                                                      | Unique modifications across all UIDs versus a separate count per UID. The requested granularity is not fully specified.                                                                                                                     | Product Architect / professor. Establish aggregation scope.                                                       |

### Severity and priority

The highest-priority clarification candidates are Q01, Q03–Q05, Q07–Q11, and Q22. These can change which events exist or what the analyzer reports.

Q02, Q06, Q13–Q15, Q18, Q20, and Q21 have substantial system-design implications. They should be handed to the System Architect with the unresolved product semantics intact.

Q17 is lower priority because the professor has not prescribed a byte-exact output format.

### Contradiction assessment

There are two particularly significant tensions, although neither yet establishes an unavoidable contradiction:

System-wide coverage versus LD_PRELOAD. A broad reading of system-wide monitoring is not satisfied by intercepting three functions within a subset of preloaded processes. The System Architect must assess the technical boundary before the promised coverage can be accepted.

Mandatory file hash versus denied access. A permission denial may prevent observation of the file's contents. Demanding a valid content hash on every denied event could therefore be infeasible without additional privilege or information. The specification does not describe a fallback representation.

Both issues must remain open rather than being resolved through an undocumented technical assumption.

## 7. Starter corpus gap assessment

Assessment method: Static inspection of the four original files at the verified commit. No files were modified, and no compilation or runtime testing is claimed.

### 7.1 `audit_logger.c`

Source: [Original audit_logger.c](https://github.com/Karageorgiou/security-access-control-logging-assignment3/blob/c31853dc398edc882c2448e2361ba66dce7087f5/raw/src_corpus/audit_logger.c?utm_source=chatgpt.com)

| Lines       | Observed evidence                                                    | Assessment                                                   |
| ----------- | -------------------------------------------------------------------- | ------------------------------------------------------------ |
| 1–10        | Includes dynamic-linking, file-stat, and OpenSSL headers.            | Preparatory scaffolding only.                                |
| 12–32       | Defines `fopen()` and delegates through `dlsym(RTLD_NEXT, "fopen")`. | Original call represented. No auditing behavior implemented. |
| 35–55       | Defines `fwrite()` and delegates through `dlsym`.                    | Original call represented. No write audit implemented.       |
| 58–76       | Defines `fclose()` and delegates through `dlsym`.                    | Original call represented. No close audit implemented.       |
| End of file | `fclose()` has an opening brace but no corresponding closing brace.  | Directly observed syntax defect.                             |

The source contains no implemented audit-record construction, persistent log writing, UID/PID collection, timestamp collection, absolute-path handling, event classification, denied-access reporting, or SHA-256 computation.

The original-function delegation establishes a useful example of the intended interception pattern. It does not establish correct or complete logging behavior.

Finding SC-01 — ESTABLISHED: The starter logger is incomplete and contains an unmatched function brace. It is not an implementation candidate ready for acceptance.

### 7.2 `audit_monitor.c`

Source: [Original audit_monitor.c](https://github.com/Karageorgiou/security-access-control-logging-assignment3/blob/c31853dc398edc882c2448e2361ba66dce7087f5/raw/src_corpus/audit_monitor.c?utm_source=chatgpt.com)

| Lines   | Observed evidence                                                                             | Assessment                                                                                        |
| ------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| 7–26    | `struct log_entry` contains UID, PID, filename, date, time, operation, denied flag, and hash. | Represents the required information conceptually, but establishes no log format.                  |
| 29–44   | Provides `usage()` describing `-s`, `-i`, and `-h`.                                           | Example CLI documentation.                                                                        |
| 47–59   | `list_unauthorized_accesses()` contains placeholders.                                         | Suspicious-user analysis absent.                                                                  |
| 62–74   | `list_file_modifications()` contains placeholders.                                            | Per-file analysis absent.                                                                         |
| 84–91   | Opens `./access_audit.log`.                                                                   | Relative log path conflicts with the shared-location expectation when working directories differ. |
| 93–105  | Uses `getopt()` to dispatch options.                                                          | Partial argument handling.                                                                        |
| 108–113 | Additional placeholders.                                                                      | No complete parsing or validation.                                                                |
| 115–119 | Closes log and adjusts argument pointers.                                                     | No complete unexpected-argument rejection.                                                        |

Additional directly observed issues:

- The log is opened before option processing. Consequently, a missing log can prevent the program from displaying its help text.
- The option-handling loop does not establish that extra positional arguments are invalid.
- The example declares date and time as `time_t` fields but does not establish their textual representation in the log.
- Neither analyzer function implements its required calculations.

Finding SC-02 — ESTABLISHED: The starter analyzer describes the desired features but does not implement them.

Finding SC-03 — ESTABLISHED: Its relative log path is not a reliable shared producer/consumer contract. The professor's shared-log requirement takes precedence.

### 7.3 `test_audit.c`

Source: [Original test_audit.c](https://github.com/Karageorgiou/security-access-control-logging-assignment3/blob/c31853dc398edc882c2448e2361ba66dce7087f5/raw/src_corpus/test_audit.c?utm_source=chatgpt.com)

The test source contains one principal loop at lines 19–29:

1. It iterates over ten filenames.
2. It opens each file using `w+`.
3. It writes the filename as content.
4. It closes the file.

This represents the basic create/write/close sequence.

However, the starter test does not deliberately demonstrate reopening existing files under different modes, permission-denied attempts, multiple-user behavior, or the suspicious-user threshold. It also does not independently validate the audit log or its hashes.

Finding SC-04 — ESTABLISHED: The original test covers only part of Step 3 and cannot demonstrate the full assignment.

### 7.4 `Makefile`

Source: [Original Makefile](https://github.com/Karageorgiou/security-access-control-logging-assignment3/blob/c31853dc398edc882c2448e2361ba66dce7087f5/raw/src_corpus/Makefile?utm_source=chatgpt.com)

The supplied Makefile includes build commands for the library, analyzer, and test program.

Its logger recipe uses the relevant shared-library flags and links against OpenSSL crypto and dynamic-loading support.

Two specific inconsistencies are visible:

- The target `audit_logger` generates `audit_logger.so`, rather than a file named `audit_logger`.
- The `run` target depends on `audit_logger.so`, but the Makefile does not declare a corresponding explicit target. A clean `make run` therefore lacks the required dependency relationship.

The `all` target may attempt the library compilation through the `audit_logger` recipe, but the supplied logger's unmatched brace is an independent compilation blocker.

Finding SC-05 — ESTABLISHED: The example Makefile is incomplete as a reliable build workflow.

These are observations, not implementation instructions. Selecting remedies belongs to the appropriate developer or System Architect work unit.

### 7.5 Overall starter-corpus coverage

| Requirement area              | Representation in starter   | Compliance established? |
| ----------------------------- | --------------------------- | ----------------------- |
| Three overridden functions    | Present                     | No                      |
| Original-function delegation  | Present                     | Not runtime-verified    |
| Shared audit records          | Absent                      | No                      |
| Required field values         | Declared partly in analyzer | No                      |
| SHA-256 hashing               | Header included             | No                      |
| Denied-operation reporting    | Absent                      | No                      |
| Suspicious-user analysis      | Empty function              | No                      |
| Per-file analysis             | Empty function              | No                      |
| Basic file operations in test | Present                     | Partial                 |
| Permission-denial tests       | Absent                      | No                      |
| Build workflow                | Present but inconsistent    | No                      |
| README                        | Root placeholder empty      | No                      |

The professor explicitly permits replacing the starter code. Accordingly, these deficiencies do not create architectural obligations to preserve its internal design.

## 8. Proposed product-level behavioral contracts

All proposals in this section have status PROPOSED. None is an accepted professor requirement or a binding technical architecture decision.

### PA-01 — Preserve the result of the underlying file operation

Related requirements: L03, L12, L19.

Problem: Denied access must be recorded without changing the intended access-control decision.

Alternatives: Preserve the delegated operation's outcome, suppress failures, or introduce separate audit-induced operation failures.

Recommendation: Preserve the original operation's observable success/failure outcome as the baseline product contract. Auditing should not manufacture access privileges.

Rationale: This aligns with the stated auditing purpose and graceful continuation requirement.

Remaining uncertainty: Error handling when the audit subsystem itself fails.

Authority: Product Architect, with System Architect review of technical feasibility and any cross-cutting implementation consequences.

### PA-02 — Explicitly separate attempted, successful, and denied operations

Related requirements: L11–L19, A03–A04.

Problem: An operation attempt is not necessarily a successful access or modification.

Alternatives: Treat all interceptions as equivalent events, distinguish denied events only, or define a fuller event-outcome classification.

Recommendation: Establish an explicit semantic distinction between attempted operations and successful operations before finalizing the record contract.

Rationale: Without that distinction, the suspicious-user analyzer and modification analysis can contradict each other.

Remaining uncertainty: Whether the professor permits additional outcome fields and which failed operations must produce records.

Authority: Joint Product/System architecture, with external clarification if necessary.

### PA-03 — Establish one consistent file-identity contract

Related requirements: L08, A04–A08.

Problem: The logger and analyzer must refer to the same logical file entities.

Alternatives: Raw absolute-path strings, normalized paths, or underlying physical-file identity.

Recommendation: One explicitly defined file-identity concept should apply consistently to logging, suspicious-user counting, and `-i` analysis.

Rationale: Inconsistent identity rules can produce incompatible outputs from the same audit data.

Remaining uncertainty: The professor has not prescribed an equivalence rule.

Authority: Product Architect owns the semantic choice; System Architect owns its representation and feasibility.

### PA-04 — Keep write count and unique modification count conceptually separate

Related requirements: A07–A08.

Problem: Writing and changing persistent content are not necessarily equivalent.

Alternatives: Count every `fwrite()` event, successful writes, changed hashes, unique content states, or distinct transitions.

Recommendation: Define two separate metrics, one for per-user modification activity and one for the requested unique-modification aggregate. Their precise formulas should follow clarification rather than assumption.

Rationale: It preserves both requested outputs without incorrectly declaring them equivalent.

Remaining uncertainty: Both formulas and the aggregate's scope.

Authority: Product Architect and professor clarification.

### PA-05 — Define what a content hash proves

Related requirements: L13, A07–A08.

Problem: A SHA-256 value has meaning only when the content snapshot it represents is identified.

Alternatives: Pre-operation state, post-operation state, post-flush state, or another documented observation.

Recommendation: Associate each hash with an explicitly defined observation point. An unavailable hash must not be represented as though it were a successfully calculated digest.

Rationale: False or ambiguous hash evidence undermines modification analysis.

Remaining uncertainty: Feasibility and a permissible representation for unavailable values.

Authority: Joint Product/System architecture, potentially professor clarification.

### PA-06 — Treat log format as a shared producer/consumer contract

Related requirements: L04–L13, A01.

Problem: The logger produces data that the analyzer must interpret consistently.

Alternatives: A fixed textual schema, a structured record format, or another explicitly defined representation.

Recommendation: Establish a common field and event contract before the two components are implemented independently.

Rationale: The professor requires structured log records but leaves serialization unspecified.

Remaining uncertainty: The exact encoding, record boundaries, ordering, and concurrency guarantees.

Authority: Product Architect for meanings, System Architect for technical representation. Explicit concurrence is needed for materially indivisible decisions.

### PA-07 — Interpret the strict suspicious-user threshold literally

Related requirements: A03–A04.

Problem: Repeated denials must not inflate a count intended to represent distinct files.

Alternatives: Count events, count distinct file identities, or count attempted operations of another type.

Recommendation: Use the directly specified threshold of six or more distinct denied-file identities, subject to resolving file identity and qualifying denial semantics.

Rationale: The phrase “more than 5 distinct files” is explicit.

Remaining uncertainty: What constitutes the same file and which denied operations count.

Authority: Product Architect for remaining semantics.

### PA-08 — Do not impose byte-exact output formatting without evidence

Related requirements: A02, A05–A09.

Problem: Output layout and ordering are unspecified.

Alternatives: Arbitrary human-readable output, deterministic tabular output, or an exact prescribed format.

Recommendation: Require complete and intelligible results as the product baseline. Treat stable ordering as desirable unless exact formatting is subsequently required.

Rationale: This avoids converting a quality preference into a fabricated professor requirement.

Remaining uncertainty: Whether external assessment uses an undisclosed byte-exact output reference.

Authority: Product Architect; professor clarification if necessary.

## 9. Requirements acceptance matrix

This is a proposed verification plan, not a claim of successful testing.

The required evidence categories are separated below.

### 9.1 Assignment compliance

| Requirements       | Required verification                                                                        | Evidence needed                                            | Status                                  |
| ------------------ | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | --------------------------------------- |
| L01, L02, L22      | Inspect shared-library artifact and required intercepted signatures; demonstrate preloading. | Library identity and executable observation.               | Not tested                              |
| L03                | Compare operation outcomes with and without interception.                                    | Matching delegated-call behavior under defined scenarios.  | Not tested                              |
| L04, L05, L18      | Perform successive audited operations against a shared log.                                  | Correct log location and preserved earlier records.        | Not tested                              |
| L06, L07           | Compare log identities with actual calling process.                                          | UID/PID correspondence.                                    | Not tested                              |
| L08                | Exercise relative paths and inspect recorded filenames.                                      | Absolute filename records.                                 | Provisional identity equivalence        |
| L09, L10           | Observe events at known UTC times.                                                           | Matching date/time fields.                                 | Precision unresolved                    |
| L11, L14, L15      | Create a new file, then open an existing file.                                               | Operation codes 0 and 1.                                   | Classification edge cases unresolved    |
| L16                | Write to an opened file.                                                                     | Corresponding operation 2 record.                          | Failed/empty write semantics unresolved |
| L17                | Close an opened file.                                                                        | Corresponding operation 3 record.                          | Failure semantics unresolved            |
| L12, L19           | Attempt permission-denied access.                                                            | Denied flag 1 and graceful continuation.                   | Denial taxonomy unresolved              |
| L13                | Compare logged digest with independently calculated content digest.                          | Matching SHA-256 for the defined file state.               | Hash timing unresolved                  |
| L21                | Assess which file operations are expected to be monitored.                                   | Coverage statement and matching observations.              | Scope unresolved                        |
| A01, A02           | Compile analyzer and invoke `-s`.                                                            | Executable and relevant output.                            | Not tested                              |
| A03, A04           | Test denied attempts against five and six distinct files, including repeated denials.        | Correct threshold behavior.                                | File identity provisional               |
| A05, A06           | Invoke `-i` for a file accessed by multiple UIDs.                                            | Complete matching UID set.                                 | Access semantics unresolved             |
| A07                | Create a known per-user modification sequence.                                               | Counts matching accepted definition.                       | Definition unresolved                   |
| A08                | Create repeated-content and changed-content sequences.                                       | Unique count matching accepted definition.                 | Definition unresolved                   |
| A09                | Invoke analyzer with missing and invalid options and arguments.                              | Appropriate help/error response.                           | Not tested                              |
| T01, T02           | Inspect and execute demonstration source.                                                    | Multiple files created.                                    | Starter partially covers                |
| T03                | Execute representative open/modify scenarios.                                                | Demonstrated variety of operations.                        | Starter partially covers                |
| T04                | Execute genuine permission-denied attempts.                                                  | Failed accesses visible in audit records.                  | Starter does not cover                  |
| T05, T06           | Execute prescribed preloading command.                                                       | Populated log after test.                                  | Not tested                              |
| T07                | Invoke both analyzer functions after generating audit data.                                  | Relevant analyzer reports.                                 | Not tested                              |
| B01, B02           | Execute specified build workflow from a clean source state.                                  | Correct library and program artifacts.                     | Not tested                              |
| B03, B04, B05, B19 | Inspect README contents.                                                                     | Both names, IDs, implementation summary.                   | Current placeholder incomplete          |
| B06–B11            | Inspect final folder contents.                                                               | All six required files.                                    | Not yet submitted                       |
| B12, B13           | Inspect ZIP layout and naming.                                                               | Correct archive and internal folder.                       | Not yet submitted                       |
| B14, B15           | Verify group participation and examination readiness.                                        | Two identified members able to explain their contribution. | Human/course evidence required          |
| B16                | Verify final submission against course deadline.                                             | Accepted submission receipt/time.                          | Not yet submitted                       |

For each row, the acceptance evidence is the stated observation or artifact. For rows labeled provisional or unresolved, an additional accepted semantic contract is required before an unqualified PASS is justified.

### 9.2 Derived behavioral verification

These tests follow reasonably from established requirements but are not individually mandated test cases.

| Test ID | Verification scenario                                                 | Purpose                                                        |
| ------- | --------------------------------------------------------------------- | -------------------------------------------------------------- |
| D01     | Repeat denial on the same file.                                       | Confirm distinct-file counting does not become event counting. |
| D02     | Compare five versus six distinct denied files.                        | Establish threshold boundary.                                  |
| D03     | Use multiple PIDs for one UID.                                        | Confirm aggregation is by UID rather than PID.                 |
| D04     | Use different UIDs for the same file.                                 | Check separation of per-user activity.                         |
| D05     | Create and reopen a file.                                             | Differentiate creation from opening.                           |
| D06     | Write identical data repeatedly.                                      | Expose write-count versus content-change ambiguity.            |
| D07     | Change content and restore a prior state.                             | Expose unique-modification ambiguity.                          |
| D08     | Exercise a truly permission-denied operation.                         | Confirm denied-flag meaning.                                   |
| D09     | Check SHA-256 against an independent computation.                     | Confirm actual file-content hashing.                           |
| D10     | Execute the producer and analyzer from different working directories. | Verify consistency of shared-log location.                     |
| D11     | Execute a failed operation unrelated to permissions.                  | Check that unrelated failures do not become false denials.     |
| D12     | Compare original program behavior with and without preload.           | Verify delegation and outcome preservation.                    |

These tests are suitable candidates for the subsequent verification plan. They are not claims that execution occurred.

### 9.3 Optional engineering quality

These are desirable qualities, not explicitly mandatory assignment requirements:

- Stable deterministic report ordering.
- Robust malformed-log handling.
- Detection of invalid or truncated records.
- Concurrency integrity under simultaneous log writers.
- Resistance to unauthorized log tampering.
- Resource and memory limits for large audit logs.
- Portability beyond the stated Linux-oriented preloading environment.
- Additional automated regression tests and CI.

The System Architect may evaluate these concerns and their costs. Their presence here does not authorize implementing them or treating them as grading requirements.

## 10. Unresolved decisions and authority routing

### 10.1 Questions recommended for the professor

The course PDF directs clarification requests to the Discussion tab. The most consequential questions are:

1. Monitoring scope: Does “system-wide” mean all qualifying calls made by processes launched with `LD_PRELOAD`, or is broader system coverage expected?
2. Denied accesses: For `-s`, do only failed `fopen()` attempts count, or do other denied operations count as well?
3. File identity: Are different absolute pathnames referencing one underlying file considered one distinct file?
4. Modification counting: Should the per-user count represent successful `fwrite()` calls or actual changes in content?
5. Unique modifications: Is this the count of distinct resulting SHA-256 hashes, content-changing transitions, or something else?
6. Hashes on denied operations: What should be recorded when the file contents cannot be read?
7. Hash observation: At what point in the operation should file contents be hashed?
8. Aggregate scope: Is the total unique-modification count per file across all users, or separately calculated for each user?

The Product Architect can propose alternatives, but cannot claim to know the professor's intended answers where the written evidence is insufficient.

### 10.2 Decisions belonging to the Product Architect

Within Product Architect authority, subject to appropriate review:

- Formalize the denied-event and successful-access semantics.
- Define file identity at the product level.
- Define the membership of the per-file accessed-user set.
- Formalize modification and unique-modification metrics.
- Establish what hash evidence means.
- Define the required observable analyzer results.
- Establish which fields and outcomes are indispensable to the audit record's meaning.

These decisions must respect the PDF and any subsequent clarification.

### 10.3 Investigations belonging to the System Architect

The following are technical-system questions, not decisions for this report:

- Actual interception coverage and limitations of `LD_PRELOAD`.
- Component interfaces between logger and analyzer.
- Representation and persistence of shared audit records.
- Concurrency and shared-log consistency.
- Reliable observation of file paths, streams, outcomes, and content states.
- Timing and feasibility of SHA-256 calculation.
- Representation of unavailable hash evidence.
- Handling of auditing failure without unintentionally changing the original operation.
- Build and verification architecture.
- Feasibility of the required permission-denial test conditions.

### 10.4 Decisions requiring joint concurrence

The Product Architect and System Architect must explicitly agree where product meaning depends on system representation.

Material joint decisions include:

| Decision              | Product dimension                                   | System dimension                                |
| --------------------- | --------------------------------------------------- | ----------------------------------------------- |
| File identity         | What counts as the same file                        | How that identity can be observed               |
| Audit event           | What an event means                                 | How and when it is captured                     |
| Content hash          | Which file state is represented                     | When the state is reliably available            |
| Denied event          | What constitutes denial                             | How the outcome is observed                     |
| Shared log            | Required semantic fields and persistence guarantees | Storage, serialization, and consistency         |
| Modification evidence | Meaning of change and uniqueness                    | Available observations and verification methods |

Neither architect can unilaterally settle both dimensions when the decision is materially indivisible.

### 10.5 Decisions reserved for human authority

The human user or professor retains authority over assignment-level risk, preferences, and external constraints that are not delegated to the architect.

In particular:

- Accepting a known compliance risk.
- Proceeding under an unresolved professor ambiguity when competing interpretations can materially change the grade or expected behavior.
- Changing the assignment objective or scope.
- Authorizing deviations from the professor's explicit requirements.
- Approving work-unit transitions and accepting review findings through the applicable governance process.

A human preference cannot convert an unsupported technical assertion into verified fact.

## 11. System Architect handoff requirements

This investigation identifies the semantic inputs and unresolved questions the System Architect needs. It does not begin that work unit.

The Supervisor should route the following handoff package after the appropriate review and disposition.

| Handoff item                       | Required input               | Expected architectural investigation                                                                            |
| ---------------------------------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------- |
| H01 — Observation scope            | L02, L21, Q01, Q19           | Establish technical coverage and identify any gap against the intended requirement.                             |
| H02 — Event lifecycle              | L11–L19, Q03, Q06, Q09, Q21  | Determine which observable operation states are technically available.                                          |
| H03 — File identity                | L08, A04–A06, Q05, Q13       | Determine feasible identity representations without preempting product semantics.                               |
| H04 — Shared audit record          | L04–L13, Q02, Q14            | Investigate component interface, record representation, storage, and consistency.                               |
| H05 — Hash observation             | L13, Q07–Q08, Q10–Q11        | Evaluate available file-content observations and their limitations.                                             |
| H06 — Analyzer verification        | A01–A09                      | Design verification architecture around accepted counting and output contracts.                                 |
| H07 — Test environment             | T01–T07, Q18                 | Determine what is required to demonstrate real denials and multiple-user cases.                                 |
| H08 — Build contract               | B01–B02, B06–B11             | Evaluate the required source-to-artifact workflow.                                                              |
| H09 — Existing starter limitations | SC-01 through SC-05          | Assess technical consequences without treating example code as accepted architecture.                           |
| H10 — Unresolved dependencies      | Q01–Q22, PA-01 through PA-08 | Identify decisions requiring joint concurrence or professor clarification before technical design is finalized. |

The System Architect must not interpret these handoff items as authorization to implement, remediate, or finalize product semantics outside its own authority.

## 12. Final role-compliance and completion gate

| Required check                                       | Result                                    |
| ---------------------------------------------------- | ----------------------------------------- |
| Operative governance independently established       | &#x20;PASS                                |
| Product Architect role and authority established     | &#x20;PASS                                |
| Assignment repository and expected baseline verified | &#x20;PASS                                |
| Original professor PDF verified                      | &#x20;PASS                                |
| Starter corpus inspected                             | &#x20;PASS                                |
| Material requirements inventoried                    | &#x20;PASS                                |
| Ambiguities preserved rather than silently resolved  | &#x20;PASS                                |
| Product decisions clearly marked as proposals        | &#x20;PASS                                |
| Technical architecture decisions avoided             | &#x20;PASS                                |
| Implementation and repository mutation avoided       | &#x20;PASS                                |
| Independent review performed                         | Not claimed — separate authority required |
| Implementation compliance verified                   | Not claimed — no execution performed      |

### Final conclusions

ESTABLISHED: The assignment specifies three software components, the interception interface, the audit fields, the two analyzer commands, the test program's principal obligations, and the final submission package.

INTERPRETED: A coherent implementation requires a shared event and file-identity model, but the PDF does not completely establish that model.

PROPOSED: PA-01 through PA-08 provide candidate behavioral contracts and recommendations. They remain unaccepted and should be examined by an independent reviewer.

UNRESOLVED: Q01 through Q22 identify outstanding uncertainties. The most consequential concern monitoring scope, access denials, file identity, modification counting, uniqueness, and hash semantics.

System Architect dependency: Technical design should be informed by these findings, and material cross-domain questions require joint concurrence rather than unilateral resolution.

Limitations: This was a static, source-grounded investigation. I did not compile the starter code, run the programs, verify runtime interception, inspect a target machine, or claim that any implementation has passed the professor's acceptance requirements.

### Completion determination

Investigation completed

Independent review pending

The report is ready to be submitted as a proposed Product Architect investigation for independent adversarial review, with its identified ambiguities and limitations preserved.

It is not an approved product architecture, an implementation authorization, or evidence of submission readiness.

Work-unit boundary reached. No System Architect work, implementation, remediation, or independent self-review has been initiated.