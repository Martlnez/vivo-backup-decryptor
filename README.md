# vivo 备份解密工具

🔓 解密 vivo/iQOO 互传（PhoneClone）备份中的加密文件

<div align="center">

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

[English](README_EN.md) | 简体中文

</div>

## ✨ 功能特点

- 🚀 **快速简单** - 纯 Python 实现，无需第三方依赖
- 📁 **智能恢复** - 自动还原原始文件名和文件夹结构
- 🎯 **多格式支持** - 支持 JPEG、WebP、PNG、MP4 等多种格式
- 🖥️ **Web 界面** - 提供易用的浏览器图形界面
- 🔍 **自动识别** - 自动检测文件类型

## 📋 支持设备

本工具适用于以下设备创建的备份：

- **vivo** 手机（X 系列、S 系列、Y 系列等）
- **iQOO** 手机（iQOO 系列、Neo 系列、Z 系列等）
- **OPPO** 手机（部分型号的互传功能）
- **Realme** 手机（部分型号的互传功能）

✅ 已在备份格式版本 2 (`backupPackageVer: 2`) 上测试通过

## 🚀 快速开始

### 方法一：命令行工具

```bash
# 基本用法
python decrypt.py "备份文件夹"

# 指定输出目录
python decrypt.py "备份文件夹" "输出文件夹"

# 详细输出模式
python decrypt.py "备份文件夹" -v

# 保留哈希文件名
python decrypt.py "备份文件夹" --keep-hash-names
```

### 方法二：Web 界面（推荐）

```bash
# 安装依赖（可选）
pip install flask

# 启动 Web 服务器
python web.py

# 在浏览器中打开
# http://localhost:5000
```

然后通过拖放或文件选择器上传您的备份文件夹。

## 📦 安装

### 系统要求

- Python 3.6 或更高版本
- 命令行工具无需外部依赖
- Web 界面需要 Flask（可选）

### 克隆仓库

```bash
git clone https://github.com/Martlnez/vivo-backup-decryptor.git
cd vivo-backup-decryptor
```

### 安装 Web 界面依赖（可选）

```bash
pip install flask
# 或使用 requirements.txt
pip install -r requirements.txt
```

## 📂 备份文件结构

```
备份文件夹/
├── .backup                 # JSON 元数据（设备型号、时间戳）
├── db/                     # LevelDB 索引（文件名映射）
│   ├── 000005.ldb
│   ├── CURRENT
│   └── MANIFEST-XXXXXX
├── 11fdb14d89dc...         # SHA-1 命名的加密数据文件
├── 00a5097ee4db...
└── ...
```

## 🔐 工作原理

### 加密算法

vivo 备份使用简单的 XOR 循环加密，密钥固定为 8 字节：

```
密钥: 5b 9d 2e f4 7f a3 c8 e1
```

加密公式：
```
密文[i] = 明文[i] XOR 密钥[i % 8]
```

### 文件格式类型

#### 类型 0/1 - 带魔术头的 JPEG

```
[4 字节: 80 7b 37 XX] + [XOR 加密数据]
```

- `807b3700` → JPEG with Exif (FFD8FFE1)
- `807b3701` → JPEG with JFIF (FFD8FFE0)

#### 无头部 - WebP/其他格式

```
[从 key[4] 开始的 XOR 加密数据]
```

使用密钥偏移 4 加密的文件，包括 WebP、PNG、MP4 等。

## 📊 使用示例

### 示例 1：基本解密

```bash
$ python decrypt.py "vivo S16 20260806_202318"

从索引中找到 114 个文件映射

  ✓ IMG_20260720_164053.jpg
  ✓ Screenshot_20240202_184845.webp
  ✓ video_20260115.mp4
  ...

==================================================
解密完成
==================================================
成功: 16 个文件
失败:  0 个文件
输出:  vivo S16 20260806_202318_decrypted
```

### 示例 2：详细输出

```bash
$ python decrypt.py "backup" "restored" -v

备份信息:
  型号: HONOR 30
  版本: 2
  状态: False

从索引中找到 114 个文件映射

  ✓ IMG_20260720_164053.jpg
  ...
```

## 🌐 Web 界面

Web 界面提供了用户友好的解密方式：

1. **上传** - 拖放或浏览选择备份文件夹
2. **处理** - 自动解密并显示进度
3. **下载** - 以 ZIP 格式获取解密后的文件

### 特性

- 📤 拖放上传
- 📊 实时进度跟踪
- 🎨 现代深色主题界面
- 📱 移动端响应式设计
- 💾 批量处理支持

