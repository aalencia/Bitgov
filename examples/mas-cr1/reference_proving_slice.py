"""BitGov MAS-I1 concrete-representation proving slice (reference, non-normative).

Proving-harness only. Python 3, standard library + ``jsonschema`` (Draft
2020-12 structural validation). This module implements:

* structural validation (JSON Schema Draft 2020-12)
* semantic validation (closed enums, versions, conditional presence,
  cross-field consistency)
* the deterministic final-reliance function G0-G9
* the proving-only reference GWO binder (exact binding, no authorization
  created)
* the proving-only reference Aegis checker (narrowing/subset law, no
  authorization created)

Authority boundaries preserved throughout::

    COGNITION != AUTHORITY, AUTHORITY != EXECUTION,
    AUTHORIZATION != CAPABILITY, CAPABILITY != EXECUTION,
    EXECUTION != EVIDENCE.

GWO MUST NOT create authorization. AEGIS MUST NOT create authorization.
EXECUTION MUST NOT self-authorize.

Opaque-identity rule: exact equality of the parsed Unicode scalar sequence
(Python ``str`` equality, which compares code points). No NFC/NFKC, no case
folding, no trimming, no locale normalization anywhere in this module.
"""

from __future__ import annotations

import copy
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - exercised only when dep missing
    Draft202012Validator = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Closed constants (mechanical transcription of the tranche specification)
# ---------------------------------------------------------------------------

MAS_CR1_VERSION_EXPECTED = "1"
SCHEMA_VERSION_EXPECTED = "1"

AUTHORIZATION_OUTCOMES = frozenset(
    {"AUTHORIZED", "DENIED", "NO-GOVERNED-DECISION", "UNRESOLVED"}
)
CONSTITUTIONAL_APPLICABILITY = frozenset(
    {"NOT_APPLICABLE", "APPLICABLE", "UNRESOLVED"}
)
CONSTITUTIONAL_DISPOSITIONS = frozenset({"ADMISSIBLE", "BLOCKED", "UNRESOLVED"})
FINALITY_REQUIREMENT_STATES = frozenset(
    {"NOT_APPLICABLE", "REQUIRED_AND_SATISFIED", "REQUIRED_AND_UNRESOLVED"}
)
FINALITY_AGGREGATES = frozenset({"FINAL", "NOT_FINAL"})
LIFECYCLE_STATES = frozenset(
    {"ACTIVE", "SUPERSEDED", "REVOKED", "INVALIDATED", "EXPIRED"}
)
EXECUTION_RELIANCE_EFFECTS = frozenset(
    {
        "RELIANCE_PERMITTED",
        "RELIANCE_PROHIBITED",
        "EFFECT_UNRESOLVED",
        "EFFECT_NOT_APPLICABLE",
    }
)
GOVERNED_PROCESS_EFFECTS = frozenset(
    {"NOT_APPLICABLE", "UNRESOLVED", "ESTABLISHED"}
)
RULE_APPLICABILITY = frozenset({"APPLICABLE", "NOT_APPLICABLE", "UNRESOLVED"})
CURRENCY_STATES = frozenset(
    {"CURRENCY_CURRENT", "CURRENCY_STALE", "CURRENCY_UNKNOWN_REQUIRED"}
)
AGENT_COMPARISON_METHODS = frozenset({"OPAQUE_EXACT", "GOVERNED_RESOLVER"})
PREDICATE_VALUES = frozenset({"TRUE", "FALSE", "UNRESOLVED"})
GOVERNED_ABSENCE_FINDINGS = frozenset(
    {"GOVERNED_ABSENCE_FOUND", "GOVERNED_ABSENCE_UNRESOLVED"}
)

PREDICATE_NAMES = (
    "authorization_bounds_exist",
    "representation_participates",
    "agent_specific",
    "appeal_applicability",
    "escalation_applicability",
    "governed_basis_exists",
    "evaluation_had_scope",
    "governed_temporal_rules_apply",
)

BINDING_LEGS = ("principal", "action", "resource", "context", "scope")

# TEST_FIXTURE_ONLY constraint subtype. Harness-only: NOT a normative BitGov
# enum, NOT production policy, NOT governance architecture. Exists solely so
# the reference Aegis checker can demonstrate consuming a carried enforcement
# constraint instead of inventing one.
TEST_ONLY_CONSTRAINT_TYPE = "TEST_FIXTURE_ONLY_IDENTITY_ALLOWLIST"

# Reliance verdicts (M-02 renaming deferred: these exact names retained).
VERDICT_PERMIT = "PERMIT"
VERDICT_PROHIBIT = "PROHIBIT"
VERDICT_NO_RELIANCE = "NO_RELIANCE_UNRESOLVED"
VERDICT_NOT_APPLICABLE = "NOT_APPLICABLE"

# RFC3339 timestamp with mandatory explicit timezone/offset. No TTL, polling,
# or clock policy is specified or implemented.
_RFC3339_EXPLICIT_TZ = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
)

# ---------------------------------------------------------------------------
# Schema loading
# ---------------------------------------------------------------------------

_SCHEMA_CACHE: Optional[Dict[str, Any]] = None


def schema_path() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(
        os.path.join(here, "..", "..", "specs",
                     "bitgov-machine-authorization-projection-v1.schema.json")
    )


def load_schema() -> Dict[str, Any]:
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is None:
        with open(schema_path(), "r", encoding="utf-8") as fh:
            _SCHEMA_CACHE = json.load(fh)
    return _SCHEMA_CACHE


def require_jsonschema() -> None:
    if Draft202012Validator is None:  # pragma: no cover
        raise RuntimeError(
            "jsonschema package is required for Draft 2020-12 validation "
            "(see requirements.txt). Refusing to substitute a homemade "
            "approximate schema engine."
        )


