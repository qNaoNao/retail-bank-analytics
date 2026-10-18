# GitHub Desktop 上传步骤（审核完成后再操作）

当前这轮升级只保存在本地，没有执行 Push，也没有部署到公网。

1. 打开 GitHub Desktop，在菜单选择 **File → Add Local Repository…**。
2. 选择真正连接 GitHub 的目录：**文稿 → Projects → retail-bank-analytics**。不要选择其他位置的旧副本。
3. 确认 Current Repository 是 `retail-bank-analytics`，Current Branch 是 `main`。
4. 在 **Changes** 查看本轮修改。应包含 SQL、Python、测试、文档和 CI 配置；不应包含原始数据、数据库或令牌。
5. 阅读 `README.md`、`docs/GROWTH_DECISION_MEMO.md` 和本地 Dashboard。确认接受本轮升级后，在 Summary 填写 `feat: add growth diagnostics and reproducible demo`，点击 **Commit to main**。
6. 点击顶部 **Push origin**。如果它先显示 Fetch origin，可以先获取远程状态。遇到冲突提示时停下，保留双方内容后再合并；不要选择强制覆盖。
7. 登录提示出现时使用 **Sign in with your browser**，在浏览器里完成你自己的 GitHub 登录授权。不要把 Google 密码填进终端的 Git Password 提示。
8. 点击 **Repository → View on GitHub**，确认最新提交出现，再到 Actions 查看新版 quality 工作流。工作流在上传后才会运行；本地通过不能代替远程结果。

此前清理浏览器描述的 `1a2d734` 提交已经保存在本地。如果它还未上传，本次 Push 会一起上传。普通提交不会清除旧提交历史里的原始文字。

官方说明：[添加本地仓库](https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-a-repository-from-your-local-computer-to-github-desktop)、[推送到 GitHub](https://docs.github.com/en/desktop/making-changes-in-a-branch/pushing-changes-to-github-from-github-desktop)。
