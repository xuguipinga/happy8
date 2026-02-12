# PowerShell 快捷操作指南 (PowerShell Shortcuts Guide)

本文档介绍 PowerShell 和终端中的各种快捷操作，帮助您高效地导航和操作文件。

---

## 📋 目录

- [Tab 自动补全](#tab-自动补全)
- [路径导航快捷键](#路径导航快捷键)
- [历史命令](#历史命令)
- [文件和目录操作](#文件和目录操作)
- [VS Code 集成终端技巧](#vs-code-集成终端技巧)

---

## ⌨️ Tab 自动补全

### 基本用法

**最重要的快捷键：`Tab`**

```powershell
# 输入部分文件名后按 Tab，会自动补全
cd eco<Tab>        # 自动补全为 ecommerce-admin
cd backend\t<Tab>  # 自动补全为 backend\tests

# 如果有多个匹配项，连续按 Tab 循环切换
cd e<Tab><Tab><Tab>  # 在所有 e 开头的目录间切换

# Shift+Tab 反向循环
cd e<Tab><Shift+Tab>  # 反向切换匹配项
```

### 高级补全

```powershell
# 补全命令
pyt<Tab>           # 自动补全为 python

# 补全参数
python -<Tab>      # 显示可用参数

# 补全文件路径（支持相对和绝对路径）
cd D:\Work<Tab>    # 补全绝对路径
cd ..\<Tab>        # 补全上级目录
```

---

## 🧭 路径导航快捷键

### 快速导航

```powershell
# 返回上一级目录
cd ..

# 返回上两级目录
cd ..\..

# 返回到用户主目录
cd ~
# 或
cd $HOME

# 返回到上一个工作目录
cd -

# 直接跳转到根目录
cd \
```

### 使用通配符

```powershell
# 使用 * 通配符
cd *admin         # 跳转到包含 admin 的目录
cd ecom*\back*    # 跳转到 ecommerce-admin\backend

# 列出所有 .py 文件
ls *.py

# 列出所有子目录中的 .md 文件
ls **\*.md
```

### 路径别名

```powershell
# 创建路径别名（当前会话有效）
$backend = "D:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\backend"
cd $backend

# 永久保存别名（添加到 PowerShell 配置文件）
# 编辑配置文件
notepad $PROFILE

# 在配置文件中添加：
function cdbackend { Set-Location "D:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\backend" }
function cdfrontend { Set-Location "D:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\frontend" }

# 使用别名
cdbackend
cdfrontend
```

---

## 🕐 历史命令

### 快捷键

```powershell
# ↑ (上箭头) - 上一条命令
# ↓ (下箭头) - 下一条命令

# Ctrl+R - 搜索历史命令（反向搜索）
# 输入关键词，按 Ctrl+R 继续搜索上一个匹配项

# F7 - 显示命令历史列表（可用箭头选择）

# F8 - 根据当前输入搜索历史
# 例如：输入 "cd"，按 F8 会显示所有 cd 开头的历史命令
```

### 历史命令管理

```powershell
# 查看历史命令
Get-History
# 或简写
h

# 执行历史命令（#123 是命令 ID）
Invoke-History 123
# 或简写
r 123

# 清除历史
Clear-History
```

---

## 📁 文件和目录操作

### 快速查看

```powershell
# 列出当前目录内容
ls
# 或
dir
# 或
Get-ChildItem

# 只显示目录
ls -Directory

# 只显示文件
ls -File

# 显示隐藏文件
ls -Force

# 树形显示目录结构
tree
# 或只显示目录
tree /F
```

### 快速创建和删除

```powershell
# 创建目录
mkdir new-folder
# 或
md new-folder

# 创建多级目录
mkdir -p parent\child\grandchild

# 创建文件
New-Item file.txt
# 或
ni file.txt

# 快速创建并写入内容
"content" > file.txt

# 删除文件
rm file.txt
# 或
del file.txt

# 删除目录（包括内容）
rm -r folder
# 或强制删除
rm -rf folder
```

### 复制和移动

```powershell
# 复制文件
cp source.txt destination.txt
# 或
copy source.txt destination.txt

# 复制目录
cp -r source-folder destination-folder

# 移动文件
mv source.txt destination.txt
# 或
move source.txt destination.txt
```

---

## 💻 VS Code 集成终端技巧

### 终端快捷键

```
Ctrl + `           - 打开/关闭终端
Ctrl + Shift + `   - 新建终端
Ctrl + Shift + 5   - 分割终端
Ctrl + PageUp/Down - 切换终端标签
```

### 右键菜单快捷操作

1. **在文件资源管理器中右键文件夹**
   - 选择 "在集成终端中打开"
   - 自动打开终端并 cd 到该目录

2. **在编辑器中右键文件**
   - 选择 "在终端中打开"
   - 自动 cd 到文件所在目录

3. **拖拽文件到终端**
   - 直接拖拽文件/文件夹到终端
   - 自动粘贴完整路径

### 路径复制技巧

```powershell
# 复制当前路径到剪贴板
pwd | clip
# 或
Get-Location | Set-Clipboard

# 复制文件路径
(Get-Item file.txt).FullName | clip
```

---

## 🚀 高级技巧

### 使用 PSReadLine 增强功能

PowerShell 5.0+ 自带 PSReadLine，提供智能补全：

```powershell
# 查看 PSReadLine 版本
Get-Module PSReadLine

# 启用预测性 IntelliSense（PowerShell 7.1+）
Set-PSReadLineOption -PredictionSource History

# 设置补全颜色
Set-PSReadLineOption -Colors @{
    Command = 'Yellow'
    Parameter = 'Green'
    String = 'DarkCyan'
}
```

### 使用 Oh My Posh 美化终端

```powershell
# 安装 Oh My Posh
winget install JanDeDobbeleer.OhMyPosh

# 安装 Nerd Font（推荐 CascadiaCode）
oh-my-posh font install

# 初始化主题
oh-my-posh init pwsh --config "$env:POSH_THEMES_PATH\paradox.omp.json" | Invoke-Expression

# 添加到配置文件永久生效
notepad $PROFILE
# 添加上面的初始化命令
```

### 使用 Z 目录跳转

```powershell
# 安装 z（智能目录跳转）
Install-Module -Name z -Force

# 使用 z 跳转到最近访问的目录
z backend      # 跳转到包含 backend 的最近目录
z ecom         # 跳转到包含 ecom 的最近目录

# z 会记住您访问过的目录，无需输入完整路径
```

---

## 📝 实用示例

### 场景 1：快速进入项目后端目录

```powershell
# 方法 1：使用 Tab 补全
cd D:\Work<Tab>\Pro<Tab>\Eco<Tab>\eco<Tab>\back<Tab>

# 方法 2：使用通配符
cd D:\*\*\Ecom*\ecom*\back*

# 方法 3：创建别名（首次设置后）
cdbackend

# 方法 4：使用 z（访问过一次后）
z backend
```

### 场景 2：启动项目（完整流程）

```powershell
# 使用 Tab 补全和历史命令
cd eco<Tab>\back<Tab>    # Tab 补全路径
.\.venv\Scripts\activate # 可以用 ↑ 调出历史命令
python run.py            # 可以用 ↑ 调出历史命令
```

### 场景 3：在 VS Code 中快速操作

1. 在左侧文件树中右键 `backend` 文件夹
2. 选择 "在集成终端中打开"
3. 输入 `.\.venv<Tab>` 自动补全激活脚本
4. 输入 `python run.py`

---

## 🎯 最佳实践总结

1. **多用 Tab 键** - 这是最基本也是最有用的快捷操作
2. **善用 ↑ 键** - 重复执行命令时非常方便
3. **使用 Ctrl+R** - 快速搜索历史命令
4. **创建别名** - 为常用路径创建快捷方式
5. **使用通配符** - 减少输入，提高效率
6. **VS Code 右键菜单** - 直接在目标目录打开终端
7. **安装增强工具** - Oh My Posh、z 等提升体验

---

**最后更新：** 2026-02-12  
**维护者：** Ecommerce Admin Team
