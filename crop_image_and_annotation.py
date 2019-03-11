import os
import copy
import xml.etree.ElementTree as ET
import scipy.misc as misc

INPUT_WIDTH = 4160
INPUT_HEIGHT = 2340
OUTPUT_HEIGHT = 300

GAP = INPUT_WIDTH - INPUT_HEIGHT

SCALE = INPUT_HEIGHT / OUTPUT_HEIGHT


def crop_and_save_image(image_dir, image_name, output_image_dir, mode):
    image_file = os.path.join(image_dir, image_name)
    image = misc.imread(image_file)
    if mode == 'left_only':
        image = image[:, :INPUT_HEIGHT, :]
        image = misc.imresize(image, [OUTPUT_HEIGHT, OUTPUT_HEIGHT])
        misc.imsave(os.path.join(output_image_dir, image_name), image)
    elif mode == 'right_only':
        image = image[:, GAP:, :]
        image = misc.imresize(image, [OUTPUT_HEIGHT, OUTPUT_HEIGHT])
        misc.imsave(os.path.join(output_image_dir, image_name), image)
    elif mode == 'left_right':
        image1 = image[:, :INPUT_HEIGHT, :]
        image2 = image[:, GAP:, :]
        image1 = misc.imresize(image1, [OUTPUT_HEIGHT, OUTPUT_HEIGHT])
        misc.imsave(os.path.join(output_image_dir, image_name.replace('.jpg', '_left.jpg')), image1)
        image2 = misc.imresize(image2, [OUTPUT_HEIGHT, OUTPUT_HEIGHT])
        misc.imsave(os.path.join(output_image_dir, image_name.replace('.jpg', '_right.jpg')), image2)


def crop_image_and_annotation(image_dir, ann_dir, output_image_dir, output_ann_dir):

    for sub_dir in [output_image_dir, output_ann_dir]:
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)
    
    for i, img in enumerate(os.listdir(image_dir)):
        
        """
        # resize image
        image_file = os.path.join(image_dir, ann)
        image = misc.imread(image_file)
        image = misc.imresize(image, [OUTPUT_HEIGHT, OUTPUT_WIDTH])
        misc.imsave(os.path.join(output_image_dir, ann), image)
        """
        ann = img.replace('.jpg', '.xml')
        try:
            tree = ET.parse(os.path.join(ann_dir, ann))
        except Exception as e:
            print(e)
            print('Ignore this bad annotation: ' + ann_dir + ann)
            continue

        # 第一次遍历得到图片中所有目标的位置
        xmin_collections = []
        xmax_collections = []
        for obj in tree.findall('object'): 
            bbox = obj.find('bndbox') 
            xmin_collections.append(int(bbox.find('xmin').text))
            xmax_collections.append(int(bbox.find('xmax').text))
        
        # 判断保留哪一部分图片
        if min(xmin_collections) >= GAP:
            crops = 'left_only'
        elif max(xmax_collections) <= 2340:
            crops = 'right_only'
        else:
            crops = 'left_right'
        
        # 裁剪图片与目标
        # left_only or right_only
        if crops == 'left_only' or crops == 'right_only':
            for obj in tree.findall('object'): 
                bbox = obj.find('bndbox') 
                # nothing to do with y coordinates
                bbox.find('ymin').text = str(round(float(bbox.find('ymin').text) / SCALE))
                bbox.find('ymax').text = str(round(float(bbox.find('ymax').text) / SCALE))
                # nothing to change with left_only
                if crops == 'left_only':
                    bbox.find('xmin').text = str(round(float(bbox.find('xmin').text) / SCALE))
                    bbox.find('xmax').text = str(round(float(bbox.find('xmax').text) / SCALE))
                # x coords should change with right only
                if crops == 'right_only':
                    bbox.find('xmin').text = str(round((float(bbox.find('xmin').text)-GAP) / SCALE))
                    bbox.find('xmax').text = str(round((float(bbox.find('xmax').text)-GAP) / SCALE))
            crop_and_save_image(image_dir, img, output_image_dir, crops)
            tree.write(os.path.join(output_ann_dir, ann))    
        
        # left and right             
        elif crops = 'left_right':
            left_tree = copy.deepcopy(tree)
            right_tree = copy.deepcopy(tree)
            # deal with left image & anno
            for obj in left_tree.findall('object'): 
                bbox = obj.find('bndbox') 
                # nothing to do with y coordinates
                bbox.find('ymin').text = str(round(float(bbox.find('ymin').text) / SCALE))
                bbox.find('ymax').text = str(round(float(bbox.find('ymax').text) / SCALE))
                xmin = int(bbox.find('xmin').text)
                xmax = int(bbox.find('xmax').text)
                if xmin >= INPUT_HEIGHT:
                    left_tree.remove(obj)
                    continue
                bbox.find('xmin').text = str(round(float(xmin) / SCALE))
                xmax = min(xmax, INPUT_HEIGHT)
                bbox.find('xmax').text = str(round(float(xmax) / SCALE))
            left_tree.write(os.path.join(output_ann_dir, ann.replace('.xml', '_left.xml')))  
            # deal with right image & anno
            for obj in right_tree.findall('object'): 
                bbox = obj.find('bndbox') 
                # nothing to do with y coordinates
                bbox.find('ymin').text = str(round(float(bbox.find('ymin').text) / SCALE))
                bbox.find('ymax').text = str(round(float(bbox.find('ymax').text) / SCALE))
                xmin = int(bbox.find('xmin').text)
                xmax = int(bbox.find('xmax').text)
                if xmax <= INPUT_HEIGHT:
                    right_tree.remove(obj)
                    continue
                bbox.find('xmax').text = str(round(float(xmax) / SCALE))
                xmin = max(xmin-GAP, 0)
                bbox.find('xmin').text = str(round(float(xmin) / SCALE))
            right_tree.write(os.path.join(output_ann_dir, ann.replace('.xml', '_right.xml')))
            # save two crops
            crop_and_save_image(image_dir, img, output_image_dir, crops)

if __name__ == '__main__':
    INPUT_IMAGE_DIR = 'D:/xgl/dataset'
    INPUT_ANN_DIR = 'D:/xgl/xml'
    OUTPUT_IMAGE_DIR = 'D:/xgll/dataset/dataset_'+str(OUTPUT_HEIGHT)
    OUTPUT_ANN_DIR = 'D:/xgll/dataset/xml_'+str(OUTPUT_HEIGHT)
    crop_image_and_annotation(INPUT_IMAGE_DIR, INPUT_ANN_DIR, OUTPUT_IMAGE_DIR, OUTPUT_ANN_DIR)
    
    trainset_file = 'D:/xgl/trainset.txt'
    valset_file = 'D:/xgl/valset.txt'
    with open(trainset_file.replace('.txt', '_'+str(OUTPUT_HEIGHT)+'.txt'), 'w') as f:
        for line in open(trainset_file, 'r'):
            n = line.strip().strip('.jpg')
            for name in os.listdir(INPUT_IMAGE_DIR):
                if re.match(n, name):
                    f.write(n + '\n')
    with open(valset_file.replace('.txt', '_'+str(OUTPUT_HEIGHT)+'.txt'), 'w') as f:
        for line in open(valset_file, 'r'):
            n = line.strip().strip('.jpg')
            for name in os.listdir(INPUT_IMAGE_DIR):
                if re.match(n, name):
                    f.write(n + '\n')
    