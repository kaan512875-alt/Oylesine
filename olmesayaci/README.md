# Ölme Sayacı

TikTok yayınına gelen hediyeleri sayan mobil uygulama.

- **Gül (Rose) gelirse +1 ölme**, **TikTok hediyesi gelirse −1 ölme.**
- Sayaç **0'ın altına inerse eksi değer "KORUMA" olarak yazılır** (ör. −2 → "2 KORUMA"). Koruma varken gül gelirse koruma azalır.
- Yayın linkini (veya @kullanıcıadı) yazıp Bağlan'a basman yeterli.
- Seri hediyelerde (1, 2, 3 diye artan olaylar) sadece yeni eklenen adet sayılır: 5'lik gül serisi +5 yapar, +15 değil.
- Hediye adları, değerler (±) ve etiketler Ayarlar'dan değiştirilebilir; sayaç elle de düzeltilebilir (±1, Geri al, Sıfırla).
- Sayaç, geçmiş ve ayarlar telefonda saklanır; uygulama kapanıp açılınca kaldığı yerden devam eder ve en son bağlıysan yayına kendiliğinden bağlanır.

## Önemli: hediyeler nereden geliyor?

TikTok'un resmi bir hediye API'si yok. Hediye olayları, TikTok'un dahili protokolünü okuyan bir **sağlayıcıdan** gelir.
Uygulama varsayılan olarak Euler Stream'in WebSocket adresine bağlanır
(`wss://ws.eulerstream.com?uniqueId=…&apiKey=…`); Ayarlar > Bağlantı'dan kendi API anahtarını ve gerekirse başka bir
sağlayıcı adresini girebilirsin. Sağlayıcıların alan adları farklı olabildiği için uygulama birkaç olası biçimi dener.
Hediye algılanmazsa Ayarlar > "Ham sağlayıcı mesajlarını göster"i aç ve gelen mesajı bana gönder.

Kısa linkler (vm.tiktok.com) çözülemez; yayının tam linkini (`https://www.tiktok.com/@kullanici/live`) veya sadece
`@kullanici` yaz.

## Kurulum

### 1) Android APK (GitHub Actions ile, bilgisayara kurulum gerekmez)

1. Bu klasörü bir GitHub deposuna yükle (`.github/workflows/build-apk.yml` dosyası dahil).
2. Depoda **Actions > APK derle > Run workflow** (ya da `main`'e push) çalıştır.
3. İş bitince **OlmeSayaci-apk** çıktısını indir, içindeki `app-debug.apk` dosyasını telefona kur
   ("bilinmeyen kaynaklardan yükleme" iznini ver).

### 2) Android Studio ile

`android/` klasörünü Android Studio'da aç (Gradle 8.9 / JDK 17), **Build > Build APK(s)**.
`android/app/src/main/assets/index.html`, `app/index.html` dosyasının kopyasıdır; arayüzü değiştirirsen ikisini eşitle.

### 3) Derlemeden, tarayıcıdan uygulama olarak (PWA)

`app/` klasörünü bir https adresinde yayınla (GitHub Pages, kendi hostin vb.), telefonda Chrome ile aç,
menüden **Ana ekrana ekle / Uygulamayı yükle**. Çevrimdışı da açılır.

## Kullanım ipuçları

- Android, arka plandaki uygulamaları kısıtlayabilir. Sayaç **ekran açıkken** en güvenilir çalışır
  (APK sürümü ön plandayken ekranı kapatmaz). Yayını telefondan yapıyorsan sayacı ikinci bir cihazda aç
  veya uygulamayı bölünmüş ekranda/yüzen pencerede tut.
- Hediye adı eşleşmiyorsa Ayarlar > "Görülen hediyeler" listesindeki yazımı kurala aynen yaz
  (büyük/küçük harf fark etmez). Hediye ID'si de yazılabilir.
- Sayaç görünümünü OBS'e almak istersen söyle, ayrı bir yayın ekranı ekleriz.

## Testler

`test/` klasöründe Playwright ile yazılmış testler var (sahte bir yayın bağlantısıyla): link ayrıştırma, seri
sayımı, sayaç ve koruma mantığı, farklı sağlayıcı mesaj biçimleri, kalıcılık, otomatik bağlanma/yeniden bağlanma,
ayarlar, PWA/çevrimdışı. Çalıştırmak için `app/` klasörünü `python3 -m http.server 8099` ile sun, sonra
`python3 test/test_app.py` ve `python3 test/test_pwa.py` (gerekli: `pip install playwright`, `playwright install chromium`).
