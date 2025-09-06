import os
import time
import shutil
import urllib.request
import urllib.error
import patoolib

EXCEPT_PATH = [".git", ".mypy_cache"]
TARGET = "https://github.com/KSP-CKAN/CKAN-meta/archive/master.tar.gz"
GHPROXY = "https://ghproxy.net"
SKIP_DOWNLOAD = False


def delete_other_files():
    """
    删除当前目录下除自身以外的所有文件
    """
    # 获取当前脚本的绝对路径，避免误删
    current_script = os.path.abspath(__file__)

    # 获取当前目录
    current_dir = os.path.dirname(current_script)
    script_name = os.path.basename(current_script)
    if not current_dir:
        current_dir = os.getcwd()
    os.chdir(current_dir)

    # 显示将要执行的操作
    print(f"当前目录: {current_dir}")
    print(f"将删除除 {script_name}，{"，".join(EXCEPT_PATH)} 以外的所有文件和文件夹")

    # 询问用户确认
    confirm = input("确认删除？(y/N)：")
    if confirm.lower() != "y":
        print("操作已取消")
        return

    deleted_count = 0
    # 遍历所有项目
    for item in os.listdir("."):
        item_path = os.path.join(current_dir, item)

        # 确保不删除自身
        if item != script_name and item not in EXCEPT_PATH:
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    print(f"删除文件：{item}")
                    os.remove(item_path)
                    print(f"已删除文件：{item}")
                    deleted_count += 1
                elif os.path.isdir(item_path):
                    # 删除目录及其内容
                    print(f"删除目录：{item}")
                    shutil.rmtree(item_path)
                    print(f"已删除目录：{item}")
                    deleted_count += 1
            except Exception as e:
                print(f"删除 {item} 时出错：{str(e)}")
        else:
            print(f"跳过 {item}")

    print(f"删除操作完成，共删除 {deleted_count} 个项目")


def replace_ghproxy(text: str):
    return text.replace("https://github.com/", GHPROXY + "/https://github.com/")


def download_file(url, filename: str):
    """
    从指定URL下载文件
    """
    print(f"从 {url} 下载文件，保存为: {filename}")

    if filename in os.listdir(".") or SKIP_DOWNLOAD:
        print("跳过下载")
        return

    try:
        urllib.request.urlretrieve(url, filename)
        print(f"文件下载完成: {filename}")
        # 显示文件大小
        file_size = os.path.getsize(filename)
        print(f"文件大小: {file_size} 字节")
    except urllib.error.URLError as e:
        raise RuntimeError(f"下载失败: {e}") from e
    except Exception as e:
        raise RuntimeError(f"下载过程中发生错误: {e}") from e


def download_file_with_ghproxy(url, filename: str):
    """
    从指定URL下载文件，并使用ghproxy加速
    """
    ghproxy_url = replace_ghproxy(url)
    download_file(ghproxy_url, filename)


def extract_tar_file(tar_filename: str, extract_to: str):
    """
    解压tar.gz文件到指定目录
    """
    print(f"解压文件 {tar_filename} 到 {extract_to} 目录")

    try:
        # 确保目标目录存在
        os.makedirs(extract_to, exist_ok=True)
        patoolib.extract_archive(tar_filename, outdir=extract_to)

        print("解压完成")
    except Exception as e:
        raise RuntimeError(f"解压过程中发生错误: {e}") from e


def process_data(filepath: str):
    for root, dirs, files in os.walk(filepath, topdown=False):
        for name in files:
            print(f"处理文件 {os.path.join(root, name)}")
            with open(os.path.join(root, name), "r", encoding="utf-8") as f:
                data = f.read()
            data = replace_ghproxy(data)
            with open(os.path.join(root, name), "w", encoding="utf-8") as f:
                f.write(data)
    print("处理完成")


def final_tidy(tar_filename: str, extract_to: str):
    print("将文件移动到根目录")
    data_path = os.path.join(".", extract_to, "CKAN-meta-master")
    for item in os.listdir(data_path):
        print(f"移动 {item} 到根目录")
        shutil.move(os.path.join(data_path, item), ".")

    print("删除临时文件")
    os.remove(tar_filename)
    shutil.rmtree(extract_to)


def main():
    print("清理当前目录")
    t0 = time.perf_counter()
    delete_other_files()
    t1 = time.perf_counter()
    print(f"清理完成，耗时: {t1 - t0:.2f} 秒")

    print("下载文件")
    t0 = time.perf_counter()
    download_file_with_ghproxy(TARGET, "_META.tar.gz")
    t1 = time.perf_counter()
    print(f"下载完成，耗时: {t1 - t0:.2f} 秒")

    print("解压文件")
    t0 = time.perf_counter()
    extract_tar_file("_META.tar.gz", "_META")
    t1 = time.perf_counter()
    print(f"解压完成，耗时: {t1 - t0:.2f} 秒")

    print("处理数据")
    t0 = time.perf_counter()
    process_data("_META")
    t1 = time.perf_counter()
    print(f"处理完成，耗时: {t1 - t0:.2f} 秒")

    print("最后整理")
    t0 = time.perf_counter()
    final_tidy("_META.tar.gz", "_META")
    t1 = time.perf_counter()
    print(f"最后整理完成，耗时: {t1 - t0:.2f} 秒")


if __name__ == "__main__":
    main()
