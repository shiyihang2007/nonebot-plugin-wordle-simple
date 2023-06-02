from nonebot import CommandGroup
from nonebot.adapters import Event
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg

import os
import random
import nonebot.adapters.onebot.v11
import nonebot.adapters.console

from .img import wordleOutput


# 命令注册

__plugin_meta__ = PluginMetadata(
    name="wordle",
    description="英语猜词",
    usage=(
        "  wordle.help 显示帮助列表\n"
        "  wordle.help <command> 显示详细帮助\n"
        "  wordle.rule 显示规则\n"
        "  wordle.start <len> 开始一局长度为 <len> 的 wordle\n"
        "  wordle.guess <word> 尝试匹配 <word> 单词\n"
        "  wordle.giveup 放弃该对局 (需要 @bot 或私聊)\n"
        "  wordle.remain 显示未使用过的字母\n"
        "  wordle.history 显示历史猜测\n"
        "注意 此功能可能会造成刷屏"
    ),
    extra={
        "unique_name": "nonebot_plugin_wordle",
        "example": "",
        "author": "shiyihang <467557146@qq.com>",
        "version": "0.2.1",
    },
)

enabled_groups = ["154976100", "576843479", "835090664"]
ban_user = [""]


async def is_enabled(event: Event) -> bool:
    session_id: str = event.get_session_id()
    if session_id.startswith("group"):
        _, group_id, user_id = event.get_session_id().split("_")
        # 不回复黑名单用户
        if user_id in ban_user:
            return False
        # 在允许的群聊中启用
        if group_id in enabled_groups:
            return True
        return False
    # 启用私聊
    return True


wordleGroup: CommandGroup = CommandGroup("wordle", rule=is_enabled)

wordle = wordleGroup.command(tuple())
help = wordleGroup.command("help")
rule = wordleGroup.command("rule")
start = wordleGroup.command("start")
guess = wordleGroup.command("guess")
giveup = wordleGroup.command("giveup", rule=to_me())
remain = wordleGroup.command("remain")
history = wordleGroup.command("history")
debug = wordleGroup.command("debug")


# 全局变量初始化
keyWord: str = ""
historyGuess: list[str] = []
historyGuessWord: list[str] = []
trycnt: int = 0
dictionary: list[str] = []
unused: list[str] = []


# 帮助列表
helpDict = dict()
helpDict.fromkeys("help", "想想你现在在用什么.")
helpDict.fromkeys("rule", "显示规则, 就像你想的那样.")
helpDict.fromkeys("start", "开始 wordle, 你需要提供一个 3~12之间的数作为单词的长度, bot 会帮你选择单词.")
helpDict.fromkeys("guess", "猜词, 你需要提供正确长度的单词, bot 会告诉你匹配情况.")
helpDict.fromkeys("giveup", "需要 @bot 或私聊 这将直接放弃该局游戏并获取正确答案,慎用!")
helpDict.fromkeys("remain", "显示未使用过的单词,就像你想的那样.")
helpDict.fromkeys("history", "显示历史猜测,按猜测顺序排列.")


@wordle.handle()
async def wordleHandle(args: Message = CommandArg()):
    await wordle.send(
        "[Error] bot: Unknown Command\n" + "Press 'wordle.help' to show command list."
    )


# 帮助
@help.handle()
async def wordleHelp(args: Message = CommandArg()):
    if len(args) == 0:
        # 简要帮助
        res: str = "bot: \n"
        res = res + "  -- Wordle --\n"
        res = res + "命令列表\n"
        res = res + "  wordle.help 显示此列表\n"
        res = res + "  wordle.help <command> 显示详细帮助\n"
        res = res + "  wordle.rule 显示规则\n"
        res = res + "  wordle.start <len> 开始一局长度为 <len> 的 wordle\n"
        res = res + "  wordle.guess <word> 尝试匹配 <word> 单词\n"
        res = res + "  wordle.giveup 放弃该对局 (需要 @bot 或私聊)\n"
        res = res + "  wordle.remain 显示未使用过的字母\n"
        res = res + "  wordle.history 显示历史猜测\n"
        res = res + "注意 此功能可能会造成刷屏"
        await help.finish(res)
    else:
        # 详细帮助
        command = args.extract_plain_text()
        if command in helpDict.keys():
            await help.finish("bot: " + helpDict[command])
        else:
            await help.finish("[Error] bot: Unknown Command; return '请给出正确的参数!'.")


# 规则
@rule.handle()
async def wordleRule():
    # await rule.finish("bot: 此功能未完成. bdfs 谢谢!")
    res: str = "bot: \n"
    res = res + "  -- Wordle --\n"
    res = res + "规则\n"
    res = res + "  你需要使用 /wordle.start <len> 来开始 wordle, \n"
    res = res + "  你需要提供一个 3~12之间的数作为单词的长度, bot 会帮你选择单词.\n"
    res = res + "  使用 /wordle.guess <word> 来猜词, 你需要提供正确长度的单词, bot 会告诉你匹配情况.\n"
    res = res + "  使用 /wordle.remain 显示未使用过的字母.\n"
    res = res + "  由于一些原因, bot 给出的匹配情况使用纯文本进行表示\n"
    res = res + "  + 表示该字母完全匹配 ? 表示该字母存在但位置错误 * 表示该字母不存在\n"
    res = res + "  祝您愉快~"
    await rule.send(res)


