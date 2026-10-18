# NumeriPlot Destek

Bu belge NumeriPlot kullanıcıları için güvenli ilk sorun giderme adımlarını
içerir. İngilizce sürüm için [`SUPPORT.md`](SUPPORT.md) belgesine bakın.

NumeriPlot 0.2.x bir Public Beta sürümüdür. Orijinal verileri ve önemli proje
dosyalarının bağımsız yedeklerini saklayın; sayısal sonuçları ayrıca doğrulayın.

## Sorun gidermeden önce

Yardım istemeden önce şu bilgileri kaydedin:

- NumeriPlot sürümü veya commit kimliği;
- macOS uygulamasını mı yoksa kaynak kodu mu kullandığınız;
- işletim sistemi ve sürümü ile donanım mimarisi;
- izlenen adımlar, beklenen sonuç ve gerçekleşen sonuç; ve
- sorunu yeniden oluşturan en küçük sentetik girdi.

Özel araştırma verilerini, öğrenci veya hasta bilgilerini, kimlik bilgilerini,
kişisel yolları veya temizlenmemiş logları herkese açık olarak paylaşmayın.

## Kurulum ve başlatma

### macOS uygulaması

[Mac kurulum kılavuzunu](docs/MACOS_INSTALL_TR.md) izleyin. Uygulama, macOS 14
veya üstü yüklü bir Apple Silicon Mac gerektirir. Disk görüntüsünü yalnızca
resmî GitHub Release sayfasından indirin; isterseniz açmadan önce SHA-256
değerini yayımlanan `.sha256` dosyasıyla karşılaştırın.

Uygulama imzasız ve noter onaysızdır. İlk açılışta macOS
**“NumeriPlot” Açılmadı** mesajını gösterir: **Bitti**'yi seçin (mavi varsayılan
düğme **Çöp Sepeti'ne Taşı**'dır), ardından **Sistem Ayarları → Gizlilik ve
Güvenlik → Yine de Aç**, **“NumeriPlot” açılsın mı?** penceresinde yine
**Yine de Aç** ve Touch ID veya parola. Düğme, açma denemesinden sonra yaklaşık
bir saat görünür. Karantina
niteliklerini rutin olarak kaldırmayın. Uygulamanın hasarlı veya zararlı yazılım
içerdiğini belirten bir uyarıyı atlamayın.

- Uygulama birkaç saniye içinde açılır. Matplotlib yazı tipi önbelleğini
  `~/Library/Caches/NumeriPlot` klasöründe tutar; bu klasör istendiğinde
  silinebilir. Açılırken simgeye tekrar tekrar tıklamak ikinci bir kopya
  başlatabilir.
- Uygulamayı disk görüntüsü penceresinden çalıştırmak yerine önce
  **Uygulamalar** klasörüne kopyalayın.
- Intel Mac'ler ile macOS 13 ve öncesi uygulama tarafından desteklenmez;
  aşağıdaki kaynak kod yolunu kullanın.

### Kaynak kod

Diğer bilgisayarlar ve geliştirme için
[kaynak kurulum kılavuzunu](docs/SOURCE_INSTALL_TR.md) izleyin. Python 3.11,
açılış ve doğrulama makinesinde görülen özel SciPy açılış hatası anlatılıyor.
Daha yeni Python sürümleri otomatik olarak doğrulanmış sayılmaz.

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

Loglar en çok 2 MiB’lık dört dosyada tutulur. Kaynak kod kurulumunda kurulum
denetimi hataları `venv/runtime-check.log` dosyasındadır; paylaşmadan kişisel
yolları ve hassas içerikleri çıkarın.
