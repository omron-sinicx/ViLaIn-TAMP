#!/usr/bin/env python

from typing import Tuple, List, Dict
import os
import re
import itertools
from collections import defaultdict


class PDDLProblem:
    def __init__(
        self, 
        pddl_problem: str,
    ):
        self.pddl_problem = pddl_problem

        self.pddl_objects = None
        self.objects = None

        self.pddl_initial_state = None
        self.initial_state = None

        self.pddl_goal = None
        self.goal_conditions = None

        self.parse_objects()
        self.parse_initial_state()
        self.parse_goal()

    # parse (:object * ) w/o newline
    def parse_objects(self):
        objects_pattern = re.compile(r"(\(:objects.*?\))", re.DOTALL)
        self.pddl_objects = objects_pattern.findall(self.pddl_problem)[0]

        object_pattern = re.compile(
            r"\s*(?P<objs>.*?)\s*-\s*(?P<type>\w+)\s*",
            re.MULTILINE,
        )
        self.objects = []

        for objs, _type in object_pattern.findall(self.pddl_objects):
            _type = _type.strip().split(";")[0]

            for obj in objs.strip().split():
                self.objects += [f"{obj} - {_type}"]

    # parse (:init * ) w/o newline
    def parse_initial_state(self):
        comment_pattern = re.compile(r"(;.*?$)", re.MULTILINE)
        pddl_problem_wo_comments = comment_pattern.sub("", self.pddl_problem)

        initial_state_pattern = re.compile(r"(\(:init.*?\))\s*\(:goal", re.DOTALL)
        self.pddl_initial_state = initial_state_pattern.findall(pddl_problem_wo_comments)[0]

        predicate_pattern = re.compile(r"(\(.*?\))", re.MULTILINE)
        self.initial_state = predicate_pattern.findall(self.pddl_initial_state)

    # parse (:goal * )* w/o newline
    def parse_goal(self):
        comment_pattern = re.compile(r"(;.*?$)", re.MULTILINE)
        pddl_problem_wo_comments = comment_pattern.sub("", self.pddl_problem)

        goal_pattern = re.compile(r"(\(:goal.*?\)\s*\)\s*\))\s*\)", re.DOTALL)
        self.pddl_goal = goal_pattern.findall(pddl_problem_wo_comments)[0]

        predicate_pattern = re.compile(r"(\(.*?\))", re.MULTILINE)
        self.goal_conditions = predicate_pattern.findall(self.pddl_goal)


class PDDLDomain:
    def __init__(
        self, 
        pddl_domain: str,
    ):
        self.pddl_domain = pddl_domain
        self.pddl_domain_flat = re.sub(
            r"\s+", " ", 
            pddl_domain.replace("\n", " "),
        )

        self.pddl_predicates = None
        self.predicates = None

        self.pddl_actions = None
        self.actions = None

        self.parse_predicates()
        self.parse_actions()

    def parse_predicates(self):
        predicates_pattern = re.compile(r"(\(:predicates.*?\s\))", re.DOTALL)
        #predicate_pattern = re.compile(r"(\(([^()]+)\))(?:\s*;\s*(.*))?", re.MULTILINE)
        predicate_pattern = re.compile(r"(\(.*?\))((?:\s*;\s*.*)?)", re.MULTILINE)

        # get predicates
        whole_pddl_predicates = predicates_pattern.findall(self.pddl_domain)[0]
        pddl_predicates_and_comments = predicate_pattern.findall(whole_pddl_predicates)

        self.pddl_predicates = [
            f"{predicate} ; {comment}" if len(comment) > 0 else f"{predicate}"
            for predicate, comment in pddl_predicates_and_comments
        ]

        # parse predicates
        self.predicates = []
        for predicate, comment in pddl_predicates_and_comments:
            predicate_name, *arguments = predicate[1:-1].split()

            self.predicates += [{
                "predicate": predicate,
                "name": predicate_name,
                "arguments": arguments,
                "comment": comment
            }]

        self.name2predicate = {}
        for predicate in self.predicates:
            self.name2predicate[predicate["name"]] = predicate

    def parse_actions(self):
        def get_start_end_idxs():
            # get start indices for actions
            start_idxs = [self.pddl_domain.index("(:action")]
            
            while True:
                idx = self.pddl_domain[start_idxs[-1] + 1:].find("(:action")

                if idx >= 0:
                    start_idxs += [start_idxs[-1] + idx + 1]
                else:
                    break

            # get end indices for actions
            end_idxs = []

            for start_idx in start_idxs:
                stack = 0 # calculate the number of unclosed parenthesis
                is_comment = False
                end_idx = -1

                for idx in range(start_idx, len(self.pddl_domain)):
                    if self.pddl_domain[idx] == "(":
                        if not is_comment:
                            stack += 1
                    elif self.pddl_domain[idx] == ")":
                        if not is_comment:
                            stack -= 1
                    elif self.pddl_domain[idx] == ";":
                        is_comment = True
                    elif self.pddl_domain[idx] == "\n":
                        is_comment = False

                    if stack <= 0:
                        end_idx = idx + 1
                        break

                assert end_idx != -1
                end_idxs += [end_idx]

            return start_idxs, end_idxs

        def extract_predicates(substr: str):
            stack = 0
            start_idx = -1
            is_comment = False

            predicates = []

            for i in range(0, len(substr)):
                if substr[i] == "(":
                    if not is_comment:
                        stack += 1

                        if stack == 1:
                            start_idx = i
                elif substr[i] == ")":
                    if not is_comment:
                        stack -= 1

                        if stack <= 0 and start_idx >= 0:
                            predicates += [substr[start_idx: i+1]]

                elif substr[i] == ";":
                    is_comment = True

                elif substr[i] == "\n":
                    is_comment = False
                    stack = 0
                    start_idx = -1

            return predicates

        # get action strs
        start_idxs, end_idxs = get_start_end_idxs()
        self.pddl_actions = []

        for start_idx, end_idx in zip(start_idxs, end_idxs):
            self.pddl_actions += [self.pddl_domain[start_idx:end_idx]]

        # parse actions
        parameters_pattern = re.compile(r":parameters\s*(\(.*?\))", re.MULTILINE)
        #precondition_pattern = re.compile(r"\s*(\(.*?\))\s*", re.MULTILINE)
        #effect_pattern = re.compile(r"\s*(\(.*?\))\s*", re.MULTILINE)
        self.actions = []

        for pddl_action in self.pddl_actions:
            parameters = parameters_pattern.findall(pddl_action)[0]

            prec_start_idx = pddl_action.index(":precondition")
            prec_end_idx = pddl_action.index(":effect")
            precondition = extract_predicates(pddl_action[prec_start_idx:prec_end_idx])

            eff_start_idx = pddl_action.index(":effect")
            effect = extract_predicates(pddl_action[eff_start_idx:])

            self.actions += [{
                "action": pddl_action,
                "name": pddl_action.strip().split()[1],
                "parameters": parameters,
                "precondition": precondition,
                "effect": effect
            }]

        self.name2action = {}
        for action in self.actions:
            self.name2action[action["name"]] = action


def convert_bboxes(bboxes: List[Tuple[str, List[float]]]):
    """Convert json bounding boxes into string.
    Assume that a bounding box is a tuple of an object name and coordinates.
    E.g., ('apple', [x, y, w, h])
    """

    return "\n".join([
        f"- {obj}: {coords}"
        for obj, coords in bboxes
    ])


def convert_predicates(pddl_domain):
    """Convert predicates and explanations into string."""

    return "\n".join([
        f"- {pred['predicate']}: {pred['comment']}"
        for pred in pddl_domain.predicates
    ])


def convert_actions(pddl_domain):
    """Convert PDDL actions into string."""

    return "\n".join(pddl_domain.pddl_actions)


def extract_pddl(
    output_raw: str,
    part: str, # init or goal or whole
):
    """Extract PDDL initial state or goal conditions from a model output."""

    if part == "init":
        start_str = "(:init"
    elif part == "goal":
        start_str = "(:goal"
    elif part == "whole":
        start_str = "(define"
    else:
        return ""

    if start_str in output_raw:
        start_idx = output_raw.index(start_str)
    else:
        return ""

    end_idx = -1
    stack = 0
    is_comment = False

    for i in range(start_idx, len(output_raw)):
        if output_raw[i] == ";":
            is_comment = True
        elif output_raw[i] == "\n":
            is_comment = False
        elif output_raw[i] == "(":
            if not is_comment:
                stack += 1
        elif output_raw[i] == ")":
            if not is_comment:
                stack -= 1

        if stack <= 0:
            end_idx = i
            break

    return output_raw[start_idx:end_idx + 1] if end_idx != -1 else ""


