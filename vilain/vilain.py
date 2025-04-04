#!/usr/bin/env python

import json
import base64
from PIL import Image
from openai import OpenAI
from typing import Dict, List, Tuple, Optional
from io import BytesIO
import rospy
import requests

from vilain.vilain_utils import PDDLProblem, PDDLDomain
from vilain.vilain_utils import extract_pddl, process_bboxes, create_pddl_objects, remove_comments, collect_predicates
# from vilain.prompts import create_prompt_for_initial_state, create_prompt_for_goal_conditions
from vilain.prompts import create_prompt_for_object_detection, create_prompt_for_initial_state, create_prompt_for_goal_conditions
# from vilain.prompts import create_prompt_for_revision, create_prompt_for_object_detection

from vilain.prompts import create_prompt_for_PD_revision, create_prompt_for_task_planning, create_prompt_for_task_plan_revision


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

        # Add the dummy objects definition as a class variable
        self.objects_dummy_output = """(:objects
        a_bot b_bot - Robot
        cucumber - PhysicalObject
        knife - Tool
        cutting_board bowl tray knife_holder - Location
    )"""

        # Add the dummy initial state as a class variable
        self.init_dummy_output = """(:init
        (Robot b_bot)
        (Robot a_bot)
        (PhysicalObject cucumber1)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)

        (Location cutting_board)
        (Location tray)
        (Location knife_holder)
        (Location bowl)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        ; (At knife knife_holder
        (At cucumber1 tray)
    )"""

        # Add the dummy goal conditions as a class variable
        self.goal_dummy_output = """(:goal
        (and
            (Served cucumber1 bowl)
            (isSliced cucumber1)
            ; (At cucumber1 cutting_board)
        )"""

        # Add the dummy revised PDDL problem as a class variable
        self.revised_pd_dummy_output = """(define (problem cooking)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        cucumber - PhysicalObject
        knife - Tool
        cutting_board bowl tray knife_holder - Location
    )

    (:init
        (Robot b_bot)
        (Robot a_bot)
        (PhysicalObject cucumber)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)

        (Location cutting_board)
        (Location tray)
        (Location knife_holder)
        (Location mattress)

        (ToolHolder knife_holder)


        (isWorkspace cutting_board)

        (At knife knife_holder)
        (At cucumber tray)
    )

    (:goal
        (and
            (Served cucumber mattress)
            (isSliced cucumber) ; revision
        )
    ))"""

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

        # completion = self.client.chat.completions.create(**inputs)
        # output = completion.choices[0].message.content

        if any(self.model.startswith(m) for m in ("gpt-4o", "o1", "o3")):
            #TODO
            PROXY_URL = "http://10.3.162.56:11111/proxy-openai/"
            response = requests.post(PROXY_URL, json=inputs)
            output = json.loads(response.json())["choices"][0]["message"]["content"]
        else:
            completion = self.client.chat.completions.create(**inputs)
            output = completion.choices[0].message.content

        return output
    
    def detect_objects(
        self,
        image: str, # a decoded base64 image (e.g., base64.b64encode(open(path, "rb").read()).decode("utf-8")
        fixed_bboxes: List[Tuple[str, List[float]]], # object labels and their bounding boxes in [0, 1] for fixed objects
        domain: str="cooking", # domain 
        size: Tuple[int, int]=(640, 640), # resize image to (width, height)
        dummy_output: bool = False,
    ):

        if dummy_output:
            return {
                "result": self.objects_dummy_output,
                "prompt": create_prompt_for_object_detection(domain),
                "bboxes": [],
            }
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
        dummy_output: bool=False,
    ):

        if dummy_output:
            return {
                "result": self.init_dummy_output,
                "prompt": create_prompt_for_initial_state(
                    pddl_domain_str,
                    pddl_problem_obj_str,
                    bboxes,
                    examples,
                ),
            }
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
                # result = extract_pddl(output, "init")
                pddl_output = extract_pddl(output, "init")

                # TODO
                preds = collect_predicates(pddl_output, "init")
                result = "(:init\n" + "\n".join([ " " * 4 + p for p in preds ]) + "\n)"

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
        dummy_output: bool=False,
    ):
        success = False
        count = 0 # in case the output format is wrong

        if dummy_output:
            return {
                "result": self.goal_dummy_output,
                "prompt": create_prompt_for_goal_conditions(
                    pddl_domain_str,
                    pddl_problem_obj_str,
                    pddl_problem_init_str,
                    instruction,
                    examples,
                ),
            }

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
                # result = extract_pddl(output, "goal")
                pddl_output = extract_pddl(output, "goal")

                # result = result.replace("(and", "\n(and\n", 1).replace(")", ")\n") #TODO
                preds = collect_predicates(pddl_output, "goal")
                result = "(:goal\n    (and\n" + "\n".join([ " " * 8 + p for p in preds ]) + "\n    )\n)"

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
        dummy_output: bool=False
    ):
        success = False
        count = 0 # in case the output format is wrong

        if dummy_output:
            return {
                "result": self.revised_pd_dummy_output,     
                "prompt": create_prompt_for_PD_revision(
                    pddl_domain_str,
                    pddl_problem_str,
                    instruction,
                    feedback,
                    prev_feedbacks,
                    prev_revisions,
                ),
            }

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
