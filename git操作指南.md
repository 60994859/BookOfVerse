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

## 10. 代理问题

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

## 11. 常用命令速查

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

## 12. 推荐工作习惯

1. 日常只对 `origin` push。
2. 只从 `upstream` fetch/merge，不向 `upstream` push。
3. 每次同步官方更新前先保证工作区干净。
4. 每次同步官方更新后，优先检查 `docs/*.md` 是否变化。
5. 中文译文、PDF 和网站构建脚本都提交到自己的仓库。
6. PDF、站点输出和临时目录不提交，按需本地重新生成。
