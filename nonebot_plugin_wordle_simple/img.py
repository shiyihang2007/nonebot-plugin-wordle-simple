import io
import os
import base64
from PIL import Image, ImageDraw, ImageFont


def image2base64(img: Image.Image) -> str:
    """将 PIL 图像转换为 base64 格式

    :param img: 要转换的 PIL 图像
    :type img: Image.Image
    :return: 以 Base64 存储的图像字符串
    :rtype: str
    """
    img_data = io.BytesIO()
    img.save(img_data, format="PNG")
    img_data_bytes = img_data.getvalue()
    encoded_image = base64.b64encode(img_data_bytes).decode("utf-8")
    return encoded_image


def wordle_output(words: list[str], font_path: str) -> str:
    """将历史记录输出到图片

    :param words: 历史记录
    :type words: list[str]
    :return: 图片的base编码
    :rtype: str
    """

    # 常量定义
    char_size = 20
    rect_size_x = char_size * 1.1
    rect_size_y = char_size * 1.5
    padding_left = 2
    padding_top = 2
    font_style = ImageFont.truetype(
        (
            os.path.split(__file__)[0] + "/" + font_path
            if font_path[0] == "."
            else font_path
        ),
        encoding="utf-8",
        size=char_size,
    )

    history_length = len(words)
    word_length = len(words[0]) // 2
    image_size_x = int(rect_size_x * word_length + padding_left * word_length * 2)
    image_size_y = int(rect_size_y * history_length + padding_top * history_length * 2)

    res_img = Image.new("RGBA", (image_size_x, image_size_y), color=(255, 255, 255))
    painter = ImageDraw.Draw(res_img)
    pos: tuple[int, int] = (0, 0)
    for word in words:
        pos = (pos[0] + 1, 0)
        for i in range(0, len(word), 2):
            pos = (pos[0], pos[1] + 1)
            pos_top: float = padding_top + (pos[0] - 1) * (
                rect_size_y + padding_top * 2
            )
            pos_left: float = padding_left + (pos[1] - 1) * (
                rect_size_x + padding_left * 2
            )
            pos_right: float = -padding_left + (pos[1]) * (
                rect_size_x + padding_left * 2
            )
            pos_buttom: float = -padding_top + (pos[0]) * (
                rect_size_y + padding_top * 2
            )
            char_pos_x: float = (
                padding_left
                + rect_size_x * 0.5
                + (pos[1] - 1) * (rect_size_x + padding_left * 2)
            )
            char_pos_y: float = (
                padding_top
                + rect_size_y * 0.5
                + (pos[0] - 1) * (rect_size_y + padding_top * 2)
            )
            fill_color: tuple[int, int, int] = (
                (0, 255, 0)
                if word[i + 1] == "+"
                else (255, 255, 0)
                if word[i + 1] == "?"
                else (192, 192, 192)
            )
            painter.rectangle(
                (pos_left, pos_top, pos_right, pos_buttom),
                fill=fill_color,
            )
            painter.text(
                xy=(char_pos_x, char_pos_y),
                text=word[i],
                font=font_style,
                anchor="mm",
                fill=(0, 0, 0),
            )
    res_img_base64: str = image2base64(res_img)
    return res_img_base64
