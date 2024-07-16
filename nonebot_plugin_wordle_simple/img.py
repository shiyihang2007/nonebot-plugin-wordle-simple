from PIL import Image, ImageDraw, ImageFont
import io
import base64


def image2base64(img: Image.Image) -> str:
    img_data = io.BytesIO()
    img.save(img_data, format="PNG")
    img_data_bytes = img_data.getvalue()
    encoded_image = base64.b64encode(img_data_bytes).decode("utf-8")
    return encoded_image


def wordleOutput(words: list[str]) -> str:
    """
    将历史记录输出到图片

    参数:
        `words: list[str]` - 历史记录

    返回:
        `str` - 图片的base编码
    """

    # 常量定义
    charSize = 20
    charRectX = charSize * 1.1
    charRectY = charSize * 1.5
    charPaddingLeft = 2
    charPaddingTop = 2
    fontStyle = ImageFont.truetype(
        "fonts/FiraCode-Medium.ttf", encoding="utf-8", size=charSize
    )

    historyLength = len(words)
    wordLength = len(words[0]) // 2
    imageSizeX = int(charRectX * wordLength + charPaddingLeft * wordLength * 2)
    imageSizeY = int(charRectY * historyLength + charPaddingTop * historyLength * 2)

    resImg = Image.new("RGBA", (imageSizeX, imageSizeY), color=(255, 255, 255))
    painter = ImageDraw.Draw(resImg)
    nowPos: tuple[int, int] = (0, 0)
    for word in words:
        nowPos = (nowPos[0] + 1, 0)
        for i in range(0, len(word), 2):
            nowPos = (nowPos[0], nowPos[1] + 1)
            nowPosTop: float = charPaddingTop + (nowPos[0] - 1) * (
                charRectY + charPaddingTop * 2
            )
            nowPosLeft: float = charPaddingLeft + (nowPos[1] - 1) * (
                charRectX + charPaddingLeft * 2
            )
            nowPosRight: float = -charPaddingLeft + (nowPos[1]) * (
                charRectX + charPaddingLeft * 2
            )
            nowPosButtom: float = -charPaddingTop + (nowPos[0]) * (
                charRectY + charPaddingTop * 2
            )
            nowPosX: float = (
                charPaddingLeft
                + charRectX * 0.5
                + (nowPos[1] - 1) * (charRectX + charPaddingLeft * 2)
            )
            nowPosY: float = (
                charPaddingTop
                + charRectY * 0.5
                + (nowPos[0] - 1) * (charRectY + charPaddingTop * 2)
            )
            fillColor: tuple[int, int, int] = (
                (0, 255, 0)
                if word[i + 1] == "+"
                else (255, 255, 0)
                if word[i + 1] == "?"
                else (192, 192, 192)
            )
            painter.rectangle(
                (nowPosLeft, nowPosTop, nowPosRight, nowPosButtom), fill=fillColor
            )
            painter.text(
                xy=(nowPosX, nowPosY),
                text=word[i],
                font=fontStyle,
                anchor="mm",
                fill=(0, 0, 0),
            )
    resImgBase64: str = image2base64(resImg)
    return resImgBase64
