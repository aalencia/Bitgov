# BitGov Decision-Basis Specification V1

Status: ACCEPTED NORMATIVE ARCHITECTURE

Source Candidate: BITGOV-DB-I1-NORMATIVE-v6

Verification: BITGOV_DECISION_BASIS_NORMATIVE_PROPOSAL_VERIFIED

Canonical Base at Architecture Verification:
- HEAD: 8badfe421557fb562e5bb2f28d83af69359214b3
- TREE: bbe67c3b52b17afe65709d528d7518ddb0e0e2e1

Authority:
This specification defines the accepted minimum generic BitGov decision-basis semantics required for fail-closed machine authorization surface design.

Scope:
Acceptance of this specification does not populate deferred governance policy, activate BIOREP-A1 or LIFE-A1, authorize implementation, or alter cross-system authority ownership.

---

## Verified Architecture Record
```text
CANDIDATE_ID:
BITGOV-DB-I1-NORMATIVE-v6
TRANCHE: BITGOV-DB-I1 DECISION-BASIS RECONCILIATION
ROLE: BITGOV MINIMUM DECISION-BASIS SPECIFICATION ARCHITECT
ACCESS CONTEXT: READ_ONLY ARCHITECTURE RETURN — NO PUBLISH, NO IMPLEMENT,
NO WORKER DISPATCH, NO BIOREP-A1 / LIFE-A1 ACTIVATION
PREDECESSOR: BITGOV-DB-I1-NORMATIVE-v5 (CORRECTION REQUIRED, NO BLOCK)
THIS TARGET: BITGOV-DB-I1-NORMATIVE-v6
```

# BITGOV-DB-I1 NORMATIVE PROPOSAL v6 — COMPLETE A–Z

## A. IDENTITY AND SCOPE

A1. This artifact is the generic normative decision-basis for BitGov.
It defines minimum machine semantics to determine authorization,
constitutional state where applicable, finality, appeal/escalation
effect where applicable, lifecycle state where applicable, with
authority lineage preserved.

A2. DB-I1 selects architecture, not substantive governance policy.
Completeness means the machine can: determine applicability, resolve
legitimate rule authority, represent missing required rules, fail
closed as UNRESOLVED, preserve lineage. Completeness does NOT require
governed policy values to be populated.

A3. Canon discipline: current BitGov canon is the verified prose corpus
at `8badfe421557fb562e5bb2f28d83af69359214b3 /
bbe67c3b52b17afe65709d528d7518ddb0e0e2e1`.
Canon motivates but does not establish DB-I1 semantics.
TruthSpine / Aegis / GWO / DB-I1 / BIOREP-A1 / LIFE-A1 are proposal
architecture terms, not canon claims.

A4. Preserved invariant:

```text
AUTHORIZATION OUTCOME
!=
CONSTITUTIONAL DISPOSITION
!=
FINALITY
```

All cross-references in this artifact were audited per §AD.

## B. AUTHORIZATION OUTCOME VOCABULARY

B1. Generic BitGov authorization outcomes, exactly:

```text
AUTHORIZED
DENIED
NO-GOVERNED-DECISION
UNRESOLVED
```

B2. Do NOT use `BLOCKED` as an authorization outcome. `BLOCKED` belongs
exclusively to constitutional disposition where constitutionally
applicable, per §Q:

```text
ADMISSIBLE
BLOCKED
UNRESOLVED
```

B3. `DENIED` is a governed negative decision;
`NO-GOVERNED-DECISION` means no applicable governed decision basis
resolves the matter; `UNRESOLVED` is deterministic epistemic
fail-closed state; `BLOCKED` is constitutional only.

B4. Preserved invariant: `FINALITY != AUTHORIZATION OUTCOME`, and
`EXECUTION / RELIANCE EFFECT` is determined only by applicable
governed effect rule per §R. No silent capability grant from
non-final authorized state.

## C. FOUR CANONICAL THRESHOLD PROCESSES

C1. The four already reconciled canonical threshold processes are,
exactly:

