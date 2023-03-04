import threading, time
import numpy 
from PIL import Image
import json, os
import base64
import sys
import argparse
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from producer_main import process_images


def receive(topic='commands'):
    
    '''
    Initiaize connection and start sending images over the KAFKA server
    
    Parameters:
            topic: matching topic of consumer_start
            
    Return:
            Trigger sending images over the KAFKA server
    
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
        
        if command=='START':
            print('SENDING IMAGES OVER KAFKA THROUGH TOPIC: PICTURES')
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