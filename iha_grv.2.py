import cv2
import numpy as np
import time
import math
from dataclasses import dataclass, field
from typing import Optional, Tuple, List
from enum import Enum

KAMERA_GENISLIK  = 640
KAMERA_YUKSEKLIK = 480
KAMERA_FOV_H     = 62.2
KAMERA_FOV_V     = 48.8

MAVI_HEDEF_BOYUT    = 4.0
KIRMIZI_HEDEF_BOYUT = 2.0

MIN_ALAN          = 800
MERKEZ_TOLERANS   = 30
KILITLI_KARE_ESIK = 15


class YukDurumu(Enum):
    YUKLU   = "YUKLU"
    BIRAKTI = "BIRAKTI"


@dataclass
class Yuk:
    renk: str
    durum: YukDurumu = YukDurumu.YUKLU


@dataclass
class HedefBilgi:
    ad: str
    renk: str
    gercek_boyut: float
    yuk_rengi: str
    hsv_alt: List[np.ndarray]
    hsv_ust: List[np.ndarray]
    kutu_rengi: Tuple[int, int, int]
    merkez: Optional[Tuple[int, int]] = None
    alan: float = 0.0
    uzaklik_m: float = 0.0
    kilitli_kare: int = 0
    teslim_edildi: bool = False


@dataclass
class IHADurum:
    yukler: List[Yuk] = field(default_factory=lambda: [
        Yuk("KIRMIZI"),
        Yuk("MAVI"),
    ])
    gorev_baslangic: float = field(default_factory=time.time)

    def yuk_var_mi(self, renk: str) -> bool:
        return any(y.renk == renk and y.durum == YukDurumu.YUKLU for y in self.yukler)

    def yuk_birak(self, renk: str):
        for y in self.yukler:
            if y.renk == renk and y.durum == YukDurumu.YUKLU:
                y.durum = YukDurumu.BIRAKTI
                return True
        return False


def hsv_mask_olustur(hsv: np.ndarray, hedef: HedefBilgi) -> np.ndarray:
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for alt, ust in zip(hedef.hsv_alt, hedef.hsv_ust):
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv, alt, ust))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return mask


def uzaklik_hesapla(piksel_boyut, gercek_boyut_m, goruntu_genisligi, fov_derece):
    if piksel_boyut <= 0:
        return 0.0
    fov_rad = math.radians(fov_derece)
    odak = goruntu_genisligi / (2.0 * math.tan(fov_rad / 2.0))
    return round((gercek_boyut_m * odak) / piksel_boyut, 2)


def sapma_hesapla(merkez_x, merkez_y, goruntu_w, goruntu_h, fov_h, fov_v, uzaklik_m):
    hata_x = merkez_x - goruntu_w / 2
    hata_y = merkez_y - goruntu_h / 2
    aci_x = math.radians((hata_x / goruntu_w) * fov_h)
    aci_y = math.radians((hata_y / goruntu_h) * fov_v)
    return round(math.tan(aci_x) * uzaklik_m, 2), round(math.tan(aci_y) * uzaklik_m, 2)


def en_buyuk_kontur(mask: np.ndarray):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, 0.0
    c = max(contours, key=cv2.contourArea)
    alan = cv2.contourArea(c)
    if alan < MIN_ALAN:
        return None, 0.0
    return c, alan


