---
name: heal
description: >-
  Self-healing compile/test loop for Rust and TypeScript. Runs the test suite, diagnoses
  failures, fixes them, and iterates until green — up to a configurable max rounds. Use
  when the build is broken, tests are failing, or after making changes that need validation.
  Trigger phrases: "heal", "fix the build", "make it green", "fix tests", "compile loop",
  "iterate until green", "self-heal".
---

# Self-Healing CI Loop

Autonomous fix-compile-test iteration. Runs the test suite, reads errors, fixes code,
and repeats until everything passes or the iteration cap is hit.

For a WRFCoin persona branch, use `wrfcoin-heal` for its focused multi-stack loop.

This eliminates the manual back-and-forth that accounts for ~25 friction incidents per
sprint (buggy_code + wrong_approach), especially in Rust where compile cycles are expensive.

---

## When to use

- After making implementation changes, before declaring work done
- When cargo check/test is failing and you need to iterate to green
- When a lane agent's PR has test failures that need fixing
- After a merge introduces regressions
- Anytime: "the build is broken, fix it"

## When NOT to use

- For pre-existing known failures (see MEMORY.md for the list)
- For test failures that require design decisions (flag those for the user)
- When the failure is in CI infrastructure, not code (use `/ci-triage` instead)

---

## Inputs

The user may specify:

- **Scope**: a specific crate (`-p wrfcoin-native-chain`), repo, or "workspace"
- **Max rounds**: default 5, can be overridden ("heal with max 10 rounds")
- **Test filter**: specific test name or module ("heal the consensus tests")
- **Mode**: "check-only" (just compilation) or "full" (compile + test, default)

If no scope is given, detect it from:
1. The current working directory
2. Recently edited files in the conversation
3. Fall back to `--workspace`

---

## Algorithm

```
round = 0
max_rounds = 5  (or user-specified)
scope = detected or user-specified

while round < max_rounds:
    round += 1

    # Step 1: Compile check
    errors = run cargo check (scoped)
    if errors:
        analyze and fix compilation errors
        continue  # re-check before running tests

    # Step 2: Run tests (if mode == "full")
    failures = run cargo test (scoped)
    if no failures:
        break  # GREEN — done

    # Step 3: Diagnose failures
    for each failing test:
        read the test code
        read the error output
        identify root cause

    # Step 4: Fix
    apply fixes (one logical fix per round)
    # The PostToolUse hook will run cargo check after each edit

# Step 5: Report
output summary: what was broken, what was fixed, current state
```

---

## Phase 1: Compile Check

### Rust

Determine the scope and run the appropriate check:

```bash
# Specific crate (preferred — fast)
cargo check -p <crate-name> 2>&1

# Whole workspace (when scope is unclear or cross-crate)
cargo check --workspace 2>&1
```

Parse the output for:
- `error[E0...]` — compiler errors (must fix)
- `warning[...]` — warnings (fix if related to the current change, ignore otherwise)

**Error triage priority:**
1. Missing/wrong imports (`E0432`, `E0433`)
2. Type mismatches (`E0308`)
3. Missing struct fields (`E0063`)
4. Wrong number of arguments (`E0061`)
5. Unresolved names (`E0425`)
6. Borrow checker (`E0502`, `E0505`, `E0507`)

### TypeScript

```bash
npx tsc --noEmit 2>&1 | head -50
```

---

## Phase 2: Run Tests

### Rust

```bash
# Specific crate
cargo test -p <crate-name> 2>&1

# Specific test
cargo test -p <crate-name> <test_name> 2>&1

# Workspace (slow — avoid unless needed)
cargo test --workspace 2>&1
```

**Timeout handling:** Rust test compilation can be slow. Use `timeout 300` (5 min)
for workspace builds. If it times out, narrow the scope:

```bash
timeout 300 cargo test --workspace 2>&1 || echo "TIMEOUT — narrow scope"
```

### TypeScript

```bash
npm test 2>&1 | tail -50
# or
npx jest --no-coverage 2>&1 | tail -50
```

---

## Phase 3: Diagnose Failures

For each failing test, gather context:

### 3.1 Read the error output

Extract the test name, assertion failure, panic message, or diff.

### 3.2 Read the test code

```bash
# Find the test
rg "fn <test_name>" --type rust -l
```

Read the test function to understand what it expects.

### 3.3 Read the code under test

Follow the call chain from the test to the implementation. Read the actual
function being tested, not just the test.

### 3.4 Classify the failure

