# Review Checklist

## Review Priority Order

1. Correctness
2. Behavioral regressions
3. Security and trust boundaries
4. Missing tests or eval coverage
5. Deployment and recovery risk
6. Maintainability
7. Style

## Core Questions

- does the change solve the stated problem?
- does it match the packet scope?
- are trust boundaries still explicit?
- could this silently fail, race, or double-execute?
- are auth, secrets, and approvals handled correctly?
- is rollback practical?
