# import packages
import cv2
import glob
import torch
import numpy as np
import time
from utils import *

import argparse
import datetime
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, DistributedSampler

import datasets
import util.misc as utils
from datasets import build_dataset, get_coco_api_from_dataset
from engine import evaluate, train_one_epoch
from models import build_model

def get_args_parser():
    parser = argparse.ArgumentParser('Set transformer detector', add_help=False)
    parser.add_argument('--lr', default=1e-4, type=float)
    parser.add_argument('--lr_backbone', default=1e-5, type=float)
    parser.add_argument('--batch_size', default=2, type=int)
    parser.add_argument('--weight_decay', default=1e-4, type=float)
    parser.add_argument('--epochs', default=300, type=int)
    parser.add_argument('--lr_drop', default=60, type=int)
    parser.add_argument('--clip_max_norm', default=0.1, type=float,
                        help='gradient clipping max norm')

    # Model parameters
    parser.add_argument('--frozen_weights', type=str, default=None,
                        help="Path to the pretrained model. If set, only the mask head will be trained")
    # * Backbone
    parser.add_argument('--backbone', default='resnet50', type=str,
                        help="Name of the convolutional backbone to use")
    parser.add_argument('--dilation', action='store_true',
                        help="If true, we replace stride with dilation in the last convolutional block (DC5)")
    parser.add_argument('--position_embedding', default='sine', type=str, choices=('sine', 'learned'),
                        help="Type of positional embedding to use on top of the image features")

    # * Transformer
    parser.add_argument('--enc_layers', default=6, type=int,
                        help="Number of encoding layers in the transformer")
    parser.add_argument('--dec_layers', default=6, type=int,
                        help="Number of decoding layers in the transformer")
    parser.add_argument('--dim_feedforward', default=2048, type=int,
                        help="Intermediate size of the feedforward layers in the transformer blocks")
    parser.add_argument('--hidden_dim', default=256, type=int,
                        help="Size of the embeddings (dimension of the transformer)")
    parser.add_argument('--dropout', default=0.1, type=float,
                        help="Dropout applied in the transformer")
    parser.add_argument('--nheads', default=8, type=int,
                        help="Number of attention heads inside the transformer's attentions")
    parser.add_argument('--num_queries', default=100, type=int,
                        help="Number of query slots")
    parser.add_argument('--pre_norm', action='store_true')

    # * Segmentation
    parser.add_argument('--masks', action='store_true',
                        help="Train segmentation head if the flag is provided")

    # Loss
    parser.add_argument('--no_aux_loss', dest='aux_loss', action='store_false',
                        help="Disables auxiliary decoding losses (loss at each layer)")
    # * Matcher
    parser.add_argument('--set_cost_class', default=1, type=float,
                        help="Class coefficient in the matching cost")
    parser.add_argument('--set_cost_bbox', default=5, type=float,
                        help="L1 box coefficient in the matching cost")
    parser.add_argument('--set_cost_giou', default=2, type=float,
                        help="giou box coefficient in the matching cost")
    # * Loss coefficients
    parser.add_argument('--mask_loss_coef', default=1, type=float)
    parser.add_argument('--dice_loss_coef', default=1, type=float)
    parser.add_argument('--bbox_loss_coef', default=5, type=float)
    parser.add_argument('--giou_loss_coef', default=2, type=float)
    parser.add_argument('--eos_coef', default=0.1, type=float,
                        help="Relative classification weight of the no-object class")

    # dataset parameters
    parser.add_argument('--dataset_file', default='coco')
    parser.add_argument('--coco_path', type=str)
    parser.add_argument('--coco_panoptic_path', type=str)
    parser.add_argument('--remove_difficult', action='store_true')

    parser.add_argument('--output_dir', default='',
                        help='path where to save, empty for no saving')
    parser.add_argument('--device', default='cuda',
                        help='device to use for training / testing')
    parser.add_argument('--seed', default=42, type=int)
    parser.add_argument('--resume', default='', help='resume from checkpoint')
    parser.add_argument('--start_epoch', default=0, type=int, metavar='N',
                        help='start epoch')
    parser.add_argument('--eval', action='store_true')
    parser.add_argument('--num_workers', default=2, type=int)

    # distributed training parameters
    parser.add_argument('--world_size', default=1, type=int,
                        help='number of distributed processes')
    parser.add_argument('--dist_url', default='env://', help='url used to set up distributed training')
    return parser
parser = argparse.ArgumentParser('DETR training and evaluation script', parents=[get_args_parser()])
args = parser.parse_args()
detr_model, criterion, postprocessors = build_model(args)

input_file = "/data/umihebi0/users/k-tanaka/adp/hongo_samples_avi/hongo_sample_1.avi"
# write to video
GENERATE_VID = True
VID_FILENAME = '/data/umihebi0/users/k-tanaka/adp/hongo_samples_avi/hongo_sample_1_detr.mp4'
fps = 338
video = None

# Get model from PyTorch hub and load it into the GPU
detr_model.load_state_dict(torch.load('./output_finetune/checkpoint.pth')['model'])
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