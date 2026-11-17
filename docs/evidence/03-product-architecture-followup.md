# **Assignment 3 — Product Architecture Review Dispositions and Semantic Decision Candidates**

Mandatory preflight passed

Product Architect · Read-only work unit · November 16, 2026

## **1. Verified authority and source identities**

### **1.1 Exact evidence verification**

The supplied `assignment3_exact_review_evidence(1).zip` passed its ZIP integrity check. I extracted both Markdown files without modifying their contents and independently calculated SHA-256 from the extracted bytes.

| Evidence                                 | Expected SHA-256 match | Result     |
| ---------------------------------------- | ---------------------- | ---------- |
| Original Product Architect investigation | `f76c094a…bcff5d3a`    | &#x20;PASS |
| Independent adversarial review           | `b49bc2b2…cf8abf88`    | &#x20;PASS |

Original investigation

VERIFIED

SHA-256 — exact match

`f76c094ad18877fd4427c95eda1621a4b93d9fb9c6448c22d94311afbcff5d3a`

Extracted original report

Independent adversarial review

VERIFIED

SHA-256 — exact match

`b49bc2b2636e824fd9b82b524a8d4a7c32a6fa8e2e0491c243b1b05bcf8abf88`

Extracted original review

These are the exact reviewed evidence bytes required by the work-unit instructions. The previous identity blocker is closed. The ZIP and both original reports remain unchanged.

### **1.2 Governance and repository verification**

I independently reread the current GitHub state, canonical governance marker, role definitions, architecture authority design, and relevant engineering process.

| Verification                 | Result                                                     |
| ---------------------------- | ---------------------------------------------------------- |
| Governance repository        | `Karageorgiou/GitDrive`                                    |
| Governance `main` SHA        | `63175d7c52bd61b3888bbb6e0576102a87157d80`                 |
| Canonical governance version | `2`                                                        |
| Activation PR                | `#64`                                                      |
| Responsible base role        | `product-architect`                                        |
| Assignment repository        | `Karageorgiou/security-access-control-logging-assignment3` |
| Assignment `main` SHA        | `c31853dc398edc882c2448e2361ba66dce7087f5`                 |
| Professor PDF Git blob       | `438410058b9d018979ef14c315fcd92c58ec60c5`                 |
| Original PDF identity        | PASS — five pages, matching pinned repository blob         |

The original professor PDF has also been inspected directly, including its testing, analysis, and submission provisions.

### **1.3 Work-unit authority**

**Authorized:** Dispose of review findings, reassess product semantics, formulate provisional behavioral contracts, identify required clarifications, and prepare architectural handoff evidence.

**Not authorized:** Implementation, repository mutation, technical-system architecture decisions, binding ADR publication, independent review of this report, or global work-unit coordination.

**Completion boundary:** Deliver the proposed disposition and decision-preparation report in this conversation, then stop.

The GitDrive governance model is applied as an authority framework. Its GitDrive-specific automation is not presumed to exist in the Assignment 3 repository.

## **2. Executive summary**

The independently reviewed requirements investigation remains valid as the assignment's evidence-based requirements baseline.

REVIEW VERDICT

# **PASS**

Blockers / Major

# **0 / 0**

Minor findings

# **3**

Observations

# **2**

The original review's PASS verdict and severity assignments remain unchanged. No evidence justifies rewriting the original investigation or claiming that its provisional contracts were accepted.

**This follow-up establishes three important corrections:**

1. Both analyzer functions must be demonstrated, while `example.txt` is merely an illustrative filename.
2. The specification's pre-delegation wording introduces a real event-lifecycle interpretation question. It does not authorize selecting an implementation sequence.
3. The professor permits `fwrite()`-based **or** hash-difference-based modification counting. Agreement between these methods is not a mandatory acceptance condition.

Two additional observations are preserved: hash differences do not independently establish user attribution, and the assignment is identified as a prerequisite for a possible future exercise.

The most significant outstanding questions remain the meaning of denied access, monitoring scope, distinct file identity, SHA-256 evidence, unique modifications, and their aggregation across users.

**Decision readiness:** Product-level decision candidates can be prepared now. Several can support technical investigation immediately. Their final acceptance remains conditional on the relevant evidence, external clarification, and cross-authority concurrence.

## **3. Independent review finding dispositions**

The following dispositions form a new addendum. They do not retroactively alter the reviewed candidate, its SHA-256, or the independent review.

### **RV-01 — Testing-command classification**

ORIGINAL SEVERITY: MINOR · PRODUCT ARCHITECT

**Evidence:** Professor PDF p.3, Step 3; original T07, §§4.3 and 9.1; independent review §C.

**Issue:** T07 mixed a mandatory demonstration obligation with an illustrative argument.

**Disposition:** Accept the review finding.

T07 is now interpreted as two separately classified elements:

| Reference | Corrected classification    | Meaning                                                                                        |
| --------- | --------------------------- | ---------------------------------------------------------------------------------------------- |
| T07a      | **Mandatory demonstration** | Invoke both `audit_monitor -s` and `audit_monitor -i <filename>` against generated audit data. |
| T07b      | **Illustrative input**      | The specified `example.txt` is an example, not a mandatory test-file name.                     |

A02 and A05 remain unchanged.

**Acceptance consequence:** Evidence of both operational analyzer modes is required. Evidence need not refer to a file literally named `example.txt`.

**Status:** Correction prepared and locally disposed; incorporation into authoritative documentation remains subject to the later documentation and review process. No professor clarification is required.

### **RV-02 — Pre-delegation wording**

ORIGINAL SEVERITY: MINOR · JOINT PRODUCT/SYSTEM

**Evidence:** Professor PDF p.1, Step 1; original L02–L03 and Q07; independent review §C.

