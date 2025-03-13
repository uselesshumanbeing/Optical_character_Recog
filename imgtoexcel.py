import cv2
import numpy as np
import pandas as pd
import tensorflow as tf
from paddleocr import PaddleOCR

def perform_ocr(path, lang='en'):
    ocr = PaddleOCR(lang=lang)
    Output = ocr.ocr(path)[0]
    boxes = [line[0] for line in Output]
    texts = [line[1][0] for line in Output]
    probabilities = [line[1][1] for line in Output]
    return ocr, Output, boxes, texts, probabilities

def draw_text_boxes(img, boxes, texts):
    image_boxes = img.copy()
    for box, text in zip(boxes, texts):
        cv2.rectangle(image_boxes, (int(box[0][0]), int(box[0][1])), (int(box[2][0]), int(box[2][1])), (0, 0, 255), 1)
        cv2.putText(image_boxes, text, (int(box[0][0]), int(box[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (222, 0, 0), 1)
    return image_boxes

def create_horizontal_vertical_boxes(img, boxes):
    im = img.copy()
    height = img.shape[0]
    width = img.shape[1]
    horiz_boxes = []
    vert_boxes = []

    for box in boxes:
        x_h, x_v = 0, int(box[0][0])
        y_h, y_v = int(box[0][1]), 0
        width_h, width_v = width, int(box[2][0] - box[0][0])
        height_h, height_v = int(box[2][1] - box[0][1]), height

        horiz_boxes.append([x_h, y_h, x_h + width_h, y_h + height_h])
        vert_boxes.append([x_v, y_v, x_v + width_v, y_v + height_v])

        cv2.rectangle(im, (x_h, y_h), (x_h + width_h, y_h + height_h), (0, 0, 255), 1)
        cv2.rectangle(im, (x_v, y_v), (x_v + width_v, y_v + height_v), (0, 255, 0), 1)
    
    return horiz_boxes, vert_boxes, im

def apply_non_max_suppression(horiz_boxes, vert_boxes, probabilities, img):
    horiz_out = tf.image.non_max_suppression(
        horiz_boxes,
        probabilities,
        max_output_size=1000,
        iou_threshold=0.1,
        score_threshold=float('-inf'),
        name=None
    )

    horiz_lines = np.sort(np.array(horiz_out))
    
    im_nms = img.copy()
    for val in horiz_lines:
        cv2.rectangle(im_nms, (int(horiz_boxes[val][0]), int(horiz_boxes[val][1])), 
                     (int(horiz_boxes[val][2]), int(horiz_boxes[val][3])), (0, 0, 255), 1)
    
    vert_out = tf.image.non_max_suppression(
        vert_boxes,
        probabilities,
        max_output_size=1000,
        iou_threshold=0.1,
        score_threshold=float('-inf'),
        name=None
    )
    vert_lines = np.sort(np.array(vert_out))
    for val in vert_lines:
        cv2.rectangle(im_nms, (int(vert_boxes[val][0]), int(vert_boxes[val][1])), 
                     (int(vert_boxes[val][2]), int(vert_boxes[val][3])), (255, 0, 0), 1)
    
    return horiz_lines, vert_lines, im_nms

def intersection(box_1, box_2):
    return [box_2[0], box_1[1], box_2[2], box_1[3]]

def iou(box_1, box_2):
    x_1 = max(box_1[0], box_2[0])
    y_1 = max(box_1[1], box_2[1])
    x_2 = min(box_1[2], box_2[2])
    y_2 = min(box_1[3], box_2[3])

    inter = abs(max((x_2 - x_1, 0)) * max((y_2 - y_1), 0))
    if inter == 0:
        return 0
        
    box_1_area = abs((box_1[2] - box_1[0]) * (box_1[3] - box_1[1]))
    box_2_area = abs((box_2[2] - box_2[0]) * (box_2[3] - box_2[1]))
    
    return inter / float(box_1_area + box_2_area - inter)

def create_table_structure(horiz_lines, vert_lines, horiz_boxes, vert_boxes, boxes, texts):
    unordered_boxes = []
    for i in vert_lines:
        unordered_boxes.append(vert_boxes[i][0])
    ordered_boxes = np.argsort(unordered_boxes)
    
    out_array = [["" for i in range(len(vert_lines))] for j in range(len(horiz_lines))]
    
    for i in range(len(horiz_lines)):
        for j in range(len(vert_lines)):
            resultant = intersection(horiz_boxes[horiz_lines[i]], vert_boxes[vert_lines[ordered_boxes[j]]])

            for b in range(len(boxes)):
                the_box = [boxes[b][0][0], boxes[b][0][1], boxes[b][2][0], boxes[b][2][1]]
                if(iou(resultant, the_box) > 0.1):
                    out_array[i][j] = texts[b]
    
    return np.array(out_array)

def save_to_csv(out_array, output_path):
    df = pd.DataFrame(out_array, columns=out_array[0])
    df.drop(0, inplace=True, axis=0)
    df.to_csv(output_path, index=False)
    return df

def main(path,output_path):
    ocr, Output, boxes, texts, probabilities = perform_ocr(path)
    img = cv2.imread(path)
    image_boxes = draw_text_boxes(img, boxes, texts)
    horiz_boxes, vert_boxes, im = create_horizontal_vertical_boxes(img, boxes)
    horiz_lines, vert_lines, im_nms = apply_non_max_suppression(horiz_boxes, vert_boxes, probabilities, img)
    out_array = create_table_structure(horiz_lines, vert_lines, horiz_boxes, vert_boxes, boxes, texts)
    df = save_to_csv(out_array, output_path)
    print(f"CSV saved to {output_path}")
    return df