```text
1. 10% CONTENTIOUS-ISSUE PETITION
   → REFERENDUM

2. 10% INTEGRATION-DECISION TRIGGER
   → INTEGRATION REFERENDUM

3. 5% FEEDBACK-ESCALATION PETITION
   → REFERENDUM OR PANEL REVIEW

4. 1% CRISIS OVERRIDE TRIGGER
   → UNPRECEDENTED-SITUATION PROCESS
   + HUMAN APPROVAL REQUIREMENT
```

C2. Keep all four distinct. Do NOT create `THE 10% RULE`. Processes 1
and 2 are distinct 10% scopes; they must not be merged.

C3. Do NOT classify `APPEAL` or `ESCALATION` as one of these four.
Appeal and escalation remain separate lifecycle/process concepts
governed in §N / §O.

C4. Panel review is a possible consequence of the 5% feedback process
in §C1 item 3, not a separate canonical threshold merely because
panels exist elsewhere. Panel validity/selection remain governed per
§H / §I.

## D. GENERIC TRIGGER SEMANTIC — ABOVE, NOT INSTEAD

D1. DB-I1 defines a generic machine concept `TRIGGER` with semantics
such as:

```text
trigger identity
trigger class
authority
scope
applicability
threshold / condition
resulting process
interaction rule
lineage
```

D2. That abstraction sits ABOVE the four canonical processes in §C.
It must not replace or rewrite them. `GENERIC TRIGGER SEMANTIC` and
current BitGov rules `10% / 10% / 5% / 1%` remain distinguishable.

D3. No invented trigger precedence. Interaction among triggers, if any,
requires applicable governed interaction rule; where required and
missing → UNRESOLVED. Trigger filing alone determines no authorization
outcome and no execution effect.

## E. CANONICAL VALUE vs MISSING OPERATIONAL SEMANTICS

E1. DB-I1 distinguishes:

```text
CANONICAL THRESHOLD VALUE
from
MISSING OPERATIONAL SEMANTICS
```

E2. The two 10% rules, the 5% feedback threshold, and the 1% crisis
override in §C are canonical within their stated scopes.

E3. For example, current canon may establish `1%` while leaving
unresolved: eligible franchise, denominator, measurement mechanics,
time window, approval quorum, interaction with other processes.
Canon value stands; operational gaps fail closed as UNRESOLVED where
required and applicable.

E4. Do not treat a canonical value as though DB-I1 is free to discard
it merely because surrounding machine semantics are incomplete.
§AB defers only what canon genuinely leaves unresolved.

## F. HUMAN FRANCHISE / DENOMINATOR — REPRESENTATION-NEUTRAL

F1. No universal `verified proof-of-personhood roll of affected scope
at close snapshot` architecture. Generic human-trigger semantics, each
from applicable governed rule:

```text
ELIGIBLE_FRANCHISE
DENOMINATOR_RULE
SIGNATURE_VALIDITY_RULE
MEASUREMENT_WINDOW
SCOPE
```

F2. For currently canonical human petition/referendum/override
processes in §C, applicable franchise may legitimately require
verified humans where current BitGov governance establishes that
requirement. Governed applicability, not architectural universal.

F3. Invariants:

```text
HUMAN FRANCHISE MODEL != UNIVERSAL FUTURE FRANCHISE MODEL
CLOSE-SNAPSHOT DENOMINATOR must not be architecture-selected unless governed
```

F4. If required franchise/denominator semantics cannot be established
→ UNRESOLVED.

## G. ORDINARY DECISION — NO POLICY SELECTION

G1. DB-I1 chooses no ordinary adoption threshold, participation/quorum
policy, or voting formula beyond preserving canonical values in
§C / §E.

G2. Ordinary authorization requires: competent decision-maker per §L,
applicable domain competence per §M, eligible franchise + denominator
rule where required per §F, applicable adoption rule satisfied, no
BLOCKED constitutional disposition where applicable per §Q, all
applicable required conditions settled for finality assessment per §R.

G3. Missing required adoption/participation rule → UNRESOLVED. No
default approval, no default DENIED.

## H. HIGH-IMPACT PANEL VALIDITY — CANONICAL FACT PRESERVED

H1. Current canon already establishes for the relevant high-impact
review class:

```text
10 CITIZENS + AI ADVOCATES
```

