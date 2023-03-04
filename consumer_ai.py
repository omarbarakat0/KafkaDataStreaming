import threading, time
import numpy 
from PIL import Image
import json, os
import base64
import argparse
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic


def receive(topic='pictures', path_to_output='output/'):
    
    '''
    Receive Images for further Processing into AI server
    
    Parameters:
            topic: matching topic of the publicher of the images
            path_to_output: where the imagew will be saved
            
    Return:
            Recieve image and save them at the AI server
    '''
    
    consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                             auto_offset_reset='latest',
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')),)
    consumer.subscribe([topic])

    print('Listening ... ... ... ')

    for message in consumer:
        payload = message.value
        payload = json.loads(payload)
        image_byte = payload['image']
        imageName = payload["Name"]

        image = base64.b64decode((image_byte))

        if not os.path.exists(path_to_output):
            os.makedirs(path_to_output)

        with open(f'{path_to_output}/{os.path.basename(imageName)}', 'wb') as f:
            f.write(image)

        print("Received !")
        
        
        
def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', type=str, default='pictures', help='define your topic')
    parser.add_argument('--path_to_output', type=str, default='output/', help='path to output')
    opt = parser.parse_args()
    
    return opt 
    
if __name__== "__main__":
    opt = parse_opt()
    receive(**vars(opt))