# ComfyUI-SmartResizer
Image Resizing Node for ComfyUI that auto sets the resolution based on Model and Image Ratio

SmartResizer will take any image, regardless of size, orientation (portrait, landscape) and aspect ratio and then resize it to fit the diffusion models recommended resolutions. 

_For example, if you provide it with an image with a resolution of 3248x7876 it detects this is closer to 16:9 than 1:1 and resizes the image to 720x1280 or 480x852. If you had an image of 239x255 it would resize this to 768x768 or 512x512 as this is closer to square. Either padding or cropping will take place depending on setting._

Note: This was designed for WAN 480p and 720p models and its variants, but should work for any model with similar resolution specifications.

>Inputs

**Image** : Connect from your Load Image node.

>Settings

**Resolution Preset** : Which model you're using. This will resize to either [480x852, 852x480, 512x512] if you select 480p and [720x1280, 1280x720, 768x768] if you select 720p
**Pad_Image**: "Pad to fit (letterbox)" will add black bars to either the side to make sure your image is the correct aspect ratio without cropping the image or stretching it. "Crop" will crop the image evenly to get it to the correct aspect ratio.

>Outputs

**Image** : The new image to connect to your workflow. I recommend also adding an image preview so you can see the changes.
**Width** : the width to connect
**Height** : the height to connect
