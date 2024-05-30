# -*- coding: utf-8 -*-
"""
Created on Wed May 22 23:39:01 2024

@author: tlooc
"""
import cv2
import re
import pytesseract
from langdetect import detect, detect_langs
from PIL import Image
import numpy as np
import os
# Đặt đường dẫn tới Tesseract executable (nếu cần thiết, chỉ áp dụng cho Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def detect_language(text):
    try:
        langs = detect_langs(text)
        if langs:
            return [lang.lang for lang in langs]
        return None
    except:
        return None

def remove_watermark(img):
    # Xóa watermark 
    alpha = 1.99
    beta = -179
    new_img = alpha * img + beta
    new_img = np.clip(new_img, 0, 255).astype(np.uint8) 
    return new_img  
    
def crop_image(img):
    # Chuyển đổi hình ảnh sang grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Áp dụng ngưỡng để nhị phân hóa hình ảnh
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Tìm các đường viền trong hình ảnh
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pickers = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w *h
        #Chỉ lấy khung lớn
        if(area>100000): 
           pickers.append([x,y,w,h])
           #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    
    pickers = np.array(pickers)
    #khởi tạo các giá trị (mặc định là khung đầu)
    x = pickers[0][0]
    y = pickers[0][1]
    w = pickers[0][2]
    h = pickers[0][3]

    #Tìm x,y,w,h cho case nhiều khung trong hình
    if (pickers.shape[0]>1):
        for i in range(pickers.shape[0]):
            if (x > pickers[i][0]):
                x = pickers[i][0]
            if (y> pickers[i][1]):
                y = pickers[i][1]
            else:
                h = pickers[i][3]
            w += pickers[i][2]
            
    # Cắt hình ảnh theo khung hình chữ nhật
    cropped_img = img[y:y+h, x:x+w]
    return cropped_img

def extract_text_from_image(image_path, target_chars='ABCD'):
    # Đọc hình ảnh
    img = cv2.imread(image_path)
    # Xóa watermark
    new_img = remove_watermark(img)
    # Cắt ảnh và lấy các contours trong ảnh đã cắt
    cropped_img = crop_image(new_img)
    # Nhận diện văn bản sơ bộ để phát hiện ngôn ngữ
    preliminary_text = pytesseract.image_to_string(cropped_img, lang='eng')
    # Phát hiện ngôn ngữ
    detected_lang_codes = detect_language(preliminary_text)
    if detected_lang_codes:
        lang_dict = {
            'vi': 'vie',
            'en': 'eng',
            'zh-cn': 'chi_sim',
            'zh-tw': 'chi_tra',
            'ja': 'jpn',
            'ko': 'kor'
        }
        # Tạo danh sách các ngôn ngữ OCR từ các mã ngôn ngữ phát hiện được
        ocr_langs = [lang_dict.get(code, 'eng') for code in detected_lang_codes]
        ocr_langs_str = '+'.join(ocr_langs)
    else:
        ocr_langs_str = 'eng'  # Mặc định sử dụng tiếng Anh nếu không phát hiện được
    
    detected_text = []

    # Sử dụng pytesseract để nhận diện văn bản từ hình ảnh đã cắt
    text = pytesseract.image_to_string(cropped_img, lang=ocr_langs_str)
    
    # Kiểm tra nếu văn bản chứa bất kỳ ký tự nào trong target_chars
    if any(char in text for char in target_chars):
        detected_text.append(text.strip())
        # Vẽ khung hình chữ nhật xung quanh các ký tự được phát hiện
        # cv2.rectangle(new_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # Hiển thị hình ảnh với các khung chữ nhật đã được vẽ (tùy chọn)
    # cv2.imshow('Detected Characters', new_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    return detected_text, ocr_langs_str, cropped_img

#Xử lý đoạn detected_text 
def format_text(detected_text):
    string = ''.join(detected_text) #Chuyển sang string
    ban_list = ['(Choose 1 answer)\n',"|","(Choose 1 answer)"] #List ký tự cần xóa
    answer_list = ['\nA','\nB','\nC','\nD'] #List đáp án

    for char in ban_list:
        if char in string:
            if char in string:
                string = string.replace(char, '') #xóa ký tự
    
    for char in answer_list:
        if char in string:
            if ('.' not in string[string.index(char)+2]):
                string = string.replace(string[string.index(char)+2],' ') #format đáp án

    if '\n\n' in string:
        string = string.replace('\n\n','\n') #Tránh cách 2 dòng

    return string.strip()

# Hàm xuất file txt
def write_txt(path,text):
    with open(f"{path}", "w",encoding="utf-8" ) as f: f.write(text)

# Hàm đọc folder
def read_folders(directory_path):
    for root, directories, files in os.walk(directory_path):
        run_files(root)   

# Hàm đọc file
def run_files(folder_path):
    for filename in os.listdir(folder_path):
        # Kiểm tra định dạng jpg
        if filename.endswith(".jpg"):
            file_path = os.path.join(folder_path, filename)
            # Nhận dạng chữ từ ảnh 
            detected_text, detected_languages,cropped_image = extract_text_from_image(file_path)
            formatted_text = format_text(detected_text)

            #In ra màn hình
            # print(filename)
            # print("\nDetected text:", detected_text)
            # print("\nDetected languages:", detected_languages)
            # print("\nCleaned text:",formatted_text)

            #Format tên file để lưu ảnh vào folder tương ứng
            file = filename[:filename.rfind("_")] 
            path = os.path.join(folder_path,file)
            # Kiểm tra folder tồn tại
            if not os.path.exists(path):
                os.makedirs(path)         

            # Lưu ảnh crop 
            img_path = os.path.join(path,filename)
            cv2.imwrite(img_path ,cropped_image)
            # Ghi file txt
            txt_path = img_path.replace(".jpg",".txt") 
            write_txt(txt_path,formatted_text)
            path = ""
            
############## Main ################  

#Đọc folder
directory_path = "nhung_dang_hinh" 
read_folders(directory_path)






