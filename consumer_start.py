import threading, time
import numpy 
from PIL import Image
import json, os
import base64
import argparse
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic


def receive(topic='commands'):
    
    '''
    Verify that Images have been successfuly received 
    
    '''
    
    consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                             auto_offset_reset='latest',
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')),)
    consumer.subscribe([topic])

    print('Listening ... ... ... ')
    
    for message in consumer:
        
        payload = message.value
        payload = json.loads(payload)
        command = payload['command']
        
        if command=='IMAGES SENT':
            print('IMAGES RECEIVED')
            process_images()
            
        else:
            print('COMMAND NOT RECOGNISED')
            sys.exit()
            
    print("Received !")
        
        
        
def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', type=str, default='commands', help='define your topic')
    opt = parser.parse_args()
    
    return opt 
    
if __name__== "__main__":
    opt = parse_opt()
    receive(**vars(opt))