#!/usr/bin/env python

# Report the success rates and the number of planning attempts of primary experiments

import re
import glob

#main_dir = "primary"
main_dir = "test_results"
result_dir = f"results/{main_dir}"


for model_name in ("qwen-vl", "gpt-4o"):
    for num_icl in (0, 1, 3):
        num_trials = 0
        num_success = 0
        num_task_attempts = 0
        num_motion_attempts = 0
#        num_syntactic_correct = 0
#        num_semantic_correct = 0

        for icl_task in ("moving", "slicing", "object_collision"):
            for trial_dir in glob.glob(f"{result_dir}/primary_{model_name}_icl-task-{icl_task}_num-icl-{num_icl}_with-comments_trial-*/*/*"):
                # get the log file
                log_paths = sorted(glob.glob(f"{trial_dir}/trial_logs/*/*"))

                if len(log_paths) <= 0:
                    continue

                log_path = log_paths[-1]
                log_text = open(log_path).read()

                # get success 
                success_lines = re.findall(r"^Success: True\s*$", log_text, flags=re.MULTILINE)
                if len(success_lines) > 0:
                    num_success += 1

                # get the number of attempts
                task_plan_attempts_line = re.findall(r"(Task Planning Attempts:.*?$)", log_text, flags=re.MULTILINE)[0]
                task_plan_attempts = int(task_plan_attempts_line.split(":")[-1])

                motion_plan_attempts_line = re.findall(r"(Motion Planning Attempts:.*?$)", log_text, flags=re.MULTILINE)[0]
                motion_plan_attempts = int(motion_plan_attempts_line.split(":")[-1])

                num_task_attempts += task_plan_attempts
                num_motion_attempts += motion_plan_attempts

#                # get the generated PDDL problem
#                problem_paths = sorted(glob.glob(f"{trial_dir}/generated_problems/*/*"))
#                problem_path = problem_paths[-1]
#                all_output = open(log_path).read()
#
#                start_idx = all_output.rindex("(define")
#                end_idx = all_output.rindex("=" * 50)
#
#                final_problem = all_output[start_idx:end_idx].strip()
#
#                # get syntactic correctness and semantic_correctness
#                is_syntactic_correct, is_semantic_correct = evaluate_by_symbolic_planner(final_problem)
#                num_syntactic_correct += 1 if is_syntactic_correct else 0
#                num_semantic_correct += 1 if is_semantic_correct else 0

                # increment the number of trials
                num_trials += 1

        if num_trials > 0:
            print("#" * 50)
            print(f"Model = {model_name} / # ICL examples = {num_icl}")
            print(f"The number of trials = {num_trials}")
            print(f"Success rate = {num_success / num_trials:.2f} ({num_success} / {num_trials})")
            print(f"Average task planning attempts   = {num_task_attempts / num_trials:.2f} ({num_task_attempts} attempts / {num_trials} trials)")
            print(f"Average motion planning attempts = {num_motion_attempts / num_trials:.2f} ({num_motion_attempts} attempts / {num_trials} trials)")
#            print(f"Syntactic correctness = {num_syntactic_correct / num_trials:.2f} ({num_syntactic_correct} / {num_trials})")
#            print(f"Semantic correctness  = {num_semantic_correct / num_trials:.2f} ({num_semantic_correct} / {num_trials})")
            print()


