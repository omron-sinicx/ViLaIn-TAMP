#!/usr/bin/env python

import json
import base64
from PIL import Image
from openai import OpenAI

from vilain.vilain_utils import PDDLProblem, PDDLDomain
from vilain.vilain_utils import extract_pddl, process_bboxes, create_pddl_objects, remove_comments
from vilain.prompts import create_prompt_for_initial_state, create_prompt_for_goal_conditions
from vilain.prompts import create_prompt_for_revision, create_prompt_for_object_detection


class ViLaIn:
    def __init__(
        self,
        model: str, # gpt-4o, o1, o3-mini
        detection_args: dict[str, str]=None, # OpenAI API arguments for object detection
        detection_model: str=None, # detection mdoel (e.g., "Qwen/Qwen2.5-VL-7B-Instruct")
    ):
        self.model = model
        self.detection_args = detection_args
        self.detection_model = detection_model

        self.client = OpenAI()

        if detection_args and detection_model:
            self.client_for_detection = OpenAI(**detection_args)

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
        image: str, # a decoded base64 image (e.g., base64.b64encode(open(path, "rb").read()).decode("utf-8")
        fixed_bboxes: list[tuple[str, list[float]]], # object labels and their bounding boxes in [0, 1] for fixed objects
        domain: str="cooking", # domain 
        size: tuple[int]=(640, 640), # resize image to (width, height)
        dummy_detection: bool=False, # if true, return dummy bounding boxes
    ):
        if not self.client_for_detection:
            return {
                "result": "To perform object detection, please specify detection_args and " + \
                          "detection_model when instantiating ViLaIn.",
                "prompt": "",
            }

        if dummy_detection:
            # Use example output from data/temp/example_output.json
            return {
                "prompt": "Detect objects and output the bounding boxes in the form of [xmin, ymin, xmax, ymax]. The objects to detect are:\n- 'cucumber': a regular cucumber.\n- 'carrot': a regular carrot with a green stem.\n- 'apple': a regular apple, but might look like tomato\n- 'plate': a flat plate. The color is light red or light green.\n- 'bowl': a white, deep bowl.\n- 'cutting_board': a square, wooden cutting board with light natural wood color.. Output the results in JSON format where the key is an object name in string and the value is the bounding box (e.g., { \"cucumber\": [x1, y1, x2, y2], \"plate\": [x1, y1, x2, y2], ...}). If multiple objects are detected for a single object type, add a number to the object name incrementally from the second object (e.g., plate, plate2, plate3, ...). Objects that do not appear in the image must not be included in the output.",
                "result": "(:objects\n    a_bot b_bot - Robot\n    cucumber - PhysicalObject\n    knife - Tool\n    cutting_board tray plate knife_holder - Location\n)",
                "bboxes": [
                    ["knife_holder", [406.89666666666665, 363.7155555555555, 456.12666666666667, 403.37185185185183]],
                    ["tray", [236.12666666666667, 501.8370370370371, 383.05, 634.482962962963]],
                    ["knife", [373.82, 363.7155555555555, 456.12666666666667, 393.80148148148146]],
                    ["cutting_board", [292.28333333333336, 363.7155555555555, 359.97333333333336, 425.2562962962963]],
                    ["cucumber", [265.36, 503.2, 306.89666666666665, 627.6444444444445]],
                    ["a_bot", [1.5133333333333334, 1.3214814814814815, 212.2833333333333, 514.1451851851853]],
                    ["bowl", [317.66666666666663, 518.2459259259259, 371.5133333333333, 609.8666666666667]],
                    ["b_bot", [433.05, 76.53333333333333, 635.3599999999999, 564.7407407407408]]
                ]
            }

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
            )

            result = create_pddl_objects(bboxes, domain)

        except Exception as e:
            result = f"The generation failed due to the following error:\n{e}"
            prompt = "N/A"

        return {
            "result": result,
            "prompt": prompt,
            "bboxes": bboxes,
        }

    def generate_initial_state(
        self,
        pddl_domain_str: str, # PDDL domain
        pddl_problem_obj_str: str, # PDDL objects
        bboxes: list[tuple[str, list[float]]], # a liist of tuples of an object name and coordinates
        image: str, # a decoded base64 image (e.g., base64.b64encode(open(path, "rb").read()).decode("utf-8")
        examples: list=[], # in-context examples
        without_comments: bool=False, # if true, remove commnets in PDDL domain
    ):
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
        without_comments: bool=False, # if true, remove commnets in PDDL domain
    ):
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
        image: str, # a decoded base64 image (e.g., base64.b64encode(open(path, "rb").read()).decode("utf-8")
        feedback: str, # motion planning feedback
        prev_feedbacks: list[str], # a list of previously provided feedbacks
        prev_revisions: list[str], # a list of previously revised PDDL problems
        without_comments: bool=False, # if true, remove commnets in PDDL domain
    ):
        try:
            if without_comments:
                pddl_domain_str = remove_comments(pddl_domain_str)

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

            if image is not None:
                content += [{
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image}"},
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