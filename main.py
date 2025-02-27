import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pydicom
from pydicom.uid import UID
from PIL import Image
import numpy as np
import logging
from datetime import datetime


# 初始化全局变量
input_folder = None
dicom_output_folder = None
png_output_folder = None
log_folder = None
structured_info_folder = None  # 结构化信息输出目录

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
    global log_file
    log_file = os.path.join(log_path, "dicom_tool.log")
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="a", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    # 将日志信息输出到 GUI
    # class TextHandler(logging.Handler):
    #     def emit(self, record):
    #         msg = self.format(record)
    #         log_text.config(state="normal")
    #         log_text.insert(tk.END, msg + "\n")
    #         log_text.config(state="disabled")
    #         log_text.yview(tk.END)  # 自动滚动到底部

    # logging.getLogger().addHandler(TextHandler())
    # logging.info("日志记录已启动。")


def select_input_folder():
    """选择输入文件夹"""
    global input_folder
    input_folder = filedialog.askdirectory()
    input_label.config(text=f"输入文件夹: {input_folder}")
    logging.info(f"选择了输入文件夹: {input_folder}")


def select_dicom_output_folder():
    """选择修改后的 DICOM 文件输出文件夹"""
    global dicom_output_folder
    dicom_output_folder = filedialog.askdirectory()
    dicom_output_label.config(text=f"DICOM 输出文件夹: {dicom_output_folder}")
    logging.info(f"选择了 DICOM 输出文件夹: {dicom_output_folder}")


def select_png_output_folder():
    """选择转换后的 PNG 文件输出文件夹"""
    global png_output_folder
    png_output_folder = filedialog.askdirectory()
    png_output_label.config(text=f"PNG 输出文件夹: {png_output_folder}")
    logging.info(f"选择了 PNG 输出文件夹: {png_output_folder}")


def select_log_folder():
    """选择日志文件夹"""
    global log_folder
    log_folder = filedialog.askdirectory()
    log_label.config(text=f"日志文件夹: {log_folder}")
    setup_logging(log_folder)
    logging.info(f"选择了日志文件夹: {log_folder}")


def select_structured_info_folder():
    """选择结构化信息输出文件夹"""
    global structured_info_folder
    structured_info_folder = filedialog.askdirectory()
    structured_info_label.config(text=f"结构化信息输出文件夹: {structured_info_folder}")
    logging.info(f"选择了结构化信息输出文件夹: {structured_info_folder}")


def reset_tags_to_default():
    """重置标签修改规则为默认值"""
    global tags_to_modify
    tags_to_modify = default_tags_to_modify.copy()
    tag_listbox.delete(0, tk.END)
    for tag, value in tags_to_modify.items():
        tag_listbox.insert(tk.END, f"{tag}: {value}")
    logging.info("标签修改规则已重置为默认值。")


def add_tag_to_modify():
    """添加需要修改的 DICOM 标签"""
    tag_name = tag_name_entry.get()
    new_value = new_value_entry.get()
    if tag_name and new_value:
        tags_to_modify[tag_name] = new_value
        tag_listbox.insert(tk.END, f"{tag_name}: {new_value}")
        tag_name_entry.delete(0, tk.END)
        new_value_entry.delete(0, tk.END)
        logging.info(f"添加了标签修改规则: {tag_name} -> {new_value}")
    else:
        messagebox.showwarning("警告", "标签名称和新值不能为空！")


def remove_tag_to_modify():
    """移除选中的标签修改规则"""
    selected = tag_listbox.curselection()
    if selected:
        tag = tag_listbox.get(selected)
        tag_name = tag.split(":")[0].strip()
        del tags_to_modify[tag_name]
        tag_listbox.delete(selected)
        logging.info(f"移除了标签修改规则: {tag_name}")


def update_progress(current, total, progress_label):
    """更新进度信息"""
    progress = int((current / total) * 100)
    progress_label.config(text=f"处理进度: {progress}% 完成")
    progress_label.update()


