# MINI_TOOL

## 简介

> 基于wxPython 实现智能数据分析工具.

![效果图]()


## 支持功能
- [x] Python3.9+版本
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

## 待优化
1. ~~结果文件“....html”菜单不能有“新建文件夹”~~
2. ~~浆距角-功率分析 横坐标-坐标轴从-5度开始~~
3. ~~风资源对比：概率密度 修改名称，改成风频~~
4. ~~首次进入没有项目的情况下，左边不展示项目（因为 没有项目）~~
5. ~~首页换成 深圳量云 介绍~~
6. ~~左边导航条的 ".mini" 影藏掉（不显示）~~
7. ~~左边打开文件“刷新”不正常~~
8. ~~最左边的边栏“Package”换成"Project" （类似透视图模式的概念）~~
9. ~~增加NoteBook右键全部关闭~~
10. ~~增加NoteBook右键分屏~~
11. ~~增加项目树双击打开文件~~
12. ~~修复点击能效总览时等待加载框自动关闭的问题~~
13. ~~修复存在两个result文件夹问题~~
14. ~~修复图片下载文字遮挡问题~~
15. ~~修复CSV浮动出现窗口过大BUG~~
16. 部分浮动窗口显示异常
17. ~~去掉bin分仓曲线为0~~
18. ~~bin分仓label排序~~ 
19. ~~加表格赛马排行~~
20. ~~增加文件图标~~
