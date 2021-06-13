import os
import glob
import random
import darknet
import time
import cv2
import numpy as np

network, class_names, class_colors = darknet.load_network(
        "./data/grayscale.cfg", #config_file
        "./data/apoli.data", #data_file
        "./data/greyscale.weights", #weights
        batch_size=1
    )

width = darknet.network_width(network)
height = darknet.network_height(network)
darknet_image = darknet.make_image(width, height, 1)


def image_detection(image, thresh):
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_resized = cv2.resize(img_gray, (width, height), interpolation = cv2.INTER_LINEAR)

    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet.detect_image(network, class_names, darknet_image, thresh=thresh)
    #darknet.free_image(darknet_image)
    image=darknet.draw_boxes(detections, image_resized, class_colors)
    cv2.imshow("image", image)
    #cv2.waitKey(0)
