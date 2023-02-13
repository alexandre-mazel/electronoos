import cv2.cv2 as cv2
import numpy as np

# Read the original image
IMAGES_FOLDER = "../alex_pytools/autotest_data/"
original_image = cv2.imread(IMAGES_FOLDER + "spoon.jpg")
#~ original_image = cv2.imread(IMAGES_FOLDER + "groot.jpg")
#~ original_image = cv2.imread(IMAGES_FOLDER + "screen_linkedin.png") # pas du tout ca!

# Define boundary rectangle containing the foreground object
height, width, _ = original_image.shape
left_margin_proportion = 0.3
right_margin_proportion = 0.3
up_margin_proportion = 0.1
down_margin_proportion = 0.1

boundary_rectangle = (
    int(width * left_margin_proportion),
    int(height * up_margin_proportion),
    int(width * (1 - right_margin_proportion)),
    int(height * (1 - down_margin_proportion)),
)

# Set the seed for reproducibility purposes
cv2.setRNGSeed(0)

# Initialize GrabCut mask image, that will store the segmentation results
mask = np.zeros((height, width), np.uint8)

# Arrays used by the algorithm internally
background_model = np.zeros((1, 65), np.float64)
foreground_model = np.zeros((1, 65), np.float64)

number_of_iterations = 5
#~ number_of_iterations = 10 # pas mieux

bUseMask = 0
bUseMask = 1

if bUseMask:
    # Binarize input image
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY)
    #~ show_image(gray_image, "Gray image")
    cv2.imshow("Gray image", gray_image)
    cv2.waitKey(100)

    binarized_image = cv2.adaptiveThreshold(
        gray_image,
        maxValue=1,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY,
        blockSize=9,
        C=7,
    )
    
    temp = cv2.equalizeHist( binarized_image );

    cv2.imshow("binarized_image", temp)
    cv2.waitKey(100)

    # Initialize the mask with known information
    mask = np.zeros((height, width), np.uint8)
    mask[:] = cv2.GC_PR_BGD
    mask[binarized_image == 0] = cv2.GC_FGD
    
    
mode = cv2.GC_INIT_WITH_RECT
if bUseMask:
    mode = cv2.GC_INIT_WITH_MASK

cv2.grabCut(
    img=original_image,
    mask=mask,
    rect=boundary_rectangle,
    bgdModel=background_model,
    fgdModel=foreground_model,
    iterCount=number_of_iterations,
    mode=mode,
)


grabcut_mask = np.where((mask == cv2.GC_PR_BGD) | (mask == cv2.GC_BGD), 0, 1).astype("uint8")
segmented_image = original_image.copy() * grabcut_mask[:, :, np.newaxis]

cv2.imshow("result", segmented_image)
cv2.waitKey(0)