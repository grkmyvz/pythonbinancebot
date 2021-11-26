# pythonbinancebot

Merhaba arkadaşlar, binance botu yazmamın amacı kendimi pythonda geliştirmek içindi. Botu bir süre kullandım fakat pek bir kazanç göremedim. İyi bir trader olmadığım için hangi değerleri kontrol etmem gerekiyor pek bilemediğim için kazandığımda oldu kaybettiğimde. Kendinizde deneyerek ve değerleri değiştirerek bekli kazanç sağlayabilirsiniz.

Çalışma Prensibi

Bot sadece RSI (14) değeri ile işleme giriyor veya çıkıyor. Kodu ilk çalıştırdığınızda api bağlantısını yapıp veritabanı yoksa veritabanını oluşturuyor. Bu veri tabanı telegrambot kullanmanız için ve geriye dönük yapılan işlemleri görmeniz için. Eğer programı durdurup tekrar çalıştırırsanız herhangi bir sorunla karşılaşmazsınız çünkü eğer veritabanı bulunuyorsa tekrar oluşturmaya çalışmaz. Devamında cüzdanınızda hangi coin olduğunu sorguluyor. Kodu çalıştırmadan önce tüm varlığınızı USDT veya "pairs" kısmına yazdığınız herhangi bir coine çevirmenizi tavsiye ederim. Çünkü bot tüm işlemleri sadece sizin belirttiğiniz pairlerde yapacaktır. Bot çalıştığında cüzdanınız sorguladığında eğer USDT varsa belirttiğiniz pairlerde en iyi sinyali bekliyor. Bu en iyi rsi sinyali 26 ve daha az ise o coini alıyor. Aldıktan bir süre sonra eğer rsi 68 den yukarı ise veya coin yüzde 2 kazanç sağladıysa coini satıyor ve tekrar en iyi sinyali beklemeye başlıyor. Kodları inceleyerek daha fazla bilgiye sahip olabilirsiniz.

Bot Ayarları

Bot kodunda "# SETTINGS" alanının içerisindeki "api_key" ve "api_secret" değişkenleri binance üzerinden alacağınız api kodları kısmıdır. "pairs" değişkeni içerisindeki dizide al sat yapmasını istediğiniz coinleri yazarak botu çalışır hale getirebilirsiniz.

winRateCalculation() = Kazanç yüzdesi process = float(lastPrice) * 2 / 100 (bu değeri değiştirip yüzde 3 - 4 - 5 yapabilirsiniz)
loseRateCalculation() = Kayıp yüzdesi process = float(lastPrice) * 2 / 100 (bu değeri değiştirip yüzde 3 - 4 - 5 yapabilirsiniz)

Telegram bot ayarı

Telegram kodunda "# SETTINGS" alanın içerisindeki "token" değişkenine telegram üzerinden aldığınız apiyi kullanın.
