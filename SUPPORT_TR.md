# NumeriPlot Destek

Bu belge NumeriPlot kullanıcıları için güvenli ilk sorun giderme adımlarını
içerir. İngilizce sürüm için [`SUPPORT.md`](SUPPORT.md) belgesine bakın.

NumeriPlot 0.1.0 bir Public Beta sürümüdür. Orijinal verileri ve önemli proje
dosyalarının bağımsız yedeklerini saklayın; sayısal sonuçları ayrıca doğrulayın.

## Sorun gidermeden önce

Yardım istemeden önce şu bilgileri kaydedin:

- NumeriPlot sürümü veya commit kimliği;
- macOS ZIP sürümünü mü yoksa kaynak kodu mu kullandığınız;
- işletim sistemi ve sürümü ile donanım mimarisi;
- izlenen adımlar, beklenen sonuç ve gerçekleşen sonuç; ve
- sorunu yeniden oluşturan en küçük sentetik girdi.

Özel araştırma verilerini, öğrenci veya hasta bilgilerini, kimlik bilgilerini,
kişisel yolları veya temizlenmemiş logları herkese açık olarak paylaşmayın.

## Kurulum ve başlatma

### macOS ZIP

Resmî ZIP talimatları bir NumeriPlot release'i yayımlandıktan sonra geçerlidir.
ZIP'in resmî GitHub Release sayfasından geldiğini doğrulayın ve dosyayı açmadan
önce SHA-256 checksum değerinin tamamını yayımlanan `.sha256` dosyasıyla
karşılaştırın.

İlk Public Beta'nın imzasız ve noter onaysız olması planlanmaktadır.
[`README_TR.md`](README_TR.md) içindeki Gatekeeper adımlarını uygulayın; uygulama
üzerinde Control-tıklayıp **Aç** seçeneğini kullanın. Karantina niteliklerini
rutin olarak kaldırmayın. Uygulamanın hasarlı veya zararlı yazılım içerdiğini
belirten bir uyarıyı atlamayın.

### Kaynak kod

NumeriPlot Python 3.11 veya üzerini gerektirir. Depo kökünde şunları çalıştırın:

```bash
bash setup.sh
source venv/bin/activate
python3 main.py
```

Kurulum başarısız olursa `python3 --version` ile Python sürümünü doğrulayın,
ilk bağımlılık indirmesinde internet erişimi bulunduğunu kontrol edin ve hata
mesajının tamamını saklayın. Paylaşmadan önce kimlik bilgilerini ve kişisel
yolları temizleyin.

## Veri içe aktarma

NumeriPlot CSV, TXT, XLSX ve XLS verilerini içe aktarır. Tablo beklendiği gibi
yorumlanmıyorsa şunları kontrol edin:

- ayırıcı ve metin kodlaması;
- dosyada başlık satırı bulunup bulunmadığı;
- içe aktarmadan önce atlanan satır sayısı;
- ondalık karakterleri ve sayısal sütun tipleri; ve
- Excel dosyalarında seçilen çalışma sayfası.

Davranışı birkaç satırlık sentetik veriyle yeniden oluşturmayı deneyin. Yeni
bir veri dosyası içe aktarmak geçerli tablonun yerini alır ve grafik, fit ve
metin öğelerini temizler; gerektiğinde önce mevcut projeyi kaydedin.

## Grafik ve fit

Eksik veya beklenmedik bir grafikte X, Y Sol, Y Sağ, X Hata ve Y Hata sütun
rollerini; ardından seçilen seriyi, grafik tipini, eksenleri ve görünür
aralıkları doğrulayın.

Bir fit sorunu için şunları kaydedin:

- seçilen model ve fit aralığı;
- parametre başlangıç değerleri ve sınırları;
- parametre birimleri ve geçerli veri alanı;
- hata mesajının tamamı; ve
- sayısal toleransla birlikte bağımsız hesaplanmış beklenen sonuç.

Bir fit işleminin yakınsaması, sonucun bilimsel olarak geçerli olduğunu tek
başına göstermez. Rezidüleri, başlangıç değerlerine ve aralığa duyarlılığı ve
modelin veriye uygunluğunu inceleyin. NumeriPlot güvenlik-kritik, klinik,
düzenleyici veya sertifikasyon hesapları için doğrulanmamıştır.

## Proje dosyaları

Yeni NumeriPlot projeleri üst düzey `"schema_version": "1.0"` alanını kullanır.
Şema tanımlayıcısı bulunmayan veya desteklenmeyen dosyalar sessizce yorumlanmak
yerine reddedilir.

Değerli bir projede sorun gidermeden önce bağımsız yedek alın. Biçimi
bilmiyorsanız proje JSON'unu elle düzenlemeyin. Sorun bildirirken davranışı
yeniden oluşturan küçük ve sentetik bir proje kullanmayı tercih edin.

## Dışa aktarma

NumeriPlot grafikleri PNG, PDF veya SVG; tabloları CSV veya XLSX; yeniden
üretilebilir kodu Python veya notebook dosyası olarak dışa aktarır. İşlem
başarısız olursa şunları kontrol edin:

- hedef dizinin var ve yazılabilir olması;
- dosya adının beklenen uzantıyı kullanması;
- hedef dosyanın başka bir uygulamada açık olup olmaması; ve
- aynı sorunun basit bir sentetik projede oluşup oluşmaması.

Üretilen betik ve notebook dosyalarını araştırmada kullanmadan önce inceleyin.
Dışa aktarılan bir dosya bağımsız sayısal doğrulamanın yerine geçmez.

## Loglar ve gizlilik

macOS'ta tanılama logları yalnızca şu yerel konumda tutulur:

```text
~/Library/Logs/NumeriPlot/numeriplot.log
```

NumeriPlot logları otomatik olarak yüklemez. Bir bölümü paylaşmadan önce
kişisel yolları, dosya adlarını, araştırma içeriğini, kimlik bilgilerini ve
diğer hassas bilgileri temizleyin. Yalnızca sorunu anlamak için gereken en
küçük bölümü paylaşın.

## Nereden yardım alınır?

Halka açık depo açıldıktan sonra:

- yeniden oluşturulabilen yazılım sorunları için
  [hata bildirimi](https://github.com/alptekin-yildiz/NumeriPlot/issues/new/choose)
  yolunu kullanın;
- odaklı özellik isteği veya belgelenmiş fit modeli önerisi için aynı issue
  seçiciyi kullanın; ve
- güvenlik açığı, gizlilik sorunu veya hassas ayrıntı içeren raporlar için
  [`SECURITY.md`](SECURITY.md) belgesini izleyin.

Güvenlik açısından hassas bilgileri herkese açık issue olarak göndermeyin. Bu
bağımsız akademik projenin bakım kapasitesi sınırlıdır ve yanıt süresi garantisi
yoktur.