| Type | Example | Fix Strategy |
|------|---------|-------------|
| **Struct mismatch** | Missing field, wrong field count | Grep all usages, fix all sites |
| **Type error** | Wrong return type after refactor | Trace the type through the call chain |
| **Logic error** | Assertion fails with wrong value | Read the implementation, fix the logic |
| **Missing impl** | Unimplemented trait or method | Add the implementation |
| **Stale test** | Test expects old behavior | Update the test to match new behavior |
| **Import error** | Module moved or renamed | Fix the use/mod path |
| **Known failure** | Pre-existing (see MEMORY.md) | Skip — do not fix |

### 3.5 Known pre-existing failures (SKIP these)

These are documented in MEMORY.md and should NOT be treated as regressions:

- `storage::tests::checkpoint_prunes_wal`
- `oracle-packet` missing field
- `economic_property_tests::commit_reveal_windows`

If a failure matches one of these, ignore it and move on.

---

## Phase 4: Fix

### Fix rules

1. **One logical fix per round.** Don't batch unrelated fixes — they compound errors.
2. **Fix the root cause, not the symptom.** If a struct changed, fix all usages, not
   just the one the compiler pointed at.
3. **Struct modification protocol:** When fixing a struct, grep for ALL usages first:
   ```bash
   rg 'StructName' --type rust -l
   ```
   Fix every call site before re-running the check.
4. **Don't change tests to match bugs.** If the test is correct and the code is wrong,
   fix the code. If the code is correct and the test is outdated, fix the test.
5. **Don't introduce new problems.** After each edit, the PostToolUse hook runs
   `cargo check` automatically. If the hook reports new errors, fix those before
   proceeding.
6. **Preserve existing behavior.** Don't refactor or "improve" code while fixing. Only
   change what's needed to make the test pass.

### Fix workflow

```
For each error/failure:
    1. Read the relevant source files
    2. Identify the minimal fix
    3. Apply the fix with Edit tool
    4. (Hook runs cargo check automatically)
    5. If hook shows new errors → fix those first
    6. Move to next error
```

---

## Phase 5: Report

After all rounds complete (or green is achieved), output a summary:

```
## Heal Report

**Scope:** <crate or workspace>
**Rounds:** <N> of <max>
**Result:** GREEN / PARTIAL / STUCK

### Fixes Applied
| Round | File | Fix | Error |
|-------|------|-----|-------|
| 1 | shared-protocol/src/block.rs:42 | Added missing field `nonce` | E0063 |
| 2 | native-chain/src/api.rs:108 | Fixed return type | E0308 |

### Remaining Failures (if any)
| Test | Error | Why Not Fixed |
|------|-------|---------------|
| test_checkpoint | assertion failed | Pre-existing (known) |
| test_complex_merge | design decision needed | Flagged for user |

### Current State
- cargo check: PASS / FAIL
- cargo test: PASS / N failures (M known, K new)
```

### Result classification

- **GREEN**: All checks pass, all tests pass (excluding known failures)
- **PARTIAL**: Compilation passes but some tests still fail (new failures, not known ones)
- **STUCK**: Hitting the same error repeatedly, or fixes are introducing new errors.
  At this point, stop and report — don't keep looping.

---

## Stuck Detection

If any of these conditions are true, STOP iterating and report:

1. **Same error twice**: The exact same error (same file, same line, same code) appeared
   in two consecutive rounds. The fix didn't work — need a different approach.
2. **Error count increasing**: More errors after a fix than before. The fix is wrong —
   revert and report.
3. **Circular fixes**: Fix A breaks B, fix B breaks A. Need architectural guidance.
4. **Max rounds hit**: Reached the iteration cap without green. Report what's left.

When stuck, output:
```
## STUCK — Need Human Input

**After <N> rounds, still failing.**

### What I tried
- Round 1: <fix> → <result>
- Round 2: <fix> → <result>

### Root cause analysis
<why the fixes aren't working>

### Suggested approaches
1. <option A>
2. <option B>

### Recommend
<which option and why>
```

---

## Integration with other skills

- **During `/auto-manage`**: After lane agents push PRs, the review sub-agent can
  invoke heal logic if tests are failing.
- **During lane work**: Lane agents should use this loop whenever cargo check/test fails
  instead of declaring work done with broken tests.
- **With `/merge-review`**: If a PR has test failures, the reviewer can note "run /heal"
  in the revision handoff.

---

## Configuration

Defaults (can be overridden per invocation):

| Setting | Default | Override example |
|---------|---------|-----------------|
| Max rounds | 5 | "heal max 10" |
| Mode | full (check + test) | "heal check-only" |
| Scope | auto-detect | "heal -p wrfcoin-native-chain" |
| Test filter | all | "heal test_block_creation" |
| Known failures | skip | "heal --include-known" |
