# Post 14: GitHub Actions被高估了，我换回了shell脚本

GitHub Actions 现在几乎成了所有开源项目的标配。我也曾是它的忠实拥趸，觉得 YAML 驱动一切很优雅。

但我最近把几个核心项目的 CI/CD 流程全部换回了原生的 shell 脚本。

我知道这个观点很有争议，但在实际操作中，shell 脚本的优势实在太明显了。

---

## 🎯 我的方法

我现在只用 GitHub Actions 做最简单的触发器：
```yaml
jobs:
  run-shell:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: bash ./scripts/deploy.sh
```

所有的逻辑都在 `./scripts/deploy.sh` 里。

---

## 💬 争议点

1. **YAML 调试是地狱**: 
   每次改个配置都要 git commit, git push, 等待 CI 运行，看它报错，然后再来一次。
   在本地运行 `bash ./scripts/deploy.sh` 只需要一秒钟。

2. **锁定平台**:
   如果有一天我要搬到 GitLab 或者自建 Jenkins，GitHub Actions 的 YAML 全都要重写。
   Shell 脚本到哪儿都能跑。

3. **依赖地狱**:
   各种 `uses: actions/setup-node@v4`, `uses: docker/login-action@v3`。
   这些 Action 本身也是依赖，也会更新，也会失效。
   `apt-get install` 永远比这些第三方 Action 稳定。

4. **过度设计**:
   大多数项目需要的只是：测试 -> 构建 -> 上传。
   为了这三步去学一整套 YAML 语法，真的值得吗？

---

## 🤔 你们怎么看？

互动问题1: 你曾经被 GitHub Actions 的 YAML 配置折磨过吗？
互动问题2: 你们更倾向于使用平台原生工具，还是保持脚本的跨平台性？
互动问题3: 你们觉得 Shell 脚本在现代 DevOps 中已经过时了吗？

评论区告诉我你们的想法！

---

#技术 #GitHub #DevOps #争议 #Shell #编程