# ---------------------------------------------------------------------------
# Structural validation (G0, part 1)
# ---------------------------------------------------------------------------

def validate_structural(projection: Any) -> Tuple[bool, List[str]]:
    """JSON-Schema structural check. Unknown fields rejected here."""
    require_jsonschema()
    validator = Draft202012Validator(load_schema())
    errors = sorted(
        validator.iter_errors(projection), key=lambda e: list(e.path)
    )
    messages = [
        "STRUCTURAL_MALFORMED at '%s': %s"
        % ("/".join(str(p) for p in e.absolute_path), e.message)
        for e in errors
    ]
    return (len(messages) == 0, messages)


# ---------------------------------------------------------------------------
# Semantic validation (G0, part 2)
# ---------------------------------------------------------------------------

def _check_enum(value: Any, allowed: frozenset, where: str,
                errors: List[Tuple[str, str]]) -> None:
    if value not in allowed:
        errors.append(
            ("UNKNOWN_REQUIRED",
             "UNKNOWN_REQUIRED at '%s': unrecognized enum member %r" % (where, value))
        )


def validate_semantic(projection: Dict[str, Any]) -> Tuple[bool, str, List[str]]:
    """Closed semantic checks. Returns (passed, classification, errors).

    Classification priority: VERSION_INCOMPATIBLE > UNKNOWN_REQUIRED >
    SEMANTIC_INCONSISTENT. Caller must run structural validation first.
    """
    problems: List[Tuple[str, str]] = []

    # -- versions: exact match, else VERSION_INCOMPATIBLE (slice-1 rule) --
    if projection.get("mas_cr1_version") != MAS_CR1_VERSION_EXPECTED:
        problems.append(
            ("VERSION_INCOMPATIBLE",
             "VERSION_INCOMPATIBLE: mas_cr1_version %r != expected %r"
             % (projection.get("mas_cr1_version"), MAS_CR1_VERSION_EXPECTED))
        )
    if projection.get("schema_version") != SCHEMA_VERSION_EXPECTED:
        problems.append(
            ("VERSION_INCOMPATIBLE",
             "VERSION_INCOMPATIBLE: schema_version %r != expected %r"
             % (projection.get("schema_version"), SCHEMA_VERSION_EXPECTED))
        )

    # -- closed enum sets: unknown member -> UNKNOWN_REQUIRED / no reliance --
    _check_enum(projection.get("authorization_outcome"), AUTHORIZATION_OUTCOMES,
                "authorization_outcome", problems)
    _check_enum(projection.get("constitutional_applicability"),
                CONSTITUTIONAL_APPLICABILITY,
                "constitutional_applicability", problems)
    if "constitutional_disposition" in projection:
        _check_enum(projection.get("constitutional_disposition"),
                    CONSTITUTIONAL_DISPOSITIONS,
                    "constitutional_disposition", problems)
    _check_enum(projection.get("lifecycle_state"), LIFECYCLE_STATES,
                "lifecycle_state", problems)
    _check_enum(projection.get("execution_reliance_effect"),
                EXECUTION_RELIANCE_EFFECTS,
                "execution_reliance_effect", problems)
    if "finality_aggregate" in projection:
        _check_enum(projection.get("finality_aggregate"), FINALITY_AGGREGATES,
                    "finality_aggregate", problems)
    for i, req in enumerate(projection.get("finality_vector", [])):
        if isinstance(req, dict):
            _check_enum(req.get("state"), FINALITY_REQUIREMENT_STATES,
                        "finality_vector[%d].state" % i, problems)
    for i, rule in enumerate(projection.get("rules_relied_upon", [])):
        if isinstance(rule, dict):
            _check_enum(rule.get("applicability"), RULE_APPLICABILITY,
                        "rules_relied_upon[%d].applicability" % i, problems)
    for i, evidence in enumerate(projection.get("absence_evidence", [])):
        if isinstance(evidence, dict):
            _check_enum(evidence.get("finding"), GOVERNED_ABSENCE_FINDINGS,
                        "absence_evidence[%d].finding" % i, problems)
    for key in ("appeal_effect", "escalation_effect"):
        if key in projection and isinstance(projection[key], dict):
            _check_enum(projection[key].get("effect"), GOVERNED_PROCESS_EFFECTS,
                        "%s.effect" % key, problems)
    temporal = projection.get("temporal_evaluation_and_currency", {})
    if isinstance(temporal, dict):
        _check_enum(temporal.get("currency_state"), CURRENCY_STATES,
                    "temporal_evaluation_and_currency.currency_state", problems)
    agent = projection.get("execution_agent_identity")
    if isinstance(agent, dict):
        _check_enum(agent.get("comparison_method"), AGENT_COMPARISON_METHODS,
                    "execution_agent_identity.comparison_method", problems)

    # -- predicate assertions: shape already structural; check semantics --
    predicates: Dict[str, Any] = projection.get("predicate_assertions", {})
    if isinstance(predicates, dict):
        for name in PREDICATE_NAMES:
            assertion = predicates.get(name)
            if not isinstance(assertion, dict):
                continue  # structural layer reports the malformation
            _check_enum(assertion.get("value"), PREDICATE_VALUES,
                        "predicate_assertions.%s.value" % name, problems)
            if assertion.get("basis_unknown") is True and assertion.get("value") != "UNRESOLVED":
                problems.append(
                    ("SEMANTIC_INCONSISTENT",
                     "SEMANTIC_INCONSISTENT: predicate_assertions.%s "
                     "basis_unknown=true permitted only when value == UNRESOLVED"
                     % name)
                )

    def pred(name: str) -> Any:
        a = predicates.get(name)
        return a.get("value") if isinstance(a, dict) else None

    # -- conditional presence: decided FROM predicate values, never from
    #    field presence, caller guess, or GWO/Aegis reconstruction --
    def require_iff(field: str, present: bool, predicate_value: Any,
                    predicate_name: str) -> None:
        if predicate_value == "TRUE" and not present:
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: '%s' required because "
                 "predicate_assertions.%s == TRUE (missing required semantic; "
                 "fail closed)" % (field, predicate_name))
            )
        elif predicate_value in ("FALSE", "UNRESOLVED") and present:
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: '%s' present while "
                 "predicate_assertions.%s == %s (conditional presence is "
                 "decided from predicates, not field presence)"
                 % (field, predicate_name, predicate_value))
            )

    # -- constitutional presence is decided from applicability, whose
    #    vocabulary (APPLICABLE / NOT_APPLICABLE / UNRESOLVED) differs from
    #    the TRUE/FALSE predicate vocabulary handled by require_iff --
    applicability = projection.get("constitutional_applicability")
    if applicability == "APPLICABLE" and "constitutional_disposition" not in projection:
        problems.append(
            ("SEMANTIC_INCONSISTENT",
             "SEMANTIC_INCONSISTENT: 'constitutional_disposition' required "
             "because constitutional_applicability == APPLICABLE (missing "
             "required semantic; fail closed)")
        )
    elif (applicability in ("NOT_APPLICABLE", "UNRESOLVED")
            and "constitutional_disposition" in projection):
        problems.append(
            ("SEMANTIC_INCONSISTENT",
             "SEMANTIC_INCONSISTENT: 'constitutional_disposition' present "
             "while constitutional_applicability == %s" % applicability)
        )
    require_iff("constraints", "constraints" in projection,
                pred("authorization_bounds_exist"), "authorization_bounds_exist")
    require_iff("representation_binding", "representation_binding" in projection,
                pred("representation_participates"), "representation_participates")
    require_iff("execution_agent_identity", "execution_agent_identity" in projection,
                pred("agent_specific"), "agent_specific")
    require_iff("appeal_state", "appeal_state" in projection,
                pred("appeal_applicability"), "appeal_applicability")
    require_iff("appeal_effect", "appeal_effect" in projection,
                pred("appeal_applicability"), "appeal_applicability")
    require_iff("escalation_state", "escalation_state" in projection,
                pred("escalation_applicability"), "escalation_applicability")
    require_iff("escalation_effect", "escalation_effect" in projection,
                pred("escalation_applicability"), "escalation_applicability")
    require_iff("context_scope_detail", "context_scope_detail" in projection,
                pred("evaluation_had_scope"), "evaluation_had_scope")
    temporal_bounds_present = isinstance(temporal, dict) and "temporal_bounds_reference" in temporal
    require_iff("temporal_evaluation_and_currency.temporal_bounds_reference",
                temporal_bounds_present,
                pred("governed_temporal_rules_apply"),
                "governed_temporal_rules_apply")

    # -- non-empty carriers -------------------------------------------------
    if "constraints" in projection and isinstance(projection["constraints"], list):
        if len(projection["constraints"]) == 0 and pred("authorization_bounds_exist") == "TRUE":
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: 'constraints' empty while "
                 "authorization_bounds_exist == TRUE")
            )
    if "unresolved_reasons" in projection and isinstance(projection["unresolved_reasons"], list):
        if len(projection["unresolved_reasons"]) == 0:
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: 'unresolved_reasons' present but empty")
            )
    if "rules_relied_upon" in projection and isinstance(projection["rules_relied_upon"], list):
        if len(projection["rules_relied_upon"]) == 0:
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: 'rules_relied_upon' present but empty")
            )
    if "absence_evidence" in projection and isinstance(projection["absence_evidence"], list):
        if len(projection["absence_evidence"]) == 0:
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: 'absence_evidence' present but empty")
            )

    # -- unresolved predicates require non-empty unresolved_reasons --------
    any_predicate_unresolved = any(
        isinstance(predicates.get(n), dict) and predicates[n].get("value") == "UNRESOLVED"
        for n in PREDICATE_NAMES
    ) if isinstance(predicates, dict) else False
    if any_predicate_unresolved:
        reasons = projection.get("unresolved_reasons")
        if not isinstance(reasons, list) or len(reasons) == 0:
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: predicate value UNRESOLVED present but "
                 "'unresolved_reasons' missing or empty (missing required "
                 "semantic; fail closed)")
            )

    # -- temporal representation -------------------------------------------
    if isinstance(temporal, dict):
        point = temporal.get("evaluation_point")
        if not isinstance(point, str) or not _RFC3339_EXPLICIT_TZ.match(point):
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: evaluation_point %r is not RFC3339 "
                 "with explicit timezone/offset" % (point,))
            )

    # -- finality aggregate consistency ------------------------------------
    if "finality_aggregate" in projection and isinstance(projection.get("finality_vector"), list):
        computed = compute_finality_aggregate(projection["finality_vector"])
        if projection["finality_aggregate"] != computed:
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: finality_aggregate %r disagrees with "
                 "finality_vector (computed %r)"
                 % (projection["finality_aggregate"], computed))
            )

    # -- constitutional block can never accompany reliance permission ------
    if (projection.get("constitutional_disposition") == "BLOCKED"
            and projection.get("execution_reliance_effect") == "RELIANCE_PERMITTED"):
        problems.append(
            ("SEMANTIC_INCONSISTENT",
             "SEMANTIC_INCONSISTENT: BLOCKED constitutional disposition with "
             "RELIANCE_PERMITTED execution effect")
        )

    # -- governed-basis predicate coherence (C2, closed CR1-R1) ------------
    # TRUE requires authority_lineage present AND (non-empty rules_relied_upon
    # OR an absence_evidence entry with finding GOVERNED_ABSENCE_FOUND).
    # Zero positive rule basis + lineaged governed absence uses TRUE, never
    # FALSE. FALSE requires rules, lineage, AND absence all absent.
    # UNRESOLVED is governed-unresolved (reasons required by the predicate
    # rule enforced above). The validator rejects contradictory carriers; it
    # never fabricates basis, rules, lineage, or absence determinations.
    def _has_valid_lineage(obj: Any) -> bool:
        return (
            isinstance(obj, dict)
            and all(isinstance(obj.get(m), str) and len(obj[m]) > 0
                    for m in ("rule_reference", "rule_version",
                              "authority_basis", "lineage_reference"))
        )

    basis_value = pred("governed_basis_exists")
    absence_carrier = projection.get("absence_evidence")
    has_found_absence = (
        isinstance(absence_carrier, list)
        and any(isinstance(e, dict) and e.get("finding") == "GOVERNED_ABSENCE_FOUND"
                for e in absence_carrier)
    )
    has_rules = (isinstance(projection.get("rules_relied_upon"), list)
                 and len(projection["rules_relied_upon"]) > 0)
    if basis_value == "TRUE":
        if not _has_valid_lineage(projection.get("authority_lineage")):
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: governed_basis_exists == TRUE "
                 "requires authority_lineage with a valid closed "
                 "AuthorityLineage (missing authority lineage; fail closed)")
            )
        if not has_rules and not has_found_absence:
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: governed_basis_exists == TRUE "
                 "requires non-empty rules_relied_upon OR absence_evidence "
                 "with finding GOVERNED_ABSENCE_FOUND (no established basis; "
                 "fail closed)")
            )
    elif basis_value == "FALSE":
        for member in ("rules_relied_upon", "authority_lineage",
                       "absence_evidence"):
            if member in projection:
                problems.append(
                    ("SEMANTIC_INCONSISTENT",
                     "SEMANTIC_INCONSISTENT: governed_basis_exists == FALSE "
                     "requires '%s' absent (contradictory carrier; fail "
                     "closed)" % member)
                )

    # -- AUTHORIZED requires established governed basis + lineage (C1, kept)
    # SI1-R4 Q1: every dispositional field carries lineage to a legitimate
    # BitGov-governed rule. Unlineaged authority -> UNRESOLVED, NEVER
    # AUTHORIZED. An AbsenceEvidence determination does NOT substitute for a
    # positive rule basis for AUTHORIZED. Gated on AUTHORIZED only so the
    # NO-GOVERNED-DECISION absence path and DENIED path keep their own rules.
    if projection.get("authorization_outcome") == "AUTHORIZED":
        if pred("governed_basis_exists") != "TRUE":
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: authorization_outcome AUTHORIZED "
                 "requires predicate_assertions.governed_basis_exists == TRUE "
                 "(got %r; unlineaged authority is never AUTHORIZED)"
                 % (pred("governed_basis_exists"),))
            )
        if not has_rules:
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: authorization_outcome AUTHORIZED "
                 "requires non-empty rules_relied_upon with at least one "
                 "valid governed RuleReference (missing lineage basis; fail "
                 "closed)")
            )
        if not _has_valid_lineage(projection.get("authority_lineage")):
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: authorization_outcome AUTHORIZED "
                 "requires authority_lineage with a valid closed "
                 "AuthorityLineage (missing authority lineage; fail closed)")
            )

    # -- agent resolver reference discipline -------------------------------
    if isinstance(agent, dict) and agent.get("comparison_method") in AGENT_COMPARISON_METHODS:
        if agent.get("comparison_method") == "GOVERNED_RESOLVER" and "resolver_reference" not in agent:
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: comparison_method GOVERNED_RESOLVER "
                 "requires resolver_reference")
            )
        if agent.get("comparison_method") == "OPAQUE_EXACT" and "resolver_reference" in agent:
            problems.append(
                ("SEMANTIC_INCONSISTENT",
                 "SEMANTIC_INCONSISTENT: comparison_method OPAQUE_EXACT must "
                 "not carry resolver_reference")
            )

    # -- appeal/escalation effect discipline when applicable ----------------
    for pname, ename in (("appeal_applicability", "appeal_effect"),
                         ("escalation_applicability", "escalation_effect")):
        if pred(pname) == "TRUE" and ename in projection:
            effect = projection[ename]
            if isinstance(effect, dict) and effect.get("effect") == "NOT_APPLICABLE":
                problems.append(
                    ("SEMANTIC_INCONSISTENT",
                     "SEMANTIC_INCONSISTENT: %s.effect == NOT_APPLICABLE while "
                     "%s == TRUE" % (ename, pname))
                )

    # -- TEST_FIXTURE_ONLY restriction discipline (harness-only) -----------
    if isinstance(projection.get("constraints"), list):
        for i, constraint in enumerate(projection["constraints"]):
            if not isinstance(constraint, dict):
                continue
            if constraint.get("constraint_type") == TEST_ONLY_CONSTRAINT_TYPE:
                restriction = constraint.get("restriction")
                if not isinstance(restriction, dict):
                    problems.append(
                        ("SEMANTIC_INCONSISTENT",
                         "SEMANTIC_INCONSISTENT: constraints[%d] %s requires "
                         "'restriction'" % (i, TEST_ONLY_CONSTRAINT_TYPE))
                    )
                else:
                    if restriction.get("field") not in BINDING_LEGS:
                        problems.append(
                            ("SEMANTIC_INCONSISTENT",
                             "SEMANTIC_INCONSISTENT: constraints[%d] restriction "
                             "field %r is not a binding leg"
                             % (i, restriction.get("field")))
                        )
                    permitted = restriction.get("permitted_identities")
                    if not isinstance(permitted, list) or len(permitted) == 0:
                        problems.append(
                            ("SEMANTIC_INCONSISTENT",
                             "SEMANTIC_INCONSISTENT: constraints[%d] restriction "
                             "requires non-empty permitted_identities" % i)
                        )

    if not problems:
        return True, "VALID", []
    priority = {"VERSION_INCOMPATIBLE": 0, "UNKNOWN_REQUIRED": 1,
                "SEMANTIC_INCONSISTENT": 2}
    problems.sort(key=lambda p: priority[p[0]])
    return False, problems[0][0], [message for _, message in problems]


