#!/usr/bin/env python

import json
import base64
from typing import List, Tuple, Dict
from io import BytesIO
from PIL import Image
from openai import OpenAI

from vilain_utils import PDDLProblem, PDDLDomain
from vilain_utils import extract_pddl, extract_json, process_bboxes, create_pddl_objects, remove_comments
from prompts import create_prompt_for_object_detection, create_prompt_for_initial_state, create_prompt_for_goal_conditions
from prompts import create_prompt_for_PD_revision, create_prompt_for_task_planning, create_prompt_for_task_plan_revision


class ViLaIn:
    def __init__(
        self,
        model: str, # gpt-4o, o1, o3-mini
        model_args: str=None, # must be specified when using models on a vLLM server
        detection_args: Dict[str, str]=None, # OpenAI API arguments for object detection
        detection_model: str=None, # detection mdoel (e.g., "Qwen/Qwen2.5-VL-7B-Instruct")
    ):
        self.model = model
        self.model_args = model_args
        self.detection_args = detection_args
        self.detection_model = detection_model

        if model_args is not None:
            self.client = OpenAI(**model_args)
        else:
            self.client = OpenAI()

        if detection_args and detection_model:
            self.client_for_detection = OpenAI(**detection_args)

    def generate(
        self,
        content: List[Dict[str, str]],
    ):
        inputs = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ],
        }

        if not any(self.model.startswith(m) for m in ("gpt-4o", "o1", "o3")):
            inputs["max_tokens"] = 8192 #TODO