The professor says that the overridden functions add auditing capabilities before delegating to the original library functions.

Two interpretations remain plausible:

- **Literal temporal interpretation:** Auditing must occur before delegation.
- **Functional description:** The wrapper adds an auditing function around the original operation, without imposing a strict sequence on each observation.

The denied flag requires knowledge of whether the operation was denied. A before-only observation may lack the actual outcome. Likewise, a write's resulting file state cannot necessarily be established solely from pre-operation information.

**Product-level conclusion:** The observable contract must distinguish the operation's intent, outcome, and any reported content state. The specification does not establish a precise ordering for collecting or recording each item.

**Not decided:** Pre-call versus post-call interception sequence, whether multiple observations are required, or how to capture those observations.

**Status:** Review finding addressed; underlying Q06/Q07/Q21 event-lifecycle issue remains open for System Architect investigation and potentially professor clarification. Joint concurrence is required for a materially cross-cutting final contract.

### **RV-03 — Modification-counting alternatives**

ORIGINAL SEVERITY: MINOR · PRODUCT ARCHITECT

**Evidence:** Professor PDF p.3, Step 2; original A07, Q10; independent review §C.

**Disposition:** Accept the finding and correct Q10's interpretation.

The professor explicitly permits modification counting based on `fwrite()` **or** differing hash values.

This means:

| Question                                                        | Corrected interpretation                                                                             |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Must both methods be implemented?                               | Not established.                                                                                     |
| Must both methods always produce identical counts?              | **No such requirement exists in the PDF.**                                                           |
| May either method support the modification count?               | Yes, subject to correctly defining the selected metric and satisfying the rest of the specification. |
| Is *unique modification* defined?                               | No. It remains materially ambiguous.                                                                 |
| Does a changed hash automatically identify the responsible UID? | No. See RV-04.                                                                                       |

An `fwrite()` event and a difference between two file-content hashes measure potentially different things. The permitted choice of evidence does not resolve the underlying definition of a modification.

**Status:** Q10's over-escalation corrected. No standalone professor clarification is required to establish that the methods are alternatives. Q09, Q11, Q22, and attribution semantics remain open.

### **RV-04 — Hash differences and user attribution**

ORIGINAL SEVERITY: OBSERVATION · JOINT PRODUCT/SYSTEM

**Evidence:** Professor PDF p.3; original A07, PA-04/PA-05; independent review §C.

**Disposition:** Preserve and incorporate the observation.

Two different hashes establish that two observed content states differ, assuming valid hashes of the relevant file contents. They do not, by themselves, establish who caused that difference.

For example, a file might be modified by another process between two observations. Attributing the observed difference to the UID of the second observation could therefore be incorrect.

**Proposed behavioral invariant:** Per-user modification attribution must be supported by evidence connecting the user to the qualifying operation or change. A hash difference alone does not provide that causal connection.

The System Architect must investigate the available attribution evidence and its limitations.

**Status:** Incorporated into the decision candidates and handoff. Technical feasibility and the final attribution contract remain open. The original reviewer observation retains its advisory severity.

### **RV-05 — Future assignment prerequisite**

ORIGINAL SEVERITY: OBSERVATION · SUPERVISOR

**Evidence:** Professor PDF p.4, Note 2; independent review §C.

**Disposition:** Preserve the course dependency in project planning context.

Assignment 3 may form the foundation for a subsequent exercise and is identified as a prerequisite.

This does **not** establish requirements for future APIs, binary compatibility, log schemas, storage architecture, or additional submitted files.

**Status:** Context recorded for Supervisor handoff. No current product-design change or professor clarification is necessary.

### **Finding closure summary**

| Finding | Disposition                              | Remaining dependency                          |
| ------- | ---------------------------------------- | --------------------------------------------- |
| RV-01   | Correction prepared                      | Documentation publication and review          |
| RV-02   | Textual tension explicitly preserved     | System investigation; possible joint decision |
| RV-03   | Counting-method interpretation corrected | Modification and uniqueness semantics         |
| RV-04   | Attribution limitation incorporated      | Joint attribution contract                    |
| RV-05   | Future prerequisite preserved            | Supervisor planning only                      |

All **three minor findings and both observations** have received explicit dispositions. This does not alter the original PASS verdict or assert independent approval of this addendum.

## **4. Updated Q01–Q22 ambiguity register**

Revision: Product semantic follow-up, November 16, 2026. All original IDs are retained.

### **Status interpretation**

- **Resolved by source:** The relevant point is established by the PDF.
- **Product proposal:** A reasonable product interpretation can be formulated but is not yet accepted.
- **System investigation:** Technical evidence is required.
- **Joint decision:** Both architectural dimensions remain material.
- **Professor clarification:** External intent is needed or strongly recommended.
- **Non-blocking:** Does not prevent relevant downstream work.

A blocking dependency applies only to the specified affected contract. It does not automatically block every architecture investigation.

### **4.1 Monitoring, denial, and file identity**

