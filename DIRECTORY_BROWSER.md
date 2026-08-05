# 目录浏览器使用说明

## 功能说明

现在可以通过图形界面选择下载目录，无需手动输入路径！

---

## 🚀 使用方法

### 方法 1: 浏览器选择（推荐）

1. 在 "Output Settings" 区域，点击 **📁 Browse** 按钮
2. 在弹出的目录浏览器中：
   - 点击文件夹名称进入子目录
   - 点击 **⬆️ Parent** 返回上级目录
   - 点击 **🏠 Home** 回到主目录
   - 点击 **🔄 Refresh** 刷新当前目录
3. 找到目标目录后，点击 **✓ Select This Directory** 确认

### 方法 2: 快捷路径

在 "Output Settings" 下方有常用路径快捷按钮：
- 🏠 **Home** - 用户主目录
- 📁 **Current Directory** - 当前工作目录
- 📥 **Downloads** - 下载文件夹
- 🖥️ **Desktop** - 桌面
- 🪟 **Windows Home** (WSL) - Windows 用户目录
- 📥 **Windows Downloads** (WSL) - Windows 下载文件夹

点击这些按钮会自动填充对应路径。

### 方法 3: 手动输入

仍然可以直接在输入框中手动输入路径，适合知道确切路径的用户。

---

## 📋 界面说明

### 目录浏览器界面

```
┌─────────────────────────────────────┐
│ 📁 Select Download Directory    ×  │
├─────────────────────────────────────┤
│ /home/user/data                     │ ← 当前路径
│                                     │
│ [⬆️ Parent] [🏠 Home] [🔄 Refresh] │ ← 导航按钮
│                                     │
│ ┌───────────────────────────────┐  │
│ │ 📁 astronomy                  │  │ ← 目录列表
│ │ 📁 downloads                  │  │   (点击进入)
│ │ 📁 projects                   │  │
│ └───────────────────────────────┘  │
│                                     │
│           [Cancel] [✓ Select]       │ ← 操作按钮
└─────────────────────────────────────┘
```

### 功能按钮

| 按钮 | 功能 |
|------|------|
| ⬆️ Parent | 返回上级目录 |
| 🏠 Home | 回到用户主目录 |
| 🔄 Refresh | 刷新当前目录 |
| Cancel | 取消选择 |
| ✓ Select | 选择当前目录 |

---

## 🌐 WSL 特殊功能

在 WSL 环境中，目录浏览器会自动检测并提供 Windows 路径：

- **Windows Home**: `/mnt/c/Users/YourName/`
- **Windows Downloads**: `/mnt/c/Users/YourName/Downloads/`
- **Windows Desktop**: `/mnt/c/Users/YourName/Desktop/`

这些路径可以在 Windows 资源管理器中直接访问。

---

## 💡 使用提示

### 推荐

- 使用浏览器选择：避免路径输入错误
- 使用快捷路径：一键选择常用目录
- WSL 用户：选择 Windows 目录更方便文件访问

### 注意事项

- 只显示目录，不显示文件
- 无权限的目录无法访问
- 目录不存在时会自动创建

---

## 🔧 技术说明

### 后端 API

- `GET /api/common-paths` - 获取常用路径列表
- `POST /api/browse` - 浏览指定路径

### 安全性

- 只能浏览文件系统，不能修改
- 自动过滤文件，只显示目录
- 无权限目录会提示错误

---

## 🎯 快速开始

1. 填写坐标信息
2. 点击 **📁 Browse** 选择下载目录
3. 选择 Survey 和参数
4. 点击 **Start Download**

简单直观，告别手动输入路径！🎉
