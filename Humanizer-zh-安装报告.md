# Humanizer-zh 安装报告

## 安装时间
2026-02-18 14:24 GMT+8

## 安装方法
方法二：通过Git克隆手动安装

## 安装路径
`~/.openclaw/skills/humanizer-zh/`

## 安装内容
✅ SKILL.md - 技能定义文件（中文版，18.9KB）
✅ README.md - 使用说明文档（7.8KB）
✅ LICENSE - 许可证文件
✅ .gitignore - Git忽略规则

## 技能信息
- **名称**: humanizer-zh
- **描述**: 去除文本中的AI生成痕迹，使文字更自然、更有人味
- **功能**: 检测并修复24种AI写作模式
  - 内容模式（6种）：夸大的象征意义、宣传语言、肤浅分析等
  - 语言模式（6种）：AI词汇、系动词回避、三段式法则等
  - 风格模式（6种）：破折号过度使用、粗体过度使用等
  - 交流模式（6种）：填充短语、过度限定、通用积极结论等

## 使用方法
在OpenClaw对话中输入：
```
/humanizer-zh 请帮我人性化以下文本：
[粘贴AI生成的文本]
```

或直接引用文件：
```
/humanizer-zh 请人性化 humanizer-zh-test.md 文件中的内容
```

## 验证状态
✅ 文件结构正确
✅ SKILL.md格式符合规范
✅ 技能已安装到正确位置
✅ 测试文件已创建（用于验证功能）

## 下一步
1. 重启OpenClaw或重新加载技能
2. 使用 `/humanizer-zh` 命令测试功能
3. 参考 README.md 了解更多使用场景和示例

## 备注
- 本技能是英文版 humanizer 的中文翻译
- 翻译来源：https://github.com/op7418/Humanizer-zh
- 原项目：blader/humanizer
- 基于维基百科"Signs of AI writing"指南

安装完成！