| ID  | Updated interpretation and source                                                                                                    | Materiality / authority        | Decision and downstream disposition                                                                                                                                                                        |
| --- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Q01 | PDF p.1 uses broad system-wide language but explicitly selects three `LD_PRELOAD` interceptions. Reviewer confirms coverage tension. | **High** · Joint + Professor   | **Unresolved.** Technical coverage can be investigated now. Final monitoring-scope claim requires scope reconciliation, preferably professor clarification. Related Q19.                                   |
| Q02 | PDF p.1 requires a log location accessible to all users. Accessibility, append permissions, and integrity are not equivalent.        | Medium · Joint                 | Product accessibility semantics and technical storage design require concurrence. No professor clarification presently essential. Blocks final shared-log guarantee, not initial investigation.            |
| Q03 | PDF p.2 defines denied as lack of privileges, not arbitrary operation failure.                                                       | **High** · Product             | **Resolved by source in principle.** Propose permission-denial-only classification. Failure diagnosis is a technical investigation. Blocks valid denied-flag behavior until classification is established. |
| Q04 | PDF p.2 defines `-s` through denied attempts to access distinct files; it does not identify every qualifying operation code.         | **High** · Product + Professor | Propose attempted file access as the relevant event category. Confirm whether denied writes/closes count. Blocks exact suspicious-user membership at edge cases.                                           |
| Q05 | PDF pp.1–2 requires absolute filenames and distinct-file counting, without defining path equivalence.                                | **High** · Joint               | Product file identity and technical representation require concurrence. Professor clarification is recommended if aliases affect grading. Blocks exact distinct-file equivalence and `-i` matching.        |
| Q06 | PDF p.2 distinguishes creation from opening using prior existence; `stat()` is a hint. RV-02 adds the event-lifecycle timing issue.  | Medium–High · Joint            | Propose outcome-aware classification, but do not specify operation order. System investigation required. Blocks classification of failed/racing edge cases.                                                |

### **4.2 Hashes, modifications, and attribution**

| ID  | Updated interpretation and source                                                                                                     | Materiality / authority            | Decision and downstream disposition                                                                                                                                                                        |
| --- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Q07 | PDF pp.1–2 requires SHA-256 of file contents without defining the observation point. RV-02 qualifies temporal assumptions.            | **High** · Joint                   | Propose explicit snapshot semantics. System feasibility investigation required. Blocks exact hash-to-event contract; clarification may follow if permitted observations do not resolve the text.           |
| Q08 | PDF p.2 requires a hash field even for events that may involve inaccessible content.                                                  | **High** · Joint + Professor       | **Unresolved.** Do not presume a null value or substitute hash is compliant. Requires feasibility investigation and professor clarification before settling unavailable-hash behavior.                     |
| Q09 | PDF p.2 classifies `fwrite()` as a modification event. An attempt, successful write, and actual content change are distinct concepts. | **High** · Product                 | Propose explicit operation-count semantics. System supplies observable outcome evidence. Blocks precise per-user counting definition, not recognition of operation code 2.                                 |
| Q10 | PDF p.3 permits `fwrite()` **or** differing hashes. RV-03 rejects a mandatory agreement rule.                                         | Medium · Product                   | **Resolved by source as alternative methods.** No standalone external clarification needed for method choice. Selected counting meaning and attribution still depend on Q09/Q11/RV-04.                     |
| Q11 | PDF p.3 requires unique modifications without defining uniqueness. Reviewer confirms material ambiguity.                              | **Critical** · Product + Professor | **Unresolved.** Distinct resulting states, distinct changes, and individual write events are not interchangeable. Professor clarification strongly recommended before accepting the metric or exact tests. |
| Q12 | PDF p.3 requires all users who accessed a specified file, but does not explicitly define inclusion of denied attempts.                | Medium–High · Product              | Propose a clearly documented membership rule. Professor clarification conditional on expected reporting of denied-only users. Blocks edge-case user-set acceptance.                                        |
| Q13 | PDF p.3 accepts a filename argument while logging requires absolute paths.                                                            | Medium · Joint                     | Product matching semantics plus System feasibility needed. Relative/absolute query verification remains provisional. Usually no professor clarification necessary.                                         |

### **4.3 Shared records, interfaces, and execution**

| ID  | Updated interpretation and source                                                                                                                    | Materiality / authority                                 | Decision and downstream disposition                                                                                                                                                         |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Q14 | PDF pp.1–2 requires structured append records but leaves serialization unspecified. Reviewer treats this principally as technical design.            | Medium · System, with Product field semantics           | Product can establish meaning of fields. System chooses representation. **Non-blocking implementation freedom** subject to a coherent shared contract.                                      |
| Q15 | PDF p.1 explicitly requires UTC date/time but not precision or exact encoding.                                                                       | Low · Joint                                             | UTC is resolved by source. Precision and formatting are non-blocking design details unless an external exact-output rule emerges.                                                           |
| Q16 | PDF p.2 requires graceful continuation after denial; the library delegates to original operations.                                                   | **High** · Product                                      | Strongly supported proposal: preserve the original success/failure outcome and do not bypass permissions. Audit-subsystem failure remains Q20. No professor clarification currently needed. |
| Q17 | PDF pp.3–4 requires correct outputs and appropriate help/errors, not fixed text or sorting.                                                          | Low · Product                                           | Complete intelligible results are required. Exact formatting and ordering remain **non-blocking freedom**. Do not invent byte-exact grading requirements.                                   |
| Q18 | PDF p.3 requires permission-denied tests but does not define the execution identity/environment.                                                     | Medium · System                                         | Test-environment investigation required. Not an unresolved product requirement or independent professor blocker.                                                                            |
| Q19 | PDF p.1 broadly refers to every open/write/close, but names exactly three functions.                                                                 | High · Joint + Professor                                | **Consolidate with Q01.** No separate coverage decision. System evaluates reachable call paths, then the scope question is resolved jointly or externally.                                  |
| Q20 | PDF pp.1–2 requires append persistence and graceful denial handling, but says nothing about audit-log write failures.                                | Medium–High · Joint + Human if risk acceptance required | Audit-failure policy remains open. Must be settled before claiming reliability or outcome-preservation under failures. Does not block nominal-path architecture investigation.              |
| Q21 | PDF pp.1–2 couples write and close events with content hashes. Buffered data complicates observation of file contents. RV-02 and RV-04 are relevant. | **High** · Joint                                        | System investigation required. Blocks final causal hash/event relationship and any claim of persistent-content modification evidence.                                                       |
| Q22 | PDF p.3 requires unique modifications for a specified file but does not define whether the total is global or per UID.                               | **High** · Product + Professor                          | Propose an explicitly defined aggregation scope. External clarification recommended, preferably alongside Q11. Blocks final unique-modification report contract.                            |

