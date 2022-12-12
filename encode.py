from moviepy.editor import *
import cv2
import numpy as np

# To convert details into binary
def to_bin(data):
    """Convert `data` to binary format as string"""
    if isinstance(data, str):
        return ''.join([ format(ord(i), "08b") for i in data ])
    elif isinstance(data, bytes):
        return ''.join([ format(i, "08b") for i in data ])
    elif isinstance(data, np.ndarray):
        return [ format(i, "08b") for i in data ]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported.")

def encode(image_name, secret_data, video):
    width, height = findVideoDim(video)
    # read the image
    image = cropImage(image_name, width, height)
    # image = cv2.imread(img)
    
    # maximum bytes to encode
    n_bytes = image.shape[0] * image.shape[1] * 3 // 8

    # convert data to binary
    binary_secret_data = to_bin(secret_data)

    # size of data to hide
    data_len = len(binary_secret_data)

    print("[*] Maximum number of bits we can encode:", n_bytes*8)
    print("[*] Number of bits to encode:", data_len)

    if len(secret_data) > n_bytes:  
        raise ValueError("[!] Insufficient bytes, need bigger image or less data.")
    
    print("[+] Encoding data...")

    # add stopping criteria
    secret_data += "====="
    data_index = 0
    
    for row in image:
        for pixel in row:
            
            # convert RGB values to binary format
            r, g, b = to_bin(pixel)
            
            # modify the least significant bit only if there is still data to store
            if data_index < data_len:
                # least significant red pixel bit
                pixel[0] = int(r[:-1] + binary_secret_data[data_index], 2)
                data_index += 1
            
            if data_index < data_len:
                # least significant green pixel bit
                pixel[1] = int(g[:-1] + binary_secret_data[data_index], 2)
                data_index += 1
            
            if data_index < data_len:
                # least significant blue pixel bit
                pixel[2] = int(b[:-1] + binary_secret_data[data_index], 2)
                data_index += 1
            
            # if data is encoded, just break out of the loop
            if data_index >= data_len:
                break
    return image

def findVideoDim(video): # To find dimension of the video
    vcap = cv2.VideoCapture(video)

    if vcap.isOpened(): 
        width  = vcap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
        height = vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
        # or
        width  = round(vcap.get(3))  # float `width`
        height = round(vcap.get(4))  # float `height`
        
        print(f"[*] Dimension of the given video: {width}p x {height}p")
        
        return (width, height)
    else:
        print("[!] Error opening video ! Exiting ...")
        exit()

def cropImage(img, width, height): # To crop the image into video dimension
    image = cv2.imread(img)
    y=0
    x=0
    crop = image[y:y+height, x:x+width].copy()
    return crop

def embed(crop, video):
    vcap = cv2.VideoCapture("video.mp4")
    clip1 = ImageClip(crop, duration = 0.1)
    clip2 = VideoFileClip("video.mp4")
    final = concatenate_videoclips([clip1, clip2])
    final.write_videofile("final.mp4", fps = round(vcap.get(cv2.CAP_PROP_FPS)))
    print('[*] Encoded video is saved as "final.mp4"')
    return final

input_image = "black.png"
output_image = "encoded_image.png"
secret_data = "{ip: '106.15.25.43', email:'aaa@gmail.com'}"
video = "video.mp4"

# encode the data into the image
encoded_image = encode(image_name=input_image, secret_data=secret_data, video = video)

# save the output image (encoded image)
cv2.imwrite(output_image, encoded_image)

encoded_video = embed(output_image, video)
print('[*] Encoded data:', secret_data)