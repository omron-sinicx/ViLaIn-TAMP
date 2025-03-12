#!/usr/bin/env python

import json
import os
from vilain import ViLaIn
from vilain.vilain_utils import PDDLProblem

def main():
    """Test ViLaIn functions"""
    ## prepare inputs
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data", "vilain_data", "cooking")
    data_rev_dir = os.path.join(project_root, "data", "vilain_tamp_data", "replanning", "cooking")

    # PDDL domain and problems
    pddl_domain_str = open(f"{data_dir}/domain.pddl").read()

    pddl_problem_strs = [
        open(f"{data_dir}/problems/problem{i}.pddl").read()
        for i in range(1, 10+1)
    ]

    pddl_problems = [
        PDDLProblem(pddl_problem_str)
        for pddl_problem_str in pddl_problem_strs
    ]

    pddl_problem_obj_strs = [
        pddl_problem.pddl_objects
        for pddl_problem in pddl_problems
    ]

    pddl_problem_init_strs = [
        pddl_problem.pddl_initial_state
        for pddl_problem in pddl_problems
    ]

    pddl_problem_goal_strs = [
        pddl_problem.pddl_goal
        for pddl_problem in pddl_problems
    ]

    # instructions
    instructions = [
        open(f"{data_dir}/instructions/problem{i}.txt").read()
        for i in range(1, 10+1)
    ]

    # image (scene observation) paths
    image_paths = [
        f"{data_dir}/observations/problem{i}.jpg"
        for i in range(1, 10+1)
    ]

    # bounding boxes for images
    all_bboxes = [
        [
            (key, val["bbox"])
            for key, val in json.load(open(f"{data_dir}/annotated_bboxes/problem{i}.json")).items()
        ]
        for i in range(1, 10+1)
    ]

    # create a model 
    model="gpt-4o-2024-11-20"
    #model="o1-2024-12-17"
    vilain = ViLaIn(model)

    # feedback for PD revision 
    mtc_comments = """
Summary of stages with complete failures:
place_2 (Place)
  -> UnGrasp (SimpleUnGrasp)
    -> compute ik (ComputeIK)
      # of failures: 8
      Failure comments:
        1:  eef in collision: b_bot_left_inner_finger - potato
        2:  eef in collision: b_bot_left_inner_finger - potato
        3:  eef in collision: b_bot_left_inner_finger - potato
        4:  eef in collision: b_bot_left_inner_finger - potato
        5:  eef in collision: b_bot_left_inner_finger - potato
        6:  eef in collision: b_bot_left_inner_finger - potato
        7:  eef in collision: b_bot_left_inner_finger - potato
        8:  eef in collision: b_bot_left_inner_finger - potato
""".strip()

    mtc_trace = """
 1) scan b_bot cucumber tray
 2) pick b_bot cucumber tray
 3) place b_bot cucumber cutting_board [FAILURE]
 """.strip()

    synthesized_message = """
No feasible motion plan was found when planning for the place_2 action.
The failure occurred due to  eef in collision: b_bot_left_inner_finger - potato.
""".strip()

    # inputs for PD revision
    pddl_domain_rev_str = open(os.path.join(data_rev_dir, "domain.pddl")).read()
    pddl_problem_rev_str = open(os.path.join(data_rev_dir, "object_collision", "failure_problems", "problem1.pddl")).read()
    instruction_rev = open(os.path.join(data_rev_dir, "object_collision", "instructions", "problem1.txt")).read()
    image_path_rev = None # do not use this time

    feedback = mtc_comments # use MTC comments as feedback

    # the first revision 
    prev_feedbacks = []
    prev_revisions = []

    # test PD revision with MTC feedbacks (object collision case, 1st time)
    result = vilain.revise_problem_description(
        pddl_domain_rev_str,
        pddl_problem_rev_str,
        instruction_rev,
        image_path_rev,
        feedback,
        prev_feedbacks,
        prev_revisions,
    )

    print("-" * 30)
    print("prompt:\n", result["prompt"])
    print("The revised PD (1st):\n", result["result"])
    print()

    # test PD revision with MTC feedbacks (object collision case, 2nd time)
    prev_feedbacks += [feedback]
    prev_revisions += [result["result"]]

    result = vilain.revise_problem_description(
        pddl_domain_rev_str,
        pddl_problem_rev_str,
        instruction_rev,
        image_path_rev,
        feedback,
        prev_feedbacks,
        prev_revisions,
    )

    print("-" * 30)
    print("prompt:\n", result["prompt"])
    print("The revised PD (2nd):\n", result["result"])
    print()

if __name__ == "__main__":
    main() 