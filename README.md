# 商业计划书撰写系统

完全基于 **商业计划书大纲2026** 标准，专注于高质量商业计划书的撰写。

## 核心特性

- ✅ **76章节专业大纲** - 完整覆盖商业计划书所有必要内容
- ✅ **高质量提示词** - 每个章节都有专业的写作指导
- ✅ **Word文档生成** - 使用python-docx生成标准格式的商业计划书
- ✅ **表格和图片支持** - 支持插入表格、图片等内容
- ✅ **中文字体支持** - 默认使用宋体和黑体，符合中文商业计划书写规范

## 文件说明

```
aurora-agent/
├── business_plan_writer.py      # 核心功能模块
├── cli.py                        # 命令行接口
├── outline_with_prompts.json    # 完整76章节大纲
├── requirements.txt              # 依赖库
└── README.md                     # 说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化项目

```bash
python cli.py init --product "您的产品名称" --company "您的公司名称" --desc "项目描述"
```

### 3. 查看大纲信息

```bash
python cli.py info
```

### 4. 撰写内容

编辑 `output/content_plan.json` 文件，将您的内容填入每个章节的 `generated_content` 字段。

### 5. 生成Word文档

```bash
python cli.py build --input output/content_plan.json --output business_plan.docx
```

## 大纲结构

包含76个专业章节，覆盖：
- **摘要与背景** - 10个章节
- **产品与技术** - 18个章节
- **市场与竞争** - 15个章节
- **运营与商业模式** - 15个章节
- **财务与融资** - 10个章节
- **风险与附录** - 8个章节

## 标准参照

完全基于《商业计划书大纲2026》标准，与D:\计划书AI保持一致。
