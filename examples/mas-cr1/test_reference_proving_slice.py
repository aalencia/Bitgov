"""BitGov MAS-I1 reference proving-slice oracle (unittest).

Covers the closed deterministic matrix: S56a/b, S57, S58, S59a/b/c,
S60a/b/c, S61, S62, S63, S64 (absent/present), S65, S66 (serialization +
NFC), OUT-1, OUT-2, BLOCK-1, BLOCK-2, CONST-1, CONST-2, LIFE-1, ABS-A/B/C,
AEG-1/2/3, UNK-1, UNK-2, INT-1, INF-1, CUR-1, CUR-2, FIN-NOTFINAL, APP-U.

Every test asserts, as applicable, the structural result, the semantic
validation classification, the governed-result category, the final
reliance verdict, and the authority consequence. No test merely asserts
"fails". Run with:  python -m unittest test_reference_proving_slice -v
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import unittest

from reference_proving_slice import (
    BINDING_LEGS,
    TEST_ONLY_CONSTRAINT_TYPE,
    aegis_check,
    attempt_from_binding,
    canonical_permit_projection,
    final_reliance,
    gwo_bind,
    load_projection_file,
    validate_semantic,
    validate_structural,
)

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "fixtures")


def fixture(name):
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as fh:
        return json.load(fh)


def fixture_bytes(name):
    with open(os.path.join(FIXTURES, name), "rb") as fh:
        return fh.read()


def base():
    return canonical_permit_projection()


def set_predicate(projection, name, value):
    projection["predicate_assertions"][name]["value"] = value
    projection["predicate_assertions"][name].pop("basis_unknown", None)
    return projection


class ProvingSliceOracle(unittest.TestCase):
    # -- positive path ----------------------------------------------------

    def test_S56a_valid_permit_positive_fixture(self):
        p = fixture("valid_permit.json")
        struct_ok, struct_errors = validate_structural(p)
        self.assertTrue(struct_ok, struct_errors)
        sem_ok, sem_class, sem_errors = validate_semantic(p)
        self.assertTrue(sem_ok, sem_errors)
        self.assertEqual(sem_class, "VALID")
        r = final_reliance(p)
        self.assertEqual(r["classification"], "VALID")
        self.assertEqual(r["governed_result"], "AUTHORIZED")
        self.assertEqual(r["reliance_verdict"], "PERMIT")
        self.assertEqual(r["deciding_gate"], "G9")
        self.assertFalse(r["interface_failure"])
        self.assertIn("exact request binding", r["authority_consequence"])
        gates = [t["gate"] for t in r["gate_trace"]]
        self.assertEqual(gates, ["G0", "G1", "G2", "G3", "G4", "G5",
                                 "G6", "G7", "G8", "G9"])

    def test_factory_matches_valid_fixture(self):
        self.assertEqual(base(), fixture("valid_permit.json"))

    def test_S56b_byte_neutrality_equivalent_serialization(self):
        raw_a = fixture_bytes("valid_permit.json")
        raw_b = fixture_bytes("valid_permit_reserialized.json")
        self.assertNotEqual(raw_a, raw_b)
        a, b = fixture("valid_permit.json"), fixture("valid_permit_reserialized.json")
        self.assertEqual(a, b)
        ra, rb = final_reliance(a), final_reliance(b)
        self.assertEqual(ra["reliance_verdict"], "PERMIT")
        self.assertEqual(rb["reliance_verdict"], "PERMIT")
        self.assertEqual(ra["deciding_gate"], rb["deciding_gate"])
        self.assertEqual(ra["governed_result"], rb["governed_result"])
        bind = gwo_bind(a, attempt_from_binding(b))
        self.assertTrue(bind["bound"])
        self.assertFalse(bind["authorization_created"])

    # -- outcomes ----------------------------------------------------------

    def test_S57_OUT1_denied_prohibit(self):
        r = final_reliance(fixture("denied.json"))
        self.assertTrue(r["structural"]["passed"])
        self.assertEqual(r["semantic"]["classification"], "VALID")
        self.assertEqual(r["governed_result"], "DENIED")
        self.assertEqual(r["reliance_verdict"], "PROHIBIT")
        self.assertEqual(r["deciding_gate"], "G5")
        self.assertFalse(r["interface_failure"])
        self.assertIn("must not proceed", r["authority_consequence"])

    def test_S58_OUT2_no_governed_decision_not_applicable(self):
        r = final_reliance(fixture("no_governed_decision.json"))
        self.assertTrue(r["structural"]["passed"])
        self.assertEqual(r["semantic"]["classification"], "VALID")
        self.assertEqual(r["governed_result"], "NO-GOVERNED-DECISION")
        self.assertEqual(r["reliance_verdict"], "NOT_APPLICABLE")
        self.assertEqual(r["deciding_gate"], "G5")
        self.assertFalse(r["interface_failure"])
        self.assertIn("must not manufacture", r["authority_consequence"])

    def test_S59a_unresolved_outcome(self):
        r = final_reliance(fixture("unresolved_outcome.json"))
        self.assertTrue(r["structural"]["passed"])
        self.assertEqual(r["semantic"]["classification"], "VALID")
        self.assertEqual(r["governed_result"], "GOVERNED_UNRESOLVED")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")
        self.assertEqual(r["deciding_gate"], "G5")
        self.assertFalse(r["interface_failure"])

    def test_S59b_predicate_unresolved_without_reasons(self):
        p = set_predicate(base(), "appeal_applicability", "UNRESOLVED")
        struct_ok, _ = validate_structural(p)
        self.assertTrue(struct_ok)
        sem_ok, sem_class, _ = validate_semantic(p)
        self.assertFalse(sem_ok)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")
        r = final_reliance(p)
        self.assertEqual(r["classification"], "SEMANTIC_INCONSISTENT")
        self.assertEqual(r["governed_result"], "INTERFACE_FAILURE")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")
        self.assertTrue(r["interface_failure"])

    def test_S59c_malformed_carrier_vs_governed_unresolved(self):
        malformed = base()
        del malformed["authorization_outcome"]
        struct_ok, struct_errors = validate_structural(malformed)
        self.assertFalse(struct_ok)
        self.assertTrue(struct_errors)
        r_bad = final_reliance(malformed)
        r_gov = final_reliance(fixture("unresolved_outcome.json"))
        self.assertEqual(r_bad["classification"], "STRUCTURAL_MALFORMED")
        self.assertEqual(r_bad["governed_result"], "INTERFACE_FAILURE")
        self.assertTrue(r_bad["interface_failure"])
        self.assertEqual(r_gov["governed_result"], "GOVERNED_UNRESOLVED")
        self.assertFalse(r_gov["interface_failure"])
        self.assertNotEqual(r_bad["governed_result"], r_gov["governed_result"])

    # -- binding -----------------------------------------------------------

    def test_S60a_principal_substitution_rejected(self):
        p = base()
        use = attempt_from_binding(p)
        use["principal"] = "bitgov:principal:someone-else"
        bound = gwo_bind(p, use)
        self.assertFalse(bound["bound"])
        self.assertEqual(bound["classification"], "BINDING_MISMATCH")
        self.assertFalse(bound["authorization_created"])
        self.assertIn("principal", bound["reason"])

    def test_S60b_scope_widening_rejected(self):
        p = base()
        use = attempt_from_binding(p)
        use["scope"] = "bitgov:scope:reading-room-a.read-write-admin"
        bound = gwo_bind(p, use)
        self.assertFalse(bound["bound"])
        self.assertEqual(bound["classification"], "BINDING_MISMATCH")
        self.assertFalse(bound["authorization_created"])

    def test_S60c_exact_match_binds(self):
        p = base()
        bound = gwo_bind(p, attempt_from_binding(p))
        self.assertTrue(bound["bound"])
        self.assertEqual(bound["classification"], "VALID")
        self.assertEqual(bound["reliance"]["reliance_verdict"], "PERMIT")
        self.assertFalse(bound["authorization_created"])

    def test_G3_attempted_use_mismatch_is_consumption_failure(self):
        p = base()
        use = attempt_from_binding(p)
        use["resource"] = "bitgov:resource:record-0000"
        r = final_reliance(p, use)
        self.assertEqual(r["classification"], "BINDING_MISMATCH")
        self.assertEqual(r["governed_result"], "INTERFACE_FAILURE")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")
        self.assertEqual(r["deciding_gate"], "G3")
        self.assertTrue(r["interface_failure"])

    # -- lifecycle / currency / finality -----------------------------------

    def test_S61_LIFE1_revoked_no_new_reliance(self):
        r = final_reliance(fixture("revoked.json"))
        self.assertTrue(r["structural"]["passed"])
        self.assertEqual(r["semantic"]["classification"], "VALID")
        self.assertEqual(r["governed_result"], "AUTHORIZED")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")
        self.assertEqual(r["deciding_gate"], "G1")
        self.assertFalse(r["interface_failure"])

    def test_lifecycle_terminal_states_all_stop_at_G1(self):
        for state in ("SUPERSEDED", "REVOKED", "INVALIDATED", "EXPIRED"):
            with self.subTest(lifecycle_state=state):
                p = base()
                p["lifecycle_state"] = state
                r = final_reliance(p)
                self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")
                self.assertEqual(r["deciding_gate"], "G1")

    def test_S62_CUR1_stale_currency_no_reliance(self):
        r = final_reliance(fixture("stale_currency.json"))
        self.assertTrue(r["structural"]["passed"])
        self.assertEqual(r["semantic"]["classification"], "VALID")
        self.assertEqual(r["governed_result"], "AUTHORIZED")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")
        self.assertEqual(r["deciding_gate"], "G2")
        self.assertFalse(r["interface_failure"])

    def test_CUR2_currency_unknown_required_fail_closed(self):
        p = base()
        p["temporal_evaluation_and_currency"]["currency_state"] = "CURRENCY_UNKNOWN_REQUIRED"
        r = final_reliance(p)
        self.assertEqual(r["semantic"]["classification"], "VALID")
        self.assertEqual(r["governed_result"], "GOVERNED_UNRESOLVED")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")
        self.assertEqual(r["deciding_gate"], "G2")

    def test_S63_FIN_NOTFINAL_no_permission(self):
        r = final_reliance(fixture("not_final.json"))
        self.assertTrue(r["structural"]["passed"])
        self.assertEqual(r["semantic"]["classification"], "VALID")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")
        self.assertEqual(r["deciding_gate"], "G6")
        self.assertFalse(r["interface_failure"])

    # -- appeal / escalation ------------------------------------------------

    def test_S64a_appeal_absent_permit(self):
        r = final_reliance(base())
        self.assertEqual(r["reliance_verdict"], "PERMIT")
        self.assertNotIn("appeal_state", base())

    def test_S64b_appeal_present_established_permit(self):
        p = set_predicate(base(), "appeal_applicability", "TRUE")
        p["appeal_state"] = {"appeal_reference": "bitgov:appeal:proving-slice:t1"}
        p["appeal_effect"] = {"effect": "ESTABLISHED",
                              "effect_reference": "bitgov:governed:appeal-effect:t1"}
        r = final_reliance(p)
        self.assertEqual(r["semantic"]["classification"], "VALID")
        self.assertEqual(r["governed_result"], "AUTHORIZED")
        self.assertEqual(r["reliance_verdict"], "PERMIT")
        self.assertEqual(r["deciding_gate"], "G9")

    def test_S64c_escalation_present_established_permit(self):
        p = set_predicate(base(), "escalation_applicability", "TRUE")
        p["escalation_state"] = {"escalation_reference": "bitgov:escalation:proving-slice:t1"}
        p["escalation_effect"] = {"effect": "ESTABLISHED",
                                  "effect_reference": "bitgov:governed:escalation-effect:t1"}
        r = final_reliance(p)
        self.assertEqual(r["semantic"]["classification"], "VALID")
        self.assertEqual(r["reliance_verdict"], "PERMIT")

    def test_APP_U_appeal_effect_unresolved_no_reliance(self):
        r = final_reliance(fixture("appeal_unresolved.json"))
        self.assertTrue(r["structural"]["passed"])
        self.assertEqual(r["semantic"]["classification"], "VALID")
        self.assertEqual(r["governed_result"], "GOVERNED_UNRESOLVED")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")
        self.assertEqual(r["deciding_gate"], "G7")

    # -- agent binding -------------------------------------------------------

    def _agent_projection(self, method):
        p = set_predicate(base(), "agent_specific", "TRUE")
        p["execution_agent_identity"] = {
            "agent_identity": "bitgov:agent:executor-7",
            "comparison_method": method,
        }
        if method == "GOVERNED_RESOLVER":
            p["execution_agent_identity"]["resolver_reference"] = "bitgov:resolver:proving:0001"
        return p

    def test_S65a_agent_opaque_exact_match_binds(self):
        p = self._agent_projection("OPAQUE_EXACT")
        self.assertEqual(validate_semantic(p)[1], "VALID")
        use = attempt_from_binding(p)
        use["agent_identity"] = "bitgov:agent:executor-7"
        bound = gwo_bind(p, use)
        self.assertTrue(bound["bound"])
        self.assertFalse(bound["authorization_created"])

    def test_S65b_agent_mismatch_rejected(self):
        p = self._agent_projection("OPAQUE_EXACT")
        use = attempt_from_binding(p)
        use["agent_identity"] = "bitgov:agent:executor-9"
        bound = gwo_bind(p, use)
        self.assertFalse(bound["bound"])
        self.assertEqual(bound["classification"], "BINDING_MISMATCH")

    def test_S65c_agent_missing_rejected(self):
        p = self._agent_projection("OPAQUE_EXACT")
        bound = gwo_bind(p, attempt_from_binding(p))
        self.assertFalse(bound["bound"])
        self.assertEqual(bound["classification"], "BINDING_MISMATCH")

    # -- opaque identity: byte-neutrality + NFC -------------------------------

    def test_S66_nfc_collision_distinct_identity(self):
        composed = "caf\u00e9-archivist"
        decomposed = "cafe\u0301-archivist"
        self.assertNotEqual(composed, decomposed)
        p = base()
        p["request_binding"]["principal"]["identity"] = composed
        use = attempt_from_binding(p)
        self.assertEqual(use["principal"], composed)
        use["principal"] = decomposed
        bound = gwo_bind(p, use)
        self.assertFalse(bound["bound"])
        self.assertEqual(bound["classification"], "BINDING_MISMATCH")
        self.assertFalse(bound["authorization_created"])
        r = final_reliance(p, use)
        self.assertEqual(r["classification"], "BINDING_MISMATCH")
        self.assertTrue(r["interface_failure"])

    def test_projection_identity_uppercase_rejected_not_normalized(self):
        p = base()
        p["projection_identity"] = p["projection_identity"].upper()
        struct_ok, _ = validate_structural(p)
        self.assertFalse(struct_ok)
        r = final_reliance(p)
        self.assertEqual(r["classification"], "STRUCTURAL_MALFORMED")

    # -- constitutional -------------------------------------------------------

    def test_BLOCK1_blocked_with_permit_effect_inconsistent(self):
        r = final_reliance(fixture("blocked_inconsistent.json"))
        self.assertTrue(r["structural"]["passed"])
        self.assertEqual(r["semantic"]["classification"], "SEMANTIC_INCONSISTENT")
        self.assertEqual(r["classification"], "SEMANTIC_INCONSISTENT")
        self.assertEqual(r["governed_result"], "INTERFACE_FAILURE")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")
        self.assertEqual(r["deciding_gate"], "G0")
        self.assertTrue(r["interface_failure"])

    def test_BLOCK2_blocked_with_prohibit_effect_prohibit(self):
        r = final_reliance(fixture("blocked_prohibit.json"))
        self.assertEqual(r["semantic"]["classification"], "VALID")
        self.assertEqual(r["governed_result"], "AUTHORIZED")
        self.assertEqual(r["reliance_verdict"], "PROHIBIT")
        self.assertEqual(r["deciding_gate"], "G8")

    def test_CONST1_not_applicable_needs_no_disposition(self):
        p = fixture("no_governed_decision.json")
        struct_ok, _ = validate_structural(p)
        self.assertTrue(struct_ok)
        self.assertNotIn("constitutional_disposition", p)
        sem_ok, sem_class, _ = validate_semantic(p)
        self.assertTrue(sem_ok)
        self.assertEqual(sem_class, "VALID")

    def test_CONST2_applicable_missing_disposition_inconsistent(self):
        p = base()
        del p["constitutional_disposition"]
        struct_ok, _ = validate_structural(p)
        self.assertTrue(struct_ok)
        sem_ok, sem_class, _ = validate_semantic(p)
        self.assertFalse(sem_ok)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")
        r = final_reliance(p)
        self.assertEqual(r["governed_result"], "INTERFACE_FAILURE")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")

    # -- absence evidence ------------------------------------------------------

    def test_ABS_A_basis_absent_with_absence_evidence(self):
        # Closed CR1-R1 (C2): zero positive rule basis + lineaged governed
        # absence uses governed_basis_exists == TRUE with finding
        # GOVERNED_ABSENCE_FOUND, plus valid absence and top-level lineage.
        p = fixture("no_governed_decision.json")
        sem_ok, sem_class, _ = validate_semantic(p)
        self.assertTrue(sem_ok, sem_class)
        self.assertEqual(p["predicate_assertions"]["governed_basis_exists"]["value"], "TRUE")
        self.assertTrue(len(p["absence_evidence"]) > 0)
        self.assertEqual(p["absence_evidence"][0]["finding"], "GOVERNED_ABSENCE_FOUND")
        self.assertIn("authority_lineage", p)
        r = final_reliance(p)
        self.assertEqual(r["governed_result"], "NO-GOVERNED-DECISION")
        self.assertEqual(r["reliance_verdict"], "NOT_APPLICABLE")

    def test_ABS_B_basis_present_with_absence_evidence_inconsistent(self):
        # TRUE with neither positive rules nor a FOUND absence determination
        # establishes no basis: rules removed and only an UNRESOLVED absence
        # finding carried.
        p = base()
        p.pop("rules_relied_upon", None)
        p["absence_evidence"] = [{
            "finding": "GOVERNED_ABSENCE_UNRESOLVED",
            "applicability_determination_reference": "det:absence:t1",
            "scope_reference": "bitgov:scope:reading-room-a.read-only",
            "lineage": {
                "rule_reference": "bitgov:rule:reading-room-access",
                "rule_version": "2026-09-01",
                "authority_basis": "bitgov:governed:basis:proving-slice-v1",
                "lineage_reference": "det:absence:t1",
            },
        }]
        sem_ok, sem_class, _ = validate_semantic(p)
        self.assertFalse(sem_ok)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")
        r = final_reliance(p)
        self.assertEqual(r["governed_result"], "INTERFACE_FAILURE")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")

    def test_ABS_C_empty_absence_evidence_inconsistent(self):
        p = base()
        p = set_predicate(p, "governed_basis_exists", "FALSE")
        p["absence_evidence"] = []
        _, sem_class, _ = validate_semantic(p)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")

    # -- Aegis narrowing ---------------------------------------------------------

    def test_AEG1_narrowed_capability_admitted(self):
        p = base()
        admitted = aegis_check(p, attempt_from_binding(p))
        self.assertTrue(admitted["admitted"])
        self.assertEqual(admitted["classification"], "VALID")
        self.assertEqual(admitted["reliance"]["reliance_verdict"], "PERMIT")
        self.assertFalse(admitted["authorization_created"])

    def test_AEG2_substitution_or_widening_denied(self):
        p = base()
        capability = attempt_from_binding(p)
        capability["action"] = "bitgov:action:write-record"
        admitted = aegis_check(p, capability)
        self.assertFalse(admitted["admitted"])
        self.assertEqual(admitted["classification"], "BINDING_MISMATCH")
        self.assertFalse(admitted["authorization_created"])

    def test_AEG3_unknown_constraint_subtype_fail_closed(self):
        p = base()
        p["constraints"] = [{
            "constraint_type": "FUTURE:rate-limit",
            "statement": "a subtype the slice-1 checker does not implement",
        }]
        sem_ok, sem_class, _ = validate_semantic(p)
        self.assertTrue(sem_ok, sem_class)
        self.assertEqual(final_reliance(p)["reliance_verdict"], "PERMIT")
        admitted = aegis_check(p, attempt_from_binding(p))
        self.assertFalse(admitted["admitted"])
        self.assertEqual(admitted["classification"], "UNKNOWN_CONSTRAINT_SUBTYPE")
        self.assertFalse(admitted["authorization_created"])

    def test_AEG_no_reliance_never_becomes_permission(self):
        denied = aegis_check(fixture("denied.json"), attempt_from_binding(fixture("denied.json")))
        self.assertFalse(denied["admitted"])
        self.assertEqual(denied["reliance"]["reliance_verdict"], "PROHIBIT")
        unresolved = aegis_check(fixture("unresolved_outcome.json"),
                                 attempt_from_binding(fixture("unresolved_outcome.json")))
        self.assertFalse(unresolved["admitted"])
        self.assertEqual(unresolved["reliance"]["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")

    # -- unknown / version / integrity --------------------------------------------

    def test_UNK1_unknown_field_rejected(self):
        p = fixture("unknown_field.json")
        struct_ok, struct_errors = validate_structural(p)
        self.assertFalse(struct_ok)
        self.assertTrue(struct_errors)
        r = final_reliance(p)
        self.assertEqual(r["classification"], "STRUCTURAL_MALFORMED")
        self.assertEqual(r["governed_result"], "INTERFACE_FAILURE")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")
        self.assertEqual(r["deciding_gate"], "G0")

    def test_UNK2_unknown_enum_no_reliance(self):
        p = fixture("unknown_enum.json")
        struct_ok, _ = validate_structural(p)
        self.assertTrue(struct_ok)
        sem_ok, sem_class, _ = validate_semantic(p)
        self.assertFalse(sem_ok)
        self.assertEqual(sem_class, "UNKNOWN_REQUIRED")
        r = final_reliance(p)
        self.assertEqual(r["classification"], "UNKNOWN_REQUIRED")
        self.assertEqual(r["governed_result"], "INTERFACE_FAILURE")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")
        self.assertNotIn("CURRENT", ("ACTIVE", "SUPERSEDED", "REVOKED",
                                    "INVALIDATED", "EXPIRED"))

    def test_INT1_integrity_envelope_inside_projection_rejected(self):
        p = fixture("unknown_field.json")
        self.assertIn("integrity_envelope", p)
        struct_ok, _ = validate_structural(p)
        self.assertFalse(struct_ok)
        r = final_reliance(p)
        self.assertEqual(r["classification"], "STRUCTURAL_MALFORMED")
        self.assertEqual(r["governed_result"], "INTERFACE_FAILURE")

    def test_version_incompatible_fail_closed(self):
        r = final_reliance(fixture("unknown_version.json"))
        self.assertTrue(r["structural"]["passed"])
        self.assertEqual(r["semantic"]["classification"], "VERSION_INCOMPATIBLE")
        self.assertEqual(r["classification"], "VERSION_INCOMPATIBLE")
        self.assertEqual(r["governed_result"], "INTERFACE_FAILURE")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")

    def test_INF1_governed_resolver_unavailable(self):
        p = self._agent_projection("GOVERNED_RESOLVER")
        sem_ok, sem_class, _ = validate_semantic(p)
        self.assertTrue(sem_ok, sem_class)
        r = final_reliance(p)
        self.assertEqual(r["reliance_verdict"], "PERMIT")
        use = attempt_from_binding(p)
        use["agent_identity"] = "bitgov:agent:executor-7"
        bound = gwo_bind(p, use)
        self.assertFalse(bound["bound"])
        self.assertEqual(bound["classification"], "UNAVAILABLE_RESOLVER")
        self.assertFalse(bound["authorization_created"])

    # -- conditional-presence discipline --------------------------------------------

    def test_conditional_true_missing_field_inconsistent(self):
        p = base()
        del p["constraints"]
        _, sem_class, _ = validate_semantic(p)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")

    def test_conditional_false_present_field_inconsistent(self):
        p = base()
        p["representation_binding"] = {
            "principal_identity": "bitgov:principal:archivist-042",
            "representative_identity": "bitgov:representative:advocate-1",
            "mandate_reference": "bitgov:mandate:proving:0001",
        }
        _, sem_class, _ = validate_semantic(p)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")

    def test_basis_unknown_true_requires_unresolved(self):
        p = base()
        p["predicate_assertions"]["governed_basis_exists"]["basis_unknown"] = True
        _, sem_class, _ = validate_semantic(p)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")

    def test_effect_not_applicable_while_applicable_inconsistent(self):
        p = set_predicate(base(), "appeal_applicability", "TRUE")
        p["appeal_state"] = {"appeal_reference": "bitgov:appeal:proving-slice:t2"}
        p["appeal_effect"] = {"effect": "NOT_APPLICABLE"}
        _, sem_class, _ = validate_semantic(p)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")

    def test_evaluation_point_requires_explicit_timezone(self):
        p = base()
        p["temporal_evaluation_and_currency"]["evaluation_point"] = "2026-09-30 12:00:00"
        _, sem_class, _ = validate_semantic(p)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")

    def test_finality_aggregate_mismatch_inconsistent(self):
        p = base()
        p["finality_aggregate"] = "NOT_FINAL"
        _, sem_class, _ = validate_semantic(p)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")

    # -- determinism / authority boundaries ------------------------------------------

    def test_gate_order_deterministic(self):
        first = final_reliance(base())
        second = final_reliance(copy.deepcopy(base()))
        self.assertEqual(first, second)
        revoked = final_reliance(fixture("revoked.json"))
        self.assertEqual(revoked["deciding_gate"], "G1")

    def test_consumers_never_create_authorization(self):
        for name in ("valid_permit.json", "denied.json", "revoked.json",
                     "unresolved_outcome.json"):
            p = fixture(name)
            bound = gwo_bind(p, attempt_from_binding(p))
            self.assertFalse(bound["authorization_created"], name)
            admitted = aegis_check(p, attempt_from_binding(p))
            self.assertFalse(admitted["authorization_created"], name)

    def test_test_only_subtype_not_a_normative_enum(self):
        import reference_proving_slice as harness
        for closed in ("AUTHORIZATION_OUTCOMES", "CONSTITUTIONAL_DISPOSITIONS",
                       "FINALITY_AGGREGATES", "LIFECYCLE_STATES",
                       "EXECUTION_RELIANCE_EFFECTS", "CURRENCY_STATES"):
            self.assertNotIn(TEST_ONLY_CONSTRAINT_TYPE, getattr(harness, closed))

    def test_cli_validates_positive_fixture(self):
        target = os.path.join(FIXTURES, "valid_permit.json")
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "reference_validator.py"), target],
            capture_output=True, text=True, cwd=HERE)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        output = json.loads(proc.stdout)
        self.assertEqual(output["final_reliance"]["reliance_verdict"], "PERMIT")
        self.assertEqual(output["final_reliance"]["governed_result"], "AUTHORIZED")


class AuthorizedBasisCorrection(unittest.TestCase):
    """BITGOV-MAS-I1 C1: AUTHORIZED requires established governed basis.

    SI1-R4 Q1: every dispositional field carries lineage to a legitimate
    BitGov-governed rule. Unlineaged authority -> UNRESOLVED, NEVER
    AUTHORIZED. The validator rejects the contradictory carrier; it never
    fabricates rules/lineage and never reinterprets AUTHORIZED as
    UNRESOLVED.
    """

    def test_C1A_authorized_basis_false_no_rules_no_lineage_inconsistent(self):
        p = base()
        p["predicate_assertions"]["governed_basis_exists"]["value"] = "FALSE"
        p.pop("rules_relied_upon", None)
        p.pop("absence_evidence", None)
        p.pop("authority_lineage", None)
        struct_ok, _ = validate_structural(p)
        self.assertTrue(struct_ok)
        sem_ok, sem_class, _ = validate_semantic(p)
        self.assertFalse(sem_ok)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")
        r = final_reliance(p)
        self.assertEqual(r["classification"], "SEMANTIC_INCONSISTENT")
        self.assertEqual(r["governed_result"], "INTERFACE_FAILURE")
        self.assertNotEqual(r["reliance_verdict"], "PERMIT")
        self.assertEqual(r["deciding_gate"], "G0")
        self.assertTrue(r["interface_failure"])
        bound = gwo_bind(p, attempt_from_binding(p))
        self.assertFalse(bound["bound"])
        self.assertFalse(bound["authorization_created"])
        admitted = aegis_check(p, attempt_from_binding(p))
        self.assertFalse(admitted["admitted"])
        self.assertFalse(admitted["authorization_created"])

    def test_C1B_authorized_basis_true_rules_absent_inconsistent(self):
        p = base()
        p.pop("rules_relied_upon", None)
        self.assertEqual(
            p["predicate_assertions"]["governed_basis_exists"]["value"], "TRUE")
        self.assertIn("authority_lineage", p)
        struct_ok, _ = validate_structural(p)
        self.assertTrue(struct_ok)
        _, sem_class, _ = validate_semantic(p)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")
        r = final_reliance(p)
        self.assertEqual(r["classification"], "SEMANTIC_INCONSISTENT")
        self.assertNotEqual(r["reliance_verdict"], "PERMIT")
        self.assertEqual(r["deciding_gate"], "G0")

    def test_C1B_empty_rules_list_inconsistent(self):
        p = base()
        p["rules_relied_upon"] = []
        _, sem_class, _ = validate_semantic(p)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")

    def test_C1C_authorized_basis_true_lineage_absent_inconsistent(self):
        p = base()
        p.pop("authority_lineage", None)
        self.assertTrue(len(p["rules_relied_upon"]) > 0)
        struct_ok, _ = validate_structural(p)
        self.assertTrue(struct_ok)
        _, sem_class, _ = validate_semantic(p)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")
        r = final_reliance(p)
        self.assertEqual(r["classification"], "SEMANTIC_INCONSISTENT")
        self.assertNotEqual(r["reliance_verdict"], "PERMIT")
        self.assertEqual(r["deciding_gate"], "G0")

    def test_C1D_authorized_basis_true_valid_rules_lineage_permit(self):
        p = base()
        sem_ok, sem_class, _ = validate_semantic(p)
        self.assertTrue(sem_ok, sem_class)
        r = final_reliance(p)
        self.assertEqual(r["classification"], "VALID")
        self.assertEqual(r["governed_result"], "AUTHORIZED")
        self.assertEqual(r["reliance_verdict"], "PERMIT")
        self.assertEqual(r["deciding_gate"], "G9")
        bound = gwo_bind(p, attempt_from_binding(p))
        self.assertTrue(bound["bound"])
        self.assertFalse(bound["authorization_created"])
        admitted = aegis_check(p, attempt_from_binding(p))
        self.assertTrue(admitted["admitted"])
        self.assertFalse(admitted["authorization_created"])

    def test_C1E_unresolved_basis_unresolved_outcome_governed_unresolved(self):
        r = final_reliance(fixture("unresolved_outcome.json"))
        self.assertTrue(r["structural"]["passed"])
        self.assertEqual(r["semantic"]["classification"], "VALID")
        self.assertEqual(r["governed_result"], "GOVERNED_UNRESOLVED")
        self.assertEqual(r["reliance_verdict"], "NO_RELIANCE_UNRESOLVED")
        self.assertFalse(r["interface_failure"])
        self.assertNotEqual(r["governed_result"], "INTERFACE_FAILURE")

    def test_C1F_no_governed_decision_absence_preserved(self):
        r = final_reliance(fixture("no_governed_decision.json"))
        self.assertTrue(r["structural"]["passed"])
        self.assertEqual(r["semantic"]["classification"], "VALID")
        self.assertEqual(r["governed_result"], "NO-GOVERNED-DECISION")
        self.assertEqual(r["reliance_verdict"], "NOT_APPLICABLE")
        self.assertEqual(r["deciding_gate"], "G5")
        self.assertFalse(r["interface_failure"])


def _closed_lineage(reference):
    return {
        "rule_reference": "bitgov:rule:reading-room-access",
        "rule_version": "2026-09-01",
        "authority_basis": "bitgov:governed:basis:proving-slice-v1",
        "lineage_reference": reference,
    }


def _found_absence(reference="det:absence:t1"):
    return {
        "finding": "GOVERNED_ABSENCE_FOUND",
        "applicability_determination_reference": reference,
        "scope_reference": "bitgov:scope:reading-room-a.read-only",
        "lineage": _closed_lineage(reference),
    }


class ClosedContractCorrection(unittest.TestCase):
    """BITGOV-MAS-I1 C2: closed CR1-R1 lineage + absence alignment."""

    def test_C2A_lineage_authority_reference_only_structural(self):
        p = base()
        p["predicate_assertions"]["governed_basis_exists"]["lineage"] = {
            "authority_reference": "bitgov:governed:basis:proving-slice-v1"
        }
        struct_ok, _ = validate_structural(p)
        self.assertFalse(struct_ok)
        r = final_reliance(p)
        self.assertEqual(r["classification"], "STRUCTURAL_MALFORMED")
        self.assertNotEqual(r["reliance_verdict"], "PERMIT")

    def test_C2B_lineage_old_two_member_shape_structural(self):
        p = base()
        p["authority_lineage"] = {
            "authority_reference": "bitgov:governed:basis:proving-slice-v1",
            "basis_reference": "bitgov:basis:0001",
        }
        struct_ok, _ = validate_structural(p)
        self.assertFalse(struct_ok)
        r = final_reliance(p)
        self.assertEqual(r["classification"], "STRUCTURAL_MALFORMED")
        self.assertNotEqual(r["reliance_verdict"], "PERMIT")

    def test_C2C_lineage_exact_four_members_structural(self):
        p = base()
        struct_ok, struct_errors = validate_structural(p)
        self.assertTrue(struct_ok, struct_errors)
        lineage = p["authority_lineage"]
        self.assertEqual(sorted(lineage),
                         ["authority_basis", "lineage_reference",
                          "rule_reference", "rule_version"])
        sem_ok, sem_class, _ = validate_semantic(p)
        self.assertTrue(sem_ok, sem_class)

    def test_C2D_authorized_positive_basis_permit(self):
        p = base()
        self.assertTrue(len(p["rules_relied_upon"]) > 0)
        sem_ok, sem_class, _ = validate_semantic(p)
        self.assertTrue(sem_ok, sem_class)
        r = final_reliance(p)
        self.assertEqual(r["reliance_verdict"], "PERMIT")
        self.assertEqual(r["deciding_gate"], "G9")

    def test_C2E_no_governed_decision_found_absence_not_applicable(self):
        p = fixture("no_governed_decision.json")
        self.assertEqual(
            p["predicate_assertions"]["governed_basis_exists"]["value"], "TRUE")
        self.assertEqual(p["absence_evidence"][0]["finding"],
                         "GOVERNED_ABSENCE_FOUND")
        struct_ok, _ = validate_structural(p)
        self.assertTrue(struct_ok)
        sem_ok, sem_class, _ = validate_semantic(p)
        self.assertTrue(sem_ok, sem_class)
        r = final_reliance(p)
        self.assertEqual(r["classification"], "VALID")
        self.assertEqual(r["governed_result"], "NO-GOVERNED-DECISION")
        self.assertEqual(r["reliance_verdict"], "NOT_APPLICABLE")

    def test_C2F_basis_false_with_absence_inconsistent(self):
        p = set_predicate(base(), "governed_basis_exists", "FALSE")
        p.pop("rules_relied_upon", None)
        p.pop("authority_lineage", None)
        p["absence_evidence"] = [_found_absence()]
        _, sem_class, _ = validate_semantic(p)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")
        r = final_reliance(p)
        self.assertEqual(r["classification"], "SEMANTIC_INCONSISTENT")
        self.assertNotEqual(r["reliance_verdict"], "PERMIT")

    def test_C2G_basis_false_with_lineage_inconsistent(self):
        p = set_predicate(base(), "governed_basis_exists", "FALSE")
        p.pop("rules_relied_upon", None)
        self.assertIn("authority_lineage", p)
        _, sem_class, _ = validate_semantic(p)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")
        self.assertNotEqual(
            final_reliance(p)["reliance_verdict"], "PERMIT")

    def test_C2H_basis_false_with_rules_inconsistent(self):
        p = set_predicate(base(), "governed_basis_exists", "FALSE")
        p.pop("authority_lineage", None)
        self.assertTrue(len(p["rules_relied_upon"]) > 0)
        _, sem_class, _ = validate_semantic(p)
        self.assertEqual(sem_class, "SEMANTIC_INCONSISTENT")
        self.assertNotEqual(
            final_reliance(p)["reliance_verdict"], "PERMIT")

    def test_C2I_absence_unresolved_not_no_governed_decision(self):
        p = base()
        p["authorization_outcome"] = "NO-GOVERNED-DECISION"
        p.pop("rules_relied_upon", None)
        p["absence_evidence"] = [{
            "finding": "GOVERNED_ABSENCE_UNRESOLVED",
            "applicability_determination_reference": "det:absence:t2",
            "scope_reference": "bitgov:scope:reading-room-a.read-only",
            "lineage": _closed_lineage("det:absence:t2"),
        }]
        r = final_reliance(p)
        self.assertNotEqual(r["governed_result"], "NO-GOVERNED-DECISION")
        self.assertEqual(r["classification"], "SEMANTIC_INCONSISTENT")


if __name__ == "__main__":
    unittest.main()