Preserved as `CURRENT CANONICAL COMPOSITION FACT`. Do not describe
the canonical ten-citizen fact as an undecided DB-I1 policy.

H2. Distinguish:

```text
CANONICAL COMPOSITION:
10 citizen seats + AI advocate participation

GOVERNED / UNRESOLVED MECHANICS:
advocate count if required
advocate decisional authority
presence quorum
voting quorum
adoption rule
minimum affirmative rule
abstention
recusal / vacancy
selection
eligibility
```

H3. Do NOT infer from §H1: AI advocate vote, AI advocate weight, AI
advocate count, quorum, adoption threshold, abstention effect,
eligibility, selection method, unless independently governed.

H4. Generic capability where applicable governed panel rule uses them:

```text
MEMBERSHIP-RELATIVE MINIMUM
MINIMUM AFFIRMATIVE FLOOR
DENOMINATOR RULE
ABSTENTION EFFECT
```

Normative rule:

```text
OPTIONAL GOVERNED PANEL VALIDITY / ADOPTION CONSTRAINT
```

DB-I1 does NOT mandate every panel employ anti-shrink. A decision is
UNRESOLVED only if the applicable governed panel rule requires such a
constraint and its required value/rule cannot be established.

H5. Panel logic:

```text
PANEL REQUIRED + APPLICABLE RULE MISSING → UNRESOLVED
PANEL NOT_APPLICABLE → no defect
APPLICABLE + REQUIRED CONSTRAINT VALUE UNESTABLISHABLE → UNRESOLVED
```

## I. PANEL SELECTION

I1. `SELECTION_PROVENANCE` neutral, required where panel selection is
part of authority basis. It does not select method. Selection method
remains governed.

I2. Generic support where applicable:

```text
ELIGIBILITY RULE
INELIGIBILITY RULE
RECUSAL RULE
VACANCY RULE
```

I3. No universal `ineligibility set`, no universal
`proposer/executor ineligible`. DB-I1 decides no membership. Actual
exclusions are governed policy.

## J. PRINCIPAL / REPRESENTATIVE

J1. Preserved:

```text
PRINCIPAL != REPRESENTATIVE
STANDING BELONGS TO PRINCIPAL
REPRESENTATIVE IDENTITY DOES NOT ALTER STANDING
```

J2. Where representation participates, distinguish:

```text
PRINCIPAL IDENTITY
REPRESENTATIVE IDENTITY
REPRESENTATION BASIS / MANDATE
REPRESENTATION PROVENANCE
```

J3. Representation without applicable basis/provenance where required
→ UNRESOLVED. `DIRECT COMMUNICATION != SCIENTIFIC INFERENCE`;
neither substitutes for mandate.

J4. Main Architect adjudication preserved:

```text
ECOLOGICAL PRINCIPAL != REPRESENTATIVE
STANDING BELONGS TO PRINCIPAL
UNIVERSAL BIOLOGICAL REPRESENTATION: ACCEPTED CROSS-SYSTEM DOCTRINE DIRECTION
```

Compatibility only; decides no future BIOREP mechanics.

## K. ECOLOGICAL / CULTURAL BOUNDARY

K1. Preserved:

```text
NO ECOLOGICAL-VOTE ASSUMPTION
DIRECT COMMUNICATION != SCIENTIFIC INFERENCE
```

K2. DB-I1 neither creates nor prohibits ecological voting mechanics.
Human trigger semantics in §F define no future ecological franchise.

K3. BIOREP-A1 and LIFE-A1 remain RECORDED / NOT ACTIVE. No activation,
no dependency, no pre-authorization.

## L. TIER COMPETENCE — GENERIC MINIMUM ONLY

L1. Deleted as normative: smallest-effective-scale as machine
presumption; enumerated higher-tier jurisdiction conditions;
no-preemption rule; forum-shopping prohibition. Subsidiarity remains
canon context only.

L2. Generic minimum:

```text
TIER / GOVERNANCE SCOPE
COMPETENCE FINDING
COMPETENCE AUTHORITY BASIS
DECISION SCOPE
CONFLICT STATE
ESCALATION STATE
RESOLUTION BASIS
```

