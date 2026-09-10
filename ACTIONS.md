# GitHub Actions 使用说明

本文件说明如何正确通过 `GitHub Actions` 自动运行本项目的签到任务。

## 一、必读：请先 `Fork`，不要直接引用上游

**本项目的 `Actions` 只能在你自己 `Fork` 出来的仓库里运行，严禁以任何形式直接引用上游仓库的 `Action` 或工作流。**

错误的用法（**禁止**）：

```yaml
# 错误示例：直接引用上游仓库的工作流。
jobs:
  sign:
    uses: Gentlesprite/nz_helper_auto_sign/.github/workflows/sign.yml@main
```

```yaml
# 错误示例：直接引用上游仓库的 Action。
steps:
  - uses: Gentlesprite/nz_helper_auto_sign@main
```

原因说明：

- 通过 `uses: 上游仓库@分支` 这种方式调用时，所有调用方的运行记录、流量和 `Actions` 用量都会被统计到上游仓库名下。
- 一旦下游用户数量变多，上游仓库会因用量异常被 `GitHub` 判定为滥用 `Actions` 服务，进而被限流、封禁工作流，甚至直接封禁整个仓库和账号。
- 这类封禁会波及所有使用者，导致所有人都无法继续更新和使用。

正确的用法：

- 点击仓库右上角的 `Fork`，把仓库复制到你自己的账号下。
- 在你自己的仓库里启用并运行 `Actions`，此时消耗的 `Actions` 时长计入你自己的账号额度，与上游仓库完全无关。
- 你仓库里的 `Actions` 运行结果、日志、`Secrets` 也只有你自己可见。

## 二、使用步骤

### 1. `Fork` 仓库

进入本仓库页面，点击右上角 `Fork` -> `Create fork`，仓库名可随意填写，建议勾选 `Copy the main branch only`。

### 2. 启用 `Actions`

`Fork` 后的仓库默认会禁用 `Actions`，需要手动开启：

1. 打开你自己的仓库，进入 `Actions` 页面。
2. 点击 `I understand my workflows, go ahead and enable them`。
3. 在左侧列表中找到 `Sign` 工作流。

### 3. 配置 `Secrets`

进入 `Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`，添加以下内容。

| 名称 | 是否必填 | 说明 |
| :--- | :--- | :--- |
| `COOKIES` | 必填 | 逆战助手的 `Cookie`，缺失时程序会直接退出。 |
| `PUSH_KEY` | 选填 | 推送密钥，用于推送领取结果，缺失时仅记录日志不推送。 |

注意：

- `Secrets` 的值一旦保存就无法再次查看，只能覆盖修改。
- 不要把 `Cookie` 明文写进代码、日志或 `Issue` 中，否则账号有被盗用的风险。
- `Cookie` 会过期，签到失败时优先检查 `COOKIES` 是否失效。

### 4. 手动运行一次

进入 `Actions` -> `Sign` -> `Run workflow` -> `Run workflow`，确认日志中签到成功后再交给定时任务。

### 5. 自动运行

工作流默认使用 `cron '17 5 * * *'`，即 `UTC` 时间每天 `5:17`、北京时间每天 `13:17` 自动执行一次，同时保留 `workflow_dispatch` 手动触发。

## 三、定时任务注意事项

- `GitHub Actions` 的 `cron` 使用 `UTC` 时间，与北京时间相差 `8` 小时，修改时间时请自行换算。
- `cron` 是"计划时间"，不是"准时执行"。在整点、整半点这类高峰时段，`GitHub` 通常会延迟几分钟到几十分钟才排队执行，建议避开 `0` 分。
- 公共仓库若 `60` 天内没有任何提交或工作流运行记录，`GitHub` 会自动停用定时触发器，届时只会看到 `This scheduled workflow is disabled` 的提示。可定期手动运行一次，或自行添加一个上传 `Artifact` 的保活步骤来避免停用。
- 免费账号的 `Actions` 额度有限，请勿把间隔改得过短，一天一次已完全够用。

## 四、同步上游更新

上游修复问题或新增功能后，需要手动同步：

1. 打开你自己仓库首页，点击 `Sync fork`。
2. 点击 `Update branch` 确认同步。
3. 若改动与你的本地修改冲突，请选择 `Discard commits` 丢弃你的改动，或自行解决冲突后再同步。

同步只会更新代码文件，不会影响你已经配置好的 `Secrets`。

## 五、禁止事项清单

使用本项目 `Actions` 时，以下行为一律禁止：

- 在自己的工作流中通过 `uses:` 引用本仓库或作者其他仓库的 `Action`、可复用工作流。
- 把本仓库的 `Actions` 用量转嫁给上游，包括但不限于共用 `Token`、共用账号、集中代跑、对外提供代签服务。
- 使用多个账号批量 `Fork` 后同时运行，制造异常用量。
- 将 `Cookie` 等隐私信息提交到仓库或公开渠道。

违反上述约定导致上游仓库被封禁的，所有使用者都将无法继续使用本项目。

## 六、常见问题

**`Actions` 页面提示工作流被禁用。**
多为长时间无活动导致，点击 `Enable workflow` 重新启用即可。

**日志提示"没有找到 `COOKIES`，请配置环境变量"。**
`COOKIES` 未配置或名称拼写错误，请检查 `Secrets` 名称与工作流中的引用是否一致。

**手动运行正常，定时运行不执行。**
检查 `cron` 的 `UTC` 时差，或确认定时触发器是否被 `GitHub` 自动停用。

**同步上游后 `Actions` 报错。**
先确认 `requirements.txt` 依赖是否安装成功，再检查 `config.py` 中的活动配置是否已过期。
