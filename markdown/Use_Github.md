# Fork工作流
### 第一天
- 在 $GitHub$ 上找到项目并 $fork$ 到我的 $GitHub$
- `git clone [url]` : 在本地下载我的远程仓库的内容
- `git remote add upstream [原项目url]` : 添加项目仓库引用
- `git checkout -b new-func` : 本地创建并转移到新分支用于完成功能
- `git add .  |  git commit -m "提交信息"` : 本地修改分支内容
- **做一半下班了**
- `git push origin new-func` : 将做一半的内容上传到我的远程仓库 **(注意不PR)**

### 第二天
- `git checkout new-func` : 切换到要做的分支
- `git pull origin new-func` : 拉取昨天的工作
- `git fetch upstream` : 更新项目仓库的main分支的新内容到本地 **(在分支更新变基)**
- `git rebase upstream/main` : 将项目仓库的main内容和本地的main内容合并
- **合并时出现冲突 : 解决冲突后**
- `git add .` : 保持冲突解决
- `git rebase --continue` : 
- `git push origin new-func --force-with-lease` : 强制推送到我的远程 **(修改了历史)**
- **继续原分支开发**
- `git add .  |  git commit -m "提交信息"` : 本地修改分支内容
- **做一半下班了**
- `git push origin new-func` : 将做一半的内容上传到我的远程仓库 **(注意不PR)**

### 第三天 : 完成功能
- `git checkout new-func` : 切换到要做的分支
- `git pull origin new-func` : 拉取昨天的工作
- `git fetch upstream` : 更新项目仓库的main分支的新内容到本地 **(在分支更新变基)**
- `git rebase upstream/main` : 将项目仓库的main内容和本地的main内容合并
- **合并时出现冲突 : 解决冲突后**
- `git add .` : 保持冲突解决
- `git rebase --continue` : 
- `git push origin new-func --force-with-lease` : 强制推送到我的远程 **(修改了历史)**
- **完成剩余开发**
- `git add .  |  git commit -m "提交信息"` : 本地修改分支内容
- `git push origin new-func` : 将完成的功能分支提交到我的 $GitHub$
- 创建提交 $PR$

### 第四天 : $PR$ 不通过
- **与*第二天*相同, $push$ 后会自动合并到 $PR$**
