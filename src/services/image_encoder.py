import io
import base64
from PIL import Image
from pdf2image import convert_from_path
import pillow_heif

def heic_image_encoder_in_base64(image_path):
    """
    HEICファイルをJPEGに変換し、Base64エンコードした文字列を返す。
    """
    try:
        # HEICファイルを読み込み
        pillow_heif.register_heif_opener()  # PillowでHEICを開けるよう登録
        image = Image.open(image_path)  # PillowでHEICを開く

        # メモリバッファにJPEG形式で保存
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")  # PillowでJPEG保存
        buffer.seek(0)

        # バッファ内容をBase64エンコード
        jpeg_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return jpeg_base64
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def pdf_encoder_in_base64(image_path):
    # ToDo: あとで変更必要
    imgs = convert_from_path(image_path, poppler_path='/opt/homebrew/bin')
    buffer = io.BytesIO()
    imgs[0].save(buffer, format="JPEG")
    encoded_jpeg = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return encoded_jpeg
