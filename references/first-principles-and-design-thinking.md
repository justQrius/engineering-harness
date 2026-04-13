# First-Principles And Design Thinking

Use this reference when the user wants stronger end-to-end development
discipline, not only implementation-phase rules.

## Goal

Encode two thinking modes into the harness:

- first-principles thinking: reduce work to root problem, constraints,
  invariants, assumptions, and necessary guarantees
- design thinking: keep the user job, friction, feedback loop, and success
  experience explicit throughout the cycle

Do not add them as slogans only. Turn them into planning, review, release, and
learning behaviors.

## Questions to encode by phase

### Planning

- what user job is being served?
- what root problem is actually being solved?
- what must remain invariant?
- what can stay flexible?
- what assumptions are being made?
- what is the smallest slice that teaches something important?

### Research

- which facts come from canon?
- which facts require current official documentation?
- which reference implementations are worth studying?
- what did existing systems get right or wrong?

### Development

- which risky assumption should be tested first?
- what is the smallest reversible slice?
- how does this preserve the intended user workflow?
- where should integration happen early rather than after local coding?

### Review

- did the change address a root cause or only a symptom?
- were assumptions tested or merely asserted?
- does the user workflow improve, stay intact, or regress?
- what should remain a convention rather than becoming a hard invariant?

### Release

- how will we know the user-facing outcome improved?
- what rollback path exists if the slice is wrong?
- what must be observed after release to validate the thesis?

### Learning

- what assumption was disproven?
- what friction did users or developers actually hit?
- what is now known to be invariant?
- what should be tightened in the harness?

## Template changes that usually help

- add packet fields for:
  - user / job to be done
  - root problem
  - root constraint or invariant
  - assumptions to test
  - smallest learning slice
  - UX success signal
- update review checklists with root-cause and UX-preservation questions
- update definition-of-done so learning capture is part of completion
- add doctrine that links planning, implementation, review, release, and
  learning rather than treating coding as the only engineering activity
