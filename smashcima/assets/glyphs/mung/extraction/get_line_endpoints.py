from typing import List
from smashcima.geometry.Point import Point
import numpy as np
import cv2


# Inspired by:
# https://stackoverflow.com/questions/67143809/finding-the-end-points-of-a-hand-drawn-line-with-opencv


def get_line_endpoints(mask: np.ndarray) -> List[Point]:
    """Runs an algorithm to find all endpoints of lines in the given mask.
    The input mask is a true/false (1/0) mask with uint8 type from MPP
    crop object."""
    assert len(mask.shape) == 2
    assert mask.dtype == np.uint8

    # pad the mask with one pixel wide margin of zeros
    # (this makes sure skeletonization does not break at the edges)
    # (it also resolves the 2D convolution border problems)
    mask = cv2.copyMakeBorder(mask, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)

    # get the skeleton (image of 0s and 1s)
    skeleton = cv2.ximgproc.thinning(mask * 255) // 255
    # TODO: replace the skeletonization algorithm with this one:
    # https://opencvpython.blogspot.com/2012/05/skeletonization-using-opencv-python.html
    # To get rid of the opencv-contrib-python dependency any only depend
    # on the core opencv-python package. Verify that the new algorithm
    # does not make any mistakes.
    
    # count the number of neighbors for each pixel (using a convolution)
    kernel = np.ones(shape=(3, 3), dtype=np.uint8)
    kernel[1, 1] = 0
    neighbor_count = cv2.filter2D(
        src=skeleton,
        ddepth=-1,
        kernel=kernel,
    )
    neighbor_count[skeleton != 1] = 0 # only count neighbors for skeleton pixels

    # get only the pixels where the neighbor count is 1
    neighbor_count[neighbor_count != 1] = 0

    # enumerate these points
    cv_points = cv2.findNonZero(neighbor_count)

    if cv_points is None:
        return []

    return [Point(x, y) for x, y in cv_points.squeeze(axis=1)]