L3. Machine question only: `Is this decision-maker competent under an
applicable legitimate governance rule?` If competence required and not
legitimately established → UNRESOLVED.

## M. DOMAIN COMPETENCE — NO RESOLUTION POLICY

M1. Withdrawn as normative unless independently established as governed
rules: `domains are tags not silos; smallest-tier-covering;
joint-or-escalated procedure`.

M2. Generic surface:

```text
DOMAIN IDENTITIES
APPLICABLE DOMAIN(S)
DOMAIN COMPETENCE FINDING
OVERLAP STATE
CONFLICT STATE
RESOLUTION BASIS
```

M3. DB-I1 chooses no resolution mechanism. Unresolved required domain
competence/conflict → UNRESOLVED.

## N. APPEAL

N1. FILED/PENDING alone determines neither revocation nor continued
effectiveness, neither AUTHORIZED nor DENIED alteration.

N2. Applicable governed appeal effect required; missing where required
→ UNRESOLVED. Effect represented separately per §W.

## O. ESCALATION

O1. No automatic REMAINS_EFFECTIVE / STAYED / default effect.

O2. Applicable governed escalation effect required; missing where
required → UNRESOLVED.

## P. CRISIS / UNPRECEDENTED-SITUATION APPROVAL

P1. Canonical human approval preserved: §C item 4 trigger initiates
Unprecedented-Situation process; action requires human approval under
applicable governed rule. Five-stage ritual is context, not machine
formalism beyond trigger + competence + approval + effect.

P2. Approval quorum/mechanics, measurement window, interaction rules
are deferred operational details per §AB, not DB-I1 selections. No
invented quorum/threshold.

P3. Missing applicable approval rule or missing approval where required
→ UNRESOLVED.

## Q. CONSTITUTIONAL APPLICABILITY AND DISPOSITION

Q1. No universal disposition requirement. Separate:

```text
CONSTITUTIONAL APPLICABILITY
from
CONSTITUTIONAL DISPOSITION
```

Q2. Applicability: `NOT_APPLICABLE / APPLICABLE`; if applicability
unestablishable where required → UNRESOLVED.

Q3. Where applicable, disposition: `ADMISSIBLE / BLOCKED / UNRESOLVED`.
Preserved fail-closed rules:

```text
NO KNOWN PROHIBITION != ADMISSIBLE
NO CONSTITUTIONAL OVERRIDE UNLESS EXPLICITLY AUTHORIZED
```

Q4. Governed applicability process may establish NOT_APPLICABLE without
manufacturing ADMISSIBLE judgment. No constitutional procedure invented.

## R. FINALITY — APPLICABILITY-SENSITIVE, NO CAPABILITY GRANT

R1. Per-requirement evaluation for participation, panel validity,
review, appeal per §N, escalation per §O, constitutional evaluation
per §Q, representation per §J, crisis approval per §P, other governed
prerequisites:

```text
NOT_APPLICABLE
REQUIRED_AND_SATISFIED
REQUIRED_AND_UNRESOLVED
```

R2. Finality means every applicable required governance condition is
sufficiently settled. It does NOT mean every possible subsystem
participated.

R3. Preserved distinction:

```text
AUTHORIZATION OUTCOME
!=
FINALITY
!=
EXECUTION / RELIANCE EFFECT
```

`AUTHORIZED + NOT_FINAL` may be representable if legitimate governance
permits such intermediate state. It does NOT imply `PERMISSION TO
EXECUTE`. If execution/reliance requires finality and finality absent,
execution permission is unavailable per applicable governed rule.

## S. LIFECYCLE — SUPERSESSION / REVOCATION / INVALIDATION

S1. Restored verified distinction:

```text
SUPERSESSION: a later valid authority basis replaces an earlier valid
authority basis

REVOCATION: valid authority is affirmatively withdrawn according to its
governed effective transition

INVALIDATION: a determination that a purported authority basis was not
valid under the applicable governing rules
```

S2. For invalidation: `HISTORICAL RECORD MUST NOT BE REWRITTEN`, but
historical reconstruction must represent that the purported basis
existed AND was later determined not to have been valid under
applicable rules.

S3. Do NOT invent retroactive punishment, retroactive remedy, automatic
reversal of downstream effects, or substantive legal consequences.

