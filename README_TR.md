# NumeriPlot

**Scientific Plotting, Data Analysis and Curve Fitting**

NumeriPlot; özellikle öğrenciler ve araştırmacılar için geliştirilen, bilimsel
grafik çizimi, veri işleme ve eğri uydurma amaçlı özgür ve açık kaynaklı bir
masaüstü uygulamasıdır.

> **Public Beta uyarısı:** NumeriPlot 0.1.0 ilk halka açık sürüm için
> hazırlanmaktadır. Arayüzler, iş akışları ve proje dosyası biçimi değişebilir.
> Araştırma, eğitim veya raporlama amacıyla kullanılacak sayısal sonuçları
> bağımsız olarak doğrulayın.

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

Henüz halka açık bir binary yayımlanmamıştır.

| Ortam | 0.1.0 durumu |
| --- | --- |
| Apple Silicon, macOS 12 veya üzeri | Planlanan ilk paket; imzasız ve noter onaysız |
| Intel Mac | 0.1.0 için paket planlanmıyor |
| Windows ve Linux | Şu anda paket veya release doğrulaması sunulmuyor |
| Python 3.11 veya üzeri | Kaynak/geliştirme yolu; ilk release doğrulaması Apple Silicon macOS hedeflidir |

Uygulamanın başka bir platformda kaynaktan açılması, o platformun NumeriPlot
release kontrol listesinden geçtiği anlamına gelmez.

## Kaynaktan çalıştırma

Python 3.11 veya üzeri ile ilk bağımlılık indirmesi için internet erişimi
gereklidir. Halka açık depo açıldıktan sonra:

```bash
git clone https://github.com/alptekin-yildiz/NumeriPlot.git
cd NumeriPlot
bash setup.sh
source venv/bin/activate
python3 main.py
```

Setup betiği yerel bir sanal ortam oluşturur ve `requirements.txt` içinde
tanımlanan runtime bağımlılıklarını kurar.

Otomatik release kapısı ayrıca sabitlenmiş geliştirme araçlarını gerektirir.
Aynı ortama kurup şu komutları çalıştırın:

```bash
bash setup.sh --dev
source venv/bin/activate
bash release_check.sh
```

## macOS ZIP kurulumu

Bu adımlar resmî `v0.1.0` release dosyaları yayımlandıktan sonra geçerli
olacaktır:

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

Planlanan ilk build Apple Developer ID ile imzalanmayacak ve Apple tarafından
noter onayından geçirilmeyecektir. Bu nedenle macOS geliştiriciyi tanıyamaz ve
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