### **4.4 Prioritization and dependency assessment**

Critical

**Q11 + Q22 — Meaning and aggregation of unique modifications**

These directly determine required analyzer results and cannot be reduced to a technical representation choice.

High

**Q01/Q19, Q04, Q05, Q07, Q08, Q09, Q12, Q21**

These affect monitored event scope, suspicious-user results, file identity, hash validity, and user attribution.

Bounded

**Q02, Q06, Q13–Q18, Q20**

These admit product proposals or technical investigation without first resolving every professor-level ambiguity.

The source already resolves the core of Q03, Q10, and Q16 strongly enough to support bounded product proposals, though implementation details remain open.

There is no justification for treating the complete ambiguity register as a single global blocker. The correct stopping points are the affected contracts: especially unique-modification semantics, unavailable hashes, final scope claims, and materially cross-cutting architecture decisions.

## **5. Assessment of PA-01 through PA-08**

The original eight proposals are preserved by identity. The disposition below identifies how each should evolve without changing the reviewed historical report.

| Original proposal                                        | Follow-up disposition               | Reason and dependency                                                                                                                         |
| -------------------------------------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **PA-01 — Preserve original outcomes**                   | **Retain and refine**               | Strongly supported by delegation and graceful continuation. Separate audit-subsystem failure policy under Q20.                                |
| **PA-02 — Distinguish attempts, successes, and denials** | **Retain and refine**               | The semantic distinction is valuable, but additional log fields are not automatically mandatory. RV-02 requires explicit lifecycle treatment. |
| **PA-03 — Consistent file identity**                     | **Retain**                          | Essential to suspicious-user and per-file analysis. Remains dependent on Q05/Q13 and joint feasibility assessment.                            |
| **PA-04 — Separate modification metrics**                | **Refine and split**                | Preserve separate required outputs, distinguish permitted measurement methods from metric definitions, and incorporate RV-03/RV-04.           |
| **PA-05 — Define hash evidence**                         | **Retain conditionally**            | A snapshot meaning is necessary. An unavailable-hash representation cannot be declared compliant without resolving Q08.                       |
| **PA-06 — Shared producer/consumer contract**            | **Retain, split by authority**      | Product owns record meaning; System owns representation, interfaces, and persistence architecture.                                            |
| **PA-07 — Strict suspicious-user threshold**             | **Retain as established invariant** | The numerical threshold is directly specified. It does not need a standalone ADR.                                                             |
| **PA-08 — Avoid invented exact formatting**              | **Retain as acceptance guidance**   | Completeness and intelligibility remain mandatory, but sorting and byte-exact formatting are not prescribed.                                  |

No proposal must be wholly rejected. However, PA-04 needs substantive refinement, and PA-06 must not be treated as one authority's complete design.

The strongest candidates for standalone product decisions concern event semantics, file identity, hash evidence, and modification analysis. Ordinary numerical thresholds and display preferences do not justify separate ADRs.

## **6. Proposed product behavioral contracts**

Each contract below is a candidate, not an accepted architecture decision. The contract IDs are new and distinct from PA-01–PA-08.

### **PC-01 — Audit events, outcomes, and permission denials**

STATUS: PROPOSED · PRODUCT DIMENSION READY FOR REVIEW

**Requirements:** L03, L11–L12, L14–L19, A03–A04.

**Related issues:** Q03, Q04, Q06, Q16, Q20, Q21; RV-02.

**Problem:** An operation attempt, its success or failure, and a permission denial are different facts. Conflating them makes the log and suspicious-user output unreliable.

**Alternatives:**

- A. Treat every intercepted operation as a successful event.
- B. Report attempts and distinguish outcomes where required.
- C. Treat every unsuccessful operation as a permission denial.

A and C conflict with the denied flag's specified meaning. B is most consistent with the assignment, but still requires an event-lifecycle interpretation.

**Proposed contract:**

> An audit event identifies a qualifying file operation and must preserve the distinction between attempted activity, confirmed operation outcome, and permission denial. A denied flag of 1 denotes lack of access privileges, not an arbitrary failure. Auditing must not grant permissions or suppress the original operation's access-control outcome.

**Consequences:** Failed non-permission operations must not generate false suspicious-user evidence. The operation codes remain 0–3 as specified.

**Remaining uncertainties:** Which unsuccessful operations require records, which denied operations qualify for `-s`, and how audit-subsystem failures affect the original operation.

**Dependencies:** System Architect observation feasibility; possible professor clarification on Q04; joint concurrence for lifecycle-related technical consequences.

**Provisional verification:** Compare original and audited operation outcomes; distinguish permission-denied and nonexistent-file failures; check the denied flag and analyzer threshold.

### **PC-02 — Monitoring coverage and truthful scope claims**

STATUS: AWAITING TECHNICAL INVESTIGATION AND CLARIFICATION

**Requirements:** L02, L21.

**Related issues:** Q01, Q19.

**Problem:** The assignment describes broad monitoring while prescribing `LD_PRELOAD` interception of three specific functions.

**Alternatives:** Literal system-wide coverage, coverage of qualifying calls made by preloaded processes, or a narrower explicitly demonstrated test scope.

**Proposed contract:** The system must not claim observation of events outside its verified interception coverage. The final compliance claim must reconcile the professor's broad wording with the explicitly required mechanism.