S4. Therefore:

```text
INVALIDATION != REVOCATION
INVALIDATION != HISTORY DELETION
```

## T. GOVERNED STATE — SEMANTIC MINIMUM RESTORED

T1. The governed state at evaluation point S must be capable of
establishing, where applicable:

```text
GOVERNED-STATE IDENTITY / REFERENCE
APPLICABLE RULE IDENTITIES + VERSIONS
RULE APPLICABILITY / EFFECTIVE STATE
DECISION / DISPOSITION STATE
DECISION SCOPE
COMPETENCE FINDINGS + AUTHORITY BASIS
FRANCHISE / PANEL / PARTICIPATION STATE where applicable
PRINCIPAL / REPRESENTATIVE / MANDATE where representation participates
APPEAL STATE + EFFECT where applicable
ESCALATION STATE + EFFECT where applicable
CONSTITUTIONAL APPLICABILITY + DISPOSITION where applicable
FINALITY STATE
LIFECYCLE STATE
TEMPORAL APPLICABILITY
AUTHORITY LINEAGE
```

This is semantic state, not storage design.

T2. Explicitly excluded as normative requirements unless a future
persistence specification independently uses such representations:

```text
Git SHA
Git tree
SCM branch
hash requirement
ledger height
state root
chain ID
database ID
IPFS CID
storage key
```

T3. Invariants:

```text
GOVERNED-STATE IDENTITY != SCM IDENTITY
SEMANTIC RECONSTRUCTABILITY != MANDATORY HASH-BASED REPRESENTATION
```

T4. Purpose is `AUTHORIZATION RECONSTRUCTION`, not implementation
provenance for its own sake. A machine result must be reconstructable
sufficiently to answer: Which legitimate rules applied? Why did they
apply? Which authority established them? What governance state existed
at evaluation? What decision/process state existed? What
representation/competence/lifecycle conditions mattered? What lineage
grounded the result?

## U. GOVERNED-RULE MODEL — CONDITIONAL APPLICABILITY

U1. Minimum relation:

```text
RULE IDENTITY
AUTHORITY
SCOPE
DECISION CLASS
APPLICABILITY
VERSION
EFFECTIVE STATE
LINEAGE
```

U2. `REQUIRED APPLICABLE RULE MISSING → UNRESOLVED` while `RULE NOT
APPLICABLE` creates no defect. Prevents
`everything-unspecified-everywhere → everything-UNRESOLVED-forever`.

U3. `MUST-DEFINE != MUST-POPULATE`. Generic surface may be complete
while governed values absent, provided absence yields UNRESOLVED where
required and applicable.

## V. AUTHORITY OWNERSHIP AND NO-HYDRA

V1. Preserved:

```text
BITGOV-GOVERNED LEGITIMACY
```

as legitimacy/authorization owner. Current canon emphasis on human
democratic governance is context, not architectural exclusivity. No
human-exclusive architectural root. No new authority domain.

V2. Preserved:

```text
MACHINE / AGI APPLIES LEGITIMATELY GOVERNED RULES
MACHINE / AGI DOES NOT SELF-AUTHOR LEGITIMACY
```

Current human authorship is canon context. Generic DB-I1 remains
compatible with future legitimate representation without
pre-authorizing it.

V3. Preserved:

```text
COGNITION != AUTHORITY
REPRESENTATION != AUTHORITY
MACHINE DERIVATION != LEGITIMACY
```

V4. No parallel lawgivers. All authority claims require lineage to
legitimate governed rule. Unlineaged authority → UNRESOLVED (or DENIED
/ NO-GOVERNED-DECISION per applicable evaluation, never assumed
AUTHORIZED).

## W. MACHINE-SURFACE OUTCOME MODEL / READINESS

W1. Surface explicitly supports at minimum:

```text
AUTHORIZATION OUTCOME: AUTHORIZED / DENIED / NO-GOVERNED-DECISION / UNRESOLVED
FINALITY: separate applicability-sensitive state per §R
CONSTITUTIONAL STATE: where applicable per §Q
APPEAL / ESCALATION EFFECT: where applicable per §N / §O
LIFECYCLE: where applicable per §S
AUTHORITY LINEAGE per §U / §V
GOVERNED-STATE MINIMUM per §T
```

W2. `BLOCKED` must not appear as top-level replacement for `DENIED`.

W3. Ready when trigger typing per §C / §D, governed-rule relation per
§U, franchise parameters per §F, panel constraints per §H / §I,
competence states per §L / §M, appeal/escalation effects per §N / §O,
crisis approval per §P, constitutional per §Q, finality plus
execution-effect separation per §R, lifecycle per §S, neutral state
per §T are implementably representable with UNRESOLVED fail-closed
and lineage. Readiness requires no populated operational values beyond
canonical values in §C / §E / §H1.

## X. FAIL-CLOSED UNRESOLVED LOGIC

X1. UNRESOLVED is deterministic epistemic state. UNRESOLVED != DENIED,
!= AUTHORIZED, != abstention, != stay. No default execution effect
from UNRESOLVED.

## Y. NON-ACTIVATION AND BOUNDARIES

Y1. No ecological franchise defined. No cultural-assimilation rule. No
constitutional procedure invented. No persistence selected. No
punishment/remedy doctrine.

Y2. BIOREP-A1 / LIFE-A1 RECORDED / NOT ACTIVE confirmed.

## Z. CLASSIFICATION CLAIM

Z1. Claimed for verifier to test:
`BITGOV_DECISION_BASIS_NORMATIVE_PROPOSAL_COMPLETE` is permitted if
generic architecture complete while substantive governed operational
details remain intentionally unresolved per §AB, with canonical values
preserved per §C / §E / §H1 and no policy leak per §AA.

---

## AA. CORRECTIONS FROM v5

AA1. Restored canonical high-impact panel composition fact: `10
CITIZENS + AI ADVOCATES` preserved as CURRENT CANONICAL COMPOSITION
FACT per §H1; prohibited inference of advocate vote/weight/count,
quorum, adoption, abstention, eligibility, selection method unless
independently governed; split CANONICAL COMPOSITION from GOVERNED /
UNRESOLVED MECHANICS per §H2.

AA2. Corrected AB panel deferral: narrowed broad `panel size` deferral;
§AB preserves `high-impact panel: 10 citizens + AI advocates` as
canonical and defers only missing mechanics listed in §AB2(h).

AA3. Restored governed-state semantic minimum per §T1–T4: identity /
reference, rule identities + versions, applicability / effective
state, decision/disposition state, scope, competence + authority,
franchise/panel/participation where applicable, principal /
representative / mandate where applicable, appeal/escalation state +
effect where applicable, constitutional applicability + disposition
where applicable, finality, lifecycle, temporal applicability,
lineage; plus reconstruction purpose and explicit persistence
exclusions and invariants
`GOVERNED-STATE IDENTITY != SCM IDENTITY` and
`SEMANTIC RECONSTRUCTABILITY != MANDATORY HASH-BASED REPRESENTATION`.

AA4. Internal reference audit completed per §AD; repaired v5 drift
including malformed finality/effect pointer, appeal/escalation section
pointers, and tier/domain/constitutional/finality pointers; all
references re-anchored to v6 letters §A–§Z.

AA5. No architecture reopened: authorization outcomes per §B,
thresholds per §C, principal/representative and biological boundary
per §J / §K, finality/execution separation per §R, lifecycle per §S,
authority ownership per §V all preserved from v5.

## AB. NORMATIVE POLICY CHOICES DEFERRED

AB1. CURRENT CANONICAL — NOT deferred as values:
(a) 10% contentious-issue scope/value per §C; (b) 10% integration
scope/value per §C; (c) 5% feedback scope/value per §C; (d) 1%
crisis-override scope/value per §C; (e) high-impact panel: 10 citizens
+ AI advocates per §H1.

