<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-wordle

_✨ 简单英语猜词 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/owner/nonebot-plugin-wordle.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-wordle">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-wordle.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

## 📖 介绍

这是一个 nonebot2 的猜词游戏 (Wordle) 插件，没有次数限制，可以自定义词库，支持群聊白名单和用户黑名单。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-wordle

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-wordle
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-wordle
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-wordle
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-wordle
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_wordle"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| wordle__groups_enabled | 是 | - | 白名单群聊, 格式为字符串列表 |
| wordle__ban_user | 否 | [] | 黑名单用户, 格式为字符串列表 |
| wordle__length_min | 否 | 4 | 最小单词长度 |
| wordle__length_max | 否 | 12 | 最大单词长度 |
| wordle__debug_enabled | 否 | False | 是否启用调试指令 |

## 🎉 使用
### 指令表

| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| wordle.debug_enable | 主人 | 否 | 全部 | 启用调试 |
| wordle.debug_disable | 主人 | 否 | 全部 | 禁用调试 |
| wordle.change_min_length | 主人 | 否 | 全部 | 更改最小单词长度 |
| wordle.change_max_length | 主人 | 否 | 全部 | 更改最大单词长度 |
| wordle.enable | 群管 | 是 | 群聊 | 将本群加入白名单 |
| wordle.disable | 群管 | 是 | 群聊 | 将本群移出白名单 |
| wordle.help | 群员 | 否 | 白名单群 | 帮助 |
| wordle.help <指令> | 群员 | 否 | 白名单群 | 特定指令的帮助 |
| wordle.rule | 群员 | 否 | 白名单群 | 游戏规则 (弃用) |
| wordle.start <单词长度> | 群员 | 否 | 白名单群 | 启动一局游戏 |
| wordle.guess <单词> | 群员 | 否 | 白名单群 | 猜测某词 |
| wordle.giveup | 群员 | 是 | 白名单群 | 放弃一局游戏 |
| wordle.remain | 群员 | 否 | 白名单群 | 给出未使用的字母 |
| wordle.history | 群员 | 否 | 白名单群 | 显示猜测历史 |
| wordle.debug | 群员 | 否 | 白名单群 | 给出答案或词典 (调试用) |

### 效果图

暂无
