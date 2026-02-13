"""nonebot-plugin-wordle-simple

nonebot2 插件，实现一个简单的英语猜词游戏
适用于 onebot.v11 适配器
"""

import os
import random
import asyncio

from nonebot import CommandGroup, get_plugin_config
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.typing import T_State

from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent

from .img import wordle_output
from .get_translate import translate
from .config import Config

# 获取配置
wordle_config = get_plugin_config(Config).wordle

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
    type="application",
    homepage="https://www.github.com/shiyihang2007/nonebot-plugin-wordle-simple/",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra={
        "unique_name": "nonebot_plugin_wordle_simple",
        "example": "",
        "author": "shiyihang <467557146@qq.com>",
        "version": "0.0.7",
    },
)


async def is_enabled(event: MessageEvent) -> bool:
    if isinstance(event, GroupMessageEvent):
        group_id = str(event.group_id)
        user_id = str(event.get_user_id())
        # 不回复黑名单用户
        if user_id in wordle_config.ban_user:
            return False
        # 在允许的群聊中启用
        if group_id in wordle_config.groups_enabled:
            return True
        return False
    # 启用私聊
    return True


async def is_admin(bot: Bot, event: MessageEvent, state: T_State) -> bool:
    if not await to_me()(bot, event, state):
        return False
    user_id: str = event.get_user_id()
    if isinstance(event, GroupMessageEvent):
        group_id: str = str(event.group_id)
        user_info: dict = await bot.call_api(
            "get_group_member_info", **{"group_id": group_id, "user_id": user_id}
        )
        user_role: str = user_info["role"]
        # 只允许管理员使用
        if user_role in ["owner", "admin"]:
            return True
        return False
    # 禁用私聊
    return False


wordleGroup: CommandGroup = CommandGroup(
    "wordle", priority=wordle_config.command_priority
)

CommandDebugEnable = wordleGroup.command("debug_enable", permission=SUPERUSER)
CommandDebugDisable = wordleGroup.command("debug_disable", permission=SUPERUSER)
CommandChangeMinLength = wordleGroup.command("change_min_length", permission=SUPERUSER)
CommandChangeMaxLength = wordleGroup.command("change_max_length", permission=SUPERUSER)

CommandEnable = wordleGroup.command("enable", aliases={"启用"}, rule=is_admin)
CommandDisable = wordleGroup.command("disable", aliases={"禁用"}, rule=is_admin)

CommandWordle = wordleGroup.command(tuple(), rule=is_enabled)
CommmandHelp = wordleGroup.command("help", rule=is_enabled)
CommandRule = wordleGroup.command("rule", rule=is_enabled)
CommandStart = wordleGroup.command("start", rule=is_enabled)
CommandGuess = wordleGroup.command("guess", rule=is_enabled)
CommandGiveup = wordleGroup.command("giveup", rule=is_enabled & to_me())
CommandRemain = wordleGroup.command("remain", rule=is_enabled)
CommandHistory = wordleGroup.command("history", rule=is_enabled)
CommandDebug = wordleGroup.command("debug", rule=is_enabled)


# 全局变量初始化
key_word: str = ""
history_guess: list[str] = []
history_guess_word: list[str] = []
try_cnt: int = 0
dictionary: list[str] = []
used_chars: set[str] = set()


@CommandDebugEnable.handle()
async def _():
    wordle_config.debug_enabled = True


@CommandDebugDisable.handle()
async def _():
    wordle_config.debug_enabled = False


@CommandChangeMinLength.handle()
async def _(args: Message = CommandArg()):
    try:
        wordle_config.length_min = int(args.extract_plain_text().strip())
    except TypeError:
        await CommandChangeMinLength.finish(
            f"{args.extract_plain_text().strip()} 不是有效的数字"
        )
    if wordle_config.length_min < 2:
        await CommandChangeMinLength.send(
            f"错误! 最小单词长度({wordle_config.length_min})过小, 已自动更改为 2."
        )
        wordle_config.length_min = 2
    await CommandChangeMinLength.send(f"最小单词长度已设为 {wordle_config.length_min}")
    if wordle_config.length_min > wordle_config.length_max:
        await CommandChangeMinLength.send(
            f"警告! 最小单词长度({wordle_config.length_min})大于最大单词长度({wordle_config.length_max})."
        )


@CommandChangeMaxLength.handle()
async def _(args: Message = CommandArg()):
    try:
        wordle_config.length_max = int(args.extract_plain_text().strip())
    except TypeError:
        await CommandChangeMaxLength.finish(
            f"{args.extract_plain_text().strip()} 不是有效的数字"
        )
    if wordle_config.length_max > 15:
        await CommandChangeMaxLength.send(
            f"错误! 最大单词长度({wordle_config.length_max})过大, 已自动更改为 15."
        )
        wordle_config.length_max = 15
    await CommandChangeMaxLength.send(f"最大单词长度已设为 {wordle_config.length_max}")
    if wordle_config.length_max < wordle_config.length_min:
        await CommandChangeMaxLength.send(
            f"警告! 最大单词长度({wordle_config.length_max})小于最小单词长度({wordle_config.length_min})."
        )