This is not a decision to reduce the professor's monitoring requirement.

**Consequences:** A bounded technical coverage statement may be accurate, but may not independently satisfy a literal broader interpretation of the assignment.

**Dependencies:** System Architect feasibility evidence, professor clarification, and human risk authorization if an unresolved compliance tradeoff remains.

**Provisional verification:** Compare claimed coverage with observed intercepted operations, including the named functions and relevant non-intercepted paths. No final compliance claim until scope is reconciled.

### **PC-03 — File identity and analyzer query equivalence**

STATUS: PROPOSED · AWAITING JOINT CONCURRENCE

**Requirements:** L08, A03–A08.

**Related issues:** Q05, Q13.

**Problem:** Suspicious-user counting and file-specific analysis require consistent identification of files, but the specification does not define equivalence between different paths referencing the same file.

**Alternatives:**

- A. Equality of recorded absolute-path strings.
- B. Equality after a defined path-normalization policy.
- C. Equality of underlying physical-file identities.

A is closely aligned with the mandatory logged filename field and is simpler to explain, but it may treat aliases as distinct. B and C handle some aliases differently and introduce additional observation requirements.

**Proposed contract:** The logger and analyzer must use one declared file-identity relation consistently. Identical file identities must not be counted more than once for the same UID in suspicious-user analysis.

I provisionally favor an explicit pathname-based identity model for the assignment's ordinary file cases, because the professor requires absolute filenames. This does not settle symlink, hard-link, rename, or canonicalization behavior.

**Dependencies:** System Architect feasibility, professor clarification where aliases affect expected results, and joint concurrence.

**Provisional verification:** Repeated attempts against identical paths, relative and absolute forms, and a controlled alias scenario after the identity policy is agreed.

### **PC-04 — File-content hash evidence**

STATUS: AWAITING TECHNICAL INVESTIGATION AND CLARIFICATION

**Requirements:** L13, L16–L17, A07–A08.

**Related issues:** Q07, Q08, Q21; RV-02, RV-04.

**Problem:** A SHA-256 digest represents content at an observation point. The specification does not define that point or explain what to record when content is inaccessible.

**Alternatives:** Pre-operation state, post-operation state, state after buffered data becomes observable, or another explicitly bounded observation.

**Proposed contract:**

> A valid file hash must be the SHA-256 digest of the file contents observed at a defined point in the event lifecycle. A digest must not be fabricated, and its presence must not be represented as proof that the logged UID caused a content change.

This does not authorize a particular missing-hash placeholder.

**Consequences:** The analyzer must not silently convert absent or incomparable hash evidence into an asserted modification.

**Dependencies:** System Architect investigation of observations and buffered file behavior; professor clarification on mandatory hash-field handling; joint concurrence on the eventual state semantics.

**Provisional verification:** Compare available digests with independent SHA-256 calculations for the agreed state; test denied/inaccessible files and multiple-process modification cases.

### **PC-05 — Per-user modifications, uniqueness, and attribution**

STATUS: AWAITING PROFESSOR CLARIFICATION

**Requirements:** L16, A07–A08.

**Related issues:** Q09–Q11, Q22; RV-03, RV-04.

**Problem:** The professor requires per-user modification counts and unique modifications without establishing every counting rule.

**Alternative interpretations:**

| Candidate metric                        | What it measures                                    | Main limitation                                                   |
| --------------------------------------- | --------------------------------------------------- | ----------------------------------------------------------------- |
| Successful `fwrite()` events            | Observed write activity per UID                     | Repeated identical writes may count.                              |
| Content-changing transitions            | Changes between consecutive observed content states | Requires comparable snapshots and attribution evidence.           |
| Distinct resulting hashes               | Number of distinct observed content states          | A repeated return to an earlier state may not add a unique value. |
| Distinct attributed modification events | Individually identified qualifying modifications    | Requires a definition of attribution and uniqueness.              |

The first two can reasonably support the professor's permitted measurement approaches. They do not establish the unique-modification formula.

**Proposed partial contract:**

> For each queried file, report per-user modification activity using a declared, permitted measurement basis. Report unique modifications as a separately defined metric. Do not assert that hash changes alone prove which UID caused them, and do not require `fwrite()`-based counts and hash-based counts to agree.

**Decision deliberately deferred:** Whether uniqueness refers to event instances, distinct resulting states, or content-changing transitions, and whether the aggregate spans all users.

**Consequences:** The analyzer's final numerical acceptance oracle cannot be completed for all scenarios until those definitions are resolved.

**Dependencies:** Professor clarification for Q11/Q22; Product Architect for metric semantics; System Architect for evidence and attribution feasibility; joint concurrence if the chosen semantic contract requires materially different observation architecture.

**Provisional verification:** Repeated identical writes, changing and restoring content, multiple UIDs, and unmonitored changes, using independently specified expected outcomes.

### **PC-06 — Users associated with a file and analyzer reporting**

STATUS: PROPOSED · CONDITIONAL CLARIFICATION

**Requirements:** A02, A05–A09, T07.

**Related issues:** Q12, Q17; RV-01.

**Problem:** The analyzer must report users associated with a file, but the PDF does not explicitly state whether failed denied-only attempts qualify as access.

**Alternatives:** All attempted accesses, only successful opens/creations, or every UID associated with any qualifying operation.

**Proposed contract:** At minimum, users with confirmed successful file accesses must be included. Whether denied-only users also belong in the `-i` set remains a separate decision, rather than an undocumented assumption.

Both analyzer commands must function and be demonstrated. Their output must be complete and intelligible. Exact row sorting and textual formatting are not established requirements.

**Dependencies:** Product interpretation of Q12, conditional professor clarification if denied-only membership affects grading, System input for file matching.

