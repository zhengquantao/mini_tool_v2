# MINI_TOOL

## 简介

> 基于wxPython 实现智能数据分析工具.

![效果图]()


## 支持功能
- [x] Python3.10+版本
- [x] 支持跨平台windows、mac、linux
- [x] 支持风场数据分析
- [x] 支持能效分析
- [x] 支持控制曲线分析
- [x] 支持本地离线数据分析
- [ ] 支持数据库数据分析

## 安装和使用

### 安装 

```bash
# 1.克隆
git clone xxx.git
# 2.进入项目
cd mini_tool_v2
# 3.安装包依赖
pip install -r requirements.txt
# 4.启动
python -m main
```

### 使用

请看教程[链接](https://www.baidu.com/)

## 打包

- PyInstaller
  ```bash
  # windows
  pyinstaller mini-tool.spec
  ```


## 注意
- wxPython==4.2.1如何去掉抓手？
    > 目前官方没有提供隐藏抓手的功能,需要更改源码的auibar.py文件注释掉对应代码。如下：
    >
    > auibar.py +3481
    > 
    > `# self._art.DrawGripper(dc, self, gripper_rect)`

- 打包pyechart报错？
    > 解决方案：https://pyecharts.org/#/zh-cn/pyinstaller_pack
