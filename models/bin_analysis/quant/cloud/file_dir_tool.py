#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 文件目录处理工具
# 功能描述：目录创建、文件保存等
#
# 主要功能：
# > 1. 目录创建
# > 2. 文件路径获取
# --------------
#
# 输入Input：
# 输出Output：
#
# 其它模块、文件关系：
#
# 备注:
# ~~~~~~~~~~~~~~~~~~~~~~
#
# <--------------------------------------------------------------------


# --------------------------------------------------------------------
# ***
# 加载包 (import package)
# ***
# --------------------------------------------------------------------
import os


# --------------------------------------------------------------------
# ***
# 数据字段名称配置
# data field name [column name]
# ***
# --------------------------------------------------------------------

# 项目分析数据目录
proj_dir_name = "proj"


# --------------------------------------------------------------------
# ***
# 文件目录辅助函数
# ***
# --------------------------------------------------------------------

def get_dir(file_str=None):
    """
    获取文件的当前路径
    
    :param file_str: 文件__file__参数
    
    :return: 文件的目录路径
    """

    if file_str is None:
        file_path = os.path.abspath(__file__)
    else:
        file_path = os.path.abspath(file_str)
    
    dir_path = os.path.dirname(file_path)

    return dir_path


def create_dir(dir_name, dir_path=None):
    """
    创建文件目录

    :param dir_name: 目录名称
    :param dir_path: 文件根路径
    
    :return: 目标文件目录路径
    """
    
    if dir_path is None:
        dir_path = get_dir()
    
    full_path = os.path.join(dir_path, dir_name)
    
    if not os.path.isdir(full_path):
        os.makedirs(full_path)
    
    return full_path


def create_proj_dir(proj_name, file_str=None):
    """
    创建项目文件目录

    :param proj_name: 项目名称
    :param dir_path: 文件根路径
    
    :return: 项目文件目录路径
    """

    # 根目录
    root_dir = get_dir(file_str)

    # 所有项目文件根目录
    proj_root_dir = create_dir(proj_dir_name, root_dir)

    target_proj_dir = create_dir(proj_name, proj_root_dir)

    return target_proj_dir


def get_full_path(dir_path, file_name):
    """生成文件完整路径

    Args:
        dir_path (str): 图像文件存储路径
        file_name (str): 文件名称
    """

    return os.path.join(dir_path, file_name)