**Provisional verification:** One user with successful access, another with only a denied attempt, and invalid command-line invocations.

### **PC-07 — Shared audit-record meaning**

STATUS: PROPOSED · SPLIT PRODUCT/SYSTEM OWNERSHIP

**Requirements:** L04–L13, L18, A01.

**Related issues:** Q02, Q14, Q15; PA-06.

**Problem:** The logger and analyzer must agree on what each audit field represents.

**Alternatives:** An undocumented implementation-specific record, an agreed semantic record with implementation-selected serialization, or a fully prescribed external record schema.

**Proposed product contract:** Each recorded event must carry the mandatory information with consistent meaning across the producer and analyzer. UID, PID, filename, UTC time, operation code, denied flag, and file-content hash must not change meaning between components.

The exact record encoding, synchronization, storage representation, and parsing architecture are not Product Architect choices.

**Dependencies:** System Architect ownership of the technical interface; joint concurrence where format constraints change semantic guarantees.

**Provisional verification:** Compare full records across different operation types and demonstrate consistent analyzer interpretation.

### **Established invariant retained without a separate decision**

The professor already establishes the suspicious-user threshold:

\\[ \left|\\{\text{distinct qualifying denied files for UID }u\\}\right|>5 \\]

Once qualification and file identity are defined, six distinct denied files must qualify while five must not.

This is not a new discretionary product preference and does not require a standalone ADR.

## **7. Product ADR candidate inventory**

ADR numbers below are provisional planning identifiers, not published repository decisions.

| Candidate                                              | Scope                  | Status                                             | Why an ADR is justified                                                |
| ------------------------------------------------------ | ---------------------- | -------------------------------------------------- | ---------------------------------------------------------------------- |
| **P-ADR-01 — Audit Event and Outcome Semantics**       | PC-01, Q03/Q04/Q06/Q16 | Proposed                                           | Foundational definition of what an audit event and denial mean.        |
| **P-ADR-02 — File Identity and Query Matching**        | PC-03, Q05/Q13         | Awaiting joint concurrence                         | Determines equivalence across logging and analysis.                    |
| **P-ADR-03 — Hash Evidence and Observation Semantics** | PC-04, Q07/Q08/Q21     | Awaiting technical investigation and clarification | Defines the evidentiary meaning and limitations of a mandatory field.  |
| **P-ADR-04 — Modification Metrics and Attribution**    | PC-05, Q09–Q11/Q22     | Awaiting professor clarification                   | Determines the reported numerical meaning of a major analyzer feature. |

### **Cross-domain architecture decisions**

PC-02 monitoring scope and PC-07 shared record semantics are cross-domain dependencies. They may warrant linked Product/System architecture decisions once feasibility evidence is available.

No shared decision can be declared accepted from this report alone.

### **Technical ADR topics reserved for the System Architect**

Potential technical subjects include interception and event-observation boundaries, shared-record interfaces, persistence and consistency guarantees, hash-observation feasibility, and verification architecture.

This inventory does not prescribe their implementation or require one ADR per technical detail.

### **Matters not warranting standalone ADRs**

The `>5` suspicious-user threshold, required operation-code values, mandatory analyzer commands, README contents, archive naming, and ordinary output presentation are already specified requirements or bounded details.

Creating ADRs for them would add process without resolving material uncertainty.

## **8. Questions requiring professor clarification**

The following questions are prioritized for the professor's Discussion tab. These are **proposed questions only**. No message has been submitted.

### **Priority 1 — Clarify before finalizing analyzer semantics**

**CL-01 — Meaning and aggregation of unique modifications**

Q11, Q22 · A07–A08 · P-ADR-04

> For `audit_monitor -i`, does “unique modifications” refer to distinct successful `fwrite()` operations, actual content-changing events, or distinct resulting SHA-256 hash values? Should the unique-modification total be calculated across all users or separately for each UID?

**Why necessary:** The alternatives can produce different numerical results from identical input events.

**Dependent decision:** PC-05. System investigation may proceed, but final analyzer counting semantics should remain provisional.

**CL-02 — Hash field when content is inaccessible**

Q08 · L12–L13 · P-ADR-03

> When an `fopen()` attempt is denied and the file contents cannot be accessed, what should be recorded in the mandatory SHA-256 field? Is an explicitly unavailable hash permitted for such events?

**Why necessary:** The PDF requires both logging denials and including a content hash, without establishing an exception when contents are unavailable.

**Dependent decision:** PC-04. System Architect can investigate feasibility independently, but cannot declare a missing-value convention compliant without sufficient authority.

**CL-03 — Intended monitoring scope**

Q01, Q19 · L02, L21 · PC-02

> Does the required “system-wide” logging refer to intercepted `fopen()`, `fwrite()`, and `fclose()` calls in processes launched with `LD_PRELOAD`, or is broader monitoring of file operations outside those processes expected?

**Why necessary:** These are materially different coverage contracts.

**Dependent decision:** PC-02. Technical feasibility investigation should proceed, but the final scope claim remains unresolved.

**CL-04 — Qualifying denied operations**

Q04 · A03–A04 · P-ADR-01

> For `audit_monitor -s`, should the analyzer count only permission-denied `fopen()` attempts, or any denied file operation represented in the log?

**Why necessary:** The qualifying event set affects which UIDs exceed the required threshold.

**Dependent decision:** PC-01. Basic permission-denial logging and threshold verification can proceed independently.

### **Priority 2 — Clarify if unresolved after technical investigation**

**CL-05 — Distinct-file identity**

Q05, Q13 · P-ADR-02

> When counting distinct files, should two different absolute pathnames referring to the same underlying file count once or twice? Should `audit_monitor -i` accept relative filenames and match them to absolute paths in the log?

