# RPView is a simulator of visual perception of peripheral view loss
# 2023/7/14 yuuji.kaneko.t1@dc.tohoku.ac.jp
import os
import sys
import numpy as np
import cv2

# Background subtractor class
class BgSub:
    def __init__(self):
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=120, detectShadows=False)
        self.kernel = np.ones((1, 1), np.uint8)
        self.init = False
        self.bg = None
        # use SD size image to subtract the background
        self.smaller = True

    # update background
    # call this every frame
    def update(self, frame):
        height, width, _ = frame.shape
        if not self.init:
            self.init = True
            self.bg = frame
        # create mask image by morphologyEx
        if self.smaller:
            small = cv2.resize(frame, (640, int(640.0 / width * height)))
            fgmask_s = self.fgbg.apply(small)
            fgmask_s = cv2.morphologyEx(fgmask_s, cv2.MORPH_OPEN, self.kernel)
            fgmask = cv2.resize(fgmask_s, (width, height))
        else:
            fgmask = self.fgbg.apply(frame)
            fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, self.kernel)

        # dilate mask
        dilate_kernel = np.ones((5, 5), np.uint8)
        fgmask_dilated = cv2.dilate(fgmask, dilate_kernel, iterations=1)

        # overwrite masked region(= moving object) by stored background
        self.bg = np.where(fgmask_dilated[..., None] == 0, frame, self.bg)
        return self.bg

        # draw object rectangle for debug
        # _, binary = cv2.threshold(fgmask, 1, 255, cv2.THRESH_BINARY)
        # contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # rectangles = [cv2.boundingRect(cnt) for cnt in contours]
        # filtered_rectangles = self.remove_small_rectangles(rectangles, 512)
        # image = self.bg.copy()
        # for (x, y, w, h) in filtered_rectangles:
        #     cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # return self.bg

# blur peripheral region
def apply_blur(image, radii, kernel_sizes):
    height, width, _ = image.shape
    center_x = width // 2
    center_y = height // 2
    
    for i in range(len(radii)):
        # create donuts mask
        inner_radius = radii[i]
        outer_radius = radii[i+1] if i+1 < len(radii) else 9999        
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), outer_radius, 255, -1)
        cv2.circle(mask, (center_x, center_y), inner_radius, 0, -1)
        
        kernel_size = kernel_sizes[i]
        blurred_image = cv2.blur(image, (kernel_size, kernel_size))        
        image = np.where(mask[:, :, np.newaxis] != 0, blurred_image, image)    
    return image

# draw center and peripheral image
def blend_image(image_center, image_peri, radius):
    height, width, _ = image_center.shape
    center_x = width // 2
    center_y = height // 2
    # create mask    
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask, (center_x, center_y), radius, 255, -1)
    image = np.where(mask[:, :, np.newaxis] != 0, image_center, image_peri)    
    return image

def add_suffix_to_filename(filepath, suffix):
    directory, filename = os.path.split(filepath)
    name, extension = os.path.splitext(filename)
    new_filename = name + suffix + extension
    new_filepath = os.path.join(directory, new_filename)    
    return new_filepath

# main
if len(sys.argv) < 2:
    print('Usage:', sys.argv[0], 'inout_filename')
    sys.exit(1)
inputfile = sys.argv[1]
outputfile = add_suffix_to_filename(inputfile, '-output')

if not os.path.isfile(inputfile):
    print('invalid input file', inputfile)
    sys.exit(1)

try:
    cap = cv2.VideoCapture(inputfile)
except:
    print('invalid input file', inputfile)
    sys.exit(1)
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(outputfile, fourcc, 30, (1920, 1080))

fno = 0
bgsub = BgSub()
while(1):
    # capture a frame
    fno += 1
    try:
        ret, frame = cap.read()
    except:
        print('invalid input file', inputfile)
    if not ret:
        # EOF
        break

    # update background
    bg = bgsub.update(frame)

    # blend center and peripheral(background)
    blended = blend_image(frame, bg, 450)

    # blur peripheral region
    radii = [     350, 500, 700]
    kernel_sizes = [9,  21,  59]
    blur = apply_blur(blended, radii, kernel_sizes)

    # show and fileout
    cv2.imshow('Result', blur)
    k = cv2.waitKey(1) & 0xff
    if k == 27:
        break
    # cv2.imwrite('pre_' + str(fno) + '.jpeg', frame)
    # cv2.imwrite('post_' + str(fno) + '.jpeg', blur)
    out.write(blur)

cap.release()
out.release()
cv2.destroyAllWindows()
