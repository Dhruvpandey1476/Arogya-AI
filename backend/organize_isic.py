"""
Sort flat ISIC 2018 Task 3 images (ISIC_0024306.jpg ...) into per-class folders
expected by this project: backend/data/raw/skin_images/{class_name}/*.jpg

Usage:
    python organize_isic.py --images path/to/images --csv path/to/ISIC2018_Task3_Training_GroundTruth.csv
"""
import argparse, csv, os, shutil

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True, help="folder with ISIC_*.jpg files")
    ap.add_argument("--csv", required=True, help="ISIC2018_Task3_Training_GroundTruth.csv")
    ap.add_argument("--out", default="data/raw/skin_images", help="output root")
    ap.add_argument("--copy", action="store_true", help="copy instead of move")
    args = ap.parse_args()

    with open(args.csv, newline="") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        onehot = [c for c in ["MEL","NV","BCC","AKIEC","BKL","DF","VASC"] if c in cols]
        dxcol = next((c for c in cols if c.lower() in ("dx","diagnosis","label")), None)
        if not onehot and not dxcol:
            raise SystemExit(f"CSV has no label columns. Found: {cols}. "
                             "Need one-hot (MEL,NV,...) or a 'dx' column (HAM10000).")
        imgcol = cols[0]  # 'image' or 'image_id'
        n = 0
        for row in reader:
            name = row[imgcol]
            if dxcol:
                label = row[dxcol].upper()
            else:
                label = max(onehot, key=lambda c: float(row[c]))
            dst_dir = os.path.join(args.out, label)
            os.makedirs(dst_dir, exist_ok=True)
            src = os.path.join(args.images, name + ".jpg")
            if not os.path.exists(src):
                continue
            dst = os.path.join(dst_dir, name + ".jpg")
            (shutil.copy2 if args.copy else shutil.move)(src, dst)
            n += 1
    print(f"Sorted {n} images into {args.out}")

if __name__ == "__main__":
    main()
