# Git 操作指南

## 1. 当前远端结构

本仓库采用双远端模式：

```text
origin   https://github.com/60994859/BookOfVerse.git
upstream https://github.com/verselang/book.git
```

含义：

1. `origin` 是你自己的 GitHub 仓库，用于上传你的中文译文、PDF 构建脚本、本地网站配置等个人改动。
2. `upstream` 是官方 Verse 文档仓库，用于拉取官方最新英文文档更新。

当前本地 `main` 分支跟踪的是：

```text
origin/main
```

所以日常执行 `git push` 时，会默认上传到你自己的仓库，而不是官方仓库。

## 2. 是否会影响官方仓库

正常操作不会影响官方仓库。

下面这些命令只是从官方仓库读取更新：

```powershell
git fetch upstream
git merge upstream/main
```

`git fetch upstream` 只下载官方更新；`git merge upstream/main` 只把已经下载的官方更新合并到你的本地分支。它们不会向官方仓库写入任何内容。

下面这个命令会上传到你自己的仓库：

```powershell
git push
```

因为当前 `main` 分支跟踪的是 `origin/main`，所以 `git push` 等价于把当前分支推到：

```text
https://github.com/60994859/BookOfVerse.git
```

不要执行下面这个命令：

```powershell
git push upstream main
```

这条命令的含义是尝试把你的本地 `main` 分支推送到官方仓库。你通常没有官方仓库写权限，所以 GitHub 大概率会拒绝；但为了避免误操作，日常不要使用它。

安全口诀：

```text
拉官方：git fetch upstream + git merge upstream/main
推自己：git push
不要推官方：不要 git push upstream main
```

## 3. 查看远端配置

随时可以用下面命令确认：

```powershell
git remote -v
```

期望输出类似：

```text
origin    https://github.com/60994859/BookOfVerse.git (fetch)
origin    https://github.com/60994859/BookOfVerse.git (push)
upstream  https://github.com/verselang/book.git (fetch)
upstream  https://github.com/verselang/book.git (push)
```

查看当前分支跟踪关系：

```powershell
git branch -vv
```

期望 `main` 后面显示：

```text
[origin/main]
```

## 4. 日常上传到自己的仓库

修改文件后，按下面流程提交并上传：

```powershell
git status
git add <需要提交的文件或目录>
git commit -m "你的提交说明"
git push
```

因为 `main` 跟踪的是 `origin/main`，所以 `git push` 会上传到：

```text
https://github.com/60994859/BookOfVerse.git
```

不会上传到官方仓库。

如果要明确指定，也可以写成：

```powershell
git push origin main
```

## 5. 拉取官方最新更新

要从官方仓库拉取最新内容，使用：

```powershell
git fetch upstream
```

然后把官方 `main` 合并到当前分支：

```powershell
git merge upstream/main
```

完整流程：

```powershell
git status
git fetch upstream
git merge upstream/main
git push
```

解释：

1. `git status` 确认本地没有未提交改动。
2. `git fetch upstream` 只下载官方更新，不改变你的工作区。
3. `git merge upstream/main` 把官方更新合并到本地 `main`。
4. `git push` 把合并后的结果上传到你自己的 `origin/main`。

## 6. 推荐的安全同步流程

每次同步官方更新前，建议先确认本地是干净的：

```powershell
git status
```

如果输出：

```text
nothing to commit, working tree clean
```

再执行：

```powershell
git fetch upstream
git merge upstream/main
git push
```

如果 `git status` 显示有未提交改动，先提交你的改动：

```powershell
git add .
git commit -m "Save local changes before upstream sync"
```

再同步官方更新。

## 7. 如果出现冲突

合并官方更新时，如果 Git 提示 conflict，说明官方改动和你的本地改动修改了同一位置。

基本处理流程：

```powershell
git status
```

打开冲突文件，查找：

```text
<<<<<<< HEAD
你的本地内容
=======
官方更新内容
>>>>>>> upstream/main
```

手动整理成最终想保留的内容，然后：

```powershell
git add <冲突文件>
git commit
git push
```

注意：不要使用 `git reset --hard` 或 `git checkout -- <file>` 来处理冲突，除非你明确知道会丢弃哪些改动。

## 8. 只查看官方更新，不合并

如果只是想看看官方有哪些新提交：

```powershell
git fetch upstream
git log --oneline main..upstream/main
```

查看官方改了哪些文件：

```powershell
git diff --name-only main..upstream/main
```

查看官方具体改动：

```powershell
git diff main..upstream/main
```

确认没问题后再合并：

```powershell
git merge upstream/main
```

## 9. 同步官方更新后的中文文档处理

