import numpy as np
from PIL import Image
file_path = '/data/umihebi0/users/k-tanaka/adp/train_file/training/images'
image_path = file_path + '/000000.png'
im = np.array(Image.open(image_path))

print(type(im))
# <class 'numpy.ndarray'>

print(im.dtype)
# uint8

print(im.shape)
# (225, 400, 3)

#img = Image.fromarray(im, 'RGB')
#img.save('my.png')

new_image = np.zeros((370, 1224, 3))
