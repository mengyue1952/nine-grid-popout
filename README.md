# Nine Grid Popout

一个用于 Codex 的九宫格突破人物合成技能。它将六张照片排成固定九宫格，并把第1张照片的透明人物抠像放在最上层；默认人物比例为原始抠像的 120%，以 P=T 规则精确定位。

第一次使用可直接阅读：[冲出九宫格照片简版教程](QUICKSTART.md)。

## 功能

- 固定六图九宫格布局
- 第1张照片的背景连续跨越第2、3、5、6格
- 默认将原始人物抠像缩放至120%
- 支持任意正比例缩放和水平、垂直平移
- 自动扩展画布，避免破框人物被裁切
- 对几何位置、图层顺序和输出像素进行确定性校验
- 全程本地处理，不上传或重新生成用户素材

## 安装

将本仓库克隆到 Codex 的个人技能目录：

```powershell
git clone https://github.com/mengyue1952/nine-grid-popout.git "$HOME/.codex/skills/nine-grid-popout"
```

也可以直接下载仓库中的 [`release/nine-grid-popout.skill`](release/nine-grid-popout.skill) 安装包。

## 使用

在 Codex 中提供以下素材：

1. 第1张照片移除人物后的修复背景图
2. 第1张照片的完整透明背景人物抠像
3. 按顺序排列的第2至第6张照片

然后提出类似请求：

```text
使用 $nine-grid-popout 生成九宫格突破人物图片。
```

首次输出默认使用120%人物比例并按 P=T 标准位置对齐。之后可以指定其他比例，例如80%、100%或140%，也可以要求人物向任意方向平移。

## 文件结构

- `SKILL.md`：技能入口与操作规则
- `scripts/nine_grid.py`：确定性拼图、缩放、合成和校验脚本
- `references/specification.md`：布局及锚点计算规范
- `references/edit-prompts.md`：缺失素材时可选的图片编辑提示
- `agents/openai.yaml`：Codex 界面信息

## 依赖

- Python 3.10+
- Pillow

## 隐私

此技能按本地文件处理流程设计。除非用户明确要求并授权，不会上传、重新生成或修改用户提供的原始图片。