官方更新通常只会改英文文档，例如：

```text
docs/*.md
```

合并官方更新后，需要检查哪些英文 Markdown 变化了：

```powershell
git diff --name-only HEAD~1..HEAD -- docs/*.md
```

然后按实际变化更新：

```text
docs/zh-llm/
docs/zh/
```

如果只维护 LLM 重译版，优先更新：

```text
docs/zh-llm/
```

更新译文后，可以重新生成 PDF：

```powershell
.\scripts\build_pdfs.ps1 -Language zh-llm
```

重新生成本地网站：

```powershell
.\scripts\build_local_site.ps1
```

构建产物默认不提交：

```text
output/pdf/
site/
tmp/
.venv/
node_modules/
```

## 10. 部署 GitHub Pages 网站

本仓库已经配置了 GitHub Actions 自动部署双语网站到 GitHub Pages。

部署 workflow 文件：

```text
.github/workflows/deploy.yml
```

公网访问地址：

```text
https://60994859.github.io/BookOfVerse/
https://60994859.github.io/BookOfVerse/zh/
https://60994859.github.io/BookOfVerse/en/
```

### 10.1 自动部署

每次你把 `main` 分支 push 到自己的仓库后，GitHub 会自动部署网站：

```powershell
git push
```

或明确写成：

```powershell
git push origin main
```

部署流程会自动执行：

1. 安装 Python。
2. 构建双语 MkDocs 网站。
3. 上传 `site/` 目录为 GitHub Pages artifact。
4. 发布到 GitHub Pages。

### 10.2 手动重新部署

如果想不提交新代码、只重新运行部署：

1. 打开 GitHub 仓库页面。
2. 进入 **Actions**。
3. 选择 **Deploy bilingual MkDocs to GitHub Pages**。
4. 点击 **Run workflow**。
5. 选择 `main` 分支并运行。

也可以打开最近一次失败或成功的 workflow，点击 **Re-run jobs**。

### 10.3 查看部署状态

查看部署是否成功：

1. 打开 GitHub 仓库页面。
2. 进入 **Actions**。
3. 查看 **Deploy bilingual MkDocs to GitHub Pages** 的最新运行。

成功时通常会看到：

```text
build   Succeeded
deploy  Succeeded
```

失败时点击失败的 job，展开日志看具体原因。

### 10.4 GitHub Pages 设置

如果部署报错提示 Pages 未启用，需要在 GitHub 网页确认：

```text
Settings -> Pages -> Build and deployment -> Source -> GitHub Actions
```

这个设置只需要做一次。设置完成后，重新运行 workflow 即可。

### 10.5 部署内容来自哪里

GitHub Pages 部署的不是仓库里的 `site/` 目录，因为 `site/` 是构建产物，默认不提交。

部署时 GitHub Actions 会在云端重新执行：

```powershell
./scripts/build_local_site.ps1 -Python python
```

然后发布生成出来的：

```text
site/
```

也就是说，只要源码、中文译文、MkDocs 配置和构建脚本提交到了仓库，GitHub 就能自动生成网站。

### 10.6 部署后需要等待

GitHub Pages 成功部署后，公网访问可能需要几十秒到几分钟刷新。如果刚部署完访问旧页面，可以稍等一会儿，或强制刷新浏览器缓存。

## 11. 代理问题

当前仓库曾经配置过本地代理：

```text
http.proxy=socks5://127.0.0.1:10808
https.proxy=socks5://127.0.0.1:10808
```

如果 `git push` 报错：

```text
ServicePointManager 不支持具有 socks5 方案的代理
```

可以临时绕过代理执行：

```powershell
git -c http.proxy= -c https.proxy= push
```

如果要永久移除本仓库的代理配置：

```powershell
git config --unset http.proxy
git config --unset https.proxy
```

如果你确实需要代理访问 GitHub，建议配置 Git 支持的 HTTP/HTTPS 代理，而不是在当前 Git Credential Manager 流程中使用 `socks5`。

## 12. 在 VS Code 中操作 Git

如果你平时习惯在 VS Code 中操作 Git，可以继续使用 VS Code 的 Source Control 面板。只要远端仍保持：

```text
origin   你的仓库
upstream 官方仓库
```

VS Code 中的日常提交和同步也不会影响官方仓库。

### 12.1 提交并推送到自己的仓库

日常修改后：

1. 打开 VS Code 左侧的 **Source Control** 面板。
2. 在变更文件列表中确认要提交的文件。
3. 点击文件旁边的 `+`，或点击 **Stage All Changes** 暂存全部改动。
4. 在消息框中输入提交说明。
5. 点击 **Commit**。
6. 点击 **Sync Changes** 或 **Push**。