def hedef_isle(frame, hsv, hedef: HedefBilgi, iha: IHADurum):
    mask = hsv_mask_olustur(hsv, hedef)
    kontur, alan = en_buyuk_kontur(mask)

    if kontur is None:
        hedef.merkez = None
        hedef.kilitli_kare = 0
        return None

    x, y, w, h = cv2.boundingRect(kontur)
    mx = x + w // 2
    my = y + h // 2

    hedef.merkez    = (mx, my)
    hedef.alan      = alan
    hedef.uzaklik_m = uzaklik_hesapla(max(w, h), hedef.gercek_boyut, KAMERA_GENISLIK, KAMERA_FOV_H)

    sapma_x, sapma_y = sapma_hesapla(mx, my, KAMERA_GENISLIK, KAMERA_YUKSEKLIK,
                                     KAMERA_FOV_H, KAMERA_FOV_V, hedef.uzaklik_m)

    gx = KAMERA_GENISLIK  // 2
    gy = KAMERA_YUKSEKLIK // 2

    goruntu_alani  = KAMERA_GENISLIK * KAMERA_YUKSEKLIK
    alan_orani     = alan / goruntu_alani
    merkez_uzaklik = math.hypot(mx - gx, my - gy)
    maks_uzaklik   = math.hypot(KAMERA_GENISLIK, KAMERA_YUKSEKLIK) * 0.5
    merkez_skoru   = 1.0 - (merkez_uzaklik / maks_uzaklik)

    if merkez_skoru > 0.4 or alan_orani > 0.15:
        hedef.kilitli_kare += 1
    else:
        hedef.kilitli_kare = max(0, hedef.kilitli_kare - 1)

    if hedef.kilitli_kare >= KILITLI_KARE_ESIK and not hedef.teslim_edildi and iha.yuk_var_mi(hedef.yuk_rengi):
        if iha.yuk_birak(hedef.yuk_rengi):
            hedef.teslim_edildi = True
            print(f"{hedef.yuk_rengi} yuk birakildi -> {hedef.ad}")

    renk = hedef.kutu_rengi
    cv2.drawContours(frame, [kontur], -1, renk, 2)
    cv2.rectangle(frame, (x, y), (x + w, y + h), renk, 3)
    cv2.circle(frame, (mx, my), 8, renk, -1)
    cv2.circle(frame, (gx, gy), MERKEZ_TOLERANS, (255, 255, 0), 1)

    bilgiler = [
        hedef.ad,
        f"Uzaklik: {hedef.uzaklik_m:.1f} m",
        f"Sapma X: {sapma_x:+.2f} m  Y: {sapma_y:+.2f} m",
        f"Alan: {int(alan)} px  ({alan_orani*100:.1f}%)",
        f"Kilitli: {hedef.kilitli_kare}/{KILITLI_KARE_ESIK}",
    ]
    if hedef.teslim_edildi:
        bilgiler.append("YUK BIRAKILDI")

    for i, satir in enumerate(bilgiler):
        cv2.putText(frame, satir, (x, y - 10 - i * 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, renk, 2)

    return mx, my


def hud_ciz(frame, iha: IHADurum, hedefler: List[HedefBilgi]):
    sure = int(time.time() - iha.gorev_baslangic)

    panel = frame.copy()
    cv2.rectangle(panel, (0, 0), (300, 150), (0, 0, 0), -1)
    cv2.addWeighted(panel, 0.45, frame, 0.55, 0, frame)

    satirlar = [f"Sure: {sure // 60:02d}:{sure % 60:02d}"]
    for yuk in iha.yukler:
        simge = "+" if yuk.durum == YukDurumu.BIRAKTI else "-"
        satirlar.append(f"{simge} {yuk.renk} [{yuk.durum.value}]")
    for ht in hedefler:
        durum = "TESLIM" if ht.teslim_edildi else (f"{ht.uzaklik_m:.1f}m" if ht.merkez else "ARAMA")
        satirlar.append(f"{ht.renk}: {durum}")

    for i, satir in enumerate(satirlar):
        cv2.putText(frame, satir, (8, 22 + i * 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (220, 220, 220), 1)

    cx, cy = KAMERA_GENISLIK // 2, KAMERA_YUKSEKLIK // 2
    cv2.line(frame, (cx - 20, cy), (cx + 20, cy), (0, 255, 255), 1)
    cv2.line(frame, (cx, cy - 20), (cx, cy + 20), (0, 255, 255), 1)


def main():
    kamera = cv2.VideoCapture(0)
    if not kamera.isOpened():
        print("Kamera acilamadi!")
        return

    kamera.set(cv2.CAP_PROP_FRAME_WIDTH,  KAMERA_GENISLIK)
    kamera.set(cv2.CAP_PROP_FRAME_HEIGHT, KAMERA_YUKSEKLIK)
    kamera.set(cv2.CAP_PROP_FPS, 30)

    hedefler = [
        HedefBilgi(
            ad="MAVI HEDEF (4x4m)",
            renk="MAVI",
            gercek_boyut=MAVI_HEDEF_BOYUT,
            yuk_rengi="KIRMIZI",
            hsv_alt=[np.array([100, 120, 50])],
            hsv_ust=[np.array([130, 255, 255])],
            kutu_rengi=(255, 80, 0),
        ),
        HedefBilgi(
            ad="KIRMIZI HEDEF (2x2m)",
            renk="KIRMIZI",
            gercek_boyut=KIRMIZI_HEDEF_BOYUT,
            yuk_rengi="MAVI",
            hsv_alt=[np.array([0,   150, 80]), np.array([170, 150, 80])],  
            hsv_ust=[np.array([8,   255, 255]), np.array([180, 255, 255])], 
            kutu_rengi=(0, 50, 255),
        ),
    ]

    iha = IHADurum()
    prev_time = time.time()

    while True:
        ret, frame = kamera.read()
        if not ret:
            break

        hsv = cv2.cvtColor(cv2.GaussianBlur(frame, (5, 5), 0), cv2.COLOR_BGR2HSV)

        for ht in hedefler:
            hedef_isle(frame, hsv, ht, iha)

        hud_ciz(frame, iha, hedefler)

        now = time.time()
        fps = 1.0 / max(now - prev_time, 1e-6)
        prev_time = now
        cv2.putText(frame, f"FPS: {fps:.1f}", (KAMERA_GENISLIK - 90, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)

        cv2.imshow("IHA Hedef Tespiti", frame)

        tus = cv2.waitKey(1) & 0xFF
        if tus == ord("q"):
            break
        elif tus == ord("r"):
            iha = IHADurum()
            for ht in hedefler:
                ht.teslim_edildi = False
                ht.kilitli_kare  = 0

    kamera.release()
    cv2.destroyAllWindows()

    for ht in hedefler:
        print(f"{ht.ad}: {'TESLIM EDILDI' if ht.teslim_edildi else 'TESLIM EDILEMEDI'}")


if __name__ == "__main__":
    main()
