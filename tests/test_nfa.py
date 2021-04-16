"""Classes and functions for testing the behavior of VisualNFAs."""

import types

import pandas as pd
from pandas.testing import assert_frame_equal

import tests.test_fa as test_fa
from visual_automata.fa.nfa import VisualNFA


class TestNFA(test_fa.TestFA):
    """A test class for testing nondeterministic finite automata."""

    def test_init_nfa(self):
        """Should define a VisualNFA from given values."""
        new_nfa = VisualNFA(
            states=self.nfa.states.copy(),
            input_symbols=self.nfa.input_symbols.copy(),
            transitions=self.nfa.transitions.deepcopy(),
            initial_state=self.nfa.initial_state,
            final_states=self.nfa.final_states.copy(),
        )
        assert isinstance(new_nfa, VisualNFA)
        self.assert_is_copy(new_nfa, self.nfa)

    def test_init_wrap_nfa(self):
        """Should define a VisualNFA from a NFA."""
        new_nfa = VisualNFA(self.nfa)
        assert isinstance(new_nfa, VisualNFA)
        self.assert_is_copy(new_nfa, self.nfa)

    def test_init_auto_input_and_states(self):
        """Should automatically find the input symbols and states."""
        new_nfa = VisualNFA(
            transitions=self.nfa.transitions.deepcopy(),
            initial_state=self.nfa.initial_state,
            final_states=self.nfa.final_states.copy(),
        )
        assert isinstance(new_nfa, VisualNFA)
        self.assert_is_copy(new_nfa, self.nfa)

    def test_setters(self):
        """Should change the values of the inherited NFA (self.nfa)."""
        states = self.nfa.states.copy()
        input_symbols = self.nfa.input_symbols.copy()
        transitions = self.nfa.transitions.deepcopy()
        initial_state = self.nfa.initial_state
        final_states = self.nfa.final_states.copy()
        new_nfa = VisualNFA.copy(self.nfa)
        new_nfa.states = states
        new_nfa.input_symbols = input_symbols
        new_nfa.transitions = transitions
        new_nfa.initial_state = initial_state
        new_nfa.final_states = final_states
        assert isinstance(new_nfa, VisualNFA)
        self.assert_is_copy(new_nfa, self.nfa)

    def test_accepts_input_true(self):
        """
        Should return True if NFA input is accepted.
        """
        assert self.nfa.accepts_input("aba")

    def test_accepts_input_false(self):
        """Should return False if NFA input is rejected."""
        assert not self.nfa.accepts_input("abba")

    def test_read_input_accepted(self):
        """Should return correct states if acceptable NFA input is given."""
        reference_states = {"q1", "q2"}
        states = self.nfa.read_input("aba")
        assert states == reference_states

    def test_read_input_step(self):
        """Should return validation generator if step flag is supplied."""
        validation_generator = self.nfa.read_input_stepwise("aba")
        assert isinstance(validation_generator, types.GeneratorType)
        reference_steps = [{"q0"}, {"q1", "q2"}, {"q0"}, {"q1", "q2"}]
        listed_steps = list(validation_generator)
        assert listed_steps == reference_steps

    def test_get_lambda_closure(self):
        """Should return True if the correct closeure are produced."""
        reference_closure = {"q1", "q2"}
        closure = self.nfgita._get_lambda_closure("q1")
        assert closure == reference_closure

    def test_get_next_current_state(self):
        """Should return True if the correct states are produced."""
        reference_states = [{"q1", "q2"}, set()]
        states = [
            self.nfa._get_next_current_states({"q0"}, "a"),
            self.nfa._get_next_current_states({"q0"}, ""),
        ]
        assert states == reference_states

    def test_table(self):
        """Should return True if the NFA table is generated correctly."""
        reference_dataframes = pd.DataFrame(
            {
                "a": {"→q0": "*q1", "*q1": "*q1", "q2": "∅"},
                "b": {"→q0": "∅", "*q1": "∅", "q2": "q0"},
                "λ": {"→q0": "∅", "*q1": "q2", "q2": "∅"},
            }
        )
        assert_frame_equal(reference_dataframes, self.nfa.table)

    def test_lambda_transition_exists(self):
        """Should return True if the NFA table is generated correctly."""
        nfa = VisualNFA(
            states={"q0", "q1", "q2", "q3"},
            input_symbols={"0", "1"},
            transitions={
                "q0": {"0": {"q0", "q1"}, "1": {"q0", "q3"}},
                "q1": {"0": {"q2"}},
                "q2": {},
                "q3": {"1": {"q2"}},
            },
            initial_state="q0",
            final_states={"q2"},
        )
        status = [
            self.nfa._lambda_transition_exists,
            nfa._lambda_transition_exists,
        ]
        assert status[0]
        assert not status[1]

    def test_eliminate_lambda(self):
        """Should return True if the NFA table is generated correctly."""
        nfa = VisualNFA.copy(self.nfa)
        elim_nfa = VisualNFA.eliminate_lambda(nfa)
        reference_table = {
            "a": {"→q0": "{*q1,q2}", "*q1": "{*q1,q2}", "q2": "∅"},
            "b": {"→q0": "∅", "*q1": "q0", "q2": "q0"},
        }
        nfa_elim_table = elim_nfa.table.to_dict()
        assert nfa_elim_table == reference_table

        nfa_no_lambda = VisualNFA.copy(nfa)
        nfa_no_lambda.transitions["q1"] = {"a": {"q1"}, "b": {"q2"}}
        elim_nfa_no_lambda = VisualNFA.eliminate_lambda(nfa_no_lambda)
        reference_table_no_lambda = {
            "a": {"→q0": "*q1", "*q1": "*q1", "q2": "∅"},
            "b": {"→q0": "∅", "*q1": "q2", "q2": "q0"},
        }
        nfa_elim_table_no_lambda = elim_nfa_no_lambda.table.to_dict()
        assert nfa_elim_table_no_lambda == reference_table_no_lambda

        nfa_multi_final_no_lambda = VisualNFA.copy(nfa)
        nfa_multi_final_no_lambda.final_states = {"q0", "q1"}
        elim_nfa_multi_final_no_lambda = VisualNFA.eliminate_lambda(
            nfa_multi_final_no_lambda
        )
        reference_table_multi_final_no_lambda = {
            "a": {"→*q0": "{*q1,q2}", "*q1": "{*q1,q2}", "q2": "∅"},
            "b": {"→*q0": "∅", "*q1": "*q0", "q2": "*q0"},
        }
        nfa_elim_table_multi_final_no_lambda = (
            elim_nfa_multi_final_no_lambda.table.to_dict()
        )
        assert (
            nfa_elim_table_multi_final_no_lambda
            == reference_table_multi_final_no_lambda
        )