因为本地 `main` 分支跟踪的是 `origin/main`，所以 VS Code 的 **Push** / **Sync Changes** 会推送到你的仓库：

```text
https://github.com/60994859/BookOfVerse.git
```

不会推送到官方仓库。

### 12.2 在 VS Code 中拉取官方更新

VS Code 的默认 **Pull** 通常是从当前分支的跟踪远端拉取，也就是 `origin/main`。这只会拉你自己仓库的更新，不会拉官方 `upstream/main`。

要拉取官方最新更新，推荐使用 VS Code 内置终端执行：

```powershell
git fetch upstream
git merge upstream/main
```

操作位置：

1. 在 VS Code 中打开项目目录。
2. 打开菜单 **Terminal -> New Terminal**。
3. 在终端执行：

```powershell
git fetch upstream
git merge upstream/main
```

合并成功后，再在 VS Code Source Control 面板中查看变更。如果合并产生了新的 commit 或文件变化，最后点击 **Push** / **Sync Changes** 上传到你自己的 `origin/main`。

### 12.3 使用 VS Code 命令面板

也可以通过命令面板执行部分 Git 操作：

1. 按 `Ctrl+Shift+P`。
2. 输入 `Git:`。
3. 选择需要的 Git 命令。

适合日常使用的命令：

```text
Git: Commit
Git: Push
Git: Pull
Git: Fetch
Git: Sync
```

但要注意：VS Code 命令面板里的 **Git: Pull** 默认不会指定 `upstream/main`。如果你的目标是拉官方更新，仍建议用终端明确执行：

```powershell
git fetch upstream
git merge upstream/main
```

### 12.4 在 VS Code 中处理冲突

如果合并官方更新时出现冲突，VS Code 会在 Source Control 面板中显示冲突文件。

打开冲突文件后，VS Code 通常会显示几个按钮：

```text
Accept Current Change
Accept Incoming Change
Accept Both Changes
Compare Changes
```

含义：

1. **Current Change**：你本地当前分支的内容。
2. **Incoming Change**：从 `upstream/main` 合并进来的官方内容。
3. **Accept Both Changes**：同时保留两边内容，通常还需要手动整理。
4. **Compare Changes**：对比两边差异。

处理建议：

1. 不要无脑点击 **Accept Incoming Change**，否则可能丢掉你的中文化改动。
2. 不要无脑点击 **Accept Current Change**，否则可能丢掉官方更新。
3. 对文档文件，通常需要人工合并英文官方更新和你的中文目录/构建脚本改动。
4. 冲突标记全部清理后，保存文件。
5. 回到 Source Control 面板暂存冲突文件。
6. 提交 merge commit。
7. 点击 **Push** 上传到自己的仓库。

### 12.5 VS Code 中要避免的操作

避免在不确定时使用这些操作：

```text
Discard Changes
Discard All Changes
Reset
Force Push
Push to...
```

尤其注意：

1. **Discard Changes** 会丢弃本地文件改动。
2. **Reset** 可能移动分支指针，处理不当会让提交消失。
3. **Force Push** 会强制覆盖远端历史，日常不要使用。
4. **Push to...** 如果选错远端，理论上可能尝试推送到 `upstream`。

日常最安全的 VS Code 操作组合是：

```text
Source Control 面板提交 -> Push/Sync 到 origin
VS Code 终端执行 git fetch upstream + git merge upstream/main 拉官方
```

### 12.6 VS Code 操作口诀

```text
提交和推送：用 Source Control 面板，推到 origin
拉官方更新：用 VS Code 终端，fetch/merge upstream
处理冲突：用 VS Code 冲突编辑器，人工确认
不要强推：不要 Force Push
不要推官方：不要 Push to upstream
```

## 13. 常用命令速查

查看当前状态：

```powershell
git status
```

提交本地改动：

```powershell
git add .
git commit -m "提交说明"
```

上传到自己的仓库：

```powershell
git push
```

拉取官方更新：

```powershell
git fetch upstream
git merge upstream/main
```

上传同步后的结果到自己的仓库：

```powershell
git push
```

查看远端：

```powershell
git remote -v
```

查看本地分支跟踪：

```powershell
git branch -vv
```

## 14. 推荐工作习惯

1. 日常只对 `origin` push。
2. 只从 `upstream` fetch/merge，不向 `upstream` push。
3. 每次同步官方更新前先保证工作区干净。
4. 每次同步官方更新后，优先检查 `docs/*.md` 是否变化。
5. 中文译文、PDF 和网站构建脚本都提交到自己的仓库。
6. PDF、站点输出和临时目录不提交，按需本地重新生成。
