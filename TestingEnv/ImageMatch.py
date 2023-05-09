import cv2

# Load the image
img = cv2.imread('sample1.jpg')

# Define the template
template = cv2.imread('template.jpg')

# Match the template
result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

# Find the best match
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

# Draw a bounding box around the matched region
top_left = max_loc
bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])
cv2.rectangle(img, top_left, bottom_right, (0, 0, 255), 2)
print(min_loc,max_loc,top_left,bottom_right)

# Save the image with the drawn bounding box
cv2.imwrite('result.jpg', img)

# Display the result
#cv2.imshow('result', img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()