This affects alias behavior and query matching. Ordinary unaliased-file behavior can be investigated without waiting.

**CL-06 — Hash observation point**

Q07, Q21 · P-ADR-03

> Should the recorded SHA-256 represent file contents before the intercepted operation, after the operation, or after any buffered writes become visible?

The System Architect should first determine which observations are technically supportable. The professor's answer is important if those choices yield materially different audit evidence.

**CL-07 — Membership in per-file user reports**

Q12 · PC-06

> For `audit_monitor -i`, should a UID that only attempted access and was denied be included among users who accessed the file, or should the list include only successful accesses?

This is a conditional clarification. It matters most if denied-only users are included in the intended test cases.

No additional professor question is recommended merely to determine whether `fwrite()` and hash-based counts must be identical: **RV-03 establishes that the professor permits alternative bases for counting**.

### **Clarification dependency rule**

Technical investigation may continue on established requirements while these questions are outstanding. However, if a final design must choose between materially different unverified interpretations before clarification arrives, that choice must be explicitly authorized as a risk decision by the human user. It cannot be silently characterized as the professor's intended behavior.

## **9. Product/System coordination dependencies**

The two architects retain separate authority dimensions.

| Decision area            | Product Architect owns                                           | System Architect owns                            | Current gate                |
| ------------------------ | ---------------------------------------------------------------- | ------------------------------------------------ | --------------------------- |
| Audit-event lifecycle    | Meaning of attempted, successful, denied, and completed activity | Observable operation states and event capture    | Joint concurrence           |
| Monitoring scope         | Intended behavioral coverage                                     | Technical coverage and limitations               | Investigation + CL-03       |
| File identity            | Definition of a distinct file                                    | Identity observation and representation          | Joint concurrence           |
| Hash evidence            | Meaning of a valid content snapshot                              | Observation timing and feasibility               | Investigation + CL-02/CL-06 |
| Modification attribution | Evidentiary conditions for assigning activity to a UID           | Available causal and operation evidence          | Joint concurrence           |
| Modification metrics     | Counts, uniqueness, and aggregation semantics                    | Observable data needed to calculate them         | CL-01                       |
| Shared audit log         | Required record meaning and observable guarantees                | Storage, interface, and consistency architecture | Joint concurrence           |
| Analyzer results         | Which users and counts must be reported                          | Data-processing and verification architecture    | Product contract first      |

### **Dependencies that can proceed now**

System Architecture may investigate `LD_PRELOAD` coverage, the observable outcomes of the three required functions, shared-log accessibility, file-state observation, hash feasibility, and test-environment requirements.

Those investigations do not require accepting every provisional product contract beforehand.

### **Dependencies that must not be silently closed**

No final technical architecture should assume that:

- All system-level file operations are necessarily observable.
- Failed operations are automatically permission denials.
- Different pathnames necessarily identify different files.
- A differing hash identifies the UID responsible for a modification.
- The permitted modification-counting methods necessarily agree.
- A missing hash representation is professor-approved.
- “Unique modification” has already been precisely defined.

Where technical evidence conflicts with a product proposal, the matter returns to the relevant architectural owners. Neither architect acquires the other's authority through such a conflict.

## **10. System Architect handoff**

This is a handoff specification, not initiation of the System Architect work unit.

### **10.1 Established behavioral guarantees**

The subsequent technical investigation may rely on the following original requirements:

| Area                 | Established contract                                                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Interception         | Override `fopen()`, `fwrite()`, `fclose()` using `LD_PRELOAD`, preserving their signatures and delegating to original libc functions. |
| Event types          | `0` created, `1` opened, `2` written, `3` closed.                                                                                     |
| Audit fields         | UID, PID, absolute filename, UTC date/time, operation, denied flag, SHA-256 content hash.                                             |
| Log                  | `access_audit.log`, shared accessible directory, append mode.                                                                         |
| Denials              | Flag indicates lack of privileges; execution continues gracefully.                                                                    |
| Suspicious-user rule | More than five distinct denied files for a UID.                                                                                       |
| Per-file analysis    | Users accessing a file, modification count per UID, unique modifications.                                                             |
| Analyzer commands    | Both `-s` and `-i <filename>` required; invalid arguments require help/error.                                                         |
| Demonstration        | Create/open/modify files, generate denials, preload logger, run analyzer.                                                             |
| Build and submission | Makefile, six prescribed files, README, pair submission, ZIP structure.                                                               |

The professor's specification remains authoritative over the example code.

### **10.2 Technical investigation requests**

| Handoff ID | Investigation                                            | Required output                                                                            |
| ---------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| SA-H01     | Actual coverage of the prescribed interception mechanism | Evidence-based coverage boundary and any incompatibility with PC-02                        |
| SA-H02     | Event timing and original-operation outcomes             | Feasible observable states, relevant limitations, and implications for PC-01               |
| SA-H03     | File identity                                            | Representable identity alternatives and consequences for PC-03                             |
| SA-H04     | SHA-256 observation                                      | Feasible content snapshots, unavailable-content conditions, and buffering limitations      |
| SA-H05     | Modification attribution                                 | Evidence available to associate a UID with a qualifying operation or content change        |
| SA-H06     | Shared audit record                                      | Technical producer/consumer contract, accessibility, persistence, and consistency concerns |
| SA-H07     | Failure behavior                                         | Effects of audit logging errors and limits of preserving original outcomes                 |
| SA-H08     | Verification environment                                 | Requirements for demonstrable permission denials, distinct files, and multiple UIDs        |
| SA-H09     | Starter corpus                                           | Consequences of SC-01–SC-05 without assuming their internal design must be preserved       |

### **10.3 Required return information**

