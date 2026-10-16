# NumeriPlot’u Mac’te kaynak koddan kurma ve kullanma

[English](SOURCE_INSTALL.md) · [Kullanım kılavuzu](https://alptekin-yildiz.github.io/NumeriPlot/)

0.1.1 için dağıtım yolu kaynak koddur; hazır Mac uygulama ZIP’i yayımlanması
planlanmıyor. Kurulumdan sonra NumeriPlot, grafik ve tabloları olan normal bir
masaüstü penceresinde açılır. Kullanmak için kod yazmanız veya `.app` üretmeniz
gerekmez. İlk kurulumda Terminal’e birkaç komut girilir; sonraki açılış daha kısadır.

## 1. Gerekenler

- İnternet bağlantısı: ilk kurulum ve güncelleme sırasında bağımlılık indirmek için.
- Python **3.11**: yerel uygulama testlerinde kullanılan Python serisi. Daha yeni Python
  sürümlerinin sabitlenmiş bağımlılıklarla uyumluluğu burada doğrulanmadı.
- Apple Silicon Mac: yerel deneme macOS 27.0.1 ve Python 3.11.1 ile yapıldı.
  Intel, Windows, Linux veya daha eski macOS sürümleri için aynı sonucu garanti
  eden bir test yapılmadı. Önceki paketin “macOS 12+” bilgisi bu kurulumun
  destek beyanı değildir.

Terminal’i Spotlight’ta **Terminal** yazarak açın. Aşağıdaki komut yalnız
Python sürümünü gösterir; bilgisayarınızda değişiklik yapmaz:

```bash
python3.11 --version
```

Python 3.11 bulunamazsa, Homebrew kullanan Mac’lerde aşağıdaki komutla
kurabilirsiniz. Bu komut Python’u ve gereken bileşenlerini indirip kurar:

```bash
brew install python@3.11
```

Homebrew yoksa önce [resmî kurulum sayfasını](https://docs.brew.sh/Installation)
izleyin ve kurulumun gösterdiği son PATH adımlarını tamamlayın. Homebrew’un
işletim sistemi gereksinimleri NumeriPlot’tan ayrıdır; kendi Mac’inizin
desteklendiğini kontrol edin. Başka bir sağlayıcıdan çalışan Python 3.11’iniz
varsa Homebrew kurmanız gerekmez. Sistem Python’unu silmeyin veya değiştirmeyin.

## 2. Kaynak kodu indirin

1. [NumeriPlot deposunu](https://github.com/alptekin-yildiz/NumeriPlot) açın.
2. [0.1.1 yayın sayfasında](https://github.com/alptekin-yildiz/NumeriPlot/releases/tag/v0.1.1)
   **Assets → Source code (zip)** bağlantısıyla kaynak kodu indirin. Bu, hazır
   uygulama ZIP’i değildir. Depodaki **Code → Download ZIP** ise gelişmeye devam
   eden `main` dalını indirir; bu kılavuz için 0.1.1 arşivini tercih edin.
3. ZIP’i açıp klasörü kalıcı bir yere taşıyın. İçinde `main.py`, `setup.sh` ve
   `requirements.txt` bulunmalıdır.
4. Terminal’e `cd` yazıp bir boşluk bırakın, Finder’daki bu klasörü Terminal’e
   sürükleyin ve Enter’a basın. Bu işlem Terminal’i proje klasörüne geçirir;
   klasörü taşımaz. Komutlar aşağıda bu klasörün içinden çalıştırılır.

Git bilen kullanıcılar bunun yerine depoyu klonlayabilir:

```bash
git clone https://github.com/alptekin-yildiz/NumeriPlot.git
cd NumeriPlot
```

## 3. Bir kez kurun

Yeni indirilmiş klasörde aşağıdaki komutları **sırayla** çalıştırın. Bir komut
hata verirse sonraki adıma geçmeden sorun giderme bölümüne bakın.

İlki yalnız bu projeye ait `venv` ortamını oluşturur; ikincisi bu ortamı
etkinleştirir. Üçüncüsü bağımlılıkları `requirements.txt` sürümleriyle indirir.
NumeriPlot bağımlılıkları sistem Python’una değil bu klasöre kurulur.

```bash
python3.11 -m venv venv
source venv/bin/activate
bash setup.sh
```

Ardından uygulamayı başlatın:

```bash
python3 main.py
```

Pencere açılırken Terminal açık kalsın. Program açıldıktan sonra normal
menüleri, dosya seçicileri ve fareyi kullanırsınız. Her açılışta kurulum
yapılmaz. Günlük kullanım için `--dev`, test araçları veya PyInstaller gerekmez.

## 4. Sonraki günlerde çift tıklayarak açma

Finder’da NumeriPlot kaynak klasörünü açın ve **`NumeriPlot.command`** dosyasına
çift tıklayın. Terminal penceresi ve ardından NumeriPlot arayüzü açılır.
Programı kullanırken Terminal penceresi açık kalsın; programı kapattıktan
sonra bu pencereyi kapatabilirsiniz. Her açılışta kurulum yapılmaz.

Dosyayı proje klasöründen çıkarmayın. Kolay erişim için Finder’da dosyayı seçip
**Dosya → Takma Ad Yarat** ile oluşturduğunuz takma adı masaüstüne taşıyabilirsiniz.

Başlatıcı kurulumu eksik bulursa kılavuzun yerini gösterir. Dosya çalıştırma
izni nedeniyle açılamıyorsa proje klasöründe aşağıdaki komutu bir kez çalıştırın;
bu yalnız başlatıcıya çalıştırma izni verir:

```bash
chmod +x NumeriPlot.command
```

macOS güvenlik uyarısı gösterirse [belgelenmiş Gatekeeper adımlarına](../README_TR.md)
bakın; hasarlı uygulama veya zararlı yazılım uyarısını aşmayın.
Terminal’den açmayı tercih ederseniz proje klasöründe şu komutu kullanın:

```bash
./venv/bin/python main.py
```

Proje klasörünü kurulumdan sonra taşımayın: sanal ortamlar taşınabilir değildir.
Taşımanız gerekiyorsa yeni bir kaynak kopyasında kurulumu tekrarlayın.

## 5. İlk kullanım kontrolü

**Dosya → Proje Aç…** ile `examples/NumeriPlot_example_project.json` dosyasını
açın. Grafik ve Analiz Raporu sekmelerine bakın. **Projeyi Farklı Kaydet…** ile
kendi kopyanızı proje klasörü dışında saklayın. Bu örnek yalnız sentetik veri
içerir. Veri yükleme, fit ve dışa aktarma için
[görselli kılavuzu](https://alptekin-yildiz.github.io/NumeriPlot/) izleyin.

Fareyle fit aralığı seçtiğinizde Katman Yönetimi listesinden veri serisini
yeniden seçip modeli belirleyin ve **Fit** düğmesine basın. Eski fit otomatik
olarak yeniden hesaplanmaz.

## 6. Sorun giderme

- **`main.py` veya `setup.sh` bulunamadı:** Terminal proje klasöründe değildir.
  2. adımdaki `cd` yöntemini tekrarlayın.
- **`ModuleNotFoundError`:** `./venv/bin/python main.py` kullanın. Kurulum
  başarısız kaldıysa ortamı etkinleştirip `bash setup.sh` adımını tamamlayın.
- **Paket sürümü bulunamadı / derleyici isteniyor:** Python sürümünü ve işlemci
  mimarisini kontrol edin. Rastgele paket sürümleriyle `requirements.txt`
  dosyasını değiştirmeyin; tam hata ile [destek kılavuzuna](../SUPPORT_TR.md) bakın.

### Apple Silicon / Python 3.11: SciPy `_spropack` veya `__thread_bss` hatası

Yerel denemede SciPy 1.15.2’nin macOS 14 wheel’i bu açılış hatasını verdi.
Aynı sürümün macOS 12 arm64 wheel’iyle açılış ve testler geçti. **Yalnız bu
hatayı Apple Silicon ve Python 3.11’de görüyorsanız** aşağıdaki adımları kullanın;
diğer makineler için bu dosyayı zorlamayın.

İlk iki komut Python serisini ve mimariyi doğrular; sonuçlar `3.11.x` ve
`arm64` olmalıdır. Sonraki komutlar aynı SciPy sürümünün alternatif resmî
PyPI wheel’ini indirip yalnız proje ortamındaki SciPy kurulumunu değiştirir:

```bash
./venv/bin/python --version
./venv/bin/python -c "import platform; print(platform.machine())"
./venv/bin/python -m pip download --only-binary=:all: --no-deps --platform macosx_12_0_arm64 --python-version 3.11 --implementation cp --abi cp311 --dest venv/wheel-downloads scipy==1.15.2
./venv/bin/python -m pip install --force-reinstall --no-deps venv/wheel-downloads/scipy-1.15.2-cp311-cp311-macosx_12_0_arm64.whl
./venv/bin/python main.py
```

Bu wheel’in dosya adındaki macOS 12, tüm uygulamanın macOS 12 desteği anlamına
gelmez. Kurulumu daha sonra yeniden yaparsanız aynı sorun yeniden oluşabilir.
Bu özel adım kaynak arşivine üçüncü taraf ikili dosya eklemez.

Başka hatalarda [SUPPORT_TR.md](../SUPPORT_TR.md) adımlarını izleyin. Log veya
hata çıktısını paylaşmadan kişisel yolları ve özel verileri çıkarın.

## 7. Güncelleme ve kaldırma

Güncellemeden önce projelerinizi kaydedin. Yeni kaynak kodu **ayrı bir klasöre**
indirip yeni bir ortam kurun; eski klasörü yeni sürümü deneyene kadar koruyun.
`venv` klasörünü yeni kopyaya taşımayın. Proje şeması bu sürümde **1.0** olarak kalır.

Kaldırmak için uygulamayı kapatın, saklamak istediğiniz proje/verileri başka
yere taşıyın ve NumeriPlot kaynak klasörünü Finder’da Çöp Sepeti’ne taşıyın.
Bu işlem ayrıca kurduğunuz Python veya Homebrew’u kaldırmaz. Yerel loglar için
[destek belgesindeki](../SUPPORT_TR.md) konuma bakın.

## 8. İsteğe bağlı: kendi Mac’inizde `.app` oluşturma

Bu adım normal kullanım için gerekli değildir. **Ayrı, temiz bir kaynak
kopyasında** uygulamayı önce yukarıdaki yöntemle çalıştırın. Sonra geliştirme
araçlarını kurup kontrolü çalıştırın; kontrol başarısızsa paketlemeye geçmeyin:

```bash
source venv/bin/activate
bash setup.sh --dev
```

Gerekmişse SciPy düzeltmesini geliştirme kurulumundan sonra yeniden uygulayın. Ardından kontrolü çalıştırın:

```bash
bash release_check.sh
```

Paketleme komutu proje klasöründeki mevcut `build/` ve `dist/` çıktılarını
**siler ve yeniden oluşturur**; bu klasörlerde saklanacak dosya bırakmayın:

```bash
bash build_macos.sh
```

Sonuç `dist/NumeriPlot.app` ve sürüm numaralı ZIP’tir. Paketleme dosyası macOS
14 alt sınırını kullanır; başka mimarilerde evrensel paket üretildiği varsayılmaz.
Apple Developer ID imzası veya noter onayı eklenmez. Hasarlı uygulama/zararlı
yazılım uyarısını aşmayın. Oluşturduğunuz paketi **başkalarına dağıtmak** ayrı
bir adımdır ve [üçüncü taraf dağıtım koşullarını](../THIRD_PARTY_NOTICES.md)
yeniden gündeme getirir; bu bölüm bir dağıtım onayı değildir.

## Kaynaklar

- [Python sanal ortamları](https://docs.python.org/3.11/library/venv.html)
- [Mac üzerinde Python](https://docs.python.org/3.11/using/mac.html)
- [Homebrew Python 3.11](https://formulae.brew.sh/formula/python@3.11)
- [GitHub kaynak arşivlerini indirme](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives)
