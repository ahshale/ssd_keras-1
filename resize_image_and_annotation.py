import os
import xml.etree.ElementTree as ET
import scipy.misc as misc

INPUT_HEIGHT = 2340
INPUT_WIDTH = 4160
OUTPUT_HEIGHT = 300
OUTPUT_WIDTH = 300

H_SCALE = INPUT_HEIGHT / OUTPUT_HEIGHT
W_SCALE = INPUT_WIDTH / OUTPUT_WIDTH

def resize_image_and_annotation(image_dir, ann_dir, output_image_dir, output_ann_dir):

    for dir in [output_image_dir, output_ann_dir]:
        if not os.path.exists(dir):
            os.makedirs(dir)
    
    for i, ann in enumerate(os.listdir(image_dir)):
        
        """
        # resize image
        image_file = os.path.join(image_dir, ann)
        image = misc.imread(image_file)
        image = misc.imresize(image, [OUTPUT_HEIGHT, OUTPUT_WIDTH])
        misc.imsave(os.path.join(output_image_dir, ann), image)
        """

        ann = ann.replace('.jpg', '.xml')
        try:
            tree = ET.parse(os.path.join(ann_dir, ann))
        except Exception as e:
            print(e)
            print('Ignore this bad annotation: ' + ann_dir + ann)
            continue
        
        idx = 0
        for elem in tree.iter():

            if 'object' in elem.tag:
                idx += 1
                for attr in list(elem):
                            
                    if 'bndbox' in attr.tag:
                        for dim in list(attr):
                            if 'xmin' in dim.tag:
                                dim.text = str(round(float(dim.text) / W_SCALE))
                            if 'ymin' in dim.tag:
                                dim.text = str(round(float(dim.text) / H_SCALE))
                            if 'xmax' in dim.tag:
                                dim.text = str(round(float(dim.text) / W_SCALE))
                            if 'ymax' in dim.tag:
                                dim.text = str(round(float(dim.text) / H_SCALE))

        tree.write(os.path.join(output_ann_dir, ann))

if __name__ == '__main__':
    INPUT_IMAGE_DIR = 'D:/xgl/dataset'
    INPUT_ANN_DIR = 'D:/xgl/xml'
    OUTPUT_IMAGE_DIR = 'D:/xgll/dataset/dataset_300'
    OUTPUT_ANN_DIR = 'D:/xgll/dataset/xml_300'
    resize_image_and_annotation(INPUT_IMAGE_DIR, INPUT_ANN_DIR, OUTPUT_IMAGE_DIR, OUTPUT_ANN_DIR)
    """
    trainset_file = 'D:/xgl/trainset.txt'
    valset_file = 'D:/xgl/valset.txt'
    for txt_file in [trainset_file, valset_file]:
        with open(txt_file.replace('.txt', '_300.txt'), 'w') as f:
            for line in open(txt_file, 'r'):
                f.write(line.strip().strip('.jpg') + '\n')
    """