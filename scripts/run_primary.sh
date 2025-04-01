#!/bin/bash

# run primary experiments with Qwen-VL and GPT-4o

#model_name="gpt-4o"
#model_name="qwen-vl"

main_dir="primary"

#for num_icl in 1 0 3; do
for num_icl in 1; do
    for model_name in "qwen-vl" "gpt-4o"; do
        # vlm server should only be launched onece
        rosrun osx_vlm_task_planning vlm_server.py --model_name ${model_name} &

        # select task (moving, slicing)
        for task in moving slicing; do

            # select problem
            for prob_i in $(seq 1 10); do

                # select ICL task
                for icl_task in moving slicing object_collision; do

                    # 3 trials for each problem
                    for trial_i in $(seq 1 3); do
                        rosrun osx_tamp run_vilain_experiment.py \
                            --main_dir ${main_dir} \
                            --exp_dir primary_${model_name}_icl-task-${icl_task}_num-icl-${num_icl}_with-comments_trial-${trial_i} \
                            --domain_name cooking \
                            --task_name ${task} \
                            --problem_name problem${prob_i} \
                            --icl_task ${icl_task} \
                            --num_icl ${num_icl} \
                            --num_retries 3 \
                            --allow_replanning 3
                    done
                done
            done
        done

        # object collision
        task=object_collision

        # select problem
        for prob_i in $(seq 1 9); do

            # select ICL task
            for icl_task in moving slicing object_collision; do

                # 3 trials for each problem
                for trial_i in $(seq 1 3); do
                    rosrun osx_tamp run_vilain_experiment.py \
                        --main_dir ${main_dir} \
                        --exp_dir primary_${model_name}_icl-task-${icl_task}_num-icl-${num_icl}_without-comments_trial-${trial_i} \
                        --domain_name cooking \
                        --task_name ${task} \
                        --problem_name problem${prob_i} \
                        --icl_task ${icl_task} \
                        --num_icl ${num_icl} \
                        --num_retries 3 \
                        --allow_replanning 3
                done
            done
        done

        # kill the vlm server
        kill %
    done
done


