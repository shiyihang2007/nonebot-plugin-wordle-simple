import re
from sys import argv
import httpx


translateServices = {
    "Bing": "https://cn.bing.com/dict/search?q=[word]",
}


def translate(word: str) -> str:
    try:
        url = translateServices["Bing"]
        url = url.replace("[word]", word)
        r = httpx.get(url)
        rp: str = r.text
        m: re.Match = re.search(
            r'<meta name="description" content="必应词典为您提供.+的释义，(.+) " ?\/?>',
            rp,
        )
        tl: str = m.group(1)
        tl = tl.replace("，", ",")
        tl = tl.replace("。", ".")
        tl = tl.replace("：", ":")
        tl = tl.replace("；", ";")
        tl_ano = re.search(r".*\[.*\]", tl).group(0)
        tl = tl.replace(tl_ano + ",", tl_ano + "\n")
        tl = tl.replace("; ", "\n")
        return tl
    except TypeError:
        return "Translate Service Error"


if __name__ == "__main__":
    if len(argv) > 1:
        for i in argv[1:]:
            print(i + ":")
            print(translate(i))
    else:
        print(translate("help"))