## 🛠️ 高级用法

### Python API

```python
from decrypt import decrypt_file, parse_file_index

# 解密单个文件
data, ext = decrypt_file('11fdb14d89dc23ae...')
if data:
    with open(f'output{ext}', 'wb') as f:
        f.write(data)

# 解析文件索引
hash_map = parse_file_index('backup/db')
print(hash_map['11fdb14d89dc23ae...'])
# 输出: storage/emulated/0/DCIM/Camera/IMG_20260720.jpg
```

## ❓ 常见问题

### 为什么有些文件没有原始文件名？

备份可能被中断（`.backup` 中显示 `"success": false`）。文件仍可解密，但只能使用哈希值命名。

### 解密后的图片能正常打开吗？

可以。所有解密文件都是完整有效的图片/视频文件，可直接用任何图片查看器/播放器打开。

### 密钥对所有 vivo 手机通用吗？

根据测试，该密钥适用于 vivo 互传备份格式版本 2（`"backupPackageVer": 2`）。其他版本可能使用不同的密钥或加密算法。

### 能恢复联系人、短信等数据吗？

理论上可以。这些数据通常存储在 SQLite 数据库文件中（也会被加密），使用相同的密钥解密后可以读取。需要进一步分析数据库结构。

### 为什么有的备份文件夹只有几个文件？

备份过程可能被中断。`.backup` 文件中 `"success": false` 表示备份未完成。已传输的文件仍可正常解密。

## 🔬 技术细节

### XOR 加密的安全性问题

该备份方案使用的 XOR 加密存在以下弱点：

1. **固定密钥** - 所有备份使用相同密钥，一旦破解即可解密所有文件
2. **无初始化向量(IV)** - 相同明文加密后结果相同
3. **已知明文攻击** - JPEG 头部固定，可轻易推导密钥
4. **频率分析** - 字节分布特征未被隐藏
5. **尾部泄露** - 零填充区域直接暴露密钥

**与现代加密对比：**
- AES-256-GCM：密钥空间 2^256，带认证，抗已知明文攻击
- ChaCha20-Poly1305：流式加密，每次使用不同的 nonce

### 为什么厂商使用弱加密？

可能的原因：
1. **性能优先** - XOR 运算极快，适合大文件加密
2. **向后兼容** - 老设备性能有限
3. **安全需求较低** - 备份数据通常存储在用户自己的电脑上
4. **混淆而非加密** - 主要目的是防止普通用户直接查看，而非抵御专业攻击

## 📝 支持的文件类型

| 格式 | 扩展名 | 检测特征 |
|------|--------|----------|
| JPEG | `.jpg` | `FFD8FF` |
| PNG | `.png` | `89504E47` |
| GIF | `.gif` | `GIF8` |
| WebP | `.webp` | `RIFF...WEBP` |
| MP4 | `.mp4` | 偏移 4 处的 `ftyp` |
| ZIP | `.zip` | `PK\x03\x04` |
| PDF | `.pdf` | `%PDF` |
| MP3 | `.mp3` | `FFFB/FFF3` |

## 🤝 贡献

欢迎贡献！请随时提交问题或拉取请求。

### 开发

```bash
# 克隆仓库
git clone https://github.com/Martlnez/vivo-backup-decryptor.git
cd vivo-backup-decryptor

# 运行测试（如果有）
python -m pytest

# 运行代码检查
python -m pylint decrypt.py
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## ⚠️ 免责声明

本工具仅供教育和个人数据恢复目的使用。用户有责任确保他们有权解密数据。作者对滥用不承担任何责任。

## 🙏 致谢

- 逆向工程和密码分析社区
- 分享备份样本的 vivo/iQOO 用户

## 📚 参考资料

- [XOR 密码 - 维基百科](https://en.wikipedia.org/wiki/XOR_cipher)
- [JPEG 文件格式](https://en.wikipedia.org/wiki/JPEG)
- [WebP 规范](https://developers.google.com/speed/webp/docs/riff_container)
- [LevelDB 文档](https://github.com/google/leveldb)

## 📖 更多文档

- [快速开始指南](QUICKSTART.md) - 详细的使用说明
- [English README](README_EN.md) - English version

---

<div align="center">

**用 ❤️ 为数据恢复而生**

[报告问题](https://github.com/Martlnez/vivo-backup-decryptor/issues) · [请求功能](https://github.com/Martlnez/vivo-backup-decryptor/issues)

</div>
