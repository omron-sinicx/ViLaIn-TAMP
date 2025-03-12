#!/usr/bin/env python
import json
import base64
from PIL import Image
from openai import OpenAI

from vilain_utils import PDDLProblem, PDDLDomain
from vilain_utils import extract_pddl
from prompts import create_prompt_for_initial_state, create_prompt_for_goal_conditions
from prompts import create_prompt_for_revision


class ViLaIn:
    def __init__(
        self,
        model: str, # gpt-4o, o1, o3-mini
    ):
        self.client = OpenAI()
        self.model = model

    def generate(
        self,
        content: list[dict[str, str]],
    ):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ]
        )

        output = completion.choices[0].message.content

        return output
    
    def detect_objects(
        self,
        image_path: str,
    ):
        pass #TODO

    def generate_initial_state(
        self,
        pddl_domain_str: str, # PDDL domain
        pddl_problem_obj_str: str, # PDDL objects
        bboxes: list[tuple[str, list[float]]], # a liist of tuples of an object name and coordinates
        image_path: str, # an image path
        examples: list=[], # in-context examples
    ):
        try:
            prompt = create_prompt_for_initial_state(
                pddl_domain_str,
                pddl_problem_obj_str,
                bboxes,
                examples,
            )

            content = [{
                "type": "text",
                "text": prompt,
            }]

            if image_path is not None:
                base64_image = base64.b64encode(open(image_path, "rb").read()).decode("utf-8")

                content += [{
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                }]

            output = self.generate(content)
            result = extract_pddl(output, "init")
        except Exception as e:
            result = f"The generation failed due to the following error:\n{e}"
            prompt = "N/A"

        return {
            "result": result,
            "prompt": prompt,
        }

    def generate_goal_conditions(
        self,
        pddl_domain_str: str, # PDDL domain
        pddl_problem_obj_str: str, # PDDL objects
        pddl_problem_init_str: str, # PDDL initial state
        instruction: str, # a linguistic instruction
        examples: list=[], # in-context examples
    ):
        try:
            prompt = create_prompt_for_goal_conditions(
                pddl_domain_str,
                pddl_problem_obj_str,
                pddl_problem_init_str,
                instruction,
                examples,
            )

            content = [{
                "type": "text",
                "text": prompt,
            }]

            output = self.generate(content)
            result = extract_pddl(output, "goal")
        except Exception as e:
            result = f"The generation failed due to the following error:\n{e}"
            prompt = "N/A"

        return {
            "result": result,
            "prompt": prompt,
        }

    def revise_problem_description(
        self,
        pddl_domain_str: str, # PDDL domain
        pddl_problem_str: str, # an initially generated PDDL problem
        instruction: str, # a linguistic instruction
        image_path: str, # an image path
        feedback: str, # motion planning feedback
        prev_feedbacks: list[str], # a list of previously provided feedbacks
        prev_revisions: list[str], # a list of previously revised PDDL problems
    ):
        try:
            prompt = create_prompt_for_revision(
                pddl_domain_str,
                pddl_problem_str,
                instruction,
                feedback,
                prev_feedbacks,
                prev_revisions,
            )

            content = [{
                "type": "text",
                "text": prompt,
            }]

            if image_path is not None:
                base64_image = base64.b64encode(open(image_path, "rb").read()).decode("utf-8")

                content += [{
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                }]

            output = self.generate(content)
            result = extract_pddl(output, "whole")
        except Exception as e:
            result = f"The generation failed due to the following error:\n{e}"
            prompt = "N/A"

        return {
            "result": result,
            "prompt": prompt,
        }


if __name__ == "__main__":
    """Test ViLaIn functions"""
    ## prepare inputs
    import json

    data_dir = "./data/vilain_data/cooking"

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

#    # test initial state generation
#    result = vilain.generate_initial_state(
#        pddl_domain_str,
#        pddl_problem_obj_strs[0],
#        all_bboxes[0],
#        image_paths[0],
#    )
#
#    print("-" * 30)
#    print("prompt:\n", result["prompt"])
#    print("The generated initial state:\n", result["result"])
#    print()

#    # test initial state generation with example
#    result = vilain.generate_initial_state(
#        pddl_domain_str,
#        pddl_problem_obj_strs[0],
#        all_bboxes[0],
#        image_paths[0],
#        [{
#            "pddl_problem_obj_str": pddl_problem_obj_strs[1],
#            "bboxes": all_bboxes[1],
#            "pddl_problem_init_str": pddl_problem_init_strs[1],
#        }],
#    )
#
#    print("-" * 30)
#    print("prompt:\n", result["prompt"])
#    print("The generated initial state with an example:\n", result["result"])
#    print()

#    # test goal conditions generation
#    result = vilain.generate_goal_conditions(
#        pddl_domain_str,
#        pddl_problem_obj_strs[0],
#        pddl_problem_init_strs[0],
#        instructions[0],
#    )
#
#    print("-" * 30)
#    print("prompt:\n", result["prompt"])
#    print("The generated goal conditions:\n", result["result"])
#    print()

#    # test goal conditions generation with example
#    result = vilain.generate_goal_conditions(
#        pddl_domain_str,
#        pddl_problem_obj_strs[0],
#        pddl_problem_init_strs[0],
#        instructions[0],
#        [{
#            "pddl_problem_obj_str": pddl_problem_obj_strs[1],
#            "pddl_problem_init_str": pddl_problem_init_strs[1],
#            "instruction": instructions[1],
#            "pddl_problem_goal_str": pddl_problem_goal_strs[1],
#        }],
#    )
#
#    print("-" * 30)
#    print("prompt:\n", result["prompt"])
#    print("The generated goal conditions with example:\n", result["result"])
#    print()

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
    data_rev_dir = "./data/vilain_tamp_data/replanning/cooking"
    pddl_domain_rev_str = open(f"{data_rev_dir}/domain.pddl").read()
    pddl_problem_rev_str = open(f"{data_rev_dir}/object_collision/failure_problems/problem1.pddl").read()
    instruction_rev = open(f"{data_rev_dir}/object_collision/instructions/problem1.txt").read()
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



