#!/usr/bin/env python

import json
import base64
from PIL import Image
from openai import OpenAI

from vilain.vilain_utils import PDDLProblem, PDDLDomain
from vilain.vilain_utils import extract_pddl
from vilain.prompts import create_prompt_for_initial_state, create_prompt_for_goal_conditions
from vilain.prompts import create_prompt_for_revision


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


