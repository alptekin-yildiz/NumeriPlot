# NumeriPlot

**Scientific Plotting, Data Analysis and Curve Fitting**

NumeriPlot; özellikle öğrenciler ve araştırmacılar için geliştirilen, bilimsel
grafik çizimi, veri işleme ve eğri uydurma amaçlı özgür ve açık kaynaklı bir
masaüstü uygulamasıdır.

## İlk kez mi kullanıyorsunuz?

**[Mac’e kur →](docs/MACOS_INSTALL_TR.md)**

1. [0.2.0 yayın sayfasından](https://github.com/alptekin-yildiz/NumeriPlot/releases/tag/v0.2.0)
   `NumeriPlot-0.2.0-macOS-AppleSilicon.dmg` dosyasını indirin.
2. Dosyayı açın ve **NumeriPlot**'u **Applications** (Uygulamalar) klasörüne
   sürükleyin.
3. NumeriPlot'u Uygulamalar'dan açın. İlk seferde **Sistem Ayarları →
   Gizlilik ve Güvenlik → Yine de Aç** ile bir kez izin verin; kılavuz her
   adımı gösterir.

Uygulama, macOS 14 veya üstü yüklü bir Apple Silicon Mac gerektirir. Python veya
Terminal gerekmez. Diğer bilgisayarlarda NumeriPlot
[kaynak koddan çalıştırılabilir](docs/SOURCE_INSTALL_TR.md).

> **Public Beta uyarısı:** NumeriPlot 0.2.0 Public Beta, bağımsız bir Mac
> uygulaması olarak dağıtılan ilk sürümdür. Arayüzler, iş akışları ve proje
> dosyası biçimi değişebilir. Araştırma, eğitim veya raporlama amacıyla
> kullanılacak sayısal sonuçları bağımsız olarak doğrulayın.

NumeriPlot, Alptekin YILDIZ tarafından sürdürülen bağımsız bir akademik yazılım
projesidir. İstanbul Teknik Üniversitesi yalnızca geliştiricinin akademik bağı
olarak belirtilir; projenin sahibi, yayımcısı, sponsoru veya destek sağlayıcısı
değildir.

Ana proje belgesi İngilizce [`README.md`](README.md) dosyasıdır.

## Mevcut yetenekler

- CSV ve Excel verisi içe aktarma ve düzenlenebilir veri tabloları
- X, Y, sağ Y, X hata ve Y hata rollerini atama
- Ayarlanabilir eksen ve lejant seçenekleriyle çizgi, saçılım ve gruplu bar
  grafikleri
- Yerleşik eğri uydurma modelleri ve fit aralığı kontrolleri
- Pik bulma ve yaygın veri işleme işlemleri
- Açık şema doğrulamasıyla proje kaydetme ve açma
- PNG, PDF, SVG, tablo, Python betiği ve notebook dışa aktarma yolları
- Türkçe ve İngilizce kullanıcı arayüzü

## Görselli kullanım kılavuzu

[Kılavuzu çevrimiçi okuyun](https://alptekin-yildiz.github.io/NumeriPlot/).

Çevrimdışı HTML kılavuzu; panelleri, menüleri, açılır seçenekleri, grafik
ayarlarını, fit ve dışa aktarmayı gerçek arayüz görüntüleriyle açıklar. Depoyu
indirdikten sonra [`docs/guide/index.html`](docs/guide/index.html) dosyasını
tarayıcıda açın; sunucu gerekmez. `docs/guide` klasörünü bir arada tutun.
[English](docs/guide/en.html).

## Ekran görüntüleri

Aşağıdaki ekran görüntüleri gerçek NumeriPlot arayüzünden, yalnızca depoda
izlenen ve yeniden üretilebilen sentetik Gauss örneği kullanılarak alınmıştır.

![Sentetik Gauss gözlemlerini, hata çubuklarını ve uyum eğrisini gösteren NumeriPlot grafik çalışma alanı](assets/screenshots/numeriplot-overview.png)

![Fit parametrelerini ve sentetik rezidüleri gösteren NumeriPlot analiz raporu](assets/screenshots/numeriplot-fit-analysis.png)

## Sentetik örnekler

[`examples/`](examples/) dizini üç deterministik sentetik CSV veri seti ve
doğrudan açılabilen bir NumeriPlot projesi içerir:

- gürültülü doğrusal veri;
- kaydedilmiş Gauss fiti ve rezidü istatistikleri içeren bir Gauss piki; ve
- tek üstel doyum verisi.

Dosyalarda araştırma, öğrenci, hasta veya kişisel veri yoktur. Formüller,
parametreler ve sabit rastgelelik tohumu için
[`examples/README.md`](examples/README.md) belgesine bakın. Veri ve projeyi depo
kökünden yeniden üretmek için:

```bash
python3 examples/generate_examples.py
```

Uygulamada örnek proje **Dosya → Örnek Projeyi Aç** ile açılır; kaynak kod
klasöründe **Dosya → Proje Aç…** de kullanılabilir. Bakımcılar aynı projeden
ekran görüntülerini şu komutla yeniden oluşturabilir:

```bash
QT_QPA_PLATFORM=offscreen python3 examples/capture_screenshots.py
```

## Durum ve platformlar

**0.2.0 Public Beta, Apple Silicon için bir Mac uygulaması olarak dağıtılır.**
Disk görüntüsünde her şeyi içinde taşıyan bir `NumeriPlot.app` bulunur; Python
gerekmez. Uygulamada Apple'ın ücretli geliştirici imzası olmadığı için macOS
ilk açılışta bir kez izin ister. Proje şeması **1.0** olarak kalır.

| Ortam | Mevcut doğrulama |
| --- | --- |
| Apple Silicon, macOS 27.0.1 | Uygulama derlendi, disk görüntüsünden kuruldu ve yerelde kontrol edildi |
| Apple Silicon, macOS 14–26 | Paketteki kütüphanelerce desteklenir (en az macOS 14); bu sürümlerde denenmedi |
| Intel Mac, Windows, Linux | Uygulama sunulmaz; kaynak koddan çalıştırmak mümkündür ama doğrulanmadı |

## Kaynaktan çalıştırma

Apple Silicon Mac'te önerilen yol yukarıdaki uygulamadır. Kaynaktan çalıştırma
diğer bilgisayarlar (Intel Mac, Windows, Linux; kullanıcının kendi emeğiyle) ve
geliştirme içindir. [Kaynak kurulum kılavuzu](docs/SOURCE_INSTALL_TR.md)
([English](docs/SOURCE_INSTALL.md)) Python kurulumunu, Git kullanmadan kaynak
indirmeyi, ilk kurulumu, açılışı, sorun gidermeyi ve güncellemeyi anlatır.

Python 3.11 kuruluysa Git bilen kullanıcılar aşağıdaki komutları sırayla
çalıştırabilir. Hata olursa durun ve kılavuzdaki sorun giderme bölümünü izleyin:

```bash
git clone https://github.com/alptekin-yildiz/NumeriPlot.git
cd NumeriPlot
python3.11 -m venv venv
source venv/bin/activate
bash setup.sh
python3 main.py
```

Sonraki açılışlarda aynı kaynak klasörüne geçip şu komutu çalıştırın:

```bash
./venv/bin/python main.py
```

Katkı verenler geliştirme araçlarını aynı ortama kurup tam kontrolü çalıştırır.
Gerekirse kılavuzdaki SciPy çözümünü kontrol öncesinde uygulayın:

```bash
source venv/bin/activate
bash setup.sh --dev
bash release_check.sh
```

## macOS uygulamasını kurma

Gereksinim: macOS 14 veya üstü yüklü bir Apple Silicon (M1 ve sonrası) Mac.
[Kurulum kılavuzu](docs/MACOS_INSTALL_TR.md) her adımı ayrıntılı anlatır.

1. `NumeriPlot-0.2.0-macOS-AppleSilicon.dmg` dosyasını yalnızca resmî
   [0.2.0 yayın sayfasından](https://github.com/alptekin-yildiz/NumeriPlot/releases/tag/v0.2.0)
   indirin.
2. İsteğe bağlı: `.sha256` dosyasını da indirip disk görüntüsünü Terminal'de
   doğrulayın. Sonuçta `OK` yazmalıdır:

   ```bash
   cd ~/Downloads
   shasum -a 256 -c NumeriPlot-0.2.0-macOS-AppleSilicon.dmg.sha256
   ```

3. Disk görüntüsüne çift tıklayın ve **NumeriPlot**'u **Applications**
   (Uygulamalar) klasörüne sürükleyin.
4. NumeriPlot'u **Uygulamalar**'dan açın ve ilk seferde aşağıdaki bölümü izleyin.
   Uygulama birkaç saniye içinde açılır.

### Gatekeeper ve imzasız beta

NumeriPlot ücretsizdir; Apple'ın ücretli geliştirici imzası (Developer ID) ve
noter onayı yoktur. Bu nedenle macOS geliştiriciyi tanıyamaz ve ilk açılışı
**“NumeriPlot” Açılmadı** mesajıyla durdurur. Bir kez izin verin:

1. Mesajda **Bitti**'yi seçin. Mavi renkli, öne çıkan düğme **Çöp Sepeti'ne
   Taşı**'dır; onu seçmeyin.
2. **Sistem Ayarları → Gizlilik ve Güvenlik** bölümünü açın, **Güvenlik**
   kısmına kaydırın ve NumeriPlot mesajının yanındaki **Yine de Aç**'ı seçin.
   Düğme, açma denemesinden sonra yaklaşık bir saat görünür.
3. **“NumeriPlot” açılsın mı?** penceresinde **Yine de Aç**'ı seçin (yine
   **Çöp Sepeti'ne Taşı**'yı değil), ardından Touch ID veya Mac parolanızla
   onaylayın.

Bundan sonra NumeriPlot normal açılır. Apple bu istisna yolunu
[Bilinmeyen geliştiriciden gelen Mac uygulamasını açma](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unknown-developer-mh40616/mac)
sayfasında açıklar.

Uygulamanın hasarlı olduğu veya zararlı yazılım içerdiği yönündeki bir uyarıyı
atlamayın. Karantina kaldırma komutunu rutin kurulum adımı olarak kullanmayın.

## İlk iş akışı

1. **Dosya → Veri Yükle…** yolunu seçerek bir CSV, TXT, XLSX veya XLS dosyası
   açın.
2. İçe aktarma penceresindeki ayırıcı, kodlama, başlık, atlanacak satır ve sütun
   tipi seçimlerini inceleyip tabloyu içe aktarın.
3. **Veri Tablosu** sekmesini açın. Sütun başlığının bağlam menüsünden roller
   atayın veya bir rol şablonu uygulayın. Tipik bir tablo bir **X** ve bir ya da
   daha fazla **Y Sol** sütunu kullanır. Yalnızca Y içeren veri setinde otomatik
   `1..n` X değerleri kullanılabilir.
4. Grafik tipini seçip **Grafik Ekle** düğmesini kullanın. Stil, eksen, lejant,
   yerleşim ve etiketleri seri listesi ile Grafik ayarlarından düzenleyin.
5. Eğri uydurmak için çizilmiş seriyi seçin, **Analiz ve Fit** bölümünden bir
   model seçin, **Fit** düğmesini kullanın; parametreleri, uyum ölçülerini ve
   rezidüleri inceleyin.
6. Çalışma projesini **Dosya → Projeyi Kaydet** ile kaydedin. Gerektiğinde
   grafik, tablo, Python betiği veya notebook çıktısını ayrıca alın.

X otomatik üretildiğinde eksik veya sayısal olmayan Y değerleri çıkarılır;
kalan gözlemler 1'den başlayarak ardışık numaralandırılır. Ölçüm zamanlarını
veya gözlemler arasındaki boşlukları korumak için açık bir X sütunu kullanın.

Fitler ağırlıksızdır: gösterilen hata çubukları fit hesabına katılmaz.
Başlangıç parametreleri sonlu sayılar olmalıdır. Sonsuz X/Y değerleri ve
geçersiz model sonuçları reddedilir; sabit Y verisinde R² tanımsız olarak
gösterilir. Parametre belirsizliği uyarısı, elde edilen eğrinin dikkatle
incelenmesi gerektiğini belirtir; yakınsama tek başına modeli doğrulamaz.

## Veri ve proje dosyaları

NumeriPlot `.csv`, `.txt`, `.xlsx` ve `.xls` verilerini içe aktarır. Görsel
çıktılar PNG, PDF veya SVG; tablo çıktıları CSV veya XLSX biçimindedir. Python
ve notebook çıktıları `.py` ve `.ipynb` uzantılarını kullanır.

NumeriPlot projesi; geçerli tablonun gömülü bir kopyasıyla birlikte grafik
serilerini, fit sonuçlarını, metin öğelerini, panel yerleşimini ve görünüm
ayarlarını içeren bir JSON dosyasıdır. Proje JSON'u kararlı bir genel veri
değişim API'si değil, uygulama biçimidir. Özellikle Public Beta döneminde
orijinal veri dosyasını ve önemli projelerin bağımsız yedeklerini saklayın.

Yeni kaydedilen projelerde üst düzey `"schema_version": "1.0"` alanı bulunur.
Desteklenmeyen veya şema tanımlayıcısı bulunmayan dosyalar sessizce
yorumlanmak yerine reddedilir.

Yeni veri dosyası yüklemek geçerli tablonun yerini alır; mevcut grafik, fit ve
metin öğelerini temizler. Tekrar gerekebilecekse önce geçerli projeyi kaydedin.
Şemayı bilmiyorsanız ve yedeğiniz yoksa proje JSON'unu elle düzenlemeyin.

## Veri, gizlilik ve loglar

NumeriPlot verileri yerel olarak işler. Telemetri, kullanıcı takibi ve otomatik
güncelleme kontrolü içermez. macOS'ta tanılama logları yalnızca şu yerel dosyaya
yazılır:

```text
~/Library/Logs/NumeriPlot/numeriplot.log
```

Uygulama ayrıca `~/Library/Caches/NumeriPlot` klasöründe Matplotlib yazı tipi
önbelleği tutar; bu klasör istendiğinde silinebilir.

Loglar otomatik olarak gönderilmez. Bir log veya proje dosyasını paylaşmadan
önce özel araştırma verilerini, kişisel yolları, kimlik bilgilerini ve diğer
hassas bilgileri temizleyin.

## Bilimsel sorumluluk

NumeriPlot garanti verilmeksizin sunulur. Fit parametreleri ve diğer sayısal
sonuçlar; veri kalitesine, modele, başlangıç değerlerine, sınırlara ve seçilen
aralığa bağlıdır. Sonuçların bağımsız doğrulanması kullanıcının
sorumluluğundadır. Yazılım güvenlik-kritik, klinik, düzenleyici veya
sertifikasyon amaçlı hesaplamalar için doğrulanmamıştır.

## Geliştirme süreci ve AI desteği

NumeriPlot; uygulama geliştirme, test, dokümantasyon ve release hazırlığında
OpenAI Codex ve Anthropic Claude Code dahil olmak üzere AI coding-agent
araçlarından önemli ölçüde destek alınarak geliştirilmiştir. İnsan bakımcı projeyi yönlendirir, yayıma dönük
değişiklikleri inceleyip kabul eder ve lisanslama, release'ler ve bilimsel
iddialar için sorumluluğu taşır. AI desteği bilimsel doğruluğun kanıtı değildir;
sayısal sonuçlar bağımsız olarak doğrulanmalıdır.

NumeriPlot çalışma sırasında AI hizmetlerini kullanmaz ve kullanıcı verilerini
AI sağlayıcılarına göndermez. Yerel veri ve log davranışı
[Veri, gizlilik ve loglar](#veri-gizlilik-ve-loglar) bölümünde açıklanır.

## Atıf

NumeriPlot bir yayın, tez, rapor veya eğitim materyaline katkı sağlıyorsa
lütfen [`CITATION.cff`](CITATION.cff) içindeki metadata ile yazılıma atıf
verin. Atıf güçlü biçimde rica edilir; ek bir lisans koşulu değildir.

## Katkı ve destek

Sorun giderme için [`SUPPORT_TR.md`](SUPPORT_TR.md), değişiklik önermeden önce
ise [`CONTRIBUTING.md`](CONTRIBUTING.md) belgesini okuyun. Halka açık depo
açıldıktan sonra normal sorular ve hata bildirimleri
[GitHub Issues](https://github.com/alptekin-yildiz/NumeriPlot/issues) üzerinden
alınacaktır. Güvenlik bildirimlerini veya hassas veri içeren raporları herkese
açık issue olarak paylaşmayın; [`SECURITY.md`](SECURITY.md) yolunu izleyin.

## Lisans

NumeriPlot yalnızca GNU General Public License v3.0 altında lisanslanır. Tam
metin için [`LICENSE`](LICENSE) dosyasına bakın. Üçüncü taraf bileşenler kendi
lisansları altında kalır; ayrıntılar [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)
dosyasındadır. Mac uygulaması Qt (LGPL v3), PyQt6 (GPL v3) ve diğer açık kaynak
bileşenleri değiştirmeden içerir. Tam lisans metinleri uygulamada
**Dosya → Hakkında → Üçüncü Taraf Lisansları** altındadır; GPL/LGPL
bileşenlerinin kaynak arşivleri her yayınla birlikte yayımlanır.
