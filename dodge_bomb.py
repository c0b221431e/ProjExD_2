import os
import random
import sys

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
        kk = pg.transform.rotozoom(kk, angle, 2.0)
        kk_imgs[k] = kk  # key:移動量タプル value:手を加えたこうかとんsurface
        angle += 45  #角度を45度回す
    kk_imgs[kk_mv[8]] = pg.transform.rotozoom(kk_img, 0, 2.0)
    return kk_imgs


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_imgs = kokaton_rotate(kk_img)  # 課題3:こうかとん画像を切り替えるための辞書を用意する関数
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20))  # 爆弾用の空Surface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 爆弾円を描く
    bb_img.set_colorkey((0, 0, 0))  # 四隅の黒を透過させる
    bomb_boost = 1.5  # 課題2: 爆弾の加速度
    bb_rct = bb_img.get_rect()  # 爆弾Rectの抽出
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5  # 爆弾速度ベクトル
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            print("ゲームオーバー")
            return
        if (tmr+1) % 250 == 0 and (tmr+1) // 250 <= 10:  #課題2：時間カウントが250ごとに(5秒ごとに)1加速、最大10回
            vx *= bomb_boost
            vy *= bomb_boost
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key] == True:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]
        kk_rct.move_ip(sum_mv)
        # こうかとんが画面外なら，元の場所に戻す
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_imgs[(sum_mv[0], sum_mv[1])], kk_rct)  # 課題3:kk_imgsがsum_mvにあうようにする
        bb_rct.move_ip(vx, vy)  # 爆弾動く
        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横にはみ出てる
            vx *= -1
        if not tate:  # 縦にはみ出てる
            vy *= -1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()