@CommandEnable.handle()
async def _(event: GroupMessageEvent):
    group_id = str(event.group_id)
    if group_id in wordle_config.groups_enabled:
        await CommandEnable.finish(f"群聊 {group_id} 已在白名单中")
    wordle_config.groups_enabled.add(group_id)
    await CommandEnable.send(f"群聊 {group_id} 加入了白名单")


@CommandDisable.handle()
async def _(event: GroupMessageEvent):
    group_id = str(event.group_id)
    if group_id not in wordle_config.groups_enabled:
        await CommandDisable.finish(f"群聊 {group_id} 不在白名单中")
    wordle_config.groups_enabled.remove(group_id)
    await CommandDisable.send(f"群聊 {group_id} 退出了白名单")


# 帮助列表
helpDict = {
    "help": "想想你现在在用什么.",
    "rule": "显示规则, 就像你想的那样.",
    "start": (
        f"开始 wordle, 你需要提供一个 {wordle_config.length_min}~{wordle_config.length_max} 之间的数作为单词的长度, "
        + "bot 会帮你选择单词."
    ),
    "guess": "猜词, 你需要提供正确长度的单词, bot 会告诉你匹配情况.",
    "giveup": "需要 @bot 或私聊 这将直接放弃该局游戏并获取正确答案,慎用!",
    "remain": "显示未使用过的单词,就像你想的那样.",
    "history": "显示历史猜测,按猜测顺序排列.",
}


@CommandWordle.handle()
async def _():
    await CommandWordle.send(
        "[Error] Unknown Command\nPress 'wordle.help' to show command list."
    )


@CommmandHelp.handle()
async def _(args: Message = CommandArg()):
    # 帮助
    if len(args) == 0:
        # 简要帮助
        res: list[str] = ["\n-- Wordle --\n命令列表\n"]
        res.extend([f"  wordle.{i} {item}" for i, item in enumerate(helpDict)])
        res.append("注意 此功能可能会造成刷屏")
        await CommmandHelp.finish("\n".join(res))
    else:
        # 详细帮助
        command = args.extract_plain_text().strip().lower()
        await CommmandHelp.finish(
            f"{helpDict[command]}"
            if command in helpDict
            else (
                f"错误: 找不到指令 {command} !\n可用指令:\n"
                + "\n".join(helpDict.keys())
            )
        )


# 规则
@CommandRule.handle()
async def _():
    res: str = f"""bot:
  -- Wordle --
规则
  你需要使用 /wordle.start <len> 来开始 wordle,
  你需要提供一个 {wordle_config.length_min}~{wordle_config.length_max}之间的数作为单词的长度, bot 会帮你选择单词.
  使用 /wordle.guess <word> 来猜词, 你需要提供正确长度的单词, bot 会告诉你匹配情况.
  使用 /wordle.remain 显示未使用过的字母.
  祝您愉快~"""
    await CommandRule.send(res)


# 调试
@CommandDebug.handle()
async def _(args: Message = CommandArg()):
    if not wordle_config.debug_enabled:
        await CommandDebug.finish("你想干什么? [恼]")
    text: str = args.extract_plain_text()
    if text == "dictionary":
        cnt: int = 0
        output: str = ""
        for i in dictionary:
            cnt = cnt + 1
            output = output + "\n" + i
            if cnt > 20:
                await CommandDebug.send("[Debug] \n -- dictionary --" + output)
                await CommandDebug.finish(
                    "[Debug] have more... [All size " + str(len(dictionary)) + "]"
                )
        await CommandDebug.send("[Debug] \n -- dictionary --" + output)
        await CommandDebug.finish(
            "[Debug] done. [All size " + str(len(dictionary)) + "]"
        )
    if text == "keyword":
        await CommandDebug.finish("[Debug] keyWord is " + str(key_word) + ".")


# 主处理流程
@CommandStart.handle()
async def _(args: Message = CommandArg()):
    global key_word
    global dictionary
    global try_cnt
    global history_guess
    global history_guess_word
    global used_chars
    if key_word != "":
        await CommandStart.finish("当前已有正在进行的 Wordle!")
    text = args.extract_plain_text()
    word_len: int = 0
    try:
        word_len = int(text)
        if word_len < wordle_config.length_min:
            await CommandStart.finish(
                f"错误: 单词长度不应小于 {wordle_config.length_min} !"
            )
        if word_len > wordle_config.length_max:
            await CommandStart.finish(
                f"错误: 单词长度不应大于 {wordle_config.length_max}"
            )
    except ValueError:
        await CommandStart.finish("请给出正确的单词长度!")
    # 读取字典
    with open(
        os.path.split(__file__)[0] + "/" + wordle_config.dictionary_answer_path,
        "r",
        encoding="utf-8",
    ) as fdict:
        dictionary = fdict.readlines()
    wordlist: list[str] = []
    for i, word in enumerate(dictionary):
        word = ((word.split())[0]).lower()
        if len(word) == word_len:
            wordlist.append(word)
    try_cnt = 0
    history_guess_word = []
    history_guess = []
    used_chars = set()
    key_word = wordlist[random.randint(0, len(wordlist))]
    with open(
        os.path.split(__file__)[0] + "/" + wordle_config.dictionary_answer_path,
        "r",
        encoding="utf-8",
    ) as fdict:
        dictionary = fdict.readlines()
    for i, word in enumerate(dictionary):
        dictionary[i] = ((word.split())[0]).lower()
    await CommandStart.send("初始化完成, 单词已确定")


