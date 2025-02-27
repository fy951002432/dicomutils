import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pydicom
from pydicom.uid import UID
from PIL import Image
import numpy as np
import logging
from datetime import datetime
from pydicom.config import enforce_valid_values
import json  # 导入 json 模块用于保存和读取目录信息

# 强制使用 pylibjpeg 解码器
enforce_valid_values()
pydicom.config.pixel_data_handlers.util.reset_pixel_data_handler("pylibjpeg")

# 定义默认目录
DEFAULT_FOLDERS = {
    "input_folder": "./input",
    "dicom_output_folder": "./output",
    "png_output_folder": "./image",
    "log_folder": "./log",
    "structured_info_folder": "./txt"
}

# 初始化全局变量
input_folder = None
dicom_output_folder = None
png_output_folder = None
log_folder = None
structured_info_folder = None  # 结构化信息输出目录

# 读取或初始化目录信息
def load_folder_info():
    try:
        with open("folder_info.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return DEFAULT_FOLDERS.copy()

# 保存目录信息
def save_folder_info(folders):
    with open("folder_info.json", "w") as f:
        json.dump(folders, f)

# 加载目录信息
folder_info = load_folder_info()
input_folder = folder_info.get("input_folder", DEFAULT_FOLDERS["input_folder"])
dicom_output_folder = folder_info.get("dicom_output_folder", DEFAULT_FOLDERS["dicom_output_folder"])
png_output_folder = folder_info.get("png_output_folder", DEFAULT_FOLDERS["png_output_folder"])
log_folder = folder_info.get("log_folder", DEFAULT_FOLDERS["log_folder"])
structured_info_folder = folder_info.get("structured_info_folder", DEFAULT_FOLDERS["structured_info_folder"])

# 创建主窗口
root = tk.Tk()
root.title("DICOM 工具")
convert_to_grayscale = tk.BooleanVar(value=True)  # 默认勾选灰度转换

# 默认的 DICOM 标签修改规则
default_tags_to_modify = {
    "PatientID": "",  # (0010,0020)
    "PatientName": "",  # (0010,0010)
    "PatientBirthDate": "",  # (0010,0030)
    "PatientSex": "",  # (0010,0040)
    "PatientAge": "",  # (0010,1010)
    "PatientComments": "",  # (0010,4000)
    "PatientSize": "",  # (0010,1020)
    "PatientWeight": "",  # (0010,1030)
    "PatientAddress": "",  # (0010,1040)
    "InstitutionName": "",  # (0008,0080)
    "InstitutionCodeSequence": "",  # (0008,0082)
    "InstitutionAddress": "",  # (0008,0081)
    "InstitutionalDepartmentName": "",  # (0008,1040)
    "OperatorsName": "",  # (0008,1070)
    "DeviceID": "",  # (0018,1003)
    "DeviceSerialNumber": "",  # (0018,1000)
    "DeviceDescription": "",  # (0050,0020)
    "ReferringPhysicianName": "",  # (0008,0090)
    "StudyInstanceUID": "",  # (0020,000d)
    "SeriesInstanceUID": "",  # (0020,000e)
    "SOPInstanceUID": "",  # (0008,0018)
    "AccessionNumber": "",  # (0008,0050)
    "StudyID": "",  # (0020,0010)
    "StudyDate": "",  # (0008,0020)
    "StudyTime": "",  # (0008,0030)
    "SeriesDate": "",  # (0008,0021)
    "SeriesTime": "",  # (0008,0031)
    "AcquisitionDate": "",  # (0008,0022)
    "ContentDate": "",  # (0008,0023)
    "AcquisitionDateTime": "",  # (0008,002a)
    "AcquisitionTime": "",  # (0008,0032)
    "ContentTime": "",  # (0008,0033)
    "DateOfSecondaryCapture": "",  # (0018,1012)
    "TimeOfSecondaryCapture": "",  # (0018,1014)
    "InstanceCreationDate": "",  # (0008,0012)
    "InstanceCreationTime": "",  # (0008,0013)
    "PerformedProcedureStepDescription": "",  # (0040,0254)
    "StudyDescription": "",  # (0008,1030)
    "SeriesDescription": ""  # (0008,103e)
}

# 当前的标签修改规则（初始化为默认值）
tags_to_modify = default_tags_to_modify.copy()


# 配置日志记录
def setup_logging(log_path):
    pass # function body is omitted


def select_input_folder():
    """选择输入文件夹"""
    global input_folder
    folder = filedialog.askdirectory(initialdir=input_folder)
    if folder:
        input_folder = folder
        input_label.config(text=f"输入文件夹: {input_folder}")
        folder_info["input_folder"] = input_folder
        save_folder_info(folder_info)


def select_dicom_output_folder():
    """选择修改后的 DICOM 文件输出文件夹"""
    global dicom_output_folder
    folder = filedialog.askdirectory(initialdir=dicom_output_folder)
    if folder:
        dicom_output_folder = folder
        dicom_output_label.config(text=f"DICOM 输出文件夹: {dicom_output_folder}")
        folder_info["dicom_output_folder"] = dicom_output_folder
        save_folder_info(folder_info)


def select_png_output_folder():
    """选择转换后的 PNG 文件输出文件夹"""
    global png_output_folder
    folder = filedialog.askdirectory(initialdir=png_output_folder)
    if folder:
        png_output_folder = folder
        png_output_label.config(text=f"PNG 输出文件夹: {png_output_folder}")
        folder_info["png_output_folder"] = png_output_folder
        save_folder_info(folder_info)


def select_log_folder():
    """选择日志文件夹"""
    global log_folder
    folder = filedialog.askdirectory(initialdir=log_folder)
    if folder:
        log_folder = folder
        log_label.config(text=f"日志文件夹: {log_folder}")
        folder_info["log_folder"] = log_folder
        save_folder_info(folder_info)


def select_structured_info_folder():
    """选择结构化信息输出文件夹"""
    global structured_info_folder
    folder = filedialog.askdirectory(initialdir=structured_info_folder)
    if folder:
        structured_info_folder = folder
        structured_info_label.config(text=f"结构化信息输出文件夹: {structured_info_folder}")
        folder_info["structured_info_folder"] = structured_info_folder
        save_folder_info(folder_info)


def reset_tags_to_default():
    """重置标签修改规则为默认值"""
    pass # function body is omitted


def add_tag_to_modify():
    """添加需要修改的 DICOM 标签"""
    pass # function body is omitted


def remove_tag_to_modify():
    """移除选中的标签修改规则"""
    pass # function body is omitted


def update_progress(current, total, progress_label):
    """更新进度信息"""
    pass # function body is omitted


def modify_dicom_tags():
    """修改 DICOM 标签"""
    pass # function body is omitted


def convert_dicom_to_png():
    """将 DICOM 文件转换为 PNG"""
    pass # function body is omitted


def save_structured_info():
    """为每个 DICOM 文件单独保存结构化信息"""
    pass # function body is omitted



# 日志显示区域
# log_text = tk.Text(root, height=10, width=60)
# log_text.pack(pady=10)
# log_text.config(state="disabled")  # 禁止用户编辑

# 文件夹选择区域
folder_frame = ttk.LabelFrame(root, text="文件夹选择")
folder_frame.pack(pady=10, padx=10, fill=tk.X)

input_label = tk.Label(folder_frame, text=f"输入文件夹: {input_folder}")
input_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
input_button = tk.Button(folder_frame, text="选择", command=select_input_folder)
input_button.grid(row=0, column=1, padx=5, pady=5)

dicom_output_label = tk.Label(folder_frame, text=f"DICOM 输出文件夹: {dicom_output_folder}")
dicom_output_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
dicom_output_button = tk.Button(folder_frame, text="选择", command=select_dicom_output_folder)
dicom_output_button.grid(row=1, column=1, padx=5, pady=5)

png_output_label = tk.Label(folder_frame, text=f"PNG 输出文件夹: {png_output_folder}")
png_output_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
png_output_button = tk.Button(folder_frame, text="选择", command=select_png_output_folder)
png_output_button.grid(row=2, column=1, padx=5, pady=5)

structured_info_label = tk.Label(folder_frame, text=f"结构化信息输出文件夹: {structured_info_folder}")
structured_info_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
structured_info_button = tk.Button(folder_frame, text="选择", command=select_structured_info_folder)
structured_info_button.grid(row=3, column=1, padx=5, pady=5)

log_label = tk.Label(folder_frame, text=f"日志文件夹: {log_folder}")
log_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
log_button = tk.Button(folder_frame, text="选择", command=select_log_folder)
log_button.grid(row=4, column=1, padx=5, pady=5)

# 配置化修改 DICOM 标签
config_frame = ttk.LabelFrame(root, text="DICOM匿名化字段配置")
config_frame.pack(pady=10, padx=10, fill=tk.X)

tk.Label(config_frame, text="标签名称").grid(row=0, column=0, padx=5, pady=5)
tag_name_entry = tk.Entry(config_frame)
tag_name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(config_frame, text="新值").grid(row=0, column=2, padx=5, pady=5)
new_value_entry = tk.Entry(config_frame)
new_value_entry.grid(row=0, column=3, padx=5, pady=5)

add_button = tk.Button(config_frame, text="添加", command=add_tag_to_modify)
add_button.grid(row=0, column=4, padx=5, pady=5)

remove_button = tk.Button(config_frame, text="移除", command=remove_tag_to_modify)
remove_button.grid(row=0, column=5, padx=5, pady=5)

reset_button = tk.Button(config_frame, text="重置为默认值", command=reset_tags_to_default)
reset_button.grid(row=0, column=6, padx=5, pady=5)

tag_listbox = tk.Listbox(config_frame, height=10, width=50)
tag_listbox.grid(row=1, column=0, columnspan=7, padx=5, pady=5)

# 初始化标签列表显示默认值
for tag, value in tags_to_modify.items():
    tag_listbox.insert(tk.END, f"{tag}: {value}")

# 配置选项
options_frame = ttk.LabelFrame(root, text="其他配置")
options_frame.pack(pady=10, padx=10, fill=tk.X)

ttk.Checkbutton(options_frame, text="图像灰度转换", variable=convert_to_grayscale).pack(side=tk.LEFT, padx=10)

# 操作按钮
button_frame = ttk.Frame(root)
button_frame.pack(pady=10, padx=10, fill=tk.X)

modify_button = tk.Button(button_frame, text="DICOM文件匿名化", command=modify_dicom_tags)
modify_button.pack(side=tk.LEFT, padx=10)

convert_button = tk.Button(button_frame, text="转换为 PNG", command=convert_dicom_to_png)
convert_button.pack(side=tk.LEFT, padx=10)

info_button = tk.Button(button_frame, text="保存结构化信息", command=save_structured_info)
info_button.pack(side=tk.LEFT, padx=10)

# 启动主循环
root.mainloop()