AB2. DEFERRED MACHINE-OPERATIONAL DETAILS — absence where required and
applicable → UNRESOLVED:
(a) human franchise denominator mechanics per trigger; (b) snapshot /
measurement-window / time-window semantics; (c) signature-validity
rules; (d) operational applicability details and scope boundaries;
(e) trigger interaction rules; (f) crisis/unprecedented approval
mechanics/quorum including human-approval operationalization;
(g) ordinary adoption formulas beyond canonical triggers where
governed rules required; (h) AI advocate count where required, AI
advocate decisional standing, quorum values, adoption values,
anti-shrink/minimum affirmative policy, abstention mechanics,
selection mechanics, eligibility / recusal / vacancy rules, other
composition mechanics not established by canon; (i) tier competence
operational rules, preemption, forum-shopping, higher-tier
jurisdiction conditions; (j) domain overlap/conflict resolution
mechanism; (k) constitutional applicability rules and
admissibility/override criteria specifics; (l) appeal/escalation
routing and suspensive effects per class; (m) finality prerequisites
per class and execution/reliance effect rules; (n) lifecycle authority
and transition specifics excluding invented retroactivity;
(o) ecological franchise/weighting/mandate (future BIOREP/LIFE scope).

## AC. VERIFICATION ARTIFACT IDENTITY

```text
CANDIDATE_ID: BITGOV-DB-I1-NORMATIVE-v6
BASE: C:/Git/Bitgov main 8badfe421557fb562e5bb2f28d83af69359214b3
TREE: bbe67c3b52b17afe65709d528d7518ddb0e0e2e1 / clean (as last verified)
PREDECESSOR: BITGOV-DB-I1-NORMATIVE-v5 (CORRECTION REQUIRED, NO BLOCK)
SUPPLY RULE: NEXT INDEPENDENT VERIFIER MUST RECEIVE THIS EXACT v6 TEXT
UNCHANGED. Classification/name alone insufficient.
VERIFICATION TARGET IDENTITY != VERIFICATION TARGET AVAILABILITY.
PROPOSED CLASSIFICATION FOR VERIFIER TO TEST:
BITGOV_DECISION_BASIS_NORMATIVE_PROPOSAL_COMPLETE
(permitted only if no policy leak, no regression per §AA, §AB correctly
scoped, outcomes per §B / §W consistent)
ALTERNATIVES: BITGOV_DECISION_BASIS_NORMATIVE_PROPOSAL_PARTIAL if generic
gaps remain; BITGOV_DECISION_BASIS_NORMATIVE_PROPOSAL_BLOCKED if
structural/activation violation.
PUBLICATION: NONE. IMPLEMENTATION: NONE.
BIOREP-A1 / LIFE-A1: RECORDED / NOT ACTIVE.
DISPATCH: NONE.
```

## AD. INTERNAL REFERENCE AUDIT

AD1. Scope: all § references, section-letter references, “see/per”
references, AA correction references, AB references, AC references
audited against assembled v6 letters §A–§Z plus §AA–§AD.

AD2. Known drift corrected:
- v5 malformed `Section Q/R effect rules in H` removed; invariant
stated directly in §B4 with correct pointer to §R.
- Appeal/escalation pointer corrected to §N / §O everywhere
(including §C3, §R1, §W1); no remaining M/N pointer.
- Tier/domain/constitutional/finality pointers corrected to
§L / §M / §Q / §R everywhere (including §G2, §R1, §W3).
- Panel pointers corrected to §H / §I; franchise to §F; crisis to §P;
lifecycle to §S; governed-state to §T; governed-rule to §U; authority
to §V; outcome/readiness to §B / §W.

AD3. Full self-audit result:

```text
all internal section references checked
all references resolved
no stale v4/v5 section pointers remain
```

AD4. No ambiguous reference remains. If verifier finds any dangling
pointer, that finding overrides §AD3 and must be reported as defect;
no guessing was used to suppress such finding.

## FINAL CLASSIFICATION

```text
BITGOV_DECISION_BASIS_NORMATIVE_PROPOSAL_COMPLETE
```

Basis: v6 restores canonical panel fact, restores governed-state
minimum, repairs references, preserves all settled v5 architecture
(authorization vocabulary, four thresholds, generic trigger above
canon, lifecycle, legitimacy, no self-authorship, finality/execution
separation, leakage fixes) while substantive governed operational
details remain intentionally deferred per §AB with fail-closed
UNRESOLVED semantics. No publish, no implement, no dispatch, no
BIOREP-A1 / LIFE-A1 activation.
