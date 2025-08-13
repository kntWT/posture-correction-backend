import cv2
import numpy as np

def resize_and_pad(image: np.ndarray, size: int = 384) -> np.ndarray:
    """
    画像をアスペクト比を維持したまま指定された正方形サイズにリサイズし、
    足りない領域を黒で埋める（レターボックス化する）。

    Args:
        image (np.ndarray): 入力画像（OpenCVで読み込んだもの）。
        size (int): ターゲットとなる正方形の一辺の長さ。

    Returns:
        np.ndarray: リサイズおよび黒埋めされた画像。
    """
    # 元画像の高さを幅を取得
    h, w, _ = image.shape
    
    # ターゲットとなる正方形のキャンバスを作成（黒で塗りつぶし）
    # image.dtypeを指定して、データ型を元画像と合わせる
    padded_image = np.zeros((size, size, 3), dtype=image.dtype)

    # アスペクト比を維持するためのリサイズ後のサイズを計算
    if h > w:
        # 縦長の画像の場合
        new_h = size
        new_w = int(w * (size / h))
    else:
        # 横長または正方形の画像の場合
        new_w = size
        new_h = int(h * (size / w))

    # 画像をリサイズ
    # cv2.resizeのサイズ指定は(幅, 高さ)の順なので注意
    resized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # 中央に配置するためのオフセットを計算
    top = (size - new_h) // 2
    left = (size - new_w) // 2

    # リサイズした画像をキャンバスの中央に配置
    padded_image[top:top + new_h, left:left + new_w] = resized_image

    return padded_image

# --- 以下、使用例 ---
if __name__ == '__main__':
    # 横長の画像を読み込む（事前に'landscape.jpg'という名前で用意してください）
    # このサンプルではダミーの横長画像を作成します
    dummy_landscape_img = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
    cv2.imwrite('landscape.jpg', dummy_landscape_img)

    # 縦長の画像を読み込む（事前に'portrait.jpg'という名前で用意してください）
    # このサンプルではダミーの縦長画像を作成します
    dummy_portrait_img = np.random.randint(0, 255, (1280, 720, 3), dtype=np.uint8)
    cv2.imwrite('portrait.jpg', dummy_portrait_img)


    # --- 横長画像の処理 ---
    img_land = cv2.imread('landscape.jpg')
    if img_land is None:
        print("横長の画像ファイル 'landscape.jpg' が見つかりません。")
    else:
        processed_land = resize_and_pad(img_land, size=384)
        print("横長画像の処理後のサイズ:", processed_land.shape)
        cv2.imwrite('processed_landscape.jpg', processed_land)
        print("処理後の横長画像を 'processed_landscape.jpg' として保存しました。")
        # cv2.imshow('Processed Landscape', processed_land) # GUI環境なら表示可能

    print("-" * 20)

    # --- 縦長画像の処理 ---
    img_port = cv2.imread('portrait.jpg')
    if img_port is None:
        print("縦長の画像ファイル 'portrait.jpg' が見つかりません。")
    else:
        processed_port = resize_and_pad(img_port, size=384)
        print("縦長画像の処理後のサイズ:", processed_port.shape)
        cv2.imwrite('processed_portrait.jpg', processed_port)
        print("処理後の縦長画像を 'processed_portrait.jpg' として保存しました。")
        # cv2.imshow('Processed Portrait', processed_port) # GUI環境なら表示可能
    
    # GUI環境で実行している場合は、以下のコメントを外すと画像が表示されます
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
