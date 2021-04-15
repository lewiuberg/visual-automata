"""Classes and functions for testing the behavior of both and VisualNFAs."""

from visual_automata.fa.nfa import VisualNFA


class TestFA(object):
    """A test class for testing all finite automata."""

    def setup(self):
        """Reset test automata before every test function."""

        # NFA which matches strings beginning with 'a', ending with 'a', and
        # containing no consecutive 'b's
        self.nfa = VisualNFA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"a": {"q1"}},
                "q1": {"a": {"q1"}, "": {"q2"}},
                "q2": {"b": {"q0"}},
            },
            initial_state="q0",
            final_states={"q1"},
        )

    def assert_is_copy(self, first, second):
        """Assert that the first FA is a deep copy of the second."""
        assert id(first.states) != id(second.states)
        assert first.states == second.states
        assert id(first.input_symbols) != id(second.input_symbols)
        assert first.input_symbols == second.input_symbols
        assert id(first.transitions) != id(second.transitions)
        assert first.transitions == second.transitions
        assert first.initial_state == second.initial_state
        assert id(first.final_states) != id(second.final_states)
        assert first.final_states == second.final_states
