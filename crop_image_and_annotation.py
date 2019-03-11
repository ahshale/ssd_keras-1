import os
import xml.etree.ElementTree as ET

INPUT_HEIGHT = 2340
INPUT_WIDTH = 4160
OUTPUT_HEIGHT = 300
OUTPUT_WIDTH = 300

INPUT_IMAGE_DIR = ''
INPUT_ANN_DIR = ''
OUTPUT_IMAGE_DIR = '' 
OUTPUT_ANN_DIR = ''


def crop_image_and_annotation(image_dir, ann_di, output_image_dir, output_ann_dir):
    
    for ann in sorted(os.listdir(ann_dir)):
        print(ann)

        try:
            tree = ET.parse(ann_dir + ann)
        except Exception as e:
            print(e)
            print('Ignore this bad annotation: ' + ann_dir + ann)
            continue
        
        idx = 0
        for elem in tree.iter():

            if 'object' in elem.tag:
                idx += 1
                for attr in list(elem):
                    if 'name' in attr.tag:
                        obj_name = attr.text
                            
                    if 'bndbox' in attr.tag:
                        for dim in list(attr):
                            if 'xmin' in dim.tag:
                                obj_xmin = int(round(float(dim.text) / resize_scale))
                            if 'ymin' in dim.tag:
                                obj_ymin = int(round(float(dim.text) / resize_scale))
                            if 'xmax' in dim.tag:
                                obj_xmax = int(round(float(dim.text) / resize_scale))
                            if 'ymax' in dim.tag:
                                obj_ymax = int(round(float(dim.text) / resize_scale))

                obj_info = [filename, obj_xmin, obj_ymin, obj_xmax, obj_ymax, obj_name]
                print(obj_info)
                csv_writer.writerow(obj_info)