def modify_dicom_tags():
    """修改 DICOM 标签"""
    if not input_folder or not dicom_output_folder:
        messagebox.showwarning("警告", "请先选择输入文件夹和 DICOM 输出文件夹！")
        logging.warning("未选择输入文件夹或 DICOM 输出文件夹。")
        return

    logging.info("DICOM 文件匿名化处理开始。")
    start_time = datetime.now()

    # 获取所有 DICOM 文件
    all_files = []
    for _root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".dcm"):
                all_files.append(os.path.join(_root, file))

    total_files = len(all_files)
    logging.info(f"总共找到 {total_files} 个 DICOM 文件。")

    # 创建进度窗口
    progress_window = tk.Toplevel(root)
    progress_window.title("处理进度")
    progress_label = tk.Label(progress_window, text="处理进度: 0% 完成")
    progress_label.pack(pady=20)

    for index, file_path in enumerate(all_files, start=1):
        try:
            ds = pydicom.dcmread(file_path)
            # 修改配置的标签
            for tag, value in tags_to_modify.items():
                if hasattr(ds, tag):
                    setattr(ds, tag, value)
            # 保存修改后的文件到输出文件夹
            relative_path = os.path.relpath(os.path.dirname(file_path), input_folder)
            output_dir = os.path.join(dicom_output_folder, relative_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, os.path.basename(file_path))
            ds.save_as(output_path)
            logging.info(f"文件 {os.path.basename(file_path)} 的 DICOM 标签已修改并保存到 {output_path}")
        except Exception as e:
            logging.error(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
        finally:
            update_progress(index, total_files, progress_label)

    end_time = datetime.now()
    logging.info(f"DICOM 文件匿名化处理完成。耗时: {end_time - start_time}")
    progress_window.destroy()
    messagebox.showinfo("完成", "DICOM 文件匿名化处理完成！")


def convert_dicom_to_png():
    """将 DICOM 文件转换为 PNG"""
    if not input_folder or not png_output_folder:
        messagebox.showwarning("警告", "请先选择输入文件夹和 PNG 输出文件夹！")
        logging.warning("未选择输入文件夹或 PNG 输出文件夹。")
        return

    logging.info("DICOM 文件转换为 PNG 开始。")
    start_time = datetime.now()

    # 获取所有 DICOM 文件
    all_files = []
    for _root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".dcm"):
                all_files.append(os.path.join(_root, file))

    total_files = len(all_files)
    logging.info(f"总共找到 {total_files} 个 DICOM 文件。")

    # 创建进度窗口
    progress_window = tk.Toplevel(root)
    progress_window.title("处理进度")
    progress_label = tk.Label(progress_window, text="处理进度: 0% 完成")
    progress_label.pack(pady=20)

    for index, file_path in enumerate(all_files, start=1):
        try:
            ds = pydicom.dcmread(file_path)
            # 获取图像数据
            image = ds.pixel_array
            if ds.PhotometricInterpretation == "MONOCHROME1":
                image = np.amax(image) - image
            if convert_to_grayscale.get():
                image = Image.fromarray(image).convert("L")  # 转换为灰度图像
            else:
                image = Image.fromarray(image)
            # 保存 PNG 文件
            relative_path = os.path.relpath(os.path.dirname(file_path), input_folder)
            output_dir = os.path.join(png_output_folder, relative_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, os.path.basename(file_path).replace(".dcm", ".png"))
            image.save(output_path)
            logging.info(f"文件 {os.path.basename(file_path)} 已成功转换为 PNG 并保存到 {output_path}")
        except Exception as e:
            logging.error(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
        finally:
            update_progress(index, total_files, progress_label)

    end_time = datetime.now()
    logging.info(f"DICOM 文件转换为 PNG 完成。耗时: {end_time - start_time}")
    progress_window.destroy()
    messagebox.showinfo("完成", "DICOM 文件转换为 PNG 完成！")


def save_structured_info():
    """为每个 DICOM 文件单独保存结构化信息"""
    if not input_folder or not structured_info_folder:
        messagebox.showwarning("警告", "请先选择输入文件夹和结构化信息输出文件夹！")
        logging.warning("未选择输入文件夹或结构化信息输出文件夹。")
        return

    logging.info("保存结构化信息开始。")
    start_time = datetime.now()

    # 获取所有 DICOM 文件
    all_files = []
    for _root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".dcm"):
                all_files.append(os.path.join(_root, file))

    total_files = len(all_files)
    logging.info(f"总共找到 {total_files} 个 DICOM 文件。")

    # 创建进度窗口
    progress_window = tk.Toplevel(root)
    progress_window.title("处理进度")
    progress_label = tk.Label(progress_window, text="处理进度: 0% 完成")
    progress_label.pack(pady=20)

    for index, file_path in enumerate(all_files, start=1):
        try:
            ds = pydicom.dcmread(file_path)
            # 为每个 DICOM 文件生成一个单独的结构化信息文件
            relative_path = os.path.relpath(os.path.dirname(file_path), input_folder)
            output_dir = os.path.join(structured_info_folder, relative_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_file_name = os.path.basename(file_path).replace(".dcm", "_info.txt")
            output_path = os.path.join(output_dir, output_file_name)
            with open(output_path, "w") as file:
                file.write(f"文件: {os.path.basename(file_path)}\n")
                for element in ds:
                    file.write(f"  {element}\n")
            logging.info(f"文件 {os.path.basename(file_path)} 的结构化信息已保存到 {output_path}")
        except Exception as e:
            logging.error(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
        finally:
            update_progress(index, total_files, progress_label)

    end_time = datetime.now()
    logging.info(f"保存结构化信息完成。耗时: {end_time - start_time}")
    progress_window.destroy()
    messagebox.showinfo("完成", "结构化信息保存完成！")



# 日志显示区域
# log_text = tk.Text(root, height=10, width=60)
# log_text.pack(pady=10)
# log_text.config(state="disabled")  # 禁止用户编辑

# 文件夹选择区域
folder_frame = ttk.LabelFrame(root, text="文件夹选择")
folder_frame.pack(pady=10, padx=10, fill=tk.X)

input_label = tk.Label(folder_frame, text="输入文件夹: 未选择")
input_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
input_button = tk.Button(folder_frame, text="选择", command=select_input_folder)
input_button.grid(row=0, column=1, padx=5, pady=5)

dicom_output_label = tk.Label(folder_frame, text="DICOM 输出文件夹: 未选择")
dicom_output_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
dicom_output_button = tk.Button(folder_frame, text="选择", command=select_dicom_output_folder)
dicom_output_button.grid(row=1, column=1, padx=5, pady=5)

png_output_label = tk.Label(folder_frame, text="PNG 输出文件夹: 未选择")
png_output_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
png_output_button = tk.Button(folder_frame, text="选择", command=select_png_output_folder)
png_output_button.grid(row=2, column=1, padx=5, pady=5)

structured_info_label = tk.Label(folder_frame, text="结构化信息输出文件夹: 未选择")
structured_info_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
structured_info_button = tk.Button(folder_frame, text="选择", command=select_structured_info_folder)
structured_info_button.grid(row=3, column=1, padx=5, pady=5)

log_label = tk.Label(folder_frame, text="日志文件夹: 未选择")
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