# 调试
@debug.handle()
async def wordleDebug(args: Message = CommandArg()):
    global keyWord
    global dictionary
    global trycnt
    global historyGuess
    await debug.finish("bot: 你想干什么? [恼]")
    text: str = args.extract_plain_text()
    if text == "dictionary":
        cnt: int = 0
        output: str = ""
        for i in dictionary:
            cnt = cnt + 1
            output = output + "\n" + i
            if cnt > 20:
                await debug.send("[Debug] bot: \n -- dictionary --" + output)
                await debug.finish(
                    "[Debug] bot: have more... [All size " + str(len(dictionary)) + "]"
                )
        await debug.send("[Debug] bot: \n -- dictionary --" + output)
        await debug.finish("[Debug] bot: done. [All size " + str(len(dictionary)) + "]")
    if text == "keyword":
        await debug.finish("[Debug] bot: keyWord is " + str(keyWord) + ".")


# 主处理流程
@start.handle()
async def wordleStart(args: Message = CommandArg()):
    global keyWord
    global dictionary
    global trycnt
    global historyGuess
    global historyGuessWord
    global unused
    if keyWord != "":
        await start.finish("bot: 当前已有正在进行的 Wordle!")
    text = args.extract_plain_text()
    wordlen: int = 0
    try:
        wordlen = int(text)
        if wordlen < 3:
            await start.finish("[Error] bot: Unexcepted Input; Return '单词长度不应小于3!'.")
        if wordlen > 12:
            await start.finish("[Error] bot: Unexcepted Input; Return '单词长度不应大于12!'.")
        # await start.send("[Info] bot: Finding Word...")
    except ValueError:
        await start.finish("[Error] bot: ValueError; Return '请给出正确的单词长度!'.")
    # 读取字典
    fdict = open(os.path.split(__file__)[0] + "/AnswerDictionary.txt", "r")
    dictionary = fdict.readlines()
    fdict.close()
    wordlist: list[str] = []
    for i in range(len(dictionary)):
        dictionary[i] = ((dictionary[i].split())[0]).lower()
        if len(dictionary[i]) == wordlen:
            wordlist.append(dictionary[i])
    trycnt = 0
    historyGuessWord = []
    historyGuess = []
    keyWord = wordlist[random.randint(0, len(wordlist))]
    unused = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
    ]
    fdict = open(os.path.split(__file__)[0] + "/GuessDictionary.txt", "r")
    dictionary = fdict.readlines()
    fdict.close()
    for i in range(len(dictionary)):
        dictionary[i] = ((dictionary[i].split())[0]).lower()
    await start.send("bot: Word Found")


@guess.handle()
async def wordleGuessPlus(
    bot: nonebot.adapters.onebot.v11.Bot,
    event: nonebot.adapters.onebot.v11.Event,
    args: nonebot.adapters.onebot.v11.Message = CommandArg(),
):
    global keyWord
    global dictionary
    global trycnt
    global historyGuess
    global historyGuessWord
    global unused
    if keyWord == "":
        await guess.finish("bot: 当前没有正在进行的 Wordle!")
    # await guess.finish("bot: 此功能未完成, 正在咕咕中! [100/100]")
    guessWord = args.extract_plain_text().split()[0]
    if dictionary.count(guessWord) == 0:
        await guess.finish("bot: " + guessWord + " 不是一个单词!")
    if len(guessWord) != len(keyWord):
        await guess.finish("bot: 请输入长度为 " + str(len(keyWord)) + " 的单词!")
    if guessWord in historyGuessWord:
        await guess.finish("bot: 此单词已经尝试过!")
    historyGuessWord.append(guessWord)
    trycnt = trycnt + 1
    if guessWord == keyWord:
        # await guess.send("bot: Game Over!")
        await bot.send_group_msg(
            group_id=int(event.get_session_id().split("_")[1]),
            message=f"bot: 游戏结束! \n[CQ:at,qq={str(int(event.get_user_id()))}] 猜到了答案为 {keyWord}!\n你们总共进行了 {str(trycnt)}次猜测.",
        )
        # await guess.send("bot: 正在清理缓存.")
        keyWord = ""
        trycnt = 0
        historyGuess.clear()
        dictionary = []
        return
        # await guess.finish("bot: 清理结束.")
    matchState: list[int] = []
    matchStateK: list[int] = []
    for i in range(len(guessWord)):
        matchState.append(0)
        matchStateK.append(0)
        try:
            unused.remove(guessWord[i])
        except ValueError:
            pass
        if guessWord[i] == keyWord[i]:
            matchState[i] = 1
            matchStateK[i] = 1
    for i in range(len(guessWord)):
        if matchState[i] == 1:
            continue
        for j in range(len(guessWord)):
            if matchStateK[j] != 0:
                continue
            if guessWord[i] == keyWord[j]:
                matchState[i] = 2
                matchStateK[j] = 2
    res: str = ""
    for i in range(len(guessWord)):
        res = res + guessWord[i]
        res = res + "*+?"[matchState[i]]
    historyGuess.append(res)
    sendImg: str = wordleOutput(historyGuess)
    sendMessage: str = "[CQ:image,file=base64://" + sendImg + "]"
    await guess.send(nonebot.adapters.onebot.v11.Message(sendMessage))


