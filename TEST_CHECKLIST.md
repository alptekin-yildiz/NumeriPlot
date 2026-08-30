# NumeriPlot - GUI Smoke Checklist

Tarih: ____ / ____ / ______
Tester: ____________________
OS: ________________________

Kural:
- `PASS`: Beklenen sonuç alındı
- `FAIL`: Sorun var (kısa not + adım)
- `SKIP`: Bu turda uygulanmadı

## 1) Açılış ve Temel Akış

- [ ] PASS / [ ] FAIL / [ ] SKIP - Uygulama açılıyor, çökme yok.
- [ ] PASS / [ ] FAIL / [ ] SKIP - Varsayılan sağ sekme `Veri Tablosu` olarak açılıyor.
- [ ] PASS / [ ] FAIL / [ ] SKIP - Sekme sırası: `Veri Tablosu`, `Grafik`, `Analiz Raporu`.

## 2) Veri Tablosu Sağ Tık Menüsü

- [ ] PASS / [ ] FAIL / [ ] SKIP - Hücre seçiminde: `Hücreleri NaN Yap`, `Hücre Sil`, `Üste/Alta Satır Ekle`.
- [ ] PASS / [ ] FAIL / [ ] SKIP - Tam satır seçiminde: `Satır Sil`, `Üste/Alta Satır Ekle`.
- [ ] PASS / [ ] FAIL / [ ] SKIP - Tam sütun seçiminde:
  `Sola/sağa boş sütun`, `Sola/sağa 1..n sütunu`, `Sütun Sil`.
- [ ] PASS / [ ] FAIL / [ ] SKIP - `Hücreleri NaN Yap` hizayı bozmaz.
- [ ] PASS / [ ] FAIL / [ ] SKIP - `Hücre Sil` (shift up) hizayı bozabilir uyarısı verir.
- [ ] PASS / [ ] FAIL / [ ] SKIP - `Geri Al` son tablo işlemini doğru geri alır.

## 3) Rol Şablonu ve Grafik Ekleme

- [ ] PASS / [ ] FAIL / [ ] SKIP - Rol şablonu seçimi çalışıyor.
- [ ] PASS / [ ] FAIL / [ ] SKIP - `Grafik Ekle` ile seri ekleniyor.
- [ ] PASS / [ ] FAIL / [ ] SKIP - `X yok` durumunda otomatik `1..n` ile çizim yapılabiliyor.

## 4) Fit Akışı

- [ ] PASS / [ ] FAIL / [ ] SKIP - Model seçimi ve fit çalışıyor.
- [ ] PASS / [ ] FAIL / [ ] SKIP - Tek `Y` + `X yok` seride fit çalışıyor (çökme yok).
- [ ] PASS / [ ] FAIL / [ ] SKIP - Hatalı/eksik veri için kullanıcıya uyarı veriyor.

## 5) Eksen ve Biçimlendirme

- [ ] PASS / [ ] FAIL / [ ] SKIP - `Değerleri Göster` aç/kapa X/SolY/SağY için çalışıyor.
- [ ] PASS / [ ] FAIL / [ ] SKIP - Format seçenekleri çalışıyor (`Auto`, `E`, `E+Offset`, `10^n`, `10^n+Offset`).

## 6) Export Akışları

- [ ] PASS / [ ] FAIL / [ ] SKIP - Grafik export: PNG/PDF/SVG.
- [ ] PASS / [ ] FAIL / [ ] SKIP - Python script export.
- [ ] PASS / [ ] FAIL / [ ] SKIP - Jupyter notebook export.
- [ ] PASS / [ ] FAIL / [ ] SKIP - Veri tablosu export: CSV/XLSX.

## 7) Dil Kontrolü

- [ ] PASS / [ ] FAIL / [ ] SKIP - TR/EN geçişinde menü ve tablo işlemleri metinleri güncelleniyor.
- [ ] PASS / [ ] FAIL / [ ] SKIP - Dil değişiminde layout bozulmuyor.

## 8) Kapanış

- [ ] PASS / [ ] FAIL / [ ] SKIP - Proje kaydet/aç sorunsuz.
- [ ] PASS / [ ] FAIL / [ ] SKIP - Uygulama kapanışı sorunsuz.

---

## Fail Notları

1. Adım:
- Beklenen:
- Gerçekleşen:
- Tekrar adımı:
- Ekran görüntüsü / log:

2. Adım:
- Beklenen:
- Gerçekleşen:
- Tekrar adımı:
- Ekran görüntüsü / log:

## Tur Özeti

- PASS: ___
- FAIL: ___
- SKIP: ___
- Sonuç: [ ] Release adayı uygun  [ ] Düzeltme gerekli
