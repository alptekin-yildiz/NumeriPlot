# NumeriPlot - Test Protocol (v1.0)

Bu doküman sürüm öncesi zorunlu test akışını tanımlar.

## 1) Zorunlu Release Gate (otomatik)

Proje kökünde çalıştır:

```bash
bash setup.sh --dev
source venv/bin/activate
bash release_check.sh
```

`release_check.sh` şunları doğrular:

- Sürüm bilgisinin okunması (`src/version.py`)
- Aktif Python ortamında sabitlenmiş pytest, PyInstaller ve Ruff araçları
- `setup.sh`, `build_macos.sh`, `release_check.sh` syntax kontrolü
- Python dosyalarının syntax kontrolü
- Ruff kritik doğruluk kontrolü
- `lang/tr.py` ve `lang/en.py` anahtar eşleşmesi
- `pytest` testlerinin tamamı

Bu adım geçmeden paketleme yapılmaz.

## 2) Zorunlu GUI Smoke (manuel)

Checklist dosyası:

- `TEST_CHECKLIST.md`

Tüm `FAIL` maddeleri kapanmadan release adayı onaylanmaz.

## 3) Paketleme Smoke (manuel)

1. `bash build_macos.sh`
2. `dist/NumeriPlot.app` açılış kontrolü
3. Kritik akış hızlı kontrol:
   - veri yükleme
   - tablo düzenleme + geri al
   - grafik ekleme + fit
   - export (image/python/notebook/table)
4. `dist/NumeriPlot_v<version>_macOS.zip` paylaşım paketi kontrolü

## 4) Crash ve log doğrulama

macOS log yolu:

- `~/Library/Logs/NumeriPlot/numeriplot.log`

Release öncesi log içinde yeni `Traceback` / `CRITICAL` kaydı olmamalı.

## 5) Kabul kriteri

Release adayı ancak şu durumda geçerlidir:

1. `release_check.sh` başarılı
2. `TEST_CHECKLIST.md` sonucu uygun
3. Paketleme smoke başarılı
