# Markdown 图片批量上传工具

## 功能特性
- 批量替换Markdown文件中的本地图片为GitHub链接
- 自动处理相对路径
- 创建备份文件(.bak)
- 支持递归处理目录

## 快速开始

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置GitHub**
- 在GitHub创建图片仓库
- 生成个人访问令牌（需勾选repo权限）
- 编辑config.json填写配置信息

3. **使用示例**
```bash
# 处理单个文件
python md_uploader.py example.md

# 递归处理目录
python md_uploader.py docs/ -r
```

## 文件结构
- 原文件：`![alt](local/image.jpg)`
- 处理后：`![alt](https://raw.githubusercontent.com/用户名/仓库名/分支/markdown_images/{markdown name}/image.jpg)`

## 注意事项
1. 自动跳过网络图片地址
2. 原始文件会生成.bak备份
3. 日志记录在upload.log文件

## 配置文件说明（config.json）

| 字段      | 说明                         |
|-----------|------------------------------|
| token     | 你的 GitHub 个人访问令牌      |
| owner     | 你的 GitHub 用户名            |
| repo      | 你的 GitHub 仓库名称          |
| branch    | 仓库分支（如 master/main）    |
| save_dir  | 图片上传保存的目录            |

请确保 config.json 配置正确，否则图片将无法上传。

## 日志说明
- 所有上传及处理信息会记录在 upload.log 文件中，便于排查问题。

## 常见问题
- GitHub Token 权限不足导致上传失败：请确保 token 具备 repo 权限。
- 图片未上传成功：检查 config.json 配置及网络连接。
- 文件未生成 .bak 备份：请确认脚本有写入权限。

## 贡献指南
1. Fork 本仓库并新建分支。
2. 提交你的修改并发起 Pull Request。
3. 欢迎提交 issue 反馈 bug 或建议。

## 联系方式
如有问题或建议，请通过 issue 或邮箱联系维护者。

---

如需进一步帮助，欢迎留言！
