#!/usr/bin/env python

from typing import List, Tuple, Dict

from vilain_utils import PDDLDomain
from vilain_utils import convert_predicates, convert_actions, convert_bboxes, get_object_list
from vilain_utils import get_action_explanations


def create_prompt_for_object_detection(domain: str):
    objects = get_object_list(domain)
#    prompt = f""" #Detect objects and output the bounding boxes in the form of [xmin, ymin, xmax, ymax]. The objects to detect are:\n{objects_str}. Output the results in JSON format where the key is an object name in string and the value is the bounding box (e.g., {{ "cucumber": [x1, y1, x2, y2], "plate": [x1, y1, x2, y2], ...}}). If multiple objects are detected for a single object type, add a number to the object name incrementally from the second object (e.g., plate, plate2, plate3, ...). Objects that do not appear in the image must not be included in the output.
#""".strip()
    prompt = f"""
Given an image showing a robotic experiment environment, detect the following objects:\n{objects}\nOutput the bounding boxes for the objects in the form of [xmin, ymin, xmax, ymax].
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
You are an agent for robot task planning. Given a linguistic instruction specifying the task and objects with types appeared in the environment, you are expected to write the desired goal conditions as a set of predicates. A predicate consists of a predicate name and its arguments, and all written predicates are assumed to be true. The predicates for the goal conditions should be predicates about target objects after completing the task. A predicate consists of a predicate name and its arguments, and written predicates are assumed to be true. Available predicates are defined as:
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


def create_prompt_for_PD_revision(
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

With the generated specification, task planner first finds a sequence of symbolic actions, and motion planner then finds a sequence of physical actions. The symbolic actions contain preconditions and effects that must be True before and after it is executed, respectively. The actions are defined as:
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
However, planning failed and returned the following feedback:
{prev_feedback}

And you revised and generated the following specification:
{prev_revision}
"""

#        # (Experimental) to see what if generating explanation and feedback (if failed) affects the results
#        prompt_2 += f"""
#However, motion planning failed and returned the following feedback:
#{prev_feedback}
#
#And you revised and generated the following specification:
#{prev_revision}
#
#By the above revision, you are expected to fix the issue as:
#{prev_explanation}
#"""

    prompt_3 = f"""
However, planning failed and returned the following feedback:
{feedback}

We assume that planning failure occurs because the problem specification is incomplete. Could you generate the revised specification?
""".strip()

    return f"{prompt_1}\n{prompt_2}\n{prompt_3}"


def create_prompt_for_task_planning(
    pddl_domain_str: str, # PDDL domain
    pddl_problem_obj_str: str, # PDDL objects
    instruction: str, # a linguistic instruction
    bboxes: List[Tuple[str, List[float]]], # a liist of tuples of an object name and coordinates
):
    pddl_domain = PDDLDomain(pddl_domain_str)
    action_explanations = "\n".join([
        f"- {k}: {v}"
        for k, v in get_action_explanations().items()
    ])

#{action_explanations}
    prompt = f"""
You are an agent that generates a plan of actions that accomplishes the task specified by a linguistic instruction. Objects for the task are given as a combination of object name and type. Locations for the objects are represented by bounding boxes.

Now the instruction is: 
{instruction}

The objects are:
{pddl_problem_obj_str}

The locations of the objects by bounding boxes are:
{convert_bboxes(bboxes)}

Available actions are defined as:
{convert_actions(pddl_domain)}

The actions have preconditions and effects that must be satisfied before and after an action. These are represneted by predicates that are defined as:
{convert_predicates(pddl_domain)}

Output the plan of actions in JSON format without further explanation. The output must be a list of actions, and the action parameters are selected from the objects. Each action is a string and the parameters must not be enclosed by "" (e.g., ["action1(argument1, argument2, ...)", ...]).
""".strip()

#The actions are represented in the form of 'action_name(parameter1, parameter2, ...)', and the parameters are selected from the objects (e.g., "pick(robot, tomato, tray)").
#Output the task plan without further explanation. Actions must be with parameters, and the parameters must be the above objects. The output must be a list of actions in JSON format, and each action must be in string (e.g., "pick(robot, tomato, plate)").
#Output the task plan completes the given instruction by using the actions defined above. The output must be a list of actions in JSON format (e.g., ["pick(...)", ...]) without further explanation.
#    prompt = f"""
#Generate a sequence of actions that accomplishes the following goal:
#"{instruction}".
#
#In the environment, the following objects exist:
#{pddl_problem_obj_str}
#
#The object locations by bounding boxes are:
#{convert_bboxes(bboxes)}
#
#Available actions are:
#{action_explanations}
#
#The output must be a list of actions in JSON format (e.g., ["action(arg1, arg2, ...)", "action(arg1, arg2, ...)", ...]).
#""".strip()

    return prompt


def create_prompt_for_task_plan_revision(
    pddl_domain_str: str, # PDDL domain
    pddl_problem_obj_str: str, # PDDL objects
    actions: List[str], # a sequence of symbolic actions
    instruction: str, # a linguistic instruction
    bboxes: List[Tuple[str, List[float]]], # a liist of tuples of an object name and coordinates
    feedback: str, # motion planning feedback for errors
    prev_feedbacks: List[str], # a list of previously obtained motion planning feedbacks
    prev_revisions: List[str], # a list of previsouly revised PDs
):
    pddl_domain = PDDLDomain(pddl_domain_str)
    action_explanations = "\n".join([
        f"- {k}: {v}"
        for k, v in get_action_explanations().items()
    ])

#{action_explanations}
    prompt_1 = f"""
You are an agent that generates a plan of actions that accomplishes the task specified by a linguistic instruction. Objects for the task are given as a combination of object name and type. Locations for the objects are represented by bounding boxes.

Now the instruction is: 
{instruction}

The objects are:
{pddl_problem_obj_str}

The locations of the objects by bounding boxes are:
{convert_bboxes(bboxes)}

Available actions are defined as:
{convert_actions(pddl_domain)}

The actions have preconditions and effects that must be satisfied before and after an action. These are represneted by predicates that are defined as:
{convert_predicates(pddl_domain)}

For the above inputs, you generated the following actions:
{actions}
""".strip()
#    prompt_1 = f"""
#Generate a sequence of actions that accomplishes the following goal:
#"{instruction}".
#
#In the environment, the following objects exist:
#{pddl_problem_obj_str}
#
#The object locations by bounding boxes are:
#{convert_bboxes(bboxes)}
#
#Available actions are:
#{action_explanations}
#
#You generated the following actinos:
#{actions}
#""".strip()

    prompt_2 = ""
    for prev_feedback, prev_revision in zip(prev_feedbacks, prev_revisions):
        prompt_2 += f"""
However, planning failed and returned the following feedback:
{prev_feedback}

And you revised and generated the following actions:
{prev_revision}
"""

    prompt_3 = f"""
However, planning failed and returned the following feedback:
{feedback}

Based on the feedback, reivse and generate a seuqnece of actions without further explanation?
""".strip()

    return f"{prompt_1}\n{prompt_2}\n{prompt_3}"