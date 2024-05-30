# -*- coding: utf-8 -*-
"""
Created on Mon May 20 21:36:46 2024

@author: tlooc
"""

import cv2
import pytesseract
from PIL import Image

# Đặt đường dẫn tới Tesseract executable (nếu cần thiết, chỉ áp dụng cho Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_contours(image_path, target_chars='ABCD', lang='eng'):
    # Đọc hình ảnh
    img = cv2.imread(image_path)
    
    # Chuyển đổi hình ảnh sang grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Áp dụng ngưỡng để nhị phân hóa hình ảnh
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Tìm các đường viền trong hình ảnh
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_text = []
    
    for contour in contours:
        # Tìm khung hình chữ nhật bao quanh đường viền
        x, y, w, h = cv2.boundingRect(contour)
        
        # Cắt hình ảnh theo khung hình chữ nhật
        cropped_img = img[y:y+h, x:x+w]
        
        # Sử dụng pytesseract để nhận diện văn bản từ hình ảnh đã cắt
        text = pytesseract.image_to_string(cropped_img, lang=lang)
        
        # Kiểm tra nếu văn bản chứa bất kỳ ký tự nào trong target_chars
        if any(char in text for char in target_chars):
            detected_text.append(text)
            
            # Vẽ khung hình chữ nhật xung quanh các ký tự được phát hiện
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # # Hiển thị hình ảnh với các khung chữ nhật đã được vẽ
    # cv2.imshow('Detected Characters', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    return detected_text

# Đường dẫn tới hình ảnh cần xử lý
image_path = 'nhung_dang_hinh/4.jpg'

# Nhận diện văn bản từ hình ảnh
detected_text = extract_text_from_contours(image_path)
print("Detected text:", detected_text)