#        completion = self.client.chat.completions.create(
#            model=self.model,
#            messages=[
#                {
#                    "role": "user",
#                    "content": content,
#                }
#            ]
#        )

        completion = self.client.chat.completions.create(**inputs)

        output = completion.choices[0].message.content

        return output
    
    def detect_objects(
        self,
        image: str, # a decoded base64 image (e.g., base64.b64encode(open(path, "rb").read()).decode("utf-8")
        fixed_bboxes: List[Tuple[str, List[float]]], # object labels and their bounding boxes in [0, 1] for fixed objects
        domain: str="cooking", # domain 
        size: tuple[int]=(640, 640), # resize image to (width, height)
    ):
        if not self.client_for_detection:
            return {
                "result": "To perform object detection, please specify detection_args and " + \
                          "detection_model when instantiating ViLaIn.",
                "prompt": "",
            }

        success = False
        count = 0 # in case the output format is wrong

        while count < 5:
            try:
                # resize image
                resized_pil_image = Image.open(BytesIO(base64.b64decode(image))).convert("RGB").resize(size)
                buffer = BytesIO()
                resized_pil_image.save(buffer, "png")
                resized_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

                # get a prompt
                prompt = create_prompt_for_object_detection(domain)

                # generate bounding boxes with parameters
                # The params were recommended at https://qwen.readthedocs.io/en/latest/deployment/vllm.html 
                # (accessed on March 14, 2025)
                completion = self.client_for_detection.chat.completions.create(
                    model=self.detection_model,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{resized_image}"},
                            },
                        ],
                    }],
                    temperature=0.7,
                    top_p=0.8,
                    max_tokens=2048,
                    extra_body={
                        "repetition_penalty": 1.05,
                    },
                )

                # extract the output in json format
                output = completion.choices[0].message.content
                bboxes = process_bboxes(
                    output, 
                    fixed_bboxes,
                    size,
                    domain,
                )

                result = create_pddl_objects(bboxes, domain)

                success = True
            except Exception as e:
                result = f"The generation failed due to the following error:\n{e}"
                prompt = "N/A"

            if success:
                break
            else:
                count += 1

        return {
            "result": result,
            "prompt": prompt,
            "bboxes": bboxes,
        }

    def generate_initial_state(
        self,
        pddl_domain_str: str, # PDDL domain
        pddl_problem_obj_str: str, # PDDL objects
        bboxes: List[Tuple[str, List[float]]], # a liist of tuples of an object name and coordinates
        image: str, # a decoded base64 image (e.g., base64.b64encode(open(path, "rb").read()).decode("utf-8")
        examples: List=[], # in-context examples
        without_comments: bool=False, # if true, remove commnets in PDDL domain
    ):
        success = False
        count = 0 # in case the output format is wrong

        while count < 5:
            try:
                if without_comments:
                    pddl_domain_str = remove_comments(pddl_domain_str)

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

                if image is not None:
                    content += [{
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                    }]

                output = self.generate(content)
                result = extract_pddl(output, "init")

                success = True
            except Exception as e:
                result = f"The generation failed due to the following error:\n{e}"
                prompt = "N/A"

            if success:
                break
            else:
                count += 1

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
        examples: List=[], # in-context examples
        without_comments: bool=False, # if true, remove commnets in PDDL domain
    ):
        success = False
        count = 0 # in case the output format is wrong

        while count < 5:
            try:
                if without_comments:
                    pddl_domain_str = remove_comments(pddl_domain_str)

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

                success = True
            except Exception as e:
                result = f"The generation failed due to the following error:\n{e}"
                prompt = "N/A"

            if success:
                break
            else:
                count += 1

        return {
            "result": result,
            "prompt": prompt,
        }

    def revise_problem_description(
        self,
        pddl_domain_str: str, # PDDL domain
        pddl_problem_str: str, # an initially generated PDDL problem
        instruction: str, # a linguistic instruction
        image: str, # a decoded base64 image (e.g., base64.b64encode(open(path, "rb").read()).decode("utf-8")
        feedback: str, # motion planning feedback
        prev_feedbacks: List[str], # a list of previously provided feedbacks
        prev_revisions: List[str], # a list of previously revised PDDL problems
        without_comments: bool=False, # if true, remove commnets in PDDL domain
    ):
        success = False
        count = 0 # in case the output format is wrong

        while count < 5:
            try:
                if without_comments:
                    pddl_domain_str = remove_comments(pddl_domain_str)

                prompt = create_prompt_for_PD_revision(
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

                if image is not None:
                    content += [{
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                    }]

                output = self.generate(content)
                result = extract_pddl(output, "whole")

                success = True
            except Exception as e:
                result = f"The generation failed due to the following error:\n{e}"
                prompt = "N/A"

            if success:
                break
            else:
                count += 1

        return {
            "result": result,
            "prompt": prompt,
        }

    def generate_task_plan(
        self,
        pddl_domain_str: str, # PDDL domain
        pddl_problem_obj_str: str, # PDDL objects
        instruction: str, # a linguistic instruction
        bboxes: List[Tuple[str, List[float]]], # a liist of tuples of an object name and coordinates
        image: str, # a decoded base64 image (e.g., base64.b64encode(open(path, "rb").read()).decode("utf-8")
        without_comments: bool=False, # if true, remove commnets in PDDL domain
    ):
        success = False
        count = 0 # in case the output format is wrong

        while count < 5:
            try:
                if without_comments:
                    pddl_domain_str = remove_comments(pddl_domain_str)

                prompt = create_prompt_for_task_planning(
                    pddl_domain_str,
                    pddl_problem_obj_str,
                    instruction,
                    bboxes,
                )

                content = [{
                    "type": "text",
                    "text": prompt,
                }]

                if image is not None:
                    content += [{
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                    }]

                output = self.generate(content)
                result = extract_json(output, "square")

                success = True
            except Exception as e:
                result = f"The generation failed due to the following error:\n{e}"
                prompt = "N/A"

            if success:
                break
            else:
                count += 1

        return {
            "result": result,
            "prompt": prompt,
        }

    def revise_task_plan(
        self,
        pddl_domain_str: str, # PDDL domain
        pddl_problem_obj_str: str, # an initially generated PDDL problem
        actions: List[str], # a sequence of symbolic actions
        instruction: str, # a linguistic instruction
        bboxes: List[Tuple[str, List[float]]], # a liist of tuples of an object name and coordinates
        image: str, # a decoded base64 image (e.g., base64.b64encode(open(path, "rb").read()).decode("utf-8")
        feedback: str, # motion planning feedback
        prev_feedbacks: List[str], # a list of previously provided feedbacks
        prev_revisions: List[str], # a list of previously revised PDDL problems
        without_comments: bool=False, # if true, remove commnets in PDDL domain
    ):
        success = False
        count = 0 # in case the output format is wrong

        while count < 5:
            try:
                if without_comments:
                    pddl_domain_str = remove_comments(pddl_domain_str)

                prompt = create_prompt_for_task_plan_revision(
                    pddl_domain_str,
                    pddl_problem_obj_str,
                    actions,
                    instruction,
                    bboxes,
                    feedback,
                    prev_feedbacks,
                    prev_revisions,
                )

                content = [{
                    "type": "text",
                    "text": prompt,
                }]

                if image is not None:
                    content += [{
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                    }]

                output = self.generate(content)
                result = extract_json(output, "square")

                # if the output is list of list
                if type(result[0]) == list:
                    result = [ r[0] for r in result ]

                success = True
            except Exception as e:
                result = f"The generation failed due to the following error:\n{e}"
                prompt = "N/A"

            if success:
                break
            else:
                count += 1

        return {
            "result": result,
            "prompt": prompt,
        }


if __name__ == "__main__":
    """Test ViLaIn functions"""
    ## prepare inputs
    import json

    data_dir = "./data/vilain_tamp_data/cooking"
    task = "slicing"
    #task = "object_collision"

    # PDDL domain and problems
    pddl_domain_str = open(f"{data_dir}/domain.pddl").read()

    pddl_problem_strs = [
        #open(f"{data_dir}/{task}/problems/problem{i}.pddl").read()
        open(f"{data_dir}/{task}/problems/problem{i}.pddl").read()
        for i in range(1, 5+1)
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
        open(f"{data_dir}/{task}/instructions/problem{i}.txt").read()
        for i in range(1, 5+1)
    ]

    # image (scene observation) paths
    images = [
        base64.b64encode(open(f"{data_dir}/{task}/observations/problem{i}.png", "rb").read()).decode("utf-8")
        for i in range(1, 5+1)
    ]

    # bounding boxes for images
    all_bboxes = [
        json.load(open(f"{data_dir}/{task}/bboxes/problem{i}.json"))
        for i in range(1, 5+1)
    ]

    fixed_bboxes = json.load(open(f"{data_dir}/{task}/bboxes/fixed_objects.json"))

    # create a model 
    # use GPT
    model = "gpt-4o-2024-11-20"
    model_args = None

    # use Qwen-Coder
#    model = "./models/quantized/gptq-int4/qwen2.5-coder-32b-instruct"
#    model_args = {
#        "base_url": "http://localhost:22222/v1",
#        "api_key": "qwen-2-5-coder-32b-instruct",
#    }

    # use Qwen-VL
    model = "Qwen/Qwen2.5-VL-7B-Instruct"

    model_args = {
        "base_url": "http://localhost:33333/v1",
        "api_key": "qwen-2-5-vl-7b-instruct",
    }

    #model="o1-2024-12-17"
    detection_model = "Qwen/Qwen2.5-VL-7B-Instruct"

    detection_args = {
        "base_url": "http://localhost:33333/v1",
        "api_key": "qwen-2-5-vl-7b-instruct",
    }

    vilain = ViLaIn(model, model_args, detection_args, detection_model)


#    # test object detection
#    for i in range(5):
#        result = vilain.detect_objects(
#            images[i],
#            fixed_bboxes,
#            "cooking",
#            (640, 640),
#        )
#
#        print("-" * 30)
#        print("### prompt:\n", result["prompt"])
#        print("### bboxes:\n", result["bboxes"])
#        print("### The generated objects:\n", result["result"])
#        print()


#    # test initial state generation without image
#    result = vilain.generate_initial_state(
#        pddl_domain_str,
#        pddl_problem_obj_strs[0],
#        all_bboxes[0],
#        #None,
#        images[0],
#    )
#
#    print("-" * 30)
#    print("prompt:\n", result["prompt"])
#    print("The generated initial state:\n", result["result"])
#    print()


#    # test initial state generation without example
#    result = vilain.generate_initial_state(
#        pddl_domain_str,
#        pddl_problem_obj_strs[0],
#        all_bboxes[0],
#        images[0],
#    )
#
#    print("-" * 30)
#    print("prompt:\n", result["prompt"])
#    print("The generated initial state with an example:\n", result["result"])
#    print()


#    # test initial state generation with example
#    result = vilain.generate_initial_state(
#        pddl_domain_str,
#        pddl_problem_obj_strs[0],
#        all_bboxes[0],
#        images[0],
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


#    # test goal conditions generation without example
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


#    # test object detection, initial state generation, and goal conditions generation
#    obj_result = vilain.detect_objects(
#        images[0],
#        fixed_bboxes,
#        "cooking",
#        (640, 640),
#    )
#
#    print("-" * 30)
#    print("### prompt:\n", obj_result["prompt"])
#    print("### bboxes:\n", obj_result["bboxes"])
#    print("### The generated objects:\n", obj_result["result"])
#    print()
#
#    init_result = vilain.generate_initial_state(
#        pddl_domain_str,
#        obj_result["result"],
#        obj_result["bboxes"],
#        images[0],
#        [{
#            "pddl_problem_obj_str": pddl_problem_obj_strs[1],
#            "bboxes": all_bboxes[1],
#            "pddl_problem_init_str": pddl_problem_init_strs[1],
#        }],
#    )
#
#    print("-" * 30)
#    print("prompt:\n", init_result["prompt"])
#    print("The generated initial state with an example:\n", init_result["result"])
#    print()
#
#    goal_result = vilain.generate_goal_conditions(
#        pddl_domain_str,
#        obj_result["result"],
#        init_result["result"],
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
#    print("prompt:\n", goal_result["prompt"])
#    print("The generated goal conditions:\n", goal_result["result"])
#    print()


#    # feedback for PD revision 
#    mtc_comments = """
#Summary of stages with complete failures:
#place_2 (Place)
#  -> UnGrasp (SimpleUnGrasp)
#    -> compute ik (ComputeIK)
#      # of failures: 8
#      Failure comments:
#        1:  eef in collision: b_bot_left_inner_finger - potato
#        2:  eef in collision: b_bot_left_inner_finger - potato
#        3:  eef in collision: b_bot_left_inner_finger - potato
#        4:  eef in collision: b_bot_left_inner_finger - potato
#        5:  eef in collision: b_bot_left_inner_finger - potato
#        6:  eef in collision: b_bot_left_inner_finger - potato
#        7:  eef in collision: b_bot_left_inner_finger - potato
#        8:  eef in collision: b_bot_left_inner_finger - potato
#""".strip()
#
#    mtc_trace = """
# 1) scan b_bot cucumber tray
# 2) pick b_bot cucumber tray
# 3) place b_bot cucumber cutting_board [FAILURE]
# """.strip()
#
#    synthesized_message = """
#No feasible motion plan was found when planning for the place_2 action.
#The failure occurred due to  eef in collision: b_bot_left_inner_finger - potato.
#""".strip()
#
#    # inputs for PD revision
#    data_rev_dir = "./data/vilain_tamp_data/replanning/cooking"
#    pddl_domain_rev_str = open(f"{data_rev_dir}/domain.pddl").read()
#    pddl_problem_rev_str = open(f"{data_rev_dir}/object_collision/failure_problems/problem1.pddl").read()
#    instruction_rev = open(f"{data_rev_dir}/object_collision/instructions/problem1.txt").read()
#    image = None # do not use this time
#
#    feedback = mtc_comments # use MTC comments as feedback
#
#    # the first revision 
#    prev_feedbacks = []
#    prev_revisions = []


#    # test PD revision with MTC feedbacks (object collision case, 1st time)
#    result = vilain.revise_problem_description(
#        pddl_domain_rev_str,
#        pddl_problem_rev_str,
#        instruction_rev,
#        image,
#        feedback,
#        prev_feedbacks,
#        prev_revisions,
#    )
#
#    print("-" * 30)
#    print("prompt:\n", result["prompt"])
#    print("The revised PD (1st):\n", result["result"])
#    print()


#    # test PD revision with MTC feedbacks (object collision case, 2nd time)
#    prev_feedbacks += [feedback]
#    prev_revisions += [result["result"]]
#
#    result = vilain.revise_problem_description(
#        pddl_domain_rev_str,
#        pddl_problem_rev_str,
#        instruction_rev,
#        image,
#        feedback,
#        prev_feedbacks,
#        prev_revisions,
#    )
#
#    print("-" * 30)
#    print("prompt:\n", result["prompt"])
#    print("The revised PD (2nd):\n", result["result"])
#    print()


    # test task plan generation
    for i in range(1):
        result = vilain.generate_task_plan(
            pddl_domain_str,
            pddl_problem_obj_strs[i],
            instructions[i],
            all_bboxes[i],
            None, #images[0],
        )

        print("-" * 30)
        print("prompt:\n", result["prompt"])
        print("The generated task plan:\n", result["result"])
        print()


        # test task plan generation with a crafted feedback
        feedback = "The generated task plan does not have a valid solution."

        result2 = vilain.revise_task_plan(
            pddl_domain_str,
            pddl_problem_obj_strs[i],
            result["result"], 
            instructions[i],
            all_bboxes[i],
            None, #images[i],
            feedback,
            [],
            [],
        )

        print("-" * 30)
        print("prompt:\n", result2["prompt"])
        print("The generated task plan:\n", result2["result"])
        print()


