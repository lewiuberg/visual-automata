"""
Classes and methods for working with visual non-deterministic finite automata.
"""

import copy
import random
import sys
from typing import Generator, Union

import numpy as np
import pandas as pd
from automata.fa.nfa import NFA
from colormath.color_objects import sRGBColor
from forbiddenfruit import curse
from graphviz import Digraph
from IPython.display import display
from pandas import DataFrame

from visual_automata.colors import (
    create_palette,
    hex_to_rgb_color,
    list_cycler,
)

sys.setrecursionlimit(10 ** 6)


def deepcopy(self) -> dict:
    return copy.deepcopy(self)


curse(dict, "deepcopy", deepcopy)


class VisualNFA:
    """A wrapper for an automata-lib non-deterministic finite automaton."""

    def __init__(
        self,
        nfa: NFA = None,
        *,
        states: set = None,
        input_symbols: set = None,
        transitions: dict = None,
        initial_state: str = None,
        final_states: set = None,
    ):
        if nfa:
            self.nfa = nfa.copy()
        else:
            if not states:
                states = {*transitions.keys()}
            if not input_symbols:
                input_symbols = set()
                for v in transitions.values():
                    symbols = [*v.keys()]
                    for symbol in symbols:
                        if symbol != "":
                            input_symbols.add(symbol)
            self.nfa = NFA(
                states=states.copy(),
                input_symbols=input_symbols.copy(),
                transitions=transitions.deepcopy(),
                initial_state=initial_state,
                final_states=final_states.copy(),
            )
        self.nfa.validate()

    # -------------------------------------------------------------------------
    # Mimic behavior of automata-lib NFA.

    @property
    def states(self) -> set:
        """Pass on .states from the NFA"""
        return self.nfa.states

    @states.setter
    def states(self, states: set):
        """Set .states on the NFA"""
        self.nfa.states = states

    @property
    def input_symbols(self) -> set:
        """Pass on .input_symbols from the NFA"""
        return self.nfa.input_symbols

    @input_symbols.setter
    def input_symbols(self, input_symbols: set):
        """Set .input_symbols on the NFA"""
        self.nfa.input_symbols = input_symbols

    @property
    def transitions(self) -> dict:
        """Pass on .transitions from the NFA"""
        return self.nfa.transitions

    @transitions.setter
    def transitions(self, transitions: dict):
        """Set .transitions on the NFA"""
        self.nfa.transitions = transitions

    @property
    def initial_state(self) -> str:
        """Pass on .initial_state from the NFA"""
        return self.nfa.initial_state

    @initial_state.setter
    def initial_state(self, initial_state: str):
        """Set .initial_state on the NFA"""
        self.nfa.initial_state = initial_state

    @property
    def final_states(self) -> set:
        """Pass on .final_states from the NFA"""
        return self.nfa.final_states

    @final_states.setter
    def final_states(self, final_states: set):
        """Set .final_states on the NFA"""
        self.nfa.final_states = final_states

    def copy(self):
        """Create a deep copy of the automaton."""
        return self.__class__(**vars(self))

    def validate(self) -> bool:
        """Return True if this NFA is internally consistent."""
        return self.nfa.validate()

    def accepts_input(self, input_str: str) -> bool:
        """Return True if this automaton accepts the given input."""
        return self.nfa.accepts_input(input_str=input_str)

    def read_input(self, input_str: str) -> set:
        """
        Check if the given string is accepted by this automaton.
        Return the automaton's final configuration if this string is valid.
        """
        return self.nfa.read_input(input_str=input_str)

    def read_input_stepwise(self, input_str: str) -> Generator:
        """
        Check if the given string is accepted by this automaton.
        Return the automaton's final configuration if this string is valid.
        """
        return self.nfa.read_input_stepwise(input_str=input_str)

    def _get_lambda_closure(self, start_state: str) -> set:
        """
        Return the lambda closure for the given state.

        The lambda closure of a state q is the set containing q, along with
        every state that can be reached from q by following only lambda
        transitions.
        """
        return self.nfa._get_lambda_closure(start_state=start_state)

    def _get_next_current_states(
        self, current_states: set, input_symbol: str
    ) -> set:
        """Return the next set of current states given the current set."""
        return self.nfa._get_next_current_states(current_states, input_symbol)

    # -------------------------------------------------------------------------
    # Define new attributes and their helper methods.

    @property
    def table(self) -> DataFrame:
        """
        Generates a transition table of the given VisualNFA.

        Returns:
            DataFrame: A transition table of the VisualNFA.
        """

        final_states = "".join(self.nfa.final_states)

        transitions = self._add_lambda(
            all_transitions=self.nfa.transitions,
            input_symbols=self.nfa.input_symbols,
        )

        table: dict = {}
        for state, transition in sorted(transitions.items()):
            if state == self.nfa.initial_state and state in final_states:
                state = "→*" + state
            elif state == self.nfa.initial_state:
                state = "→" + state
            elif state in final_states:
                state = "*" + state
            row: dict = {}
            for input_symbol, next_states in transition.items():
                cell: list = []
                for next_state in sorted(next_states):
                    if next_state in final_states:
                        cell.append("*" + next_state)
                    else:
                        cell.append(next_state)
                if len(cell) == 1:
                    cell = cell.pop()
                else:
                    cell = "{" + ",".join(cell) + "}"
                row[input_symbol] = cell
            table[state] = row

        table = pd.DataFrame.from_dict(table).fillna("∅").T
        table = table.reindex(sorted(table.columns), axis=1)

        return table

    @staticmethod
    def _add_lambda(all_transitions: dict, input_symbols: str) -> dict:
        """
        Replacing '' key name for empty string (lambda/epsilon) transitions.

        Args:
            all_transitions (dict): The NFA's transitions with '' for lambda transitions.
            input_symbols (str): The NFA's input symbols/alphabet.

        Returns:
            dict: Transitions with λ for lambda transitions
        """
        all_transitions = all_transitions.deepcopy()
        input_symbols = input_symbols.copy()
        # Replacing '' key name for empty string (lambda/epsilon) transitions.
        for transitions in all_transitions.values():
            for state, transition in list(transitions.items()):
                if state == "":
                    transitions["λ"] = transition
                    del transitions[""]
                    input_symbols.add("λ")
        return all_transitions

    # -------------------------------------------------------------------------
    # Define new class methods and their helper methods.

    @property
    def _lambda_transition_exists(self) -> bool:
        """
        Checks if the nfa has lambda transitions.

        Returns:
            bool: If the nfa has lambda transitions, returns True; else False.
        """
        status = False
        for transitions in self.nfa.transitions.values():
            if "" in transitions:
                return True
        return status

    @classmethod
    def eliminate_lambda(cls, nfa):
        """
        Eliminates lambda transitions, and returns a new nfa.

        Args:
            nfa (VisualNFA): A VisualNFA object.

        Returns:
            VisualNFA: A VisualNFA object without lambda transitions.
        """
        if nfa._lambda_transition_exists:
            nfa_lambda_eliminated = nfa.copy()

            for state in sorted(nfa_lambda_eliminated.transitions):
                # Find lambda closure for the state.
                closures = nfa_lambda_eliminated._get_lambda_closure(state)

                if nfa_lambda_eliminated.initial_state == state:
                    if closures.difference(state).issubset(
                        nfa_lambda_eliminated.final_states
                    ):
                        [
                            nfa_lambda_eliminated.final_states.add(state)
                            for state in closures.intersection(state)
                        ]

                for input_symbol in nfa_lambda_eliminated.input_symbols:
                    next_states = nfa.nfa._get_next_current_states(
                        closures, input_symbol
                    )

                    # Check if a dead state was returned.
                    if next_states != set():
                        # Update the transition after lambda move has been eliminated.
                        nfa_lambda_eliminated.transitions[state][
                            input_symbol
                        ] = next_states

                # Delete the lambda transition.
                if "" in nfa_lambda_eliminated.transitions[state]:
                    del nfa_lambda_eliminated.transitions[state][""]

            return nfa_lambda_eliminated
        else:
            return nfa

    # -------------------------------------------------------------------------
    # Define new methods and their helper methods.

    def _pathfinder(
        self,
        input_str: str,
        status: bool = False,
        counter: int = 0,
        main_counter: int = 0,
    ) -> Union[bool, list]:  # pragma: no cover. Too many possibilities.
        """
        Searches for a appropriate path to return to input_check.

        Args:
            input_str (str): Input symbols
            status (bool, optional): If a path is found. Defaults to False.
            counter (int, optional): To keep track of recursion limit in __pathsearcher. Defaults to 0.
            main_counter (int, optional): To keep track of recursion limit in _pathfinder. Defaults to 0.

        Returns:
            Union[bool, list]: If a path is found, and a list of transition tuples.
        """

        counter += 1
        nfa = self.copy()
        recursion_limit = 50
        result = self.__pathsearcher(nfa, input_str, status)

        if result:
            return status, result
        else:
            main_counter += 1
            if main_counter <= recursion_limit:
                return self._pathfinder(
                    input_str, status, counter, main_counter=main_counter
                )
            else:
                status = (
                    "[NO VALID PATH FOUND]\n"
                    "Try to eliminate lambda transitions and try again.\n"
                    "Example: nfa_lambda_removed = nfa.eliminate_lambda()"
                )
                return status, []

    @staticmethod
    def __pathsearcher(
        nfa, input_str: str, status: bool = False, counter: int = 0
    ) -> list:  # pragma: no cover. Too many possibilities.
        """
        Searches for a appropriate path to return to _pathfinder.

        Args:
            nfa (VisualNFA): A VisualNFA object.
            input_str (str): Input symbols.
            status (bool, optional): If a path is found. Defaults to False.
            counter (int, optional): To keep track of recursion limit. Defaults to 0.

        Returns:
            list: a list of transition tuples.
        """

        recursion_limit = 20000
        counter += 1
        current_state = {(nfa.initial_state)}
        path = []
        for symbol in input_str:
            next_curr = nfa._get_next_current_states(current_state, symbol)
            if next_curr == set():
                if not status:
                    state = {}
                    path.append(("".join(current_state), state, symbol))
                    return path
                else:
                    break
            else:
                state = random.choice(list(next_curr))
            path.append(("".join(current_state), state, symbol))
            current_state = {(state)}

        # Accepted path opptained.
        if (
            status
            and len(input_str) == (len(path))
            and path[-1][1] in nfa.final_states
        ):
            return path
        # Rejected path opptained.
        elif not status and len(input_str) == (len(path)):
            return path
        # No path opptained. Try again.
        else:
            if counter <= recursion_limit:
                return nfa.__pathsearcher(nfa, input_str, status, counter)
            else:
                return False

    @staticmethod
    def _transition_steps(
        initial_state,
        final_states,
        input_str: str,
        transitions_taken: list,
        status: bool,
    ) -> DataFrame:  # pragma: no cover. Too many possibilities.
        """
        Generates a table of taken transitions based on the input string and it's result.

        Args:
            initial_state (str): The NFA's initial state.
            final_states (set): The NFA's final states.
            input_str (str): The input string to run on the NFA.
            transitions_taken (list): Transitions taken from the input string.
            status (bool): The result of the input string.

        Returns:
            DataFrame: Table of taken transitions based on the input string and it's result.
        """
        current_states = transitions_taken.copy()
        for i, state in enumerate(current_states):

            if state == "" or state == {}:
                current_states[i] = "∅"

            elif state == initial_state and state in final_states:
                current_states[i] = "→*" + state
            elif state == initial_state:
                current_states[i] = "→" + state
            elif state in final_states:
                current_states[i] = "*" + state

        new_states = current_states.copy()
        del current_states[-1]
        del new_states[0]
        inputs = [str(x) for x in input_str]
        inputs = inputs[: len(current_states)]

        transition_steps: dict = {
            "Current state:": current_states,
            "Input symbol:": inputs,
            "New state:": new_states,
        }

        transition_steps = pd.DataFrame.from_dict(transition_steps)
        transition_steps.index += 1
        transition_steps = pd.DataFrame.from_dict(
            transition_steps
        ).rename_axis("Step:", axis=1)
        if status:
            transition_steps.columns = pd.MultiIndex.from_product(
                [["[Accepted]"], transition_steps.columns]
            )
            return transition_steps, inputs
        else:
            transition_steps.columns = pd.MultiIndex.from_product(
                [["[Rejected]"], transition_steps.columns]
            )
            return transition_steps, inputs

    @staticmethod
    def _transitions_pairs(
        all_transitions: dict,
    ) -> list:  # pragma: no cover. Too many possibilities.
        """
        Generates a list of all possible transitions pairs for all input symbols.

        Args:
            transition_dict (dict): NFA transitions.

        Returns:
            list: All possible transitions for all the given input symbols.
        """
        all_transitions = all_transitions.deepcopy()
        transition_possibilities: list = []
        for state, state_transitions in all_transitions.items():
            for symbol, transitions in state_transitions.items():
                if len(transitions) < 2:
                    if transitions != "" and transitions != {}:
                        transitions = transitions.pop()
                    transition_possibilities.append(
                        (state, transitions, symbol)
                    )
                else:
                    for transition in transitions:
                        transition_possibilities.append(
                            (state, transition, symbol)
                        )
        return transition_possibilities

    def input_check(
        self, input_str: str, return_result=False
    ) -> Union[
        bool, list, DataFrame
    ]:  # pragma: no cover. Too many possibilities.
        """
        Checks if string of input symbols results in final state.

        Args:
            input_str (str): The input string to run on the NFA.
            return_result (bool, optional): Returns results to the show_diagram method. Defaults to False.

        Raises:
            TypeError: To let the user know a string has to be entered.

        Returns:
            Union[bool, list, list]: If the last state is the final state, transition pairs, and steps taken.
        """

        if not isinstance(input_str, str):
            raise TypeError(
                f"input_str should be a string. "
                f"{input_str} is {type(input_str)}, not a string."
            )

        # Check if input string is accepted.
        status: bool = self.nfa.accepts_input(input_str=input_str)

        status, taken_transitions_pairs = self._pathfinder(
            input_str=input_str, status=status
        )
        if not isinstance(status, bool):
            if return_result:
                return status, [], DataFrame, input_str
            else:
                return status
        current_states = self.initial_state
        transitions_taken = [current_states]

        for transition in range(len(taken_transitions_pairs)):
            transitions_taken.append(taken_transitions_pairs[transition][1])

        taken_steps, inputs = self._transition_steps(
            initial_state=self.nfa.initial_state,
            final_states=self.final_states,
            input_str=input_str,
            transitions_taken=transitions_taken,
            status=status,
        )
        if return_result:
            return status, taken_transitions_pairs, taken_steps, inputs
        else:
            return taken_steps

    def show_diagram(
        self,
        input_str: str = None,
        filename: str = None,
        format_type: str = "png",
        path: str = None,
        *,
        view=False,
        cleanup: bool = True,
        horizontal: bool = True,
        reverse_orientation: bool = False,
        fig_size: tuple = (8, 8),
        font_size: float = 14.0,
        arrow_size: float = 0.85,
        state_seperation: float = 0.5,
    ) -> Digraph:  # pragma: no cover. Too many possibilities.
        """
        Generates the graph associated with the given NFA.

        Args:
            nfa (NFA): Deterministic Finite Automata to graph.
            input_str (str, optional): String list of input symbols. Defaults to None.
            filename (str, optional): Name of output file. Defaults to None.
            format_type (str, optional): File format [svg/png/...]. Defaults to "png".
            path (str, optional): Folder path for output file. Defaults to None.
            view (bool, optional): Storing and displaying the graph as a pdf. Defaults to False.
            cleanup (bool, optional): Garbage collection. Defaults to True.
            horizontal (bool, optional): Direction of node layout. Defaults to True.
            reverse_orientation (bool, optional): Reverse direction of node layout. Defaults to False.
            fig_size (tuple, optional): Figure size. Defaults to (8, 8).
            font_size (float, optional): Font size. Defaults to 14.0.
            arrow_size (float, optional): Arrow head size. Defaults to 0.85.
            state_seperation (float, optional): Node distance. Defaults to 0.5.

        Returns:
            Digraph: The graph in dot format.
        """
        # Converting to graphviz preferred input type,
        # keeping the conventional input styles; i.e fig_size(8,8)
        fig_size = ", ".join(map(str, fig_size))
        font_size = str(font_size)
        arrow_size = str(arrow_size)
        state_seperation = str(state_seperation)

        # Defining the graph.
        graph = Digraph(strict=False)
        graph.attr(
            size=fig_size,
            ranksep=state_seperation,
        )
        if horizontal:
            graph.attr(rankdir="LR")
        if reverse_orientation:
            if horizontal:
                graph.attr(rankdir="RL")
            else:
                graph.attr(rankdir="BT")

        # Defining arrow to indicate the initial state.
        graph.node("Initial", label="", shape="point", fontsize=font_size)

        # Defining all states.
        for state in sorted(self.nfa.states):
            if (
                state in self.nfa.initial_state
                and state in self.nfa.final_states
            ):
                graph.node(state, shape="doublecircle", fontsize=font_size)
            elif state in self.nfa.initial_state:
                graph.node(state, shape="circle", fontsize=font_size)
            elif state in self.nfa.final_states:
                graph.node(state, shape="doublecircle", fontsize=font_size)
            else:
                graph.node(state, shape="circle", fontsize=font_size)

        # Point initial arrow to the initial state.
        graph.edge("Initial", self.nfa.initial_state, arrowsize=arrow_size)

        # Define all tansitions in the finite state machine.
        all_transitions_pairs = self._transitions_pairs(self.nfa.transitions)

        # Replacing '' key name for empty string (lambda/epsilon) transitions.
        for i, pair in enumerate(all_transitions_pairs):
            if pair[2] == "":
                all_transitions_pairs[i] = (pair[0], pair[1], "λ")

        if input_str is None:
            for pair in all_transitions_pairs:
                graph.edge(
                    pair[0],
                    pair[1],
                    label=" {} ".format(pair[2]),
                    arrowsize=arrow_size,
                    fontsize=font_size,
                )
            status = None

        else:
            (
                status,
                taken_transitions_pairs,
                taken_steps,
                inputs,
            ) = self.input_check(input_str=input_str, return_result=True)
            if not isinstance(status, bool):
                print(status)
                return

            remaining_transitions_pairs = [
                x
                for x in all_transitions_pairs
                if x not in taken_transitions_pairs
            ]

            # Define color palette for transitions
            if status:
                start_color = hex_to_rgb_color("#FFFF00")
                end_color = hex_to_rgb_color("#00FF00")
            else:
                start_color = hex_to_rgb_color("#FFFF00")
                end_color = hex_to_rgb_color("#FF0000")
            number_of_colors = len(inputs)
            palette = create_palette(
                start_color, end_color, number_of_colors, sRGBColor
            )
            color_gen = list_cycler(palette)

            # Define all tansitions in the finite state machine with traversal.
            counter = 0
            for i, pair in enumerate(taken_transitions_pairs):
                dead_state = "\u00D8"
                edge_color = next(color_gen)
                counter += 1
                if pair[1] != {}:
                    graph.edge(
                        pair[0],
                        pair[1],
                        label=" [{}]\n{} ".format(counter, pair[2]),
                        arrowsize=arrow_size,
                        fontsize=font_size,
                        color=edge_color,
                        penwidth="2.5",
                    )
                else:
                    graph.node(dead_state, shape="circle", fontsize=font_size)
                    graph.edge(
                        pair[0],
                        dead_state,
                        label=" [{}]\n{} ".format(counter, inputs[-1]),
                        arrowsize=arrow_size,
                        fontsize=font_size,
                        color=edge_color,
                        penwidth="2.5",
                    )

            for pair in remaining_transitions_pairs:
                graph.edge(
                    pair[0],
                    pair[1],
                    label=" {} ".format(pair[2]),
                    arrowsize=arrow_size,
                    fontsize=font_size,
                )

        # Write diagram to file. PNG, SVG, etc.
        if filename:
            graph.render(
                filename=filename,
                format=format_type,
                directory=path,
                cleanup=cleanup,
            )

        if view:
            graph.render(view=True)
        if input_str:
            display(taken_steps)
            return graph
        else:
            return graph
