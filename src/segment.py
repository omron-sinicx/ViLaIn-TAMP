#!/usr/bin/env python

import json
import cv2
import base64
import supervision as sv
import numpy as np
from typing import List, Tuple, Dict
from io import BytesIO
from PIL import Image
from openai import OpenAI


def extract(output: str):
    #start = output.index("{")
    start = output.index("[")
    end = None
    stack = 0

    for i in range(start, len(output)):
        #if output[i] == "{":
        if output[i] == "[":
            stack += 1
        #if output[i] == "}":
        if output[i] == "]":
            stack -= 1

        if stack <= 0:
            end = i
            break

    return output[start: end+1]


def resize_image(
    image: str, # base64 image
    width: int=640,
    height: int=640,
):
    pil_image = Image.open(BytesIO(base64.b64decode(image))).convert("RGB").resize((width, height))
    cv2_image = cv2.cvtColor(np.array(pil_image).astype(np.uint8), cv2.COLOR_RGB2BGR)

    buffer = BytesIO()
    pil_image.save(buffer, format="PNG")
    resized_base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return pil_image, cv2_image, resized_base64_image


def detect_objects(
    detection_model,
    detection_args,
    base64_image,
    prompt,
):
    client = OpenAI(**detection_args)

    completion = client.chat.completions.create(
        model=detection_model,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
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

    output = completion.choices[0].message.content
    result = json.loads(extract(output))

    return result


def segment_whole_objects(
    image: str, # base64 image
    object_name: str, # cucumber, carrot, apple, etc.
    detection_model: str,
    detection_args: Dict[str, str],
    predictor, # SAM2 predictor
    save_path: str,
):
    prompt = f"You are a helpful assistant for object detection. Detect whole {object_name} and output the bounding boxes in the form of [xmin, ymin, xmax, ymax] in JSON format."

    pil_image, cv2_image, resized_base64_image = resize_image(image)

    result = detect_objects(
        detection_model,
        detection_args,
        resized_base64_image,
        prompt,
    )

    # get only cucumbers
    bboxes = np.array([ 
        b["bbox_2d"] 
        for b in result 
        if "cucumber" in b["label"] 
    ])

    image_bgr = cv2_image
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    height, width = image_bgr.shape[:2]

    image_bgr = cv2.resize(image_bgr, ((width, height)))
    image_rgb = cv2.resize(image_rgb, ((width, height)))

    predictor.set_image(image_rgb)

    masks, scores, logits = predictor.predict(
        box=bboxes,
        multimask_output=False
    )

    if bboxes.shape[0] != 1:
        masks = np.squeeze(masks)

    detections = sv.Detections(
        xyxy=sv.mask_to_xyxy(masks=masks),
        mask=masks.astype(bool)
    )

    box_annotator = sv.BoxAnnotator(color_lookup=sv.ColorLookup.INDEX)
    mask_annotator = sv.MaskAnnotator(color_lookup=sv.ColorLookup.INDEX)

    source_image = box_annotator.annotate(scene=image_bgr.copy(), detections=detections)
    segmented_image = mask_annotator.annotate(scene=image_bgr.copy(), detections=detections)

    cv2.imwrite(
        save_path,
        cv2.hconcat([source_image, segmented_image]),
    )


def detect_sliced_objects(
    image: str, # base64 image
    object_name: str, # cucumber, carrot, apple, etc.
    detection_model: str,
    detection_args: Dict[str, str],
    predictor, # SAM2 predictor
    save_path: str,
):
    prompt = "You are a helpful assistant for object detection. Detect cucumber slices or pieces. Output the bounding boxes in the form of [xmin, ymin, xmax, ymax] in JSON format."

    pil_image, cv2_image, resized_base64_image = resize_image(image)

    result = detect_objects(
        detection_model,
        detection_args,
        resized_base64_image,
        prompt,
    )

    # get only cucumbers
    bboxes = np.array([ 
        b["bbox_2d"] 
        for b in result 
        if "cucumber" in b["label"] 
    ])

    x_min = 1e13
    y_min = 1e13
    x_max = -1
    y_max = -1

    for b in result:
        bbox = b["bbox_2d"]
        x_min = min(x_min, bbox[0])
        y_min = min(y_min, bbox[1])
        x_max = max(x_max, bbox[2])
        y_max = max(y_max, bbox[3])

    merged_bboxes = np.array([[x_min, y_min, x_max, y_max]])

    image_bgr = cv2_image
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    height, width = image_bgr.shape[:2]

    image_bgr = cv2.resize(image_bgr, ((width, height)))
    image_rgb = cv2.resize(image_rgb, ((width, height)))

    predictor.set_image(image_rgb)
    masks, scores, logits = predictor.predict(
        box=merged_bboxes,
        multimask_output=False
    )

    box_annotator = sv.BoxAnnotator(color_lookup=sv.ColorLookup.INDEX)
    mask_annotator = sv.MaskAnnotator(color_lookup=sv.ColorLookup.INDEX)

    box_annotator = sv.BoxAnnotator(color_lookup=sv.ColorLookup.INDEX)
    mask_annotator = sv.MaskAnnotator(color_lookup=sv.ColorLookup.INDEX)

    #print("masks  = ", masks.shape)
    #print("masks2 = ", sv.mask_to_xyxy(masks=masks))
    if merged_bboxes.shape[0] != 1:
        masks = np.squeeze(masks)

    detections = sv.Detections(
        xyxy=sv.mask_to_xyxy(masks=masks),
        mask=masks.astype(bool)
    )

    def get_bounding_boxes(mask):
        # Find contours of connected components
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Get bounding boxes
        boxes = [cv2.boundingRect(cnt) for cnt in contours]  # (x, y, width, height)

        new_boxes = []
        for x, y, w, h in boxes:
            # remove very small objects
            if w * h > 25:
                new_boxes += [(x, y, x+w, y+h)]

        new_boxes = np.array(new_boxes)
        
        return new_boxes

    new_bboxes = get_bounding_boxes(masks.astype(np.uint8).squeeze(0))

    new_masks, _, _ = predictor.predict(
        box=new_bboxes,
        multimask_output=False
    )

    if new_bboxes.shape[0] != 1:
        new_masks = np.squeeze(new_masks)

    new_detections = sv.Detections(
        xyxy=sv.mask_to_xyxy(masks=new_masks),
        mask=new_masks.astype(bool)
    )

    source_image = box_annotator.annotate(scene=image_bgr.copy(), detections=detections)
    segmented_image = mask_annotator.annotate(scene=image_bgr.copy(), detections=detections)
    detected_image = box_annotator.annotate(scene=image_bgr.copy(), detections=new_detections)

    cv2.imwrite(
        save_path,
        cv2.hconcat([source_image, segmented_image, detected_image]),
    )


if __name__ == "__main__":
    import glob

    # install SAM2 by 
    #   git clone https://github.com/facebookresearch/sam2.git && cd sam2
    #   pip install -e .

    # load sam2
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator

    sam2_dir = "SOMEWHERE" # set the path that contains the SAM2 checkpoint
    CONFIG = f"configs/sam2.1/sam2.1_hiera_l.yaml" # make a direcotry "configs/sam2.1" under the SAM2 repository and place the yaml file there
    CHECKPOINT = f"{sam2_dir}/sam2.1_hiera_large.pt" 
    sam2_model = build_sam2(CONFIG, CHECKPOINT, apply_postprocessing=False)
    predictor = SAM2ImagePredictor(sam2_model)

    # args for vllm server of qwenvl
    detection_model = "Qwen/Qwen2.5-VL-7B-Instruct"
    detection_args = {
        "base_url": "http://localhost:33333/v1",
        "api_key": "qwen-2-5-vl-7b-instruct",
    }

    # segment whole cucumbers
    data_dir = "./data/misc/whole_cucumbers"

    for i_path, path in enumerate(sorted(glob.glob(f"{data_dir}/example_*png"))):
        image = Image.open(path).convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

        object_name = "cucumber" #TODO
        save_path = f"{data_dir}/segment_{i_path+1}.jpg"

        segment_whole_objects(
            base64_image,
            object_name,
            detection_model,
            detection_args,
            predictor,
            save_path,
        )

    # detect cucumber slices
    data_dir = "./data/misc/sliced_cucumbers"

    for i_path, path in enumerate(sorted(glob.glob(f"{data_dir}/example_*png"))):
        image = Image.open(path).convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

        object_name = "cucumber" #TODO
        save_path = f"{data_dir}/segment_{i_path+1}.jpg"

        detect_sliced_objects(
            base64_image,
            object_name,
            detection_model,
            detection_args,
            predictor,
            save_path,
        )


