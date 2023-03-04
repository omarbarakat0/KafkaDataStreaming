import threading, time
from PIL import Image
import json, os
import base64
import argparse
import shutil
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic


def start(topic='commands', command='START'):
    
    '''
    Initialize connection over KAFKA at specified topic
    
    Parameters:
            topic: topic of established connection
            command: Start the connection
            
        
    '''
    
    payload = json.dumps({"command": command})
    producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    producer.send(topic, payload)
    time.sleep(1)

           
    producer.close()
        

        
def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', type=str, default='commands', help='define your topic')
    parser.add_argument('--command', type=str, default='START', help='YOUR MESSAGE')
    opt = parser.parse_args()
    
    return opt 
    
if __name__== "__main__":
    opt = parse_opt()
    start(**vars(opt))