# ---------------------------------------------------------------------------
# Finality aggregation
# ---------------------------------------------------------------------------

def compute_finality_aggregate(finality_vector: List[Dict[str, Any]]) -> str:
    """FINAL iff every requirement is NOT_APPLICABLE or REQUIRED_AND_SATISFIED."""
    for req in finality_vector:
        if req.get("state") == "REQUIRED_AND_UNRESOLVED":
            return "NOT_FINAL"
    return "FINAL"


# ---------------------------------------------------------------------------
# Final reliance function G0-G9
# ---------------------------------------------------------------------------

def _base_result(projection: Any) -> Dict[str, Any]:
    identity = projection.get("projection_identity") if isinstance(projection, dict) else None
    return {
        "projection_identity": identity,
        "structural": {"passed": False, "errors": []},
        "semantic": {"passed": False, "classification": "NOT_EVALUATED", "errors": []},
        "classification": "NOT_EVALUATED",
        "governed_result": "INTERFACE_FAILURE",
        "reliance_verdict": VERDICT_NO_RELIANCE,
        "authority_consequence": "",
        "deciding_gate": "G0",
        "gate_trace": [],
        "interface_failure": False,
    }


_CONSEQUENCE = {
    VERDICT_PERMIT: "RELIANCE_PERMITTED under exact request binding: execution may rely on this projection and nothing else; binding target is (projection_identity, parsed semantic object), never serialized bytes; GWO/Aegis create no authorization.",
    VERDICT_PROHIBIT: "RELIANCE_PROHIBITED: execution must not proceed under this projection.",
    VERDICT_NO_RELIANCE: "NO_RELIANCE: fail closed; execution must not treat this projection as permission. Governed-UNRESOLVED vs interface/consumption failure is preserved in governed_result.",
    VERDICT_NOT_APPLICABLE: "NOT_APPLICABLE: no governed decision is carried for reliance; execution must not manufacture one.",
}


