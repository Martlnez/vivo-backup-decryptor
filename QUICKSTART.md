# Quick Start Guide

## 快速开始指南

### 方法一：命令行工具

#### 1. 克隆仓库
```bash
git clone https://github.com/Martlnez/vivo-backup-decryptor.git
cd vivo-backup-decryptor
```

#### 2. 运行解密
```bash
# 基础用法（输出到默认目录）
python decrypt.py "备份文件夹路径"

# 指定输出目录
python decrypt.py "备份文件夹路径" "输出文件夹路径"

# 详细输出模式
python decrypt.py "备份文件夹路径" -v
```

#### 示例
```bash
# Windows
python decrypt.py "C:\Users\YourName\Desktop\vivo S16 20260806_202318"

# Linux/macOS
python decrypt.py "/home/user/backup/vivo S16 20260806_202318"
```

---

### 方法二：Web 界面（推荐）

#### 1. 安装依赖
```bash
pip install flask
# 或使用 requirements.txt
pip install -r requirements.txt
```

#### 2. 启动 Web 服务器
```bash
python web.py
```

#### 3. 打开浏览器
访问：`http://localhost:5000`

#### 4. 使用界面
1. 拖拽或选择备份文件夹
2. 点击"开始解密"
3. 等待处理完成
4. 下载解密后的 ZIP 文件

---

## 常见问题

### ❓ 备份文件夹在哪里？

**Windows：**
- 通常在 `此电脑\手机型号\内部存储\PhoneClone` 或
- 连接手机后在 `MTP设备` 下查找

**Android：**
- `/storage/emulated/0/PhoneClone/`
- `/sdcard/PhoneClone/`

### ❓ 文件夹结构是什么样的？

正确的备份文件夹应包含：
```
备份文件夹/
├── .backup          (JSON 元数据文件)
├── db/              (索引目录)
│   ├── *.ldb
│   └── MANIFEST-*
└── [40位哈希文件]   (加密的数据文件)
```

### ❓ 解密失败怎么办？

1. **确认是 vivo/iQOO 备份**
   - 检查是否有 `.backup` 文件
   - 确认备份版本是否为 2

2. **检查文件完整性**
   - 备份是否完整（`.backup` 中 `success: true`）
   - 文件是否损坏

3. **Python 版本**
   - 确保 Python 3.6 或更高版本
   - 运行 `python --version` 检查

---

## 输出说明

### 成功示例
```
Found 114 file mappings in index

  ✓ IMG_20260720_164053.jpg
  ✓ Screenshot_20240202_184845.webp
  ✓ video_20260115.mp4
  ...

==================================================
Decryption Complete
==================================================
Success: 16 files
Failed:  0 files
Output:  vivo S16 20260806_202318_decrypted
```

### 输出目录结构
解密后会尽可能还原原始目录结构：
```
输出文件夹/
├── DCIM/
│   └── Camera/
│       └── IMG_20260720_164053.jpg
├── Pictures/
│   └── Screenshots/
│       └── Screenshot_20240202.webp
└── Download/
    └── file.zip
```

---

## 高级选项

### 保持哈希文件名
```bash
python decrypt.py "备份文件夹" --keep-hash-names
```
输出将使用 `<hash>.jpg` 格式，不恢复原始文件名。

### 仅解密特定文件
修改 `decrypt.py` 中的过滤条件：
```python
if filename.startswith('.') or len(filename) != 40:
    continue
# 添加自定义过滤
if not filename.startswith('11fdb'):  # 仅处理特定哈希
    continue
```

---

## 性能说明

| 文件数量 | 处理时间 | 内存占用 |
|---------|---------|---------|
| 10-50   | < 5 秒   | < 100 MB |
| 100-500 | < 30 秒  | < 200 MB |
| 1000+   | 1-3 分钟 | < 500 MB |

*实际性能取决于文件大小和硬盘速度*

---

## 安全说明

✅ **安全的操作：**
- 解密自己的备份数据
- 数据恢复和迁移
- 学习加密算法原理

❌ **禁止的操作：**
- 未经授权访问他人数据
- 用于任何非法目的
- 商业化使用他人数据

---

## 技术支持

- **GitHub Issues**: [提交问题](https://github.com/Martlnez/vivo-backup-decryptor/issues)
- **查看文档**: [README.md](README.md)
- **检查更新**: `git pull origin master`

---

## 更新日志

### v1.0.0 (2026-08-06)
- ✨ 初始版本发布
- ✨ 支持命令行和 Web 界面
- ✨ 自动识别多种文件格式
- ✨ 恢复原始文件名和目录结构
- ✨ 现代化深色主题 UI

---

**祝您数据恢复顺利！** 🎉
