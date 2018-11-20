import os
import pytesseract

import timeit
from PIL import Image, ImageEnhance



"""
--psm
0 = Orientation and script detection (OSD) only.
1 = Automatic page segmentation with OSD.
2 = Automatic page segmentation, but no OSD, or OCR.
3 = Fully automatic page segmentation, but no OSD. (Default)
4 = Assume a single column of text of variable sizes.
5 = Assume a single uniform block of vertically aligned text.
6 = Assume a single uniform block of text.
7 = Treat the image as a single text line.
8 = Treat the image as a single word.
9 = Treat the image as a single word in a circle.
10 = Treat the image as a single character.
"""


"""
image mode:
1 (1-bit pixels, black and white, stored with one pixel per byte)
L (8-bit pixels, black and white)
P (8-bit pixels, mapped to any other mode using a colour palette)
RGB (3x8-bit pixels, true colour)
RGBA (4x8-bit pixels, true colour with transparency mask)
CMYK (4x8-bit pixels, colour separation)
YCbCr (3x8-bit pixels, colour video format)
I (32-bit signed integer pixels)
F (32-bit floating point pixels)
"""

#test pytesseract save image
"""
import tempfile
from os.path import realpath, normpath, normcase
from pkgutil import find_loader
numpy_installed = find_loader('numpy') is not None
if numpy_installed:
    from numpy import ndarray


RGB_MODE = 'RGB'
def prepare(image):
    if isinstance(image, Image.Image):
        return image

    if numpy_installed and isinstance(image, ndarray):
        return Image.fromarray(image)

    raise TypeError('Unsupported image object')

def save_image(image):
    temp_name = tempfile.mktemp(prefix='tess_')
    if isinstance(image, str):
        return temp_name, realpath(normpath(normcase(image)))

    image = prepare(image)
    img_extension = image.format
    if image.format not in {'JPEG', 'PNG', 'TIFF', 'BMP', 'GIF'}:
        img_extension = 'PNG'

    if not image.mode.startswith(RGB_MODE):
        image = image.convert(RGB_MODE)

    if 'A' in image.getbands():
        # discard and replace the alpha channel with white background
        background = Image.new(RGB_MODE, image.size, (255, 255, 255))
        background.paste(image, (0, 0), image)
        image = background

    input_file_name = temp_name + os.extsep + img_extension
    image.save(input_file_name, format=img_extension, **image.info)
    return temp_name, input_file_name
"""

def resize_image_ifNeeded(image, mwidth=500, mheight=500):

    w,h = image.size
    if w <= mwidth and h <= mheight:
        #no need to resize
        return  image

    scale = 1
    if (1.0*w/mwidth) > (1.0*h/mheight):
        scale = 1.0*w/mwidth
    else:
        scale = 1.0*h/mheight
    image = image.resize((int(w/scale), int(h/scale)), Image.ANTIALIAS)

    return image

def process_image(imagePath,show="",lang=None,config="", expected=""):
    image = Image.open(imagePath)

    print('----------------')
    print("process new image:", imagePath)

    if not "dpi" in image.info:
        config +=" --dpi 120"
        dpi = (120,120)
        print("dpi:", dpi,  "size:", image.size, "image mode:", image.mode)
    else:
        print("dpi:", image.info['dpi'],  "size:", image.size, "image mode:", image.mode)

    start = timeit.default_timer()

    resizedImage = resize_image_ifNeeded(image)

    #temp_name, input_filename = save_image(image)

    text = pytesseract.image_to_string(resizedImage,lang,config)
    if text == "":
        text = pytesseract.image_to_string(resizedImage,lang,'--psm 7')

    end = timeit.default_timer()
    print('process cost:', end - start, 's')
    print('extracted text:', text)

    successful = 1
    #checkpoint
    if expected:
        if expected != text:
            print('extract fail!! ----', 'expected is: ', expected, ',actrual is: ', text)
            successful = 0
            image.show()
        elif show:
            image.show()
    return text, successful


#from skimage import transform,data
if os.sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
    tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR/tessdata"'

#Assume a single uniform block of text
tessdata_dir_config1 =  '--psm 6'
#Treat the image as a single text line.
tessdata_dir_config2 =  '--psm 7'

"""
with open("C:\\Users\\xueli\\c.txt", mode = 'rb') as output_file2:
    tt2 = output_file2.read().decode('utf-8')
    tt3 = tt2.strip()
"""    

#text = process_image("./ImageData/SignIn_verygray.png", config='', expected='SIGN IN')
#print(text)

#prepare input data
path = "./ImageData" 
files= os.listdir(path)
expectedTextList = []
with open("./expectedList.txt",mode = 'r', encoding='utf-8') as expectedLstFile:
    expectedTextList = expectedLstFile.readlines()


failedNum = 0
i = 0
for file in files:
    image = path + '/' + file
    expectedText = expectedTextList[i].rstrip()
    expectedText = expectedText.replace('\\n','\n') #escape
    i += 1

    text, success = process_image(image,  expected=expectedText)
    if success == 0:
        failedNum +=1

failedRatio = failedNum * 100 / len(files)
print("================")
print("summary:", failedNum,'/',len(files), "failed. Failure Ratio:", '%.2f' %(failedRatio),"%")


"""
image2 = "./ImageData/checkout_pay.png"
#imgry = image2.convert('L')  # enhance: convert to gray
#sharpness = ImageEnhance.Contrast(imgry)  # amplify contrast
#sharp_img = sharpness.enhance(2.0)
#sharp_img.save("./ImageData/IOS_1_Ham_Cart_Input_Button_cropped1_enhanced.png")
text = process_image(image2,config=tessdata_dir_config1, expected="CHECKOUT (PAY 179.99)")
print(text)


image3 = "./ImageData/IOS_1_Ham_Cart_Input_Button_cropped1.png"
text = process_image(image3,config=tessdata_dir_config1)
print(text)                     


image4 = "./ImageData/Login_messyBorder2.png"
text = process_image(image4,config=tessdata_dir_config1,expected="LOGIN")
print(text)  

# multiple lines of text
image4 = "./ImageData/DontHaveAccount.png"
text = process_image(image4,show = False, config=tessdata_dir_config1)
print(text)  

"""