def final_reliance(projection: Any,
                   attempted_use: Optional[Dict[str, Any]] = None
                   ) -> Dict[str, Any]:
    """Deterministic reference reliance function, gates G0-G9.

    ``attempted_use``, when supplied, maps each of the five binding legs to
    an attempted identity string and is compared at G3 with exact opaque
    equality. ``None`` evaluates the projection alone (G3 binding-use check
    vacuous; use the reference GWO binder for consumption-time binding).
    """
    result = _base_result(projection)
    trace = result["gate_trace"]

    def stop(gate: str, reason: str, verdict: str, governed: str,
             classification: str, interface_failure: bool) -> Dict[str, Any]:
        trace.append({"gate": gate, "outcome": "STOP", "reason": reason})
        result["deciding_gate"] = gate
        result["classification"] = classification
        result["governed_result"] = governed
        result["reliance_verdict"] = verdict
        result["authority_consequence"] = _CONSEQUENCE[verdict]
        result["interface_failure"] = interface_failure
        return result

    def note(gate: str, reason: str) -> None:
        trace.append({"gate": gate, "outcome": "PASS", "reason": reason})

    # -- G0 CONFORMANCE -----------------------------------------------------
    if not isinstance(projection, dict):
        result["structural"] = {"passed": False,
                                "errors": ["STRUCTURAL_MALFORMED: top-level projection must be a JSON object"]}
        return stop("G0", "top-level projection is not an object",
                    VERDICT_NO_RELIANCE, "INTERFACE_FAILURE",
                    "STRUCTURAL_MALFORMED", True)
    struct_passed, struct_errors = validate_structural(projection)
    result["structural"] = {"passed": struct_passed, "errors": struct_errors}
    if not struct_passed:
        result["semantic"] = {"passed": False, "classification": "NOT_EVALUATED",
                              "errors": []}
        return stop("G0", "structural validation failed (%d error(s))"
                    % len(struct_errors),
                    VERDICT_NO_RELIANCE, "INTERFACE_FAILURE",
                    "STRUCTURAL_MALFORMED", True)
    sem_passed, sem_class, sem_errors = validate_semantic(projection)
    result["semantic"] = {"passed": sem_passed, "classification": sem_class,
                          "errors": sem_errors}
    if not sem_passed:
        return stop("G0", "semantic validation failed: %s" % sem_errors[0],
                    VERDICT_NO_RELIANCE, "INTERFACE_FAILURE", sem_class, True)
    note("G0", "conformance: structural and semantic validation passed")
    result["classification"] = "VALID"

    predicates = projection["predicate_assertions"]
    outcome = projection["authorization_outcome"]

    def unresolved_stop(gate: str, reason: str) -> Dict[str, Any]:
        return stop(gate, reason, VERDICT_NO_RELIANCE, "GOVERNED_UNRESOLVED",
                    "VALID", False)

    # -- G1 LIFECYCLE -------------------------------------------------------
    if projection["lifecycle_state"] != "ACTIVE":
        return stop("G1",
                    "lifecycle_state=%s: no new reliance under that projection"
                    % projection["lifecycle_state"],
                    VERDICT_NO_RELIANCE,
                    outcome if outcome != "UNRESOLVED" else "GOVERNED_UNRESOLVED",
                    "VALID", False)
    note("G1", "lifecycle ACTIVE")

    # -- G2 CURRENCY --------------------------------------------------------
    currency = projection["temporal_evaluation_and_currency"]["currency_state"]
    if currency == "CURRENCY_STALE":
        return stop("G2", "CURRENCY_STALE: no reliance on stale evaluation",
                    VERDICT_NO_RELIANCE, outcome
                    if outcome != "UNRESOLVED" else "GOVERNED_UNRESOLVED",
                    "VALID", False)
    if currency == "CURRENCY_UNKNOWN_REQUIRED":
        return unresolved_stop("G2", "currency unknown where required: fail closed")
    if predicates["governed_temporal_rules_apply"]["value"] == "UNRESOLVED":
        return unresolved_stop("G2", "governed_temporal_rules_apply UNRESOLVED: fail closed")
    note("G2", "currency current; temporal rules resolved")

    # -- G3 REQUEST / USE BINDING -------------------------------------------
    for pname in ("representation_participates", "agent_specific",
                  "evaluation_had_scope"):
        if predicates[pname]["value"] == "UNRESOLVED":
            return unresolved_stop("G3", "%s UNRESOLVED: binding scope undecidable" % pname)
    if attempted_use is not None:
        for leg in BINDING_LEGS:
            bound = projection["request_binding"][leg]["identity"]
            attempted = attempted_use.get(leg)
            # Exact opaque equality: parsed Unicode scalar sequence only.
            if not isinstance(attempted, str) or attempted != bound:
                trace.append({"gate": "G3", "outcome": "STOP",
                              "reason": "binding mismatch on leg '%s'" % leg})
                result["deciding_gate"] = "G3"
                result["classification"] = "BINDING_MISMATCH"
                result["governed_result"] = "INTERFACE_FAILURE"
                result["reliance_verdict"] = VERDICT_NO_RELIANCE
                result["authority_consequence"] = _CONSEQUENCE[VERDICT_NO_RELIANCE]
                result["interface_failure"] = True
                return result
        note("G3", "attempted use matches exact request binding on all five legs")
    else:
        note("G3", "request binding well-formed; no attempted use supplied")

    # -- G4 CONSTITUTIONAL STATE --------------------------------------------
    applicability = projection["constitutional_applicability"]
    if applicability == "UNRESOLVED":
        return unresolved_stop("G4", "constitutional applicability UNRESOLVED")
    if applicability == "APPLICABLE":
        disposition = projection["constitutional_disposition"]
        if disposition == "UNRESOLVED":
            return unresolved_stop("G4", "constitutional disposition UNRESOLVED")
        if disposition == "BLOCKED":
            note("G4", "constitutional disposition BLOCKED (carried; reliance gated at G8)")
        else:
            note("G4", "constitutional disposition ADMISSIBLE")
    else:
        note("G4", "constitution not applicable")

    # -- G5 AUTHORIZATION OUTCOME --------------------------------------------
    if predicates["governed_basis_exists"]["value"] == "UNRESOLVED":
        return unresolved_stop("G5", "governed_basis_exists UNRESOLVED")
    if outcome == "DENIED":
        return stop("G5", "governed outcome DENIED", VERDICT_PROHIBIT,
                    "DENIED", "VALID", False)
    if outcome == "NO-GOVERNED-DECISION":
        return stop("G5", "no governed decision carried", VERDICT_NOT_APPLICABLE,
                    "NO-GOVERNED-DECISION", "VALID", False)
    if outcome == "UNRESOLVED":
        return unresolved_stop("G5", "governed outcome UNRESOLVED")
    note("G5", "governed outcome AUTHORIZED")

    # -- G6 FINALITY ----------------------------------------------------------
    for req in projection["finality_vector"]:
        if req.get("state") == "REQUIRED_AND_UNRESOLVED":
            return unresolved_stop(
                "G6", "finality requirement %r unresolved" % req.get("requirement"))
    aggregate = compute_finality_aggregate(projection["finality_vector"])
    if aggregate == "NOT_FINAL":
        return stop("G6", "finality NOT_FINAL: no permission from non-final state",
                    VERDICT_NO_RELIANCE, "AUTHORIZED", "VALID", False)
    note("G6", "finality FINAL")

    # -- G7 APPEAL / ESCALATION EFFECT ----------------------------------------
    for pname, ename in (("appeal_applicability", "appeal_effect"),
                         ("escalation_applicability", "escalation_effect")):
        if predicates[pname]["value"] == "UNRESOLVED":
            return unresolved_stop("G7", "%s UNRESOLVED" % pname)
        if predicates[pname]["value"] == "TRUE":
            if projection[ename]["effect"] == "UNRESOLVED":
                return unresolved_stop("G7", "%s UNRESOLVED where required" % ename)
            note("G7", "%s ESTABLISHED" % ename)
    note("G7", "appeal/escalation effects settled")

    # -- G8 EXECUTION RELIANCE EFFECT ------------------------------------------
    if predicates["authorization_bounds_exist"]["value"] == "UNRESOLVED":
        return unresolved_stop("G8", "authorization_bounds_exist UNRESOLVED")
    effect = projection["execution_reliance_effect"]
    if effect == "RELIANCE_PROHIBITED":
        return stop("G8", "execution reliance prohibited", VERDICT_PROHIBIT,
                    "AUTHORIZED", "VALID", False)
    if effect == "EFFECT_UNRESOLVED":
        return unresolved_stop("G8", "execution reliance effect unresolved")
    if effect == "EFFECT_NOT_APPLICABLE":
        return stop("G8", "no execution reliance effect applies",
                    VERDICT_NOT_APPLICABLE, "AUTHORIZED", "VALID", False)
    note("G8", "execution reliance permitted by carried effect")

    # -- G9 PERMIT --------------------------------------------------------------
    if projection.get("constitutional_disposition") == "BLOCKED":
        # Defensive: G0 semantic validation already rejects
        # BLOCKED + RELIANCE_PERMITTED; this is unreachable by construction.
        return stop("G9", "constitutional BLOCKED reached PERMIT gate",
                    VERDICT_NO_RELIANCE, "INTERFACE_FAILURE",
                    "SEMANTIC_INCONSISTENT", True)
    trace.append({"gate": "G9", "outcome": "PERMIT",
                  "reason": "all required gates satisfied + RELIANCE_PERMITTED"})
    result["deciding_gate"] = "G9"
    result["classification"] = "VALID"
    result["governed_result"] = "AUTHORIZED"
    result["reliance_verdict"] = VERDICT_PERMIT
    result["authority_consequence"] = _CONSEQUENCE[VERDICT_PERMIT]
    result["interface_failure"] = False
    return result


# ---------------------------------------------------------------------------
# Reference GWO binder (proving-only)
# ---------------------------------------------------------------------------

def gwo_bind(projection: Dict[str, Any],
             attempted_use: Dict[str, Any]) -> Dict[str, Any]:
    """Proving-only reference binder: exact binding, zero authorization.

    Validates the projection, compares attempted use against the exact
    request binding, checks carried temporal/agent state, rejects mismatch,
    and consumes the final reliance result. Creates no authorization,
    changes no outcome, infers no missing predicate, drops no constraint,
    widens no scope, repairs nothing, recomputes no constitutional meaning.
    Binding target: (projection_identity, parsed semantic object).
    """
    reliance = final_reliance(projection)
    if reliance["reliance_verdict"] != VERDICT_PERMIT:
        return {
            "bound": False,
            "reason": "no reliance to bind: verdict %s at %s"
                      % (reliance["reliance_verdict"], reliance["deciding_gate"]),
            "classification": reliance["classification"],
            "reliance": reliance,
            "authorization_created": False,
        }
    for leg in BINDING_LEGS:
        bound = projection["request_binding"][leg]["identity"]
        attempted = attempted_use.get(leg)
        if not isinstance(attempted, str) or attempted != bound:
            return {
                "bound": False,
                "reason": "BINDING_MISMATCH on leg '%s': attempted use does not "
                          "exactly equal bound identity (no substitution, no "
                          "widening)" % leg,
                "classification": "BINDING_MISMATCH",
                "reliance": reliance,
                "authorization_created": False,
            }
    agent = projection.get("execution_agent_identity")
    if agent is not None:
        if agent["comparison_method"] == "GOVERNED_RESOLVER":
            return {
                "bound": False,
                "reason": "UNAVAILABLE_RESOLVER: agent comparison requires a "
                          "governed resolver; none exists in the proving slice",
                "classification": "UNAVAILABLE_RESOLVER",
                "reliance": reliance,
                "authorization_created": False,
            }
        attempted_agent = attempted_use.get("agent_identity")
        if not isinstance(attempted_agent, str) or attempted_agent != agent["agent_identity"]:
            return {
                "bound": False,
                "reason": "BINDING_MISMATCH on agent_identity",
                "classification": "BINDING_MISMATCH",
                "reliance": reliance,
                "authorization_created": False,
            }
    return {
        "bound": True,
        "reason": "exact binding on (projection_identity, parsed semantic "
                  "object); carried constraints untouched; reliance consumed, "
                  "not created",
        "classification": "VALID",
        "reliance": reliance,
        "authorization_created": False,
    }


