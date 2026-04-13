# Product Doctrine

This file turns the product vision into daily engineering rules.

## Non-Negotiables

1. Vision is the north star.
2. Production comes first.
3. Ship in reversible thin slices.
4. Keep trust boundaries explicit.
5. Treat reliability as a product feature.
6. Treat privacy and security as defaults.
7. Keep the platform durable beyond current tools or runtimes.

## Development Implications

- start from user outcome, not tool novelty
- choose the least autonomous pattern that achieves the outcome
- keep side effects behind policy and approval boundaries
- write code so business logic can survive runtime swaps
- treat evals and observation as part of the product loop
