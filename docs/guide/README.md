# NumeriPlot illustrated guide / Görselli kullanım kılavuzu

Open `index.html` (Türkçe) or `en.html` (English) in a browser. Keep this
directory and its assets together. No installation, network connection, or
web server is needed. GitHub shows HTML source; download the repository to
read the rendered guide. Repository documentation links require the complete
repository folder.

Tarayıcıda `index.html` (Türkçe) veya `en.html` (English) dosyasını açın.
Bu klasörü ve görsellerini bir arada tutun. Kurulum, internet veya sunucu
gerekmez. GitHub HTML kaynağını gösterir; kılavuzu okumak için depoyu indirin.
Depo belgelerine verilen bağlantılar için tüm depo klasörü gereklidir.

The guide describes the current NumeriPlot 0.1.0 source and schema 1.0.
Older packaged builds may differ. Screenshots come from real Qt widgets with
synthetic data, using the Fusion style; native macOS appearance may differ.
Search, image enlargement, language switching, and print controls run locally.
All text remains readable without JavaScript.

Kılavuz mevcut NumeriPlot 0.1.0 kaynak kodunu ve şema 1.0'ı açıklar.
Önceki uygulama paketleri farklı olabilir. Görseller gerçek Qt bileşenlerinden,
sentetik veriyle ve Fusion stiliyle alınır; macOS görünümü farklı olabilir.
Arama, görsel büyütme, dil geçişi ve yazdırma yerel olarak çalışır.
JavaScript kapalıyken de bütün metinler okunabilir.

## Maintenance / Bakım

From the repository root with the pinned development environment activated:
Depo kökünde, sabitlenmiş geliştirme ortamı etkinken:

```bash
QT_QPA_PLATFORM=offscreen python3 examples/capture_guide.py
python3 examples/build_guide.py
python3 -m pytest -q tests/test_user_guide.py
bash release_check.sh
```

Edit bilingual content in `essentials.json`, `workflows.json`, and
`settings.json`; regenerate both HTML files with the builder. Recapture images
when controls change. Verify descriptions against code and screenshots, and
inspect the generated pages in a browser. Do not use private data in captures.

İki dilli içeriği JSON dosyalarında düzenleyip HTML dosyalarını yeniden üretin.
Kontroller değiştiğinde görüntüleri yenileyin. Açıklamaları kod ve görüntülerle
karşılaştırın; sayfaları tarayıcıda inceleyin. Görsellerde özel veri kullanmayın.