# ---------------------------------------------------------------------------
# Reference Aegis checker (proving-only)
# ---------------------------------------------------------------------------

def aegis_check(projection: Dict[str, Any],
                narrowed_capability: Dict[str, Any]) -> Dict[str, Any]:
    """Proving-only reference checker: AEGIS_NARROWED_CAPABILITY ⊆ bounds.

    Admits only when the narrowed capability exactly matches the authorized
    binding legs and satisfies every carried constraint. Unknown constraint
    subtype fails closed. Creates no authorization, grants nothing from
    NO_RELIANCE, infers no constraint, reinterprets nothing, widens nothing.
    """
    reliance = final_reliance(projection)
    if reliance["reliance_verdict"] != VERDICT_PERMIT:
        return {
            "admitted": False,
            "reason": "no permission to narrow: verdict %s at %s"
                      % (reliance["reliance_verdict"], reliance["deciding_gate"]),
            "classification": reliance["classification"],
            "reliance": reliance,
            "authorization_created": False,
        }
    if set(narrowed_capability.keys()) != set(BINDING_LEGS):
        return {
            "admitted": False,
            "reason": "narrowed capability must carry exactly the five binding "
                      "legs (no more, no fewer)",
            "classification": "BINDING_MISMATCH",
            "reliance": reliance,
            "authorization_created": False,
        }
    for leg in BINDING_LEGS:
        bound = projection["request_binding"][leg]["identity"]
        narrowed = narrowed_capability.get(leg)
        if not isinstance(narrowed, str) or narrowed != bound:
            return {
                "admitted": False,
                "reason": "narrowing violation on leg '%s': capability exceeds "
                          "authorized bounds (substitution/widening rejected)" % leg,
                "classification": "BINDING_MISMATCH",
                "reliance": reliance,
                "authorization_created": False,
            }
    for constraint in projection.get("constraints", []):
        ctype = constraint.get("constraint_type")
        if ctype == TEST_ONLY_CONSTRAINT_TYPE:
            restriction = constraint.get("restriction", {})
            field = restriction.get("field")
            if narrowed_capability.get(field) not in restriction.get("permitted_identities", []):
                return {
                    "admitted": False,
                    "reason": "carried TEST_FIXTURE_ONLY constraint not satisfied "
                              "for field '%s'" % field,
                    "classification": "CONSTRAINT_VIOLATION",
                    "reliance": reliance,
                    "authorization_created": False,
                }
        else:
            return {
                "admitted": False,
                "reason": "UNKNOWN_CONSTRAINT_SUBTYPE %r: fail closed; the "
                          "reference checker enforces only the marked "
                          "TEST_FIXTURE_ONLY harness subtype" % (ctype,),
                "classification": "UNKNOWN_CONSTRAINT_SUBTYPE",
                "reliance": reliance,
                "authorization_created": False,
            }
    return {
        "admitted": True,
        "reason": "narrowed capability within authorized bounds; carried "
                  "constraints satisfied; permission consumed, not created",
        "classification": "VALID",
        "reliance": reliance,
        "authorization_created": False,
    }


