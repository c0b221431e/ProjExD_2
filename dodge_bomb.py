import os
import random
import sys
import math # ベクトル計算用にmathライブラリをインポート
import pygame as pg


WIDTH, HEIGHT = 1100,650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]: #課題4：ベクトル計算の定義
    """
    org（爆弾）からdst（こうかとん）への方向ベクトルを計算する。
    ただし、距離が300未満の場合は現在の速度ベクトルを維持する。

    Args:
        org (pg.Rect): 爆弾のRectオブジェクト
        dst (pg.Rect): こうかとんのRectオブジェクト
        current_xy (tuple[float, float]): 現在の速度ベクトル

    Returns:
        tuple[float, float]: 更新された速度ベクトル
    """
    # orgからdstへのベクトル（座標差）
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery

    # ノルム（ベクトルの長さ）を計算
    norm = math.sqrt(dx**2 + dy**2)

    # 距離が300未満なら現在の速度を維持
    if norm < 300:
        return current_xy

    # 正規化して速度ベクトルを計算
    scale = math.sqrt(50) / norm  # ノルムを√50にするスケール
    return dx * scale, dy * scale


def kokaton_rotate(kk_img: pg.Surface):  # 課題3:飛ぶ方向に従ってこうかとん画像を切り替える
    """
    こうかとんの移動量のタプルとrotozoomした画像の辞書を返す
    引数:こうかとんの画像(Surface型)
    戻り値:移動量タプルとrotozoom画像の辞書
    """
    kk_imgs = {}
    kk_mv = [(0, +5), (+5, +5), (+5, 0), (+5, -5), (0, -5), (-5, -5), (-5, 0), (-5, +5), (0, 0)]  # 移動量のタプルのリスト
    angle = -90  # こうかとんの角度
    flip = True
    for k in kk_mv[:8]:
        if angle > 90:  # 角度が半周以上したら
            angle -= 180  # 角度を一度リセットして
            flip = False  # 左右反転
        kk = kk_img
        kk = pg.transform.flip(kk, flip, False)
        kk = pg.transform.rotozoom(kk, angle, 0.9)
        kk_imgs[k] = kk  # key:移動量タプル value:手を加えたこうかとんsurface
        angle += 45  #角度を45度回す
    kk_imgs[kk_mv[8]] = pg.transform.rotozoom(kk_img, 0, 0.9)
    return kk_imgs

def game_over(screen: pg.Surface) -> None: #課題１：ゲームオーバー画面の生成
    """
    ゲームオーバー時に画面をブラックアウトし、
    泣いているこうかとん画像と「Game Over」の文字列を表示する。
    """
    # 半透明の黒い画面を描画
    overlay = pg.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)  # 半透明
    overlay.fill((0, 0, 0))  # 黒
    screen.blit(overlay, (0, 0))

    # 「Game Over」のテキストを描画
    font = pg.font.Font(None, 100)
    text = font.render("Game Over", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)

    # 泣いているこうかとん画像を「Game Over」の横に配置
    cry_kokaton = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.0)
    cry_kokaton_left_rect = cry_kokaton.get_rect(midright=(text_rect.left - 20, text_rect.centery))
    cry_kokaton_right_rect = cry_kokaton.get_rect(midleft=(text_rect.right + 20, text_rect.centery))
    screen.blit(cry_kokaton, cry_kokaton_left_rect)
    screen.blit(cry_kokaton, cry_kokaton_right_rect)

    # 画面更新と5秒間の表示
    pg.display.update()
    pg.time.wait(5000)  # 5秒間停止


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_imgs = kokaton_rotate(kk_img)  # 課題3:こうかとん画像を切り替えるための辞書を用意する関数
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # 課題2:爆弾の画像を段階ごとに作成（10段階）
    bb_accs = [1.0 + 0.5 * i for i in range(10)]  # 加速リスト
    bb_imgs = []  # サイズ段階ごとの爆弾画像リスト
    for r in range(1, 11):  # 爆弾サイズを10段階に分ける
        img = pg.Surface((20 * r, 20 * r), pg.SRCALPHA)  # SRCALPHAで透明背景
        pg.draw.circle(img, (255, 0, 0), (10 * r, 10 * r), 10 * r)  # 円を描画
        bb_imgs.append(img)

    bb_rct = bb_imgs[0].get_rect()  # 爆弾Rectの抽出
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5  # 爆弾速度ベクトル

    clock = pg.time.Clock()
    tmr = 0  # タイマー
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            game_over(screen)
            return

        # 課題2:爆弾の加速と拡大
        level = min(tmr // 500, 9)  # 500フレーム（10秒ごと）でレベルアップし、最大9まで
        vx = bb_accs[level] * (5 if vx > 0 else -5)  # 加速度に基づいて速度を更新
        vy = bb_accs[level] * (5 if vy > 0 else -5)

        screen.blit(bg_img, [0, 0])  # 背景描画

        # こうかとんの操作
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):  # 画面外チェック
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_imgs[(sum_mv[0], sum_mv[1])], kk_rct)  # こうかとん描画

        # 課題4：爆弾の速度ベクトルを更新
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))

        # 爆弾の動き
        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横にはみ出ている
            vx *= -1
        if not tate:  # 縦にはみ出ている
            vy *= -1


        # 拡大された爆弾の描画
        screen.blit(bb_imgs[level], bb_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()