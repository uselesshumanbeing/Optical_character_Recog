#All imports here
import pytesseract
from pytesseract import Output
import cv2
from PIL import Image
import paddleocr

def gettext(file):
    img=Image.open(file)
    txt=pytesseract.image_to_string(img)
    return txt

def saveindifferentfile(file):
    img=Image.open(file)
    data=pytesseract.image_to_data(img,output_type=Output.DICT)
    length=len(data['text'])
    for i in range(length):
        if (float(data['conf'][i]))>30:
            (x,y,width,height)=(data['left'][i],data['top'][i],data['width'][i],data['height'][i])
            cropped=img[y:y+height,x:x+width]
            if(img.size!=0):
                    data1=pytesseract.image_to_data(cropped,output_type=Output.DICT)
                    if (len(data1['text'])>0):
                        file_name_path="/Users/divypashine/College/Project/im1"+str(i)+'.jpg'
                        cv2.imwrite(file_name_path,cropped)
