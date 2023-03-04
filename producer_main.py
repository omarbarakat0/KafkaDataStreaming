import threading, time
import numpy as np
from PIL import Image
import json, os
import base64
import argparse
import shutil
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic


def join_image(image1_path, image2_path):
    
    '''
    Join matching sides
    
    Parameters:
            images_path: image path of first side
            image2_path: image path of second side
            
            
    Return:
            one single image of both sides
    
    '''
    
    # load first image
    image1 = Image.open(image1_path)
    
    # load second image
    image2 = Image.open(image2_path)
    
    # rotate second image
    image2_rot = image2
    
    #load images as array
    image1_array = np.asarray(image1)[:,:,:3]
    image2_array = np.asarray(image2_rot)[:,:,:3]
    
    if image1_array.shape==image2_array.shape:
    
        #extract imageshape
        imH, _, _ = image1_array.shape

        # cut images
        face01 = image1_array[:int(imH/2)]
        face02 = image2_array[int(imH/2):]

        # merge image parts
        image = np.concatenate([face01, face02], axis=0)
        
    else:
        print("images shapes do not match")
    
    return image1, image2, image

def process_images(topic='pictures', path_to_images='./', path_to_output='../Processed_images/'):
    '''
    
    this function send images over KAFKA server once the connection is triggered
    
    Parameters:
            topic: topic of the kafka server
            path_to_images: directory of images that have to be sent over the server to the client
            path_to_output: path where the sent images will be saved
            
    Return:
            Client receied 6 images out of 10 images after processing and joining
    
    '''
    
    ###############################################################
    ###############################################################
    ###############################################################
    '''
    Image Processing
    INPUT: 10 images of all sides
    OUTPUT: 6  preprocessed images
    '''
    
    if not os.path.exists(path_to_output):
        os.makedirs(path_to_output)
    
    # join images as per their names and time stamp
    images = os.listdir(path_to_images)
    images = [f for f in images if f.endswith('.jpg')]
    imagesName = [f[:f.index('.')] for f in images]
    imagesID = [f[-6:] for f in imagesName]
    timestamps = np.unique(np.array(imagesID), return_index=False)
    
    images_original = [os.path.join(path_to_images, f) for f in images]
    
    
    list_of_images = []
    for t in timestamps:
        one_piece_images = dict()
        for image in images:
            if t in image:
                image_side = image[:image.index('_')]
                one_piece_images[image_side] = image

        list_of_images.append(one_piece_images)
        
    for list_of_one_piece_images in list_of_images:
        timestamp = list_of_one_piece_images['side1a'][list_of_one_piece_images['side1a'].index('_')+1:list_of_one_piece_images['side1a'].index('.')]
        for i in range(1, 5):
            _, _, side = join_image(image1_path=list_of_one_piece_images[f'side{i}a'],                    
                                    image2_path=list_of_one_piece_images[f'side{i}b'])

            side_image = Image.fromarray(side)
            side_image.save(f'{path_to_output}/side{i}_{timestamp}.jpg')

        shutil.copy(list_of_one_piece_images['bottomview'], path_to_output)
        shutil.copy(list_of_one_piece_images['topview'], path_to_output)
        
    ##################################################################
    ##################################################################
    ##################################################################
    
    '''
    Sending Images over the KAFKA server
    INPUT: 6 images
    RETURN: Save images at the client
    
    '''
        
    
    Files = os.listdir(path_to_output)
    Files = [os.path.join(path_to_output, f) for f in Files if not f.startswith('.') and f.endswith('.jpg')]
    images_dictionary = list()
    for image in Files:
        image_file = image
        with open(image_file, "rb") as f:
            im_bytes = f.read() 

        im_b64 = base64.b64encode(im_bytes).decode("utf8")
        payload = json.dumps({"image": im_b64, "Name": image_file})
    


        producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topic, payload)
        time.sleep(1)

        
    payload = json.dumps({"command": 'IMAGES SENT'})
    producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    producer.send('commands', payload)
    time.sleep(1)
    producer.close()
        
        
        

        
def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', type=str, default='pictures', help='define your topic')
    parser.add_argument('--path_to_images', type=str, default='./', help='path to original images')
    parser.add_argument('--path_to_output', type=str, default='../Processed_images', help='path to output')
    opt = parser.parse_args()
    
    return opt 
    
if __name__== "__main__":
    opt = parse_opt()
    process_images(**vars(opt))