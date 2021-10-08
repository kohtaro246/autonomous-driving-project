# import packages
import cv2
import glob
import torch
import numpy as np
import time
from utils import *


input_file = "/data/umihebi0/users/k-tanaka/adp/hongo_samples_avi/hongo_sample_7.avi"
# write to video
GENERATE_VID = True
VID_FILENAME = '/data/umihebi0/users/k-tanaka/adp/hongo_samples_avi/hongo_sample_7_detr_coco.mp4'
fps = 338
video = None

# Get model from PyTorch hub and load it into the GPU
detr_model = torch.hub.load('facebookresearch/detr', 'detr_resnet101', pretrained=True)
detr_model.eval()
detr_model = detr_model.cuda()

# get list of images
#img_fnames = sorted(glob.glob(img_path))

# number of samples to try this on
#n_samples = 1000

# list of time taken in milliseconds for each frame
time_taken = []

# iterate through all the images
cap = cv2.VideoCapture(input_file)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
size = (width, height)
if (GENERATE_VID == True):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(VID_FILENAME,fourcc, fps, size)
while cap.isOpened():
    # read the image
    #img_bgr = cv2.imread(img_fname)
    #img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    # create video writer
    ret, frame = cap.read()
    #print("here")
    if ret:
        # convert to tensor and load to GPU
        img_tensor = transform(frame).unsqueeze(0).cuda()
    
        # perform inference
        pred = None
        with torch.no_grad():
            # log start time
            t_start_ms = time.time_ns() / 100000.0
            # forward pass through model
            pred = detr_model(img_tensor)
            # log end time
            t_end_ms = time.time_ns() / 100000.0
            time_taken.append(t_end_ms-t_start_ms)
        print(t_end_ms-t_start_ms)
        img_bbox = draw_bbox(frame, pred)
    
        # write to video
        if GENERATE_VID == True:
            print("generating")
            img_bbox = cv2.resize(img_bbox,size)
            video.write(img_bbox)
        
    # visualize image with bounding-box
    #cv2.imshow('img', img_bbox)
        cv2.waitKey(1)
    else:
        break
    
avg_time_taken = np.mean(time_taken)
'''
print('Tested on {} frames. Average time taken for prediction: {:.2f} ms; FPS: {:.2f}'.format(min(n_samples, len(img_fnames)),  
                                                                                              avg_time_taken, 
                                                                                              1000.0/avg_time_taken))
'''
# close all open windows
cv2.destroyAllWindows()
if GENERATE_VID == True:
    video.release()