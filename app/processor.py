from PIL import Image, ImageFilter, ImageOps

def apply_image_filter(image: Image.Image, filter_type: str) -> Image.Image:
    # RGBA 같은 포맷을 안전하게 RGB로 변환
    if image.mode != 'RGB':
        image = image.convert('RGB')
        
    if filter_type == 'grayscale':
        return ImageOps.grayscale(image)
    elif filter_type == 'edge':
        return image.filter(ImageFilter.FIND_EDGES)
    elif filter_type == 'blur':
        return image.filter(ImageFilter.BLUR)
    
    return image # 기본값은 원본