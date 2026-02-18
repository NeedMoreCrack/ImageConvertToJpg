import os
import sys
from PIL import Image
from multiprocessing import Pool, cpu_count, freeze_support, Value

# 正確取得 exe 所在目錄
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

input_dir = os.path.join(base_dir, "input")
output_dir = os.path.join(base_dir, "output")

os.makedirs(output_dir, exist_ok=True)


def convert_file(filename):
    try:
        input_path = os.path.join(input_dir, filename)
        with Image.open(input_path) as img:
            img = img.convert("RGB")
            output_name = os.path.splitext(filename)[0] + ".jpg"
            output_path = os.path.join(output_dir, output_name)
            img.save(output_path, "JPEG", quality=95)
        return True
    except Exception:
        return False


def update_progress(result):
    global progress_count
    with progress_count.get_lock():  # Value 有 lock，可以多進程安全操作
        progress_count.value += 1
        percent = progress_count.value / total * 100
        bar_length = 30
        filled_len = int(bar_length * progress_count.value // total)
        bar = '=' * filled_len + '-' * (bar_length - filled_len)
        print(f"\r[{bar}] {percent:6.2f}% ({progress_count.value}/{total})", end='')


if __name__ == "__main__":
    freeze_support()

    if not os.path.exists(input_dir):
        print("找不到 input 資料夾，請建立 input 並放入 webp / avif 圖片")
        input("按 Enter 結束...")
        exit()

    files = [f for f in os.listdir(input_dir)
             if f.lower().endswith((".webp", ".avif"))]

    if not files:
        print("input 資料夾內沒有 webp 或 avif 檔案")
        input("按 Enter 結束...")
        exit()

    total = len(files)
    print(f"開始轉換 {total} 張圖片...\n")

    # 讓使用者選擇 CPU 核心數
    max_cores = cpu_count()
    print(f"檢測到 CPU 核心數: {max_cores}")
    while True:
        try:
            cores_input = input(f"請輸入要使用的核心數 (1-{max_cores})，留空則使用最大核心數: ")
            cores = int(max_cores if cores_input == "" else cores_input)
            if 1 <= cores <= max_cores:
                break
            else:
                print(f"請輸入 1 到 {max_cores} 的數字")
        except ValueError:
            print("請輸入有效數字")

    print(f"\n使用 {cores} 核心開始轉換...\n")

    # 使用 multiprocessing.Value 取代 Manager().Value
    progress_count = Value('i', 0)  # 'i' 表示整數型

    results = []
    with Pool(processes=cores) as pool:
        for f in files:
            results.append(pool.apply_async(convert_file, args=(f,), callback=update_progress))
        pool.close()
        pool.join()

    success_count = sum(r.get() for r in results)
    fail_count = len(results) - success_count

    print("\n\n轉換完成！")
    print(f"成功: {success_count}, 失敗: {fail_count}")
    input("按 Enter 結束...")
