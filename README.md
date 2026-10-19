# 官网多语言维护与验收

在现有官网中补齐翻译并检查语言路由、回退、审核状态与桌面手机表现；适用于多语言网站维护及可审核变更交付。

## 安装

将本仓库完整下载或克隆到 Codex 技能目录，文件夹名使用 `website-localization-qa`：

```sh
git clone https://github.com/AndrewDavidWY/Sill-website-localization-qa.git ~/.codex/skills/website-localization-qa
```

如果目标文件夹已存在，先保留已有修改，再决定是否更新。重新打开聊天后，检查技能列表。

## 使用

在 Codex 中使用 `$website-localization-qa` 调用，并提供本次任务的资料与要求。技能会先读取配套经验记录，再按当前任务开展工作。

## 文件

- `SKILL.md`：适用范围、工作方法与验收要求。
- `agents/openai.yaml`：技能在界面中的名称与简介。
- `references/lessons.md`：历史经验及其来源边界。

## 来源与使用边界

来自《协作经验 Skills 六件套》（2026-10-19）。历史案例中的日期、尺寸、配色和项目状态只作参考；每次执行以当前项目资料与用户要求为准。无需访问原聊天或私有项目，也不附带原项目素材。