# ---------------------------------------------------------------------------
# Canonical valid-projection factory (mirrors fixtures/valid_permit.json)
# ---------------------------------------------------------------------------

CANONICAL_PROJECTION_IDENTITY = "0193e8d5-6f5a-7b1c-9d2e-3f4a5b6c7d8e"


def _lineage(determination_reference: str,
             authority: str = "bitgov:governed:basis:proving-slice-v1"
             ) -> Dict[str, Any]:
    """Closed CR1-R1 AuthorityLineage for proving fixtures."""
    return {
        "rule_reference": "bitgov:rule:reading-room-access",
        "rule_version": "2026-09-01",
        "authority_basis": authority,
        "lineage_reference": determination_reference,
    }


def _assertion(value: str, determination_reference: str,
               authority: str = "bitgov:governed:basis:proving-slice-v1",
               basis_unknown: Optional[bool] = None) -> Dict[str, Any]:
    assertion: Dict[str, Any] = {
        "value": value,
        "determination_reference": determination_reference,
        "lineage": _lineage(determination_reference, authority),
    }
    if basis_unknown is not None:
        assertion["basis_unknown"] = basis_unknown
    return assertion


def canonical_permit_projection() -> Dict[str, Any]:
    """Smallest fully-valid AUTHORIZED projection (-> PERMIT), with Aegis
    still bound by the subset/narrowing law via a carried constraint."""
    return {
        "mas_cr1_version": "1",
        "schema_version": "1",
        "projection_identity": CANONICAL_PROJECTION_IDENTITY,
        "governed_state_reference": {
            "reference": "bitgov:governed-state:proving-slice:0001"
        },
        "authorization_outcome": "AUTHORIZED",
        "request_binding": {
            "principal": {"identity": "bitgov:principal:archivist-042"},
            "action": {"identity": "bitgov:action:read-record"},
            "resource": {"identity": "bitgov:resource:record-7f3a"},
            "context": {"identity": "bitgov:context:reading-room-a"},
            "scope": {"identity": "bitgov:scope:reading-room-a.read-only"},
        },
        "constitutional_applicability": "APPLICABLE",
        "constitutional_disposition": "ADMISSIBLE",
        "finality_vector": [
            {"requirement": "constitutional-evaluation", "state": "REQUIRED_AND_SATISFIED"},
            {"requirement": "competence-finding", "state": "REQUIRED_AND_SATISFIED"},
            {"requirement": "participation", "state": "NOT_APPLICABLE"},
        ],
        "finality_aggregate": "FINAL",
        "lifecycle_state": "ACTIVE",
        "execution_reliance_effect": "RELIANCE_PERMITTED",
        "temporal_evaluation_and_currency": {
            "evaluation_point": "2026-09-30T12:00:00Z",
            "temporal_bounds_reference": "bitgov:temporal-bounds:proving-slice:0001",
            "currency_state": "CURRENCY_CURRENT",
        },
        "predicate_assertions": {
            "authorization_bounds_exist": _assertion("TRUE", "det:bounds:0001"),
            "representation_participates": _assertion("FALSE", "det:representation:0001"),
            "agent_specific": _assertion("FALSE", "det:agent:0001"),
            "appeal_applicability": _assertion("FALSE", "det:appeal:0001"),
            "escalation_applicability": _assertion("FALSE", "det:escalation:0001"),
            "governed_basis_exists": _assertion("TRUE", "det:basis:0001"),
            "evaluation_had_scope": _assertion("TRUE", "det:scope:0001"),
            "governed_temporal_rules_apply": _assertion("TRUE", "det:temporal:0001"),
        },
        "context_scope_detail": {
            "context_reference": "bitgov:context:reading-room-a",
            "scope_reference": "bitgov:scope:reading-room-a.read-only",
        },
        "constraints": [
            {
                "constraint_type": TEST_ONLY_CONSTRAINT_TYPE,
                "statement": "TEST_FIXTURE_ONLY: permit only the bound read-record action",
                "restriction": {
                    "field": "action",
                    "permitted_identities": ["bitgov:action:read-record"],
                },
            }
        ],
        "rules_relied_upon": [
            {
                "rule_identity": "bitgov:rule:reading-room-access",
                "version": "2026-09-01",
                "applicability": "APPLICABLE",
                "authority_reference": "bitgov:governed:basis:proving-slice-v1",
            }
        ],
        "authority_lineage": {
            "rule_reference": "bitgov:rule:reading-room-access",
            "rule_version": "2026-09-01",
            "authority_basis": "bitgov:governed:basis:proving-slice-v1",
            "lineage_reference": "det:basis:0001",
        },
    }


def load_projection_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def attempt_from_binding(projection: Dict[str, Any]) -> Dict[str, str]:
    """Exact-match attempted use derived from a projection's binding."""
    return {
        leg: projection["request_binding"][leg]["identity"] for leg in BINDING_LEGS
    }