The System Architect should return, through Supervisor coordination:

- Which proposed behavioral contracts are technically supportable.
- Which contracts require material qualification.
- Which alternatives have materially different consequences.
- Which questions require joint architectural concurrence.
- Which facts remain unverified.
- Whether any professor clarification becomes unnecessary or more important after technical investigation.

No technical solution is prescribed by this handoff.

### **10.4 Verification considerations carried forward**

The independent reviewer recommended additional verification for relative and absolute file queries, inaccessible hashes, event timing, content changes caused by other UIDs or mechanisms, complete record fields, and unique-modification scenarios involving multiple UIDs.

Those scenarios should inform subsequent verification architecture once the underlying behavioral contracts have been accepted. They are not individually established professor requirements.

## **11. Durable documentation publication recommendations**

This work unit creates no repository content. The following describes a possible future publication structure, subject to Supervisor coordination and separate write authorization.

| Document class                      | Content to preserve                | Identity/status rule                                      |
| ----------------------------------- | ---------------------------------- | --------------------------------------------------------- |
| Original requirements investigation | Unmodified reviewed report         | Preserve exact SHA-256 `f76c094a…bcff5d3a`                |
| Original independent review         | Unmodified review and PASS verdict | Preserve exact SHA-256 `b49bc2b2…cf8abf88`                |
| Review-disposition addendum         | This report, including RV-01–RV-05 | New identity, linked to both originals                    |
| Open-question register              | Q01–Q22 with updated statuses      | Preserve original IDs and maintain revision history       |
| Decision register                   | PC-01–PC-07, PA dispositions       | Proposed or explicitly awaiting further authority         |
| Product ADR candidates              | P-ADR-01 through P-ADR-04          | Not Accepted                                              |
| Cross-domain decisions              | Linked Product/System dimensions   | Awaiting joint concurrence where material                 |
| External clarifications             | CL-01–CL-07 and eventual responses | Record response provenance rather than assuming an answer |

### **Historical integrity**

The original investigation must continue to say what it said when reviewed. RV-01's correction, RV-03's refinement, and other additions belong in this addendum or later reviewed decisions.

The original review's PASS verdict remains a review of its exact candidate, not an independent approval of this new report.

### **Proposed decision states**

| Decision | Current state                                      |
| -------- | -------------------------------------------------- |
| PC-01    | Proposed                                           |
| PC-02    | Awaiting technical investigation and clarification |
| PC-03    | Awaiting joint concurrence                         |
| PC-04    | Awaiting technical investigation and clarification |
| PC-05    | Awaiting professor clarification                   |
| PC-06    | Proposed; conditional clarification                |
| PC-07    | Proposed; split Product/System ownership           |

None is marked **Accepted**.

### **Publication boundary**

Repository paths, documentation structure, branch strategy, PR creation, and publication validation are deferred to a separately authorized documentation work unit. GitDrive's own repository automation is not assumed to enforce the Assignment 3 documentation lifecycle.

## **12. Remaining uncertainty and completion assessment**

### **12.1 Quality and role-compliance gate**

| Required verification                                       | Result  |
| ----------------------------------------------------------- | ------- |
| Exact original investigation hash                           | PASS    |
| Exact independent review hash                               | PASS    |
| Assignment repository baseline                              | PASS    |
| Canonical Governance v2                                     | PASS    |
| Product Architect authority                                 | PASS    |
| Professor specification verified                            | PASS    |
| All three minor findings disposed                           | PASS    |
| Both reviewer observations preserved                        | PASS    |
| All Q01–Q22 reassessed                                      | PASS    |
| All PA-01–PA-08 proposals assessed                          | PASS    |
| New candidates traceable to requirements/review findings    | PASS    |
| Product/System boundaries preserved                         | PASS    |
| Professor clarification dependencies explicit               | PASS    |
| Provisional decisions distinguished from accepted contracts | PASS    |
| Original reports preserved unchanged                        | PASS    |
| Repository mutations or implementation performed            | None    |
| Independent review of this new addendum                     | Pending |

### **12.2 What remains unresolved**

**Professor-level dependencies:** Especially the definition and aggregation of unique modifications, handling of unavailable hashes, and intended monitoring scope.

**Product-semantic dependencies:** Qualifying denied events, file equivalence, per-file user membership, modification attribution, and the final definitions of counted activity.

**System-architecture dependencies:** Interception coverage, observation timing, hash feasibility, shared-log semantics, and audit-failure behavior.

**Joint decisions:** File identity, event lifecycle, hash evidence, attribution, and any materially shared semantic/technical contract.

These are scoped dependencies, not grounds for rejecting the original requirements investigation.

### **12.3 Final determination**

**Product Architect follow-up completed**

Read-only report delivered. Further decision acceptance and independent review remain separate gates.

**Review findings:** All five have explicit dispositions, preserving the original three MINOR findings and two OBSERVATIONS.

**Product decisions:** Seven new candidate contracts prepared, with four proposed Product ADR candidates.

**Professor clarification:** Seven scoped questions prepared, prioritized by compliance impact. No message was submitted.

**System Architect readiness:** **YES — for bounded technical investigation.** The established requirements and provisional contracts provide sufficient inputs. Final cross-domain decisions remain conditional on concurrence and evidence.

**Independent review readiness:** **YES — this follow-up report is ready to be independently challenged.** It is not self-approved.

**Implementation authorization:** **NOT ESTABLISHED.**

**Submission readiness:** **NOT ESTABLISHED.**

The previously blocked Product Architect work unit has now reached its authorized completion boundary. The exact evidence identities were verified, the original reports were preserved unchanged, and no implementation, technical ADR publication, repository modification, or next work unit was initiated.

**REPORT COMPLETE — STOP.**