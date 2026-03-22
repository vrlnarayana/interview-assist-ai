# Interview Guide - Technical Lead (Interview Date: March 23, 2026)

## Scoring Method
- Rate each answer on 1-5 for: Technical, Functional, Leadership.
- 5: Deep, specific, production examples with metrics and tradeoffs.
- 3: Correct but generic, limited scale/context.
- 1: Vague, theoretical, no ownership.

## Decision Rule
- Select to next round: overall >= 75/100 AND no dimension < 60/100.
- Borderline: 65-74 or one weak dimension.
- Reject for this role: < 65 or clear mismatch in hands-on leadership/architecture.

## Candidate 1: Jayalakshmi Senthilkumar
### Profile Fit Snapshot
- Strengths: .NET Core backend depth, API/security/SQL, AWS delivery, performance optimization.
- Risks: Angular depth unclear, AI/ML integration ownership unclear, environment-from-scratch proof needed.

### Questions, Expected Answers, and Rating
1. Ask: "Design the backend architecture for this product from day 1, supporting Angular web + mobile clients and future AI services."
- Expect: service boundaries, API gateway, auth (JWT/OAuth), versioning, SQL design, observability, scale strategy.
- 5/5 signs: gives modular architecture with concrete technology choices and failure handling.
- 3/5 signs: mostly API + DB discussion, little platform/ops design.
- 1/5 signs: no architecture decomposition.

2. Ask: "Tell me a project where you set up CI/CD and environments from scratch. Exact pipeline stages and rollback strategy?"
- Expect: branch strategy, build/test/security scans, container build, deploy to dev/stage/prod, rollback and approvals.
- 5/5 signs: clear end-to-end ownership with incidents/lessons.
- 3/5 signs: participated but did not own design.
- 1/5 signs: only used existing pipeline.

3. Ask: "How have you integrated external/AI services into production systems?"
- Expect: API contracts, timeout/retry/circuit breaker, prompt/model versioning (if used), monitoring and fallback.
- 5/5 signs: concrete reliability controls and cost/latency tradeoffs.
- 3/5 signs: simple API consume only.
- 1/5 signs: no real integration experience.

4. Ask: "What would be your Angular integration strategy with backend contracts?"
- Expect: OpenAPI/Swagger, DTO versioning, error contracts, pagination/filtering, release coordination.
- 5/5 signs: strong contract-first approach and frontend collaboration model.
- 3/5 signs: basic endpoint discussion only.
- 1/5 signs: weak understanding of frontend-backend coupling.

5. Ask: "Describe a time you mentored developers and improved quality metrics."
- Expect: code review rubric, standards, measurable quality improvements.
- 5/5 signs: metrics (defect reduction, lead time, coverage) plus repeatable process.
- 3/5 signs: mentoring claims but weak evidence.
- 1/5 signs: no leadership ownership.

### What Confirms Fit
- Demonstrates architecture ownership, not only coding.
- Can run platform setup independently.
- Shows practical cross-team leadership and hands-on coding continuity.

## Candidate 2: K A Neha
### Profile Fit Snapshot
- Strengths: strong Angular leadership, migration experience, micro-frontends, delivery ownership.
- Risks: deep backend architecture in .NET uncertain, auth/SQL depth unclear, AI integration unclear.

### Questions, Expected Answers, and Rating
1. Ask: "For this role, backend depth is critical. Walk me through a .NET API system you designed end-to-end, including DB, auth, and scaling."
- Expect: layered design, SQL schema/indexing, JWT/OAuth, caching, async patterns, scaling bottlenecks.
- 5/5 signs: specific backend design decisions with performance/security metrics.
- 3/5 signs: mostly consumer-level API integration experience.
- 1/5 signs: limited backend ownership.

2. Ask: "How would you define API contracts for Angular + mobile + future AI services?"
- Expect: OpenAPI governance, backward compatibility, versioning policy, contract testing.
- 5/5 signs: practical governance model plus release process.
- 3/5 signs: conceptual only.
- 1/5 signs: no contract/version discipline.

3. Ask: "Give an example of leading from architecture through execution across teams."
- Expect: decision log, risk management, quality gates, delivery outcomes.
- 5/5 signs: clear tradeoff decisions and measurable impact.
- 3/5 signs: project coordination without architectural ownership.
- 1/5 signs: individual contributor only.

4. Ask: "How would you set up Dev/Staging/Prod with CI/CD and Docker for a new greenfield platform?"
- Expect: infra baseline, IaC preference, secrets management, monitoring/alerts, rollback.
- 5/5 signs: concrete environment strategy and operational maturity.
- 3/5 signs: partial understanding.
- 1/5 signs: no setup ownership.

5. Ask: "How will you integrate AI model outputs safely into business workflows?"
- Expect: validation layer, confidence thresholds, human-in-loop for high-risk steps, observability.
- 5/5 signs: robust production controls and failure handling.
- 3/5 signs: generic API call understanding.
- 1/5 signs: no practical AI integration approach.

### What Confirms Fit
- Proves backend architecture depth beyond frontend leadership.
- Demonstrates technical lead behavior in platform-level decisions.
- Shows readiness for a hands-on full-stack + AI-enabled systems role.

## Side-by-Side Conclusion Logic
- Prefer Jayalakshmi if backend architecture + CI/CD/platform setup answers are clearly stronger and leadership is sufficient.
- Prefer Neha if she demonstrates unexpected backend depth plus strong leadership and platform setup clarity, not only frontend strengths.
- If both are borderline on AI integration, proceed only with the one who shows stronger system-design rigor and ownership under ambiguity.
