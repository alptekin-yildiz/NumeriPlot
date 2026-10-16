# NumeriPlot

**Scientific Plotting, Data Analysis and Curve Fitting**

NumeriPlot; özellikle öğrenciler ve araştırmacılar için geliştirilen, bilimsel
grafik çizimi, veri işleme ve eğri uydurma amaçlı özgür ve açık kaynaklı bir
masaüstü uygulamasıdır.

## İlk kez mi kullanıyorsunuz?

**[Mac’te kur ve kullan →](docs/SOURCE_INSTALL_TR.md)**

Kod yazmanız veya uygulamayı derlemeniz gerekmez. Kılavuz, kaynak kodu
indirmeyi ve bir defalık kurulumu adım adım anlatır. Kurulumdan sonra
Finder’da **`NumeriPlot.command` dosyasına çift tıklayın**; programın
grafik arayüzü açılır. Başlatıcıyı proje klasöründe tutun.

> **Public Beta uyarısı:** NumeriPlot 0.1.1 bir Public Beta sürümüdür.
> 0.1.1 kaynak kod olarak dağıtılır; hazır Mac ZIP’i içermez.
> Arayüzler, iş akışları ve proje dosyası biçimi
> değişebilir. Araştırma, eğitim veya raporlama amacıyla kullanılacak sayısal
> sonuçları bağımsız olarak doğrulayın.

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

Örnek proje **Dosya → Proje Aç…** yoluyla açılabilir. Bakımcılar aynı projeden
ekran görüntülerini şu komutla yeniden oluşturabilir:

```bash
QT_QPA_PLATFORM=offscreen python3 examples/capture_screenshots.py
```

## Durum ve platformlar

**0.1.1 Public Beta kaynak kod olarak dağıtılır.** Hazır 0.1.1 Mac
uygulama ZIP’i içermez. Kullanıcı bağımlılıkları kendi
bilgisayarına kurar ve normal masaüstü arayüzünü kaynak koddan çalıştırır.
Proje şeması **1.0** olarak kalır.

| Ortam | Mevcut doğrulama |
| --- | --- |
| Apple Silicon, macOS 27.0.1, Python 3.11.1 | Kaynak kod akışı ve otomatik testler yerelde kontrol edildi; belgelenmiş SciPy çözümüne bakın |
| Diğer macOS veya Python sürümleri | Bu çalışmada bağımsız olarak doğrulanmadı |
| Intel Mac, Windows, Linux | Eşdeğer kaynak veya paket doğrulaması yapıldığı iddia edilmiyor |

[Önceki 0.1.0 pre-release](https://github.com/alptekin-yildiz/NumeriPlot/releases/tag/v0.1.0)
eski bir uygulama paketi içerir. 0.1.1 düzeltmelerini içermez ve aşağıdaki
kurulum yolunun parçası değildir. Mevcut release dosyaları kaldırılmadı.

## Kaynaktan çalıştırma

[Adım adım Mac kurulum kılavuzuyla](docs/SOURCE_INSTALL_TR.md) başlayın
([English](docs/SOURCE_INSTALL.md)). Python kurulumu, Git kullanmadan kaynak
indirme, ilk kurulum, günlük açılış, sorun giderme ve güncelleme anlatılıyor.
Günlük kullanım için `.app` oluşturmak gerekmez.

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

## macOS ZIP kurulumu

**Yalnız önceki 0.1.0 paketi için.** 0.1.1 için yukarıdaki kaynak kurulumunu izleyin.

Bu adımlar [NumeriPlot GitHub Releases sayfasındaki](https://github.com/alptekin-yildiz/NumeriPlot/releases/tag/v0.1.0)
resmî `v0.1.0` pre-release dosyaları için geçerlidir:

1. `NumeriPlot_v0.1.0_macOS.zip` ve `.sha256` dosyasını yalnızca resmî
   NumeriPlot GitHub Release sayfasından indirin.
2. Terminal'de indirilen ZIP'in checksum değerini hesaplayın:

   ```bash
   shasum -a 256 NumeriPlot_v0.1.0_macOS.zip
   ```

   ZIP'i açmadan önce sonucun tamamını yayımlanan checksum ile karşılaştırın.
3. ZIP'e çift tıklayın ve `NumeriPlot.app` dosyasını `Applications` klasörüne
   taşıyın.
4. `NumeriPlot.app` üzerinde Control-tıklayın veya sağ tıklayın, **Aç**
   seçeneğini kullanın ve devam edip etmeyeceğinize karar vermeden önce macOS
   uyarısını inceleyin.

### Gatekeeper ve imzasız beta

Public beta build'i Apple Developer ID ile imzalanmamıştır ve Apple tarafından
noter onayından geçirilmemiştir. Bu nedenle macOS geliştiriciyi tanıyamaz ve
uygulamanın Apple tarafından zararlı yazılım açısından kontrol edildiğini
doğrulayamaz.

Uygulamayı açmayı denedikten sonra macOS hâlâ engelliyorsa önce dosyanın resmî
release sayfasından geldiğini ve checksum değerinin eşleştiğini doğrulayın.
Ardından devam etmeyi seçerseniz **Sistem Ayarları → Gizlilik ve Güvenlik**
bölümünü açın, **Güvenlik** altındaki engellenen uygulama mesajını bulun,
**Yine de Aç** seçeneğini kullanın ve onay penceresini inceleyin. Apple bu
istisna yolunu
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
OpenAI Codex dahil olmak üzere AI coding-agent araçlarından önemli ölçüde destek
alınarak geliştirilmiştir. İnsan bakımcı projeyi yönlendirir, yayıma dönük
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
dosyasındadır.
