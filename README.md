# RPView
Peripheral Vision Loss Simulator

## jcss.py
jcss.py is a version "Hakodate" of the Peripheral Vision Loss Simulator, for 2023 Conference of Japan Cognitive Science Society.

Here is the detail parameters of image processing:
- Python: 3.8.16
- numpy: 1.24.4
- cv2: 4.8.0
- Input video format: 1920x1080 MP4, 30fps
- Output video format: 1920x1080 MP4, 30fps
  - the filename shall be: [input filename]-output.[input file extension]
- Back ground subtraction:
  - createBackgroundSubtractorMOG2()
    - history: 120
    - detectShadows: False
    - kernel: (1, 1)
- Central vision
  - radius: 400
    - It displays the raw frame image inside of this circle
- blur
  - blur()
    - apply blur to donuts region as:
      - inner_radius: 350, outer_radius: 500, kernel_size: 9x9
      - inner_radius: 500, outer_radius: 700, kernel_size: 21x21
      - inner_radius: 700, outer_radius: inf, kernel_size: 59x59