@CommandGuess.handle()
async def _(
    event: MessageEvent,
    args: Message = CommandArg(),
):
    global key_word
    global dictionary
    global try_cnt
    global used_chars
    if key_word == "":
        await CommandGuess.finish("当前没有正在进行的 Wordle!")
    guess_word = args.extract_plain_text().split()[0].lower()
    if dictionary.count(guess_word) == 0:
        await CommandGuess.finish(f"{guess_word} 不是一个单词!")
    if len(guess_word) != len(key_word):
        await CommandGuess.finish(f"请输入长度为 {len(key_word)} 的单词!")
    if guess_word in history_guess_word:
        await CommandGuess.finish("此单词已经尝试过!")
    history_guess_word.append(guess_word)
    try_cnt = try_cnt + 1
    if guess_word == key_word:
        asyncio.create_task(
            CommandGuess.send(
                "\n".join(
                    [
                        "游戏结束!",
                        f"""{
                            f"[CQ:at,qq={int(event.get_user_id())}] 猜到了"
                            if isinstance(event, GroupMessageEvent)
                            else ""
                        }答案为 {key_word}.""",
                        f"你们总共进行了 {try_cnt}次猜测.",
                    ]
                ),
            )
        )
        asyncio.create_task(
            CommandGuess.send(
                f"单词 {key_word} 翻译:\n{await translate(key_word)}",
            )
        )
        key_word = ""
        try_cnt = 0
        history_guess.clear()
        dictionary = []
        used_chars = set()
        return
    match_state: list = [0] * len(key_word)
    match_count: list = [0] * 26
    for i, key in enumerate(key_word):
        used_chars.add(guess_word[i])
        if guess_word[i] == key:
            match_state[i] = 1
            match_count[ord(guess_word[i]) - ord("a")] += 1
    for i, guess in enumerate(guess_word):
        if match_state[i] == 1:
            continue
        if match_count[ord(guess) - ord("a")] < key_word.count(guess):
            match_state[i] = 2
            match_count[ord(guess) - ord("a")] += 1
    history_guess.append(
        "".join(
            [f"{guess}{'*+?'[match_state[i]]}" for i, guess in enumerate(guess_word)]
        )
    )
    if args.extract_plain_text() in ["-p", "--plain"]:
        send_message_list: list[str] = [f"尝试次数: {try_cnt}"]
        send_message_list.extend(history_guess)
        send_message = "\n".join(send_message_list)
    else:
        send_img: str = wordle_output(history_guess, wordle_config.font_path)
        send_message: str = f"[CQ:image,file=base64://{send_img}]"
    await CommandHistory.send(Message(send_message))


@CommandGiveup.handle()
async def _():
    global key_word
    global try_cnt
    if key_word == "":
        await CommandGiveup.finish("当前没有正在进行的 Wordle!")
    asyncio.create_task(
        CommandGiveup.send(
            "\n".join(
                [
                    "放弃了这局 wordle!",
                    f"答案为 {key_word} !",
                    f"你们总共进行了 {try_cnt} 次猜测.",
                ]
            )
        )
    )
    key_word = ""
    try_cnt = 0
    history_guess.clear()
    dictionary.clear()


@CommandRemain.handle()
async def _():
    if key_word == "":
        await CommandRemain.finish("当前没有正在进行的 Wordle!")
    send_message_list: list[str] = [
        "未使用的字母: ",
        ", ".join(
            [chr(x) for x in range(ord("a"), ord("z") + 1) if chr(x) not in used_chars]
        ),
    ]
    await CommandRemain.send("\n".join(send_message_list))


@CommandHistory.handle()
async def _(args: Message = CommandArg()):
    if key_word == "":
        await CommandRemain.finish("当前没有正在进行的 Wordle!")
    if args.extract_plain_text() in ["-p", "--plain"]:
        send_message_list: list[str] = [f"尝试次数: {try_cnt}"]
        send_message_list.extend(history_guess)
        send_message = "\n".join(send_message_list)
    else:
        send_img: str = wordle_output(history_guess, wordle_config.font_path)
        send_message: str = f"[CQ:image,file=base64://{send_img}]"
    await CommandHistory.send(Message(send_message))
