#!/usr/bin/env python

import json
import os
import base64
import copy
from vilain import ViLaIn
from vilain.vilain_utils import PDDLProblem


def get_project_root():
    """Get absolute path to project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    """Test ViLaIn functions"""
    # Get project root directory and data paths
    project_root = get_project_root()
    data_dir = os.path.join(project_root, "data", "vilain_data", "cooking")

    # PDDL domain and problems
    pddl_domain_str = open(os.path.join(data_dir, "domain.pddl")).read()

    pddl_problem_strs = [
        open(os.path.join(data_dir, "problems", f"problem{i}.pddl")).read()
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
        open(os.path.join(data_dir, "instructions", f"problem{i}.txt")).read()
        for i in range(1, 10+1)
    ]

    # image (scene observation) paths
    images = [
        base64.b64encode(open(os.path.join(data_dir, "observations", f"problem{i}.jpg"), "rb").read()).decode("utf-8")
        for i in range(1, 10+1)
    ]

    # bounding boxes for images
    all_bboxes = [
        [
            (key, val["bbox"])
            for key, val in json.load(open(os.path.join(data_dir, "annotated_bboxes", f"problem{i}.json"))).items()
        ]
        for i in range(1, 10+1)
    ]

    # create a model 
    model="gpt-4o-2024-11-20"
    #model="o1-2024-12-17"
    detection_model = "Qwen/Qwen2.5-VL-7B-Instruct"
    detection_args = {
        "base_url": "http://localhost:33333/v1",
        "api_key": "qwen-2-5-vl-7b-instruct",
    }

    vilain = ViLaIn(model, detection_args, detection_model)

    # test object detection
    fixed_bboxes = copy.deepcopy(all_bboxes[-1])
    obj_len = len(fixed_bboxes)

    for i in reversed(range(obj_len)):
        obj = fixed_bboxes[i][0]

        if obj in ("cucumber", "carrot", "tomato", "cutting_board", "bowl"):
            del fixed_bboxes[i]
        else:
            bbox = fixed_bboxes[i][1]
            fixed_bboxes[i] = (obj, [ b / 512 for b in bbox ])

#    # test initial state generation
    result = vilain.detect_objects(
        images[-1],
        fixed_bboxes,
        "cooking",
        (640, 640),
        dummy_detection=False,
    )

    print("-" * 30)
    print("### prompt:\n", result["prompt"])
    print("### bboxes:\n", result["bboxes"])
    print("### The generated objects:\n", result["result"])
    print()