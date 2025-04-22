
# Tutorial: Processing Model Coordinate Outputs

**Note**: For complete action space parsing, please refer to [OSWorld `uitars_agent.py`](https://github.com/xlang-ai/OSWorld/blob/main/mm_agents/uitars_agent.py). This tutorial assumes that we have already obtained the raw coordinate output from the model and will process it to determine the actual position in the image that the model intends to click.

---

## Steps:

1. **Download the Example Image**  
   Download the [example image](https://cdn-lfs-us-1.hf.co/repos/f7/27/f727ac161fcc1b2767ad196fd9a6739610be0204ccd217c0d091b018dd26ca86/d8d344455a0aeea1605888de226fd0fedf7b5218a9748a56dddef15111da7704?response-content-disposition=inline%3B+filename*%3DUTF-8%27%27output_image_13.png%3B+filename%3D%22output_image_13.png%22%3B&response-content-type=image%2Fpng&Expires=1745313853&Policy=eyJTdGF0ZW1lbnQiOlt7IkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc0NTMxMzg1M319LCJSZXNvdXJjZSI6Imh0dHBzOi8vY2RuLWxmcy11cy0xLmhmLmNvL3JlcG9zL2Y3LzI3L2Y3MjdhYzE2MWZjYzFiMjc2N2FkMTk2ZmQ5YTY3Mzk2MTBiZTAyMDRjY2QyMTdjMGQwOTFiMDE4ZGQyNmNhODYvZDhkMzQ0NDU1YTBhZWVhMTYwNTg4OGRlMjI2ZmQwZmVkZjdiNTIxOGE5NzQ4YTU2ZGRkZWYxNTExMWRhNzcwND9yZXNwb25zZS1jb250ZW50LWRpc3Bvc2l0aW9uPSomcmVzcG9uc2UtY29udGVudC10eXBlPSoifV19&Signature=m%7E02qVd%7EnnYxeep%7ECayO43YTx3V0DfQQAvJ5BnteqSyWz9lxWVGnThOXHNB2Em%7EtNycVOId9DgCsAMGiCoa3fOc9lWUq%7E3CUi99OI3x3qypbDh3aVJ%7Ea0qe8T1lZiXSNEOFRm0qc1OWnu1l%7EJzgB%7EfEMeAbalnVhjLpMt%7EeJX0hqmd2w8QXf3YaNvAC2fVuv7c9X6oWjywFhIhUCOphn0WD8HyfXqVrHv9qsj6eO61RpnI-0VLZ-PSCDpjoQ12GRAEDgfHDAS0F22vJH65h1kblfYBCPeIi2FpJwe7Me4NSpr8LxKdnKb7sfvZ7wViPMK%7ELNuNWKzVjaqzxlhEGGYA__&Key-Pair-Id=K24J24Z295AEI9) to your local machine.

2. **Visualize the Model's Output Coordinates**  
   Use the code provided below to process the model's output and visualize the coordinates on the image.

## Code Example
```python
# Assume model output
model_raw_response = """Thought: xxx
Action: click(start_box='(197,525)')"""

# Please use re to parse the coordinate values
model_output_width = 197
model_output_height = 525

from PIL import Image
import matplotlib.pyplot as plt

import json
import base64
from io import BytesIO
from PIL import Image

import math

IMAGE_FACTOR = 28
MIN_PIXELS = 100 * 28 * 28
MAX_PIXELS = 16384 * 28 * 28
MAX_RATIO = 200

VIDEO_MIN_PIXELS = 128 * 28 * 28
VIDEO_MAX_PIXELS = 768 * 28 * 28
FRAME_FACTOR = 2
FPS = 2.0
FPS_MIN_FRAMES = 4
FPS_MAX_FRAMES = 768

def round_by_factor(number: int, factor: int) -> int:
    """Returns the closest integer to 'number' that is divisible by 'factor'."""
    return round(number / factor) * factor

def ceil_by_factor(number: int, factor: int) -> int:
    """Returns the smallest integer greater than or equal to 'number' that is divisible by 'factor'."""
    return math.ceil(number / factor) * factor

def floor_by_factor(number: int, factor: int) -> int:
    """Returns the largest integer less than or equal to 'number' that is divisible by 'factor'."""
    return math.floor(number / factor) * factor

def smart_resize(
    height: int, width: int, factor: int = IMAGE_FACTOR, min_pixels: int = MIN_PIXELS, max_pixels: int = MAX_PIXELS
) -> tuple[int, int]:
    """
    Rescales the image so that the following conditions are met:

    1. Both dimensions (height and width) are divisible by 'factor'.

    2. The total number of pixels is within the range ['min_pixels', 'max_pixels'].

    3. The aspect ratio of the image is maintained as closely as possible.
    """
    if max(height, width) / min(height, width) > MAX_RATIO:
        raise ValueError(
            f"absolute aspect ratio must be smaller than {MAX_RATIO}, got {max(height, width) / min(height, width)}"
        )
    h_bar = max(factor, round_by_factor(height, factor))
    w_bar = max(factor, round_by_factor(width, factor))
    if h_bar * w_bar > max_pixels:
        beta = math.sqrt((height * width) / max_pixels)
        h_bar = floor_by_factor(height / beta, factor)
        w_bar = floor_by_factor(width / beta, factor)
    elif h_bar * w_bar < min_pixels:
        beta = math.sqrt(min_pixels / (height * width))
        h_bar = ceil_by_factor(height * beta, factor)
        w_bar = ceil_by_factor(width * beta, factor)
    return h_bar, w_bar

# Open the image
img = Image.open('./data/coordinate_process_image.png')
width, height = img.size
print(f'Original coordinate: {width}, {height}')
# Calculate the new dimensions
new_height, new_width = smart_resize(height, width)
new_coordinate = (int(model_output_width/new_width * width), int(model_output_height/new_height * height))
print(f'Resized dimensions: {new_width}, {new_height}')
print(new_coordinate)

# Display the image
plt.imshow(img)
plt.scatter([new_coordinate[0]], [new_coordinate[1]], c='red', s=50)  # Mark the point with a red dot
plt.title('Visualize Coordinate')
plt.axis('off')  # Set to 'off' to hide the axes
plt.savefig('./data/coordinate_process_image_som.png', dpi=350)
```

3. The output SOM image should look like this:

![Output SOM Image](./data/coordinate_process_image_som.png)