@guess.handle()
async def wordleGuess(args: nonebot.adapters.console.Message = CommandArg()):
    global keyWord
    global dictionary
    global trycnt
    global historyGuess
    global historyGuessWord
    global unused
    if keyWord == "":
        await guess.finish("bot: 当前没有正在进行的 Wordle!")
    # await guess.finish("bot: 此功能未完成, 正在咕咕中! [100/100]")
    guessWord = args.extract_plain_text().split()[0]
    if dictionary.count(guessWord) == 0:
        await guess.finish("bot: " + guessWord + " 不是一个单词!")
    if len(guessWord) != len(keyWord):
        await guess.finish("bot: 请输入长度为 " + str(len(keyWord)) + " 的单词!")
    if guessWord in historyGuessWord:
        await guess.finish("bot: 此单词已经尝试过!")
    historyGuessWord.append(guessWord)
    trycnt = trycnt + 1
    if guessWord == keyWord:
        # await guess.send("bot: Game Over!")
        await guess.send(
            "bot: 游戏结束! \n答案为 " + keyWord + "!\n" + "你们总共进行了 " + str(trycnt) + "次猜测."
        )
        # await guess.send("bot: 正在清理缓存.")
        keyWord = ""
        trycnt = 0
        historyGuess.clear()
        dictionary = []
        # await guess.finish("bot: 清理结束.")
    matchState: list[int] = []
    matchStateK: list[int] = []
    for i in range(len(guessWord)):
        matchState.append(0)
        matchStateK.append(0)
        try:
            unused.remove(guessWord[i])
        except ValueError:
            pass
        if guessWord[i] == keyWord[i]:
            matchState[i] = 1
            matchStateK[i] = 1
    for i in range(len(guessWord)):
        if matchState[i] == 1:
            continue
        for j in range(len(guessWord)):
            if matchStateK[j] != 0:
                continue
            if guessWord[i] == keyWord[j]:
                matchState[i] = 2
                matchStateK[j] = 2
    res: str = ""
    for i in range(len(guessWord)):
        res = res + guessWord[i]
        res = res + "*+?"[matchState[i]]
    historyGuess.append(res)
    sendMessage: str = "bot: \n" + "尝试次数: " + str(trycnt)
    for i in historyGuess:
        sendMessage = sendMessage + "\n" + i
    await guess.send(sendMessage)


@giveup.handle()
async def wordleGiveUp():
    global keyWord
    global dictionary
    global trycnt
    global historyGuess
    if keyWord == "":
        await giveup.finish("bot: 当前没有正在进行的 Wordle!")
    await guess.send(
        "bot: 放弃了这局 wordle! \n答案为 "
        + keyWord
        + "!\n"
        + "你们总共进行了 "
        + str(trycnt)
        + "次猜测."
    )
    keyWord = ""
    trycnt = 0
    historyGuess.clear()
    dictionary = []
    await giveup.finish("bot: 清理结束.")


@remain.handle()
async def wordleRemain(args: Message = CommandArg()):
    global keyWord
    global unused
    if keyWord == "":
        await remain.finish("bot: 当前没有正在进行的 Wordle!")
    output: str = "bot: \n 未使用的字母: "
    for i in unused:
        output = output + i + " "
    await remain.send(output)


@history.handle()
async def wordleHistoryPlus(args: nonebot.adapters.onebot.v11.Message = CommandArg()):
    global keyWord
    global dictionary
    global trycnt
    global historyGuess
    if keyWord == "":
        await remain.finish("bot: 当前没有正在进行的 Wordle!")
    sendMessage: str = "bot: \n" + "尝试次数: " + str(trycnt)
    for i in historyGuess:
        sendMessage = sendMessage + "\n" + i
    await history.send(sendMessage)


@history.handle()
async def wordleHistory(args: nonebot.adapters.console.Message = CommandArg()):
    global keyWord
    global dictionary
    global trycnt
    global historyGuess
    if keyWord == "":
        await remain.finish("bot: 当前没有正在进行的 Wordle!")
    sendImg: str = wordleOutput(historyGuess)
    sendMessage: str = "[CQ:image,file=base64://" + sendImg + "]"
    await guess.send(nonebot.adapters.onebot.v11.Message(sendMessage))
