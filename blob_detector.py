import cv2
import numpy as np
from skimage.filters import threshold_local
from config import *


def display_image(title, img):
		cv2.imshow(title, img)
		cv2.waitKey(0) & 0xFF
		cv2.destroyAllWindows()

def remove_lines(im_with_blobs, method, size = 11, off = 10):
    T = threshold_local(im_with_blobs, size, offset = off, method = method)#generic, mean, median
    im_with_blobs = (im_with_blobs > T).astype("uint8") * 255

    im_inv = (255 - im_with_blobs)
    kernel = cv2.getStructuringElement(ksize=(1, int(im_inv.shape[0] / 500)), shape=cv2.MORPH_RECT)
    horizontal_lines = cv2.morphologyEx(im_inv, cv2.MORPH_OPEN, kernel)
    horizontal_lines = (255 - horizontal_lines)
    return horizontal_lines

def detect_blobs(input_image, staffs):
    """
    Detects blobs with given parameters.
    https://www.learnopencv.com/blob-detection-using-opencv-python-c/
    """
    im_with_blobs = input_image.copy()

    horizontal_removed = remove_lines(im_with_blobs, "mean", size = 11, off = 20)
    horizontal_removed = cv2.erode(horizontal_removed, np.ones((9, 5)))    

    # return horizontal_removed

    # im_with_blobs = vertical_lines
    im_with_blobs = horizontal_removed
    im_with_blobs = cv2.cvtColor(im_with_blobs, cv2.COLOR_GRAY2BGR)

    # Set up the SimpleBlobDetector with default parameters.
    params = cv2.SimpleBlobDetector_Params()
    params.minThreshold = 10
    params.maxThreshold = 3000
    params.minDistBetweenBlobs = 0
    params.filterByArea = True
    params.minArea = 250
    params.maxArea = 700
    params.filterByCircularity = False
#     params.minCircularity = 0
    params.filterByConvexity = False
#     params.minConvexity = 0
    params.filterByInertia = False
#     params.minInertiaRatio = 0.01

    detector = cv2.SimpleBlobDetector_create(params)
#     detector = cv2.SimpleBlobDetector_create()
    keypoints = detector.detect(im_with_blobs)

    cv2.drawKeypoints(im_with_blobs, keypoints=keypoints, outImage=im_with_blobs, color=(0, 0, 255),
                      flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # cv2.imwrite("Witam.jpg", im_with_blobs)

    # return horizontal_removed, im_with_blobs

    # '''
    # Here we enumerate notes.
    # '''
    staff_diff = 3 / 5 * (staffs[0].max_range - staffs[0].min_range)
    # lista dwuelementowych list zawierających [min-diff, max+diff] - poszerzamy pięciolinię
    #
    bins = [x for sublist in [[staff.min_range - staff_diff, staff.max_range + staff_diff] for staff in staffs] for x in
            sublist]

    keypoints_staff = np.digitize([key.pt[1] for key in keypoints], bins)
    sorted_notes = sorted(list(zip(keypoints, keypoints_staff)), key=lambda tup: (tup[1], tup[0].pt[0]))

    im_with_numbers = im_with_blobs.copy()

    for idx, tup in enumerate(sorted_notes):
        cv2.putText(im_with_numbers, str(idx), (int(tup[0].pt[0]), int(tup[0].pt[1])),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1, color=(255, 0, 0))
        cv2.putText(im_with_blobs, str(tup[1]), (int(tup[0].pt[0]), int(tup[0].pt[1])),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1, color=(255, 0, 0))

    cv2.imwrite("output/8c_with_numbers.jpg", im_with_numbers)
    cv2.imwrite("output/8d_with_staff_numbers.jpg", im_with_blobs)

    print("Keypoints length : " + str(len(keypoints)))

    return horizontal_removed, im_with_blobs

    # return sorted_notes