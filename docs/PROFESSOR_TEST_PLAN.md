# Assignment 3 — Professor-First Acceptance Test Plan (P01–P14)

**Status:** Human approved the P01–P14 *scenario coverage plan*, 2026-11-17. **Documentation only.** No new CI suite has been written or executed under this plan. Scenario details for a redesigned `test_audit.c` are **human choices pending**; this document does not authorize code changes.

**Authority / source:** Supervisor coordination record under GitDrive Governance v2. The requirements are taken from the professor's original `raw/Assignment 3 2026.pdf` (five pages). The exact professor PDF, not this summary, controls grading. Compare against the original starter `raw/src_corpus/` and the final accepted Product/System architecture when necessary. This plan records *what to test*, not a new implementation architecture or independent review verdict.

**Fixed implementation baseline:** `feature/a3-stage4-integration` @ `3f8906ab99a7aae256da1e3b743df6da4aec33cf`; PR [#5](https://github.com/Karageorgiou/security-access-control-logging-assignment3/pull/5), open and unmerged. Existing Stage 1–4 GitHub Actions suites have passed on this SHA. The cumulative independent review reported **PASS WITH DISCLOSED RISKS**. Human WSL execution is pending.

## Acceptance order and separation of responsibilities

- **Submitted `test_audit.c` is a demonstrator**, not the CI assertion engine. It performs real fopen/fwrite/fclose operations and permission-denied attempts chosen by the human, so the logger produces events.
- **The CI suite is the examiner.** It compiles, runs the demonstrator with `LD_PRELOAD`, independently reads and checks records, executes `audit_monitor -s` and `-i`, and compares results against expected outcomes.
- **Professor's ordinary use first:** build → preload → create/open/write/close → inspect recorded fields and hashes → genuine denial → analyzer suspicious and per-file results → help, README and six-file package. Edge-case regressions stay separate and must not replace mandatory scenarios.
- **Reuse existing tests** in `tests/stage1_ci.py`, `stage2_ci.py`, `stage3_ci.py` and `stage4_ci.py` wherever their real assertions already prove the required result; avoid duplicated test logic without a clear reason. Green workflows do not, alone, settle a professor-compliance ambiguity.
- CI tests use ordinary unprivileged Linux UIDs for actual denial outcomes. Multiple users mean **distinct real UIDs**, not fictional IDs printed by one process.
- The professor's example `./audit_monitor -i example.txt` currently does **not** select the demonstrator's `/tmp/a3-assignment-XXXXXX/example.txt` from the repository directory. Preserve and flag this discrepancy during collaborative design; do not silently redefine the demonstrator's path contract.

## P01–P14 requirement and assertion matrix

| Test | Professor requirement / PDF reference | Assertion to implement or reuse | Existing CI evidence | Redesign dependency |
|---|---|---|---|---|
| **P01 Build** | Makefile compiles the library and programs (p. 4) | In clean Ubuntu environment `make clean all` exits successfully; three expected outputs exist | Stage 4 workflow | None |
| **P02 Intercept** | `LD_PRELOAD` and exactly the `fopen`, `fwrite`, `fclose` overrides (p. 1) | Verify exactly these exported override names and run actual C file operations under `LD_PRELOAD=./audit_logger.so` | Stage 1–4 workflow and probes | None |
| **P03 Create** | Creation when `fopen` opens a previously nonexistent file with creation-capable mode (pp. 1–2) | Real absent-file open returns success and logger records operation 0; compare non-existing versus existing | Stage 1 `fopen` probe | Demonstrator's chosen modes pending |
| **P04 Open** | Existing file opening has operation 1 (pp. 1–2) | Real existing-file fopen emits code 1, correct pathname and successful outcome | Stage 1 `fopen` probe | Demonstrator's chosen modes pending |
| **P05 Write / close** | `fwrite` operation 2 and `fclose` operation 3 (p. 2) | Exercise real positive write(s) and close; assert both record types and preserved libc return/errno | Stage 2 probes and Stage 4 | Human-chosen write counts and ordering pending |
| **P06 Required audit fields** | UID, PID, absolute filename, UTC date/time, operation, denied flag, SHA-256 (pp. 1–2) | Parse actual records: real UID/PID, normalized absolute path, UTC timestamp within execution interval, valid op and denied values, hash field | Stage 1 and Stage 4 assertions | None |
| **P07 SHA-256** | File-content SHA-256 via OpenSSL EVP (p. 2) | Hash a known safely readable regular file independently and compare with logged digest at a defined observation point (not arbitrary buffered state) | Stage 1/2/4 genuine-hash assertions | Final content depends on approved scenario |
| **P08 Denied open** | Denied accesses logged and original program continues gracefully (p. 2, demo p. 3) | Under non-root UID, create an unreadable file, attempt `fopen`, assert `EACCES`/`EPERM`, denied flag 1, no unexpected process failure; restore permission | Stage 1 and Stage 4 genuine denials | Human chooses scenario count/order; no root-only false denial |
| **P09 Append / shared log** | System-wide `/tmp/access_audit.log`, append not overwrite (pp. 1–2) | Run independent operations/processes, assert earlier rows persist, new records are complete; where testing multiuser, both different ordinary UIDs append/read | Stage 2 and Stage 4 genuine two-UID CI | None |
| **P10 Suspicious `-s`** | Users denied access to **more than 5 distinct** files (p. 3) | Exactly five distinct denied names must not flag UID; six must; repeat of same denied pathname does not raise distinct count | Stage 3 fixture and Stage 4 real six-denial demo | Professor fixes threshold; human decides other arbitrary scenario details |
| **P11 File activity `-i`** | List accessed users, per-UID modifications, unique modifications (p. 3) | For real successful accesses/writes, assert exact displayed UID(s), per-UID counts and total. Verify selected event-count interpretation and report 'unique' ambiguity rather than redefining silently | Stage 3 fixtures and Stage 4 end-to-end demo | Filename, writes and user execution chosen by human |
| **P12 Professor demonstrator** | `test_audit.c`: create several files, open and modify under various conditions, attempt denied opens (p. 3) | Run exactly `LD_PRELOAD=./audit_logger.so ./test_audit` with proper log provisioning; inspect actual effects/log. Execute `audit_monitor -s` and `-i` on the demonstrated target, compare to approved scenario | Stage 4 multi-UID CI verifies current program | **Entire new demonstration sequence pending human approval** |
| **P13 CLI errors** | Invalid/missing audit-monitor arguments produce appropriate help or errors (p. 4) | Assert `-s`, `-i filename`, help and invalid/missing argument handling and return status | Stage 3 CLI tests | None |
| **P14 Submission archive** | Required six files, folder/ZIP naming and Makefile, README (pp. 4–5) | Archive has exactly `README`, `Makefile`, `audit_logger.c`, `audit_logger.so`, `audit_monitor.c`, `test_audit.c` inside `2015030123_2006030122_assign3/`; ZIP integrity and extraction/rebuild pass. Manually inspect README identifiers and approach | Stage 4 ZIP build/extract assertions; independent reviewer | New candidate archive required after any code changes |

**Naming note:** These P01–P14 IDs are our own traceability identifiers, not professor test IDs.

## Human-directed redesign inputs — DO NOT PRE-FILL

The Developer must ask the human one meaningful question at a time, then present the full scenario before coding. Record answers here **only after explicit approval**:

| Choice | Current status |
|---|---|
| One ordinary UID or a multi-UID sequence | **Pending human decision** |
| File names and where created (including `example.txt` invocation behavior) | **Pending human decision** |
| Initial file states, file content and operation modes | **Pending human decision** |
| Number of successful opens, writes, closes and denials per file/user | **Pending human decision** |
| Exact order of operations and any repetition | **Pending human decision** |
| Suspicious UID(s), expected `-s` output | **Pending human decision** |
| For each `-i` file, expected per-UID count and total | **Pending human decision** |
| Cleanup and safe operation under unprivileged UIDs | **Pending human decision** |

**Randomness policy:** No agent-generated arbitrary numbers, seeds, filenames, operation counts or iteration counts. Ask the human to supply them. Mandatory constants (e.g. threshold `>5`) come from the PDF and are not random. Prefer deterministic, ordered operations for CI. If the human explicitly requests randomized sequences, first ask for a seed, parameter ranges and iteration counts, and explain reproducibility. UID, PID, UTC timestamps and `mkdtemp` suffixes are runtime observations that tests discover dynamically, not agent-chosen test inputs.

## Review risks and non-gating tests (do not silently redefine scope)

The independent reviewer identified no mandatory source-code correction *before human WSL testing*, but these matters remain:

1. **Universal SHA-256 wording vs logger `N/A`** for an unobservable file: compliance risk. Positive assertions of genuine SHA-256 do not erase this gap.
2. **Exact `audit_monitor -i example.txt` example vs printed absolute target path:** explicitly decide in the human-designed demonstration.
3. **'Unique modifications' semantic ambiguity:** per-successful-`fwrite` counting is defensible, but differing-hash interpretation is also mentioned in PDF.
4. **README student IDs/logins wording:** current names and student numbers are present; need human confirmation if distinct login identifiers exist and are required.
5. **Creation attempts categorized as code 0:** review identified partial compliance ambiguity.
6. **Additional optional evidence:** deterministic real partial-positive `fwrite`; two real UIDs modifying the *same* target file; post-close identity race. Tests for these are valuable but not substitutes for professor-first cases.
7. **Human WSL professor-first end-to-end execution** remains pending. The final submitted compiled library must be from a tracked, verified candidate; no merge or submission without separate human authorization.

## Change control and CI reporting

No implementation/test change is authorized by merely publishing this plan. After the human approves the demonstrator scenario, the Supervisor should explicitly scope a **new stacked Developer work unit** based on verified Stage 4 head. Developer then implements the agreed demonstrator, minimal professor-scenario CI additions, and updates affected existing assertions as required. All earlier suites must continue to pass. Inspect completed push/PR jobs at the exact changed SHA, actual PASS assertions, package contents and origin, then route code changes to appropriate independent re-review. Do not merge existing implementation PRs or docs PR #1 without subsequent authorization.

**References:** [Current architecture and handoff](CURRENT_ARCHITECTURE_AND_HANDOFF.md); [Stage 4 PR #5](https://github.com/Karageorgiou/security-access-control-logging-assignment3/pull/5).
