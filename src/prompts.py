#!/usr/bin/env python

from typing import List, Tuple, Dict

from vilain_utils import PDDLDomain
from vilain_utils import convert_predicates, convert_actions, convert_bboxes


def create_prompt_for_object_detection(domain: str):
    if domain == "cooking":
        objects = {
            "cucumber": "a regular cucumber.",
            "carrot": "a regular carrot with a green stem.",
            "apple": "a regular apple, but might look like tomato",
            "plate": "a flat plate. The color is light red or light green.", 
            "bowl": "a white, deep bowl.",
            "cutting_board": "a square, wooden cutting board with light natural wood color.",
        }

        objects_str = "\n".join([ f"- '{obj}': {objects[obj]}" for obj in objects ])

        prompt = f"""
Detect objects and output the bounding boxes in the form of [xmin, ymin, xmax, ymax]. The objects to detect are:\n{objects_str}. Output the results in JSON format where the key is an object name in string and the value is the bounding box (e.g., {{ "cucumber": [x1, y1, x2, y2], "plate": [x1, y1, x2, y2], ...}}). If multiple objects are detected for a single object type, add a number to the object name incrementally from the second object (e.g., plate, plate2, plate3, ...). Objects that do not appear in the image must not be included in the output.
""".strip()

    return prompt


def create_prompt_for_initial_state(
    pddl_domain_str: str, # PDDL domain
    pddl_problem_obj_str: str, # PDDL objects
    bboxes: List[Tuple[str, List[float]]], # a liist of tuples of an object name and coordinates
    examples: List[Dict[str, str]]=[], # in-context examples
):
    pddl_domain = PDDLDomain(pddl_domain_str)

    prompt1 = f"""
You are an agent for robot task planning. Given a scene observation of image, objects with types appeared in the environment, and their locations by bounding boxes, you are expected to write the initial state of the environment as a set of predicates. A predicate consists of a predicate name and its arguments, and all written predicates are assumed to be true. Negatie predicates (e.g., (not (predicate ...)) do not appear in the initial state. Available predicates are defined as:
{convert_predicates(pddl_domain)}
""".strip()

    prompt2 = ""
    if len(examples) > 0:
        prompt2 += f"The following is input-output examples.\n"

        for i_ex, example in enumerate(examples):
            prompt2 += f"""
### Example {i_ex+1} (start)
The objects_are:
{example["pddl_problem_obj_str"]}

The bounding boxes are:
{convert_bboxes(example["bboxes"])}

The corresponding initial state is:
{example["pddl_problem_init_str"]}
### Example {i_ex+1} (end)
"""

    prompt3 = f"""
The objects are:
{pddl_problem_obj_str}

Bounding boxes are:
{convert_bboxes(bboxes)}

Could you write a set of predicates of the initial state for the given objects and locations? Theset of predicates are enclosed by '(:init' and ')' so that '(:init (predicate1 ...) (predicate2 ...) ...)'.
""".strip()

    return f"{prompt1}\n{prompt2}\n{prompt3}"


def create_prompt_for_goal_conditions(
    pddl_domain_str: str, # PDDL domain
    pddl_problem_obj_str: str, # PDDL objects
    pddl_problem_init_str: str, # PDDL initial state
    instruction: str, # a linguistic instruction
    examples: List[Dict[str, str]]=[], # in-context examples
):
    pddl_domain = PDDLDomain(pddl_domain_str)

    prompt1 = f"""
You are an agent for robot task planning. Given a linguistic instruction that specifies the task and objects with types appeared in the environment, you are expected to write the desired goal conditions as a set of predicates. A predicate consists of a predicate name and its arguments, and all written predicates are assumed to be true. The predicates for the goal conditions should be about target objects after completing the task. A predicate consists of a predicate name and its arguments, and written predicates are assumed to be true. Available predicates are defined as:
{convert_predicates(pddl_domain)}
""".strip()

    prompt2 = ""
    if len(examples) > 0:
        prompt2 += f"The following is input-output examples.\n"

        for i_ex, example in enumerate(examples):
            prompt2 += f"""
### Example {i_ex+1} (start)
The objects_are:
{example["pddl_problem_obj_str"]}

The initial state is:
{example["pddl_problem_init_str"]}

The linguistic instruction is: 
{example["instruction"]}

The corresponding goal conditions are:
{example["pddl_problem_goal_str"]}
### Example {i_ex+1} (end)
"""

    prompt3 = f"""
The objects are:
{pddl_problem_obj_str}

The initial state is:
{pddl_problem_init_str}

The linguistic instruction is: 
{instruction}

Could you write a set of predicates of the goal conditions for the given instruction and objects? The set of predicates are enclosed by '(:goal (and' and ')' so that '(:goal (and (predicate1 ...) (predicate2 ...) ...))'.
""".strip()

    return f"{prompt1}\n{prompt2}\n{prompt3}"


def create_prompt_for_revision(
    pddl_domain_str: str, # PDDL domain
    pddl_problem_str: str, # PDDL problem
    instruction: str, # a linguistic instruction
    feedback: str, # motion planning feedback for errors
    prev_feedbacks: List[str], # a list of previously obtained motion planning feedbacks
    prev_revisions: List[str], # a list of previsouly revised PDs
):
    pddl_domain = PDDLDomain(pddl_domain_str)

    prompt_1 = f"""
You are an agent for robot task planning. Given a linguistic instruction and a scene observation of image, you are expected to write a problem specification that consists of objects, the initial state of the environment, and the desired goal conditions. The initial state and the goal conditions are expressed by predicates. A predicate consists of a predicate name and its arguments, and all written predicates are assume to be true. Negative predicates (e.g., (not (predicate ...)) do not appear in the initial state. Avaiable predicates are defined as:
{convert_predicates(pddl_domain)}

With the generated specification, task planner first finds a sequence of symbolic actions, and motion planner then finds a sequence of physical actions. The symbolic actions contais preconditions and effects that must be True before and after it is executed, respectively. The actions are defined as:
{convert_actions(pddl_domain)}

Now you are given the instruction and scene observation.
The instruction is: 
{instruction}

You created the following problem specification:
{pddl_problem_str}
""".strip()

    prompt_2 = ""
    for prev_feedback, prev_revision in zip(prev_feedbacks, prev_revisions):
        prompt_2 += f"""
However, motion planning failed and returned the following feedback:
{prev_feedback}

And you revised and wrote the following specification:
{prev_revision}
"""

#        # (Experimental) to see what if generating explanation and feedback (if failed) affects the results
#        prompt_2 += f"""
#However, motion planning failed and returned the following feedback:
#{prev_feedback}
#
#And you revised and wrote the following specification:
#{prev_revision}
#
#By the above revision, you are expected to fix the issue as:
#{prev_explanation}
#"""

    prompt_3 = f"""
However, motion planning failed and returned the following feedback:
{feedback}

We assume that motion planning failure occurs because the problem specification is incomplete. Could you revise the above specification by revising the initial state or the goal conditions?
""".strip()

#    # (Experimental) to see what if generating explanation and feedback (if failed) affects the results
#    prompt_3 = f"""
#However, motion planning failed and returned the following feedback:
#{feedback}
#
#Could you (1) revise the above problem specification based on the feedback to fix the issue and (2) explain what improvments you expect with this revision? Answers to (1) and (2) must be enclosed by ``` respectively.
#""".strip()

    return f"{prompt_1}\n{prompt_2}\n{prompt_3}"


