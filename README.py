# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light,md
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Visual Automata
# Copyright 2021 Lewi Lie Uberg\
# _Released under the MIT license_
#
# Visual Automata is a Python 3 library built as a wrapper for **Caleb Evans'** [Automata](https://github.com/caleb531/automata) library to add more visualization features.
#
# ## Prerequisites
# ---
# [Automata](https://github.com/caleb531/automata)\
# `pip install automata-lib`
#
# ## Installing
# ---
# `pip install visual-automata`
#
# ## Contents
# ---
#
# - [VisualDFA](#VisualDFA)
#     - [Importing](#Importing)
#     - [Instantiating DFAs](#Instantiating-DFAs)
#     - [Converting](#Converting)
#     - [Minimal DFA](#Minimal-DFA)
#     - [Transition Table](#Transition-Table)
#     - [Check input strings](#Check-input-strings)
#     - [Show Diagram](#Show-Diagram)
#
# ### VisualDFA
# #### Importing
# Import needed classes.

# +
from automata.fa.dfa import DFA

from visual_automata.fa.dfa import VisualDFA
# -

# #### Instantiating DFAs
# Define an automata-lib DFA that can accept any string ending with 00 or 11.

dfa = VisualDFA(
    states={"q0", "q1", "q2", "q3", "q4"},
    input_symbols={"0", "1"},
    transitions={
        "q0": {"0": "q3", "1": "q1"},
        "q1": {"0": "q3", "1": "q2"},
        "q2": {"0": "q3", "1": "q2"},
        "q3": {"0": "q4", "1": "q1"},
        "q4": {"0": "q4", "1": "q1"},
    },
    initial_state="q0",
    final_states={"q2", "q4"},
)

# #### Converting
# An automata-lib DFA can be converted to a VisualDFA.
#
# Define an automata-lib DFA that can accept any string ending with 00 or 11.

dfa = DFA(
    states={"q0", "q1", "q2", "q3", "q4"},
    input_symbols={"0", "1"},
    transitions={
        "q0": {"0": "q3", "1": "q1"},
        "q1": {"0": "q3", "1": "q2"},
        "q2": {"0": "q3", "1": "q2"},
        "q3": {"0": "q4", "1": "q1"},
        "q4": {"0": "q4", "1": "q1"},
    },
    initial_state="q0",
    final_states={"q2", "q4"},
)

# Convert automata-lib DFA to VisualDFA.

dfa = VisualDFA(dfa)

# #### Minimal-DFA
# Creates a minimal DFA which accepts the same inputs as the old one. Unreachable states are removed and equivalent states are merged. States are renamed by default.

new_dfa = VisualDFA(
    states={'q0', 'q1', 'q2'},
    input_symbols={'0', '1'},
    transitions={
        'q0': {'0': 'q0', '1': 'q1'},
        'q1': {'0': 'q0', '1': 'q2'},
        'q2': {'0': 'q2', '1': 'q1'}
    },
    initial_state='q0',
    final_states={'q1'}
)

new_dfa.table

new_dfa.show_diagram()

minimal_dfa = VisualDFA.minify(new_dfa)
minimal_dfa.show_diagram()

minimal_dfa.table

# #### Transition Table
# Outputs the transition table for the given DFA.

dfa.table

# #### Check input strings
# `1001` does not end with `00` or `11`, and is therefore `Rejected`

dfa.input_check("1001")

# `10011` does end with `11`, and is therefore `Accepted`

dfa.input_check("10011")

# #### Show Diagram
# For IPython `dfa.show_diagram()` may be used.\
# For a python script `dfa.show_diagram(view=True)` may be used to automatically view the graph as a PDF file.

dfa.show_diagram()

# The `show_diagram` method also accepts input strings, and will return a graph with gradient `red` arrows for `Rejected` results, and gradient `green` arrows for `Accepted` results. It will also display a table with transitions states stepwise. The steps in this table will correspond with the `[number]` over eached traversed arrow.
#
# Please note that for visual purposes additional arrows are added if a transition is traversed more than once.

dfa.show_diagram("1001")

dfa.show_diagram("10011")

# ## Authors
# ---
#
# * **Lewi Lie Uberg** - [uberg.me](https://uberg.me/)
#
# ## License
# ---
#
# This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
#
# ## Acknowledgments
# ---
#
# * [Caleb Evans](https://github.com/caleb531) for his work on automata-lib.
# * [Geir Arne Hjelle](https://github.com/gahjelle) and [Michal Porteš](https://github.com/mportesdev) for their general counsel.
# * [JFLAP](http://www.jflap.org) for their work on a GUI based Automata application.
