# 官网多语言维护与验收

在现有网站中补齐翻译，并核对语言路由、回退、源文版本、审核状态和桌面手机表现，用语言 × 视图 × 宽度的交互矩阵覆盖实际页面，而不只检查翻译文件。

技能名称：`website-localization-qa` · [查看技能指令](SKILL.md)

## 适合什么时候用

- 网站增加新语言，需要检查菜单、正文和元数据的覆盖。
- 中文更新后，其他语言可能仍是旧版本。
- 翻译已生成，但需要交付可审核的代码和验收结果。
- 多语言看板或交互页面需要验证语言切换、加载失败、轮播与数据一致性。

## 开始前准备什么

- 网站仓库、分支、语言清单和允许修改的范围。
- 现有语言结构、内容 ID、审核及发布规则。
- 源文、已有译文、术语和需要优先处理的页面。

## 工作方式

1. 确认当前工程和已有修改，建立逐内容逐语言覆盖表。
2. 分别处理导航、分类、正文和元数据。
3. 保留审核、发布锁定与回退规则，标记需要复核的译文。
4. 运行项目要求的检查和构建，按本次语言、视图和宽度建立矩阵，再核对真实页面和适用交互。
5. 交付可审核变更，并分别说明翻译、审校、合并与发布状态。

## 可以得到什么

- 授权范围内的译文及网站代码变更。
- 内容与语言覆盖记录、剩余审校事项。
- 构建、相关测试和实际页面验收的结果说明。
- 可追溯的交互矩阵，区分已通过、失败、受阻、未执行和不适用。

## 安装与调用

将完整仓库克隆到自己的技能目录，安装文件夹使用技能名称 `website-localization-qa`：

```sh
git clone https://github.com/AndrewDavidWY/Sill-website-localization-qa.git ~/.codex/skills/website-localization-qa
```

如果使用自定义 `CODEX_HOME`，请放到其 `skills/` 下。同名目录已经存在时先比较版本并保留自己的修改，不要直接覆盖。下载 ZIP 时，同样需保留完整文件结构，并把解压后的安装目录命名为技能名称。

在新会话中确认技能可用，再用下面的方式提出任务：

```text
使用 $website-localization-qa，检查这个官网的英文和泰文覆盖。保留现有路由与审核规则，补齐缺失翻译，检查桌面和手机页面，先提交可审核结果，不部署。
```

## 文件与维护

- [SKILL.md](SKILL.md)：技能入口、适用范围和执行方法。

- [agents/openai.yaml](agents/openai.yaml)：界面名称、简介与调用提示。

- [references/](references/)：按任务读取的专项方法与经验。

- [references/interaction-regression.md](references/interaction-regression.md)：多语言交互、加载状态、轮播、数据口径与证据方法。

- [assets/regression-plan.example.json](assets/regression-plan.example.json) 与 [scripts/build_regression_matrix.py](scripts/build_regression_matrix.py)：离线生成待测矩阵。示例仅演示结构，语言、视图和宽度必须按本次范围调整。

生成清单的示例：

```sh
python3 scripts/build_regression_matrix.py assets/regression-plan.example.json --output regression-matrix.csv
```

脚本不访问网站、不执行测试。所有行初始为 `NOT_RUN`；清单行数不能当作已完成测试数量。已有 CSV 不会被覆盖，重测应另存新文件并保留运行批次；生成命令失败留下的新文件应视为不完整。

说明与源码版本以本仓库为准。更新时先查看提交差异；修改方法后再同步自己的安装副本，其他电脑不会自动获得更新。

## 使用边界

这是维护与验收方法，不是独立的网站程序或翻译服务。机器翻译、模型交叉审校和母语人工审校是不同状态；不能复制中文后标记为已译，也不能为通过检查擅自开放语言。

## 来源

初始方法来自《协作经验 Skills 六件套》（2026-10-19），本轮补充可配置的交互回归方法。经验仅保留可复用方法，不附原聊天、私有项目材料或原项目素材；案例日期、尺寸、配色与状态不能直接套用到新任务。
