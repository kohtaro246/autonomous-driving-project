import random
import shutil
import glob
import re
import os
import numpy as np


random.seed(1)

image_file = glob.glob('/data/umihebi0/users/k-tanaka/adp/train_file/training/images/*')
image_file.sort()
label_file = glob.glob('/data/umihebi0/users/k-tanaka/adp/train_file/training/labels/*')
label_file.sort()


numbers = list(range(7481))


random.shuffle(numbers)


with open('num_list.npy', 'wb') as f:
    np.save(f, numbers)

for i,num in enumerate(numbers):
    if i < 500:
        shutil.copy(image_file[num], '/data/umihebi0/users/k-tanaka/adp/train_file/new_training/test/images/')
        shutil.copy(label_file[num], '/data/umihebi0/users/k-tanaka/adp/train_file/new_training/test/labels/')


    else:
        shutil.copy(image_file[num], '/data/umihebi0/users/k-tanaka/adp/train_file/new_training/train/images/')
        shutil.copy(label_file[num], '/data/umihebi0/users/k-tanaka/adp/train_file/new_training/train/labels/')
