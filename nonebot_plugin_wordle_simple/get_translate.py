"""从 Bing 词典 API 获取单词翻译"""

import re
from sys import argv
import httpx
from nonebot.log import logger


translateServices = {
    "Bing": "https://cn.bing.com/dict/search?q=[word]",
}


async def translate(word: str) -> str:
    for _ in range(3):
        url = translateServices["Bing"]
        url = url.replace("[word]", word)
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
        rp: str = r.text
        m = re.search(
            r'<meta name="description" content="必应词典为您提供.+的释义，(.+) " ?\/?>',
            rp,
        )
        if not m:
            logger.warning(f"Cannot find content in webpage `{rp}`")
            continue
        tl: str = (
            m.group(1)
            .replace("，", ", ")
            .replace("。", ". ")
            .replace("：", ": ")
            .replace("；", "; ")
        )
        m = re.search(r".*\[.*\]", tl)
        if not m:
            logger.warning(f"Cannot find content in meta-info `{tl}`")
            continue
        tl_ano = m.group(0)
        tl = tl.replace(tl_ano + ",", tl_ano + "\n")
        tl = tl.replace("; ", "\n")
        return tl
    return "Translate Service Error"


if __name__ == "__main__":
    if len(argv) > 1:
        for i in argv[1:]:
            print(i + ":")
            print(translate(i))
    else:
        print(translate("help"))
