import os
import sys
from PIL import Image
from multiprocessing import Pool, cpu_count, freeze_support

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
            img = img.convert("RGB")  # JPG 不支援透明
            # 不管原本是 .webp 或 .avif 都轉成 .jpg
            output_name = os.path.splitext(filename)[0] + ".jpg"
            output_path = os.path.join(output_dir, output_name)
            img.save(output_path, "JPEG", quality=95)

        return True  # 成功

    except Exception as e:
        return False


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

    # 使用單執行緒循環 + 同行進度
    results = []
    for i, file in enumerate(files, 1):
        success = convert_file(file)
        results.append(success)

        # 進度百分比
        percent = i / total * 100
        # 進度條長度 30 個 = 符號
        bar_length = 30
        filled_len = int(bar_length * i // total)
        bar = '=' * filled_len + '-' * (bar_length - filled_len)

        # \r 回到行首，end='' 不換行
        print(f"\r[{bar}] {percent:6.2f}% ({i}/{total})", end='')

    print("\n\n轉換完成！")
    success_count = sum(results)
    fail_count = len(results) - success_count
    print(f"成功: {success_count}, 失敗: {fail_count}")
    input("按 Enter 結束...")
