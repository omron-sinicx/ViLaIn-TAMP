import os
import base64
from pathlib import Path
from vilain import ViLaIn, PDDLProblem  # Add this with the other imports

def get_project_root() -> Path:
    """Get the absolute path to the project root directory"""
    # Get the absolute path of the current script
    current_dir = Path(__file__).resolve().parent
    # The data directory is in the ViLaIn-TAMP directory
    return current_dir.parent

if __name__ == "__main__":
    """Test ViLaIn functions"""
    ## prepare inputs
    import json

    task = "slicing"

    # Get project root directory and data paths
    project_root = get_project_root()
    print(f"Project root: {project_root}")
    
    # Data directory is directly in the ViLaIn-TAMP directory
    data_dir = project_root / "data" / "vilain_tamp_data" / "cooking"
    
    if not data_dir.exists():
        raise FileNotFoundError(
            f"Could not find data directory at:\n"
            f"  {data_dir}"
        )
    
    print(f"Using data directory: {data_dir}")
    
    # Verify the domain file exists
    domain_path = os.path.join(data_dir, "domain.pddl")
    if not os.path.exists(domain_path):
        raise FileNotFoundError(f"Domain file not found at: {domain_path}")
        
    # PDDL domain and problems
    pddl_domain_str = open(domain_path).read()

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
    #model="o1-2024-12-17"
    model_args = None

    # use Qwen-Coder
#    model = "./models/quantized/gptq-int4/qwen2.5-coder-32b-instruct"
#    model_args = {
#        "base_url": "http://localhost:22222/v1",
#        "api_key": "qwen-2-5-coder-32b-instruct",
#    }

    # use Qwen-VL
#    model = "Qwen/Qwen2.5-VL-7B-Instruct"
#
#    model_args = {
#        "base_url": "http://localhost:33333/v1",
#        "api_key": "qwen-2-5-vl-7b-instruct",
#    }

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

    mtc_trace = """
1) scan b_bot cucumber tray
2) pick b_bot cucumber tray
3) place b_bot cucumber cutting_board [FAILURE]
    """

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
