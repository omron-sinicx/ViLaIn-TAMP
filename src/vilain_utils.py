#!/usr/bin/env python

import os
import re
import json
import itertools
from collections import defaultdict
from typing import List, Tuple, Dict


class PDDLProblem:
    def __init__(
        self, 
        pddl_problem: str, # PDDL problem by open(pddl_problem_path).read()
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
        pddl_domain: str, # PDDL domain by open(pddl_domain_path).read()
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


def convert_predicates(pddl_domain: PDDLDomain):
    """Convert predicates and explanations into string."""

    return "\n".join([
        f"- {pred['predicate']}: {pred['comment']}"
        for pred in pddl_domain.predicates
    ])


def convert_actions(pddl_domain: PDDLDomain):
    """Convert PDDL actions into string."""

    return "\n".join(pddl_domain.pddl_actions)


def extract_json(
    output: str,
    output_format: str="brace",
):
    if output_format == "brace":
        left = "{"
        right = "}"
    elif output_format == "square":
        left = "["
        right = "]"

    start = output.index(left)
    end = None
    stack = 0

    for i in range(start, len(output)):
        if output[i] == left:
            stack += 1
        if output[i] == right:
            stack -= 1

        if stack <= 0:
            end = i
            break

    return output[start: end+1]


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


def rescale_bboxes(
    bboxes: List[Tuple[str, List[float]]],
    size: Tuple[int], # (width, height)
):
    # sanity check
    val_min = min([ min(bbox) for _, bbox in bboxes ])
    val_max = max([ max(bbox) for _, bbox in bboxes ])

    if val_min < 0 or val_max > 1:
        print("(val_min, val_max) = ", (val_min, val_max))
        raise RuntimeError("Bounding box coordinates should be in [0, 1].")

    # rescale values 
    new_bboxes = []
    width, height = size

    for label, bbox in bboxes:
        new_bbox = [
            bbox[0] * width,
            bbox[1] * height,
            bbox[2] * width,
            bbox[3] * height,
        ]

        new_bboxes += [(label, new_bbox)]

    return new_bboxes


def compute_iou(
    bbox1,
    bbox2,
):
    xmin_1, ymin_1, xmax_1, ymax_1 = bbox1
    xmin_2, ymin_2, xmax_2, ymax_2 = bbox2

    inter_xmin = max(xmin_1, xmin_2)
    inter_ymin = max(ymin_1, ymin_2)
    inter_xmax = min(xmax_1, xmax_2)
    inter_ymax = min(ymax_1, ymax_2)

    inter_width = max(0, inter_xmax - inter_xmin)
    inter_height = max(0, inter_ymax - inter_ymin)
    inter_area = inter_width * inter_height

    area1 = (xmax_1 - xmin_1) * (ymax_1 - ymin_1)
    area2 = (xmax_2 - xmin_2) * (ymax_2 - ymin_2)

    union_area = area1 + area2 - inter_area

    iou = inter_area / union_area

    return iou


def get_object_list(domain: str):
    if domain == "cooking":
        objects = [
            {"label": "cucumber", "description": "a regular cucumber."}, 
            {"label": "carrot", "description": "a regular carrot."},
            {"label": "apple", "description": "a regular apple"},
            {"label": "plate", "description": "a flat, light green or light red plate."},
            {"label": "bowl", "description": "a deep, white bowl."},
#            "cutting_board": "a square, wooden cutting board with light natural wood color.",
        ]

    return objects


def process_bboxes(
    output: str,
    fixed_bboxes: List[Tuple[str, List[float]]],
    size: Tuple[int],
    domain: str,
):
    """Extract bboxes in json from the output and post-process the generated bounding boxes"""

    # get generated bboxes
    output_json = json.loads(extract_json(output, "square"))

    objects = get_object_list(domain)

    obj_bboxes = defaultdict(list) # store bounding boxes for each object type
    all_bboxes = [] # store all bounding boxes 
    result = {}

    for x in output_json:
        bbox = x["bbox_2d"]

        if len(bbox) == 4:
            label = None

            for obj in objects:
                if x["label"].startswith(obj["label"]):
                    label = x["label"]
                    break

            if label is None:
                continue
            else:
                is_overlapped = False

                for seen_bbox in obj_bboxes[label]:
                    iou = compute_iou(bbox, seen_bbox)

                    if iou >= 0.9:
                        #print(f"{label} is overlapped: {bbox} and {seen_bbox}")
                        is_overlapped = True

                for seen_bbox in all_bboxes:
                    iou = compute_iou(bbox, seen_bbox)

                    if iou >= 0.99:
                        #print(f"{label} is overlapped: {bbox} and {seen_bbox}")
                        is_overlapped = True

                if not is_overlapped:
                    obj_label = label

                    if len(obj_bboxes[label]) > 0:
                        obj_label += str(len(obj_bboxes[label]) + 1)

                    result[obj_label] = bbox

                    obj_bboxes[label] += [bbox]
                    all_bboxes += [bbox]

    bboxes = [
        [key, result[key]]
        for key in sorted(result.keys())
    ]

    # rescale bounding boxes for fixed objects
    fixed_bboxes = rescale_bboxes(
        fixed_bboxes, 
        size,
    )

    # merge two bboxes
    bboxes = fixed_bboxes + bboxes

    return bboxes


def associate_types(
    objects: List[str],
    domain: str="cooking",
):
    objects_with_types = []

    if domain == "cooking":
        robots = ("a_bot", "b_bot")
        vegetables = ("cucumber", "carrot", "apple")
        tools = ("knife", )
        locations = ("plate", "bowl", "tray", "knife_holder", "cutting_board")

        for obj in objects:
            if obj in robots:
                objects_with_types += [(obj, "Robot")]

            elif any(len(re.findall(f"{v}\d*", obj)) > 0 for v in vegetables):
                objects_with_types += [(obj, "PhysicalObject")]

            elif any(len(re.findall(f"{v}\d*", obj)) > 0 for v in tools):
                objects_with_types += [(obj, "Tool")]

            elif any(len(re.findall(f"{v}\d*", obj)) > 0 for v in locations):
                objects_with_types += [(obj, "Location")]

    return objects_with_types


def create_pddl_objects(
    bboxes: List[Tuple[str, List[float]]],
    domain: str="cooking",
):
    objects = [ x[0] for x in bboxes ]

    objects_with_types = associate_types(
        objects, 
        domain,
    )

    type2objects = defaultdict(list)

    for obj, _type in objects_with_types:
        type2objects[_type] += [obj]

    objs_type_strs = "\n".join([
        "    " + " ".join(objs) + " - " + _type
        for _type, objs in type2objects.items()
    ])

    pddl = f"(:objects\n{objs_type_strs}\n)" 

    return pddl


def remove_comments(pddl: str):
    """Remove comments in PDDL Problem or Domain."""
    pattern = re.compile(r"(;.*?$)", re.MULTILINE)
    new_pddl = pattern.sub("", pddl)

    return new_pddl


def get_action_explanations(domain: str="cooking"):
    if domain == "cooking":
#        explanations = {
#            "scan": "The 'scan' action has 3 parameters: a robot, an object, and a location. Preconditions: The robot must be a valid robot with an empty hand, the object should be a valid physical object located at the specified location, and the object must not already be registered by the robot. Effects: After executing this action, the object becomes registered by the robot.",
#            "pick": "The 'pick' action has 3 parameters: a robot, an object, and a location. Preconditions: The robot must be a valid robot with an empty hand, the object should be a valid physical object registered to the robot and located at the specified location, and the robot must be able to reach the object. Effects: The robot starts grasping the object, the robot's hand is no longer empty, and the object is no longer at the location.",
#            "place": "The 'place' action has 3 parameters: a robot, an object, and a location. Preconditions: The robot must be a valid robot grasping an object, with the object not at the specified location, and the robot must be able to reach the object. Effects: The object is placed at the location, the robot stops grasping the object, the robot's hand becomes empty, and the object is no longer registered by the robot.",
#            "equip_tool": "The 'equip_tool' action has 4 parameters: a robot, a tool, a tool holder location, and an object. Preconditions: The robot must be a valid robot with an empty hand, the tool must be at the tool holder location, and the object is fixtured. The robot must be able to reach the tool. Effects: The robot becomes equipped with the tool, the tool is no longer at the location, and the robot's hand is no longer empty.",
#            "fixture": "The 'fixture' action has 3 parameters: a robot, an object, and a workspace location. Preconditions: The robot must be a valid robot with an empty hand, the object must be at the location, and the location must be a workspace. The robot must be able to reach the object. Effects: The object becomes fixtured, and the robot's hand is no longer empty.",
#            "slice": "The 'slice' action has 4 parameters: a robot, a tool, an object, and a workspace location. Preconditions: The robot must be equipped with the tool, and the object must be fixtured and located at a workspace. Effects: The object becomes sliced, and it is no longer registered by the robot.",
#            "unequip_tool": "The 'unequip_tool' action has 3 parameters: a robot, a tool, and a tool holder location. Preconditions: The robot must be a valid robot equipped with a tool, and there must be a tool holder at the location for the tool. Effects: The tool is placed at the location, the robot's hand becomes empty, and the robot is no longer equipped with the tool.",
#            "clean_up": "The 'clean_up' action has 2 parameters: a robot and an object. Preconditions: The robot must be a valid robot, and the object must be sliced. Effects: The object is no longer fixtured, and the robot's hand remains empty.",
#            "serve_food": "The 'serve_food' action has 3 parameters: a robot, an object, and a location. Preconditions: The robot must be a valid robot with an empty hand, the object must be sliced and not fixtured, and the robot must be able to reach the object. Effects: The object is served at the specified location."
#        }
        explanations = {
            "scan(<robot>, <obj>, <loc>)": "The 'scan' action has 3 parameters: a robot, an object, and a location. As preconditions, the robot must be a valid robot with an empty hand, the object should be a valid physical object located at the specified location, and the object must not already be registered by the robot. As effects, after executing this action, the object becomes registered by the robot.",
            "pick(<robot>, <obj>, <loc>)": "The 'pick' action has 3 parameters: a robot, an object, and a location. As preconditions, the robot must be a valid robot with an empty hand, the object should be a valid physical object registered to the robot and located at the specified location, and the robot must be able to reach the object. As effects, the robot starts grasping the object, the robot's hand is no longer empty, and the object is no longer at the location.",
            "place(<robot>, <obj>, <loc>)": "The 'place' action has 3 parameters: a robot, an object, and a location. As preconditions, the robot must be a valid robot grasping an object, with the object not at the specified location, and the robot must be able to reach the object. As effects, the object is placed at the location, the robot stops grasping the object, the robot's hand becomes empty, and the object is no longer registered by the robot.",
            "equip_tool(<robot>, <tool>, <loc>, <obj>)": "The 'equip_tool' action has 4 parameters: a robot, a tool, a tool holder location, and an object. As preconditions, the robot must be a valid robot with an empty hand, the tool must be at the tool holder location, and the object is fixtured. The robot must be able to reach the tool. As effects, the robot becomes equipped with the tool, the tool is no longer at the location, and the robot's hand is no longer empty.",
            "fixture(<robot>, <obj>, <loc>)": "The 'fixture' action has 3 parameters: a robot, an object, and a workspace location. As preconditions, the robot must be a valid robot with an empty hand, the object must be at the location, and the location must be a workspace. The robot must be able to reach the object. As effects, the object becomes fixtured, and the robot's hand is no longer empty.",
            "slice(<robot>, <tool>, <obj>, <loc>)": "The 'slice' action has 4 parameters: a robot, a tool, an object, and a workspace location. As preconditions, the robot must be equipped with the tool, and the object must be fixtured and located at a workspace. As effects, the object becomes sliced, and it is no longer registered by the robot.",
            "unequip_tool(<robot>, <tool>, <loc>)": "The 'unequip_tool' action has 3 parameters: a robot, a tool, and a tool holder location. As preconditions, the robot must be a valid robot equipped with a tool, and there must be a tool holder at the location for the tool. As effects, the tool is placed at the location, the robot's hand becomes empty, and the robot is no longer equipped with the tool.",
            "clean_up(<robot>, <obj>)": "The 'clean_up' action has 2 parameters: a robot and an object. As preconditions: The robot must be a valid robot, and the object must be sliced. As effects, the object is no longer fixtured, and the robot's hand remains empty.",
            "serve_food(<robot>, <obj>, <loc>)": "The 'serve_food' action has 3 parameters: a robot, an object, and a location. As preconditions, the robot must be a valid robot with an empty hand, the object must be sliced and not fixtured, and the robot must be able to reach the object. As effects, the object is served at the specified location."
        }

    return explanations


