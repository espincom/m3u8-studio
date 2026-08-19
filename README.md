***Türkçe** · [English](README.en.md)*

# M3U8 Studio

<img width="1062" height="792" alt="Ekran Alıntısı" src="https://github.com/user-attachments/assets/7755a192-70a6-45c0-a1b5-a6bac5dd972b" />


HLS (`.m3u8`) yayınlarını en yüksek kalitede indiren, PyQt6 ile yazılmış masaüstü uygulaması.

Bir video linkini yapıştırıyorsunuz, program playlist'i çözümleyip segmentleri paralel indiriyor,
tek dosyada birleştiriyor ve isterseniz ffmpeg ile MP4'e dönüştürüyor.

**Öne çıkanlar**

- Master playlist içindeki **en yüksek kaliteyi otomatik seçer** (çözünürlük + bitrate)
- **Pano izleyici** — tarayıcıdan bir `.m3u8` linki kopyaladığınızda bildirim çıkar,
  "Hemen İndir" veya "Kuyruğa Ekle" diyebilirsiniz
- **Kuyruk sistemi** ve **toplu link ekleme**, eş zamanlı indirme
- **AES-128 şifreli** yayınları çözer, fMP4 ve byte-range destekler
- İndirme sırasında videodan **canlı önizleme görseli** çıkarır
- Yarım kalan indirmeyi **kaldığı yerden devam ettirir** (segment önbelleği)
- **İki dil**: İngilizce / Türkçe, anında geçiş
- Ses efektleri, animasyonlu koyu tema

---

## 1. Gereksinimler

| Gereksinim | Sürüm | Not |
|---|---|---|
| İşletim sistemi | Windows 10 / 11 | Linux ve macOS'ta da çalışır |
| Python | 3.9 veya üzeri | 3.11 ile geliştirildi ve test edildi |
| PyQt6 | 6.5+ | Arayüz ve ses/video motoru (QtMultimedia birlikte gelir) |
| requests | 2.28+ | HTTP indirme |
| pycryptodome | 3.17+ | AES-128 şifreli yayınların çözülmesi |
| imageio-ffmpeg | 0.4.9+ | ffmpeg ikilisini getirir (MP4 dönüşümü için, isteğe bağlı) |

Ayrıca ~2 GB boş disk alanı yeterlidir; indirilen videolar geçici olarak segment segment
saklandığı için **indireceğiniz videonun iki katı kadar** geçici alan gerekebilir.

---

## 2. Python kurulumu (ilk kez kuranlar için)

Bilgisayarınızda Python yoksa:

1. <https://www.python.org/downloads/> adresinden Windows sürümünü indirin.
2. Kurulum ekranında **"Add python.exe to PATH"** kutusunu mutlaka işaretleyin.
   Bu kutu işaretlenmezse aşağıdaki komutlar çalışmaz.
3. Kurulum bitince yeni bir komut istemi (PowerShell veya CMD) açıp doğrulayın:

```bash
python --version
```

`Python 3.11.x` gibi bir çıktı görmelisiniz.

**Linux:** Python çoğu dağıtımda kuruludur. Değilse `sudo apt install python3 python3-pip`
(Debian/Ubuntu) veya dağıtımınızın paket yöneticisini kullanın. Komutlarda `python` yerine
`python3`, `pip` yerine `pip3` yazmanız gerekebilir.

**macOS:** `brew install python` ya da python.org'daki macOS yükleyicisi.

---

## 3. Programı kurma

Komut istemini açıp sırasıyla:

```bash
git clone https://github.com/espincom/m3u8-studio.git
```

```bash
cd m3u8_studio
```

```bash
pip install -r requirements.txt
```

Git kullanmıyorsanız GitHub'daki yeşil **Code → Download ZIP** düğmesiyle indirip bir klasöre
çıkarabilir, komut isteminde o klasöre girip yalnızca `pip install` komutunu çalıştırabilirsiniz.

Linux ve macOS'ta `pip` yerine `pip3` gerekebilir.

Bağımlılıkları tek tek kurmak isterseniz:

```bash
pip install PyQt6 requests pycryptodome imageio-ffmpeg
```

---

## 4. Çalıştırma

```bash
python m3u8_downloader.py
```

Program açılışta **İngilizce** gelir. Sağ üstteki 🇹🇷 bayrağına tıklayarak Türkçeye
geçebilirsiniz; seçiminiz kaydedilir, sonraki açılışta Türkçe gelir.

---

## 5. Kullanım

### Link ekleme

1. Videonun `.m3u8` linkini kopyalayın (tarayıcıda F12 → Network sekmesi → `.m3u8` araması).
2. Programdaki kutuya yapıştırın.
3. **Hemen İndir** anında başlatır, **Kuyruğa Ekle** sıraya alır (satırdaki ⬇ ile başlatılır).

**Pano izleyici** açıksa 2. adımı atlayabilirsiniz: linki kopyaladığınız anda sağ altta
bildirim çıkar ve oradan seçim yaparsınız.

**Toplu Ekle** ile birden fazla linki alt alta yapıştırabilirsiniz. İsim vermek isterseniz:

```
https://site.com/video1/master.m3u8
https://site.com/video2/index.m3u8 | 2-bolum.mp4
```

### Ayarlar

| Ayar | Ne işe yarar |
|---|---|
| **Kayıt klasörü** | Videoların indirileceği yer. Kalıcı olarak kaydedilir. |
| **Referer** | Sunucu 403 dönerse: videonun oynatıldığı sayfanın adresi. Origin başlığı bundan türetilir. |
| **Cookie** | Giriş gerektiren sitelerde tarayıcıdan kopyaladığınız Cookie başlığı. |
| **Segment bağlantısı** | Aynı anda kaç segment indirileceği (varsayılan 8). Sunucu hız sınırı uygularsa 3–4'e düşürün. |
| **Eş zamanlı video** | Aynı anda kaç videonun indirileceği (varsayılan 2). |
| **Eklenince otomatik başlat** | Kuyruğa eklenen her link hemen indirilmeye başlar. |
| **ffmpeg ile MP4'e dönüştür** | Kapalıysa dosya ham `.ts` olarak kaydedilir. |

---

## 6. ffmpeg hakkında

ffmpeg **zorunlu değildir**. Olmadan da her şey çalışır, sadece çıktı `.ts` uzantılı olur
(VLC, MPC-HC gibi oynatıcılar sorunsuz açar).

ffmpeg varsa iki şey kazanırsınız: çıktı gerçek `.mp4` olur ve önizleme görselleri daha
isabetli çıkarılır.

En kolay kurulum yolu `requirements.txt` içinde zaten var:

```bash
pip install imageio-ffmpeg
```

Program ffmpeg'i şu sırayla arar:

1. Ayarlarda elle seçtiğiniz yol
2. Sistem `PATH`'i
3. `imageio-ffmpeg` paketinin getirdiği ikili
4. Program klasöründeki `ffmpeg` / `ffmpeg.exe` (veya `ffmpeg/bin/` altındaki)

Bulunamazsa ayarlar panelindeki **ffmpeg…** düğmesi kurulum yardımı gösterir; oradan
"Yeniden Ara" veya "Dosya Seç" diyebilirsiniz.

---

## 7. Dosyaların yeri

| Ne | Nerede |
|---|---|
| İndirilen videolar | Seçtiğiniz kayıt klasörü |
| Tanılama günlüğü | Program klasöründe `m3u8_studio.log` |
| Segment önbelleği | Sistemin geçici klasöründe `m3u8studio_cache` (Windows: `%TEMP%`, Linux/macOS: `/tmp`) — başarılı indirmede silinir, 3 günden eskiler otomatik temizlenir |
| Ayarlar | Windows: `HKEY_CURRENT_USER\Software\m3u8studio` · Linux: `~/.config/m3u8studio` · macOS: `~/Library/Preferences` |

Yarım kalan bir indirmeyi tekrar eklerseniz, önbellekte duran segmentler yeniden
indirilmez; kaldığı yerden devam eder. Link imzalı olup değişse bile eşleşme sağlanır.

Satırdaki **Klasörde göster** düğmesi her üç işletim sisteminde de çalışır: Windows'ta
Gezgin, macOS'ta Finder dosyayı seçili olarak açar. Linux'ta önce standart dosya yöneticisi
arayüzü (`org.freedesktop.FileManager1`) denenir, olmazsa Nautilus, Dolphin, Nemo, Caja,
Thunar veya PCManFM aranır; hiçbiri yoksa dosyanın bulunduğu klasör açılır.

---

## 8. Sorun giderme

**403 Forbidden alıyorum**
Ayarlardaki **Referer** alanına videonun oynatıldığı sayfanın adresini yazın. Gerekirse
tarayıcıdan Cookie başlığını da kopyalayın.

**İndirme yavaşladı ya da durdu**
Satırdaki metne bakın. Anlık hız düşüp *"yeniden deneme"* sayısı artıyorsa sunucu sizi
kısıtlıyordur — **Segment bağlantısı** değerini 3–4'e, **Eş zamanlı video**'yu 1'e çekin.
Yalnızca ortalama hız düşüyor ve anlık hız sabitse sorun yoktur.

**"%73 indirildi" gibi eksik bir dosya oluştu**
O videonun bazı segmentleri kaynak sunucuda erişilemiyor. Program, tüm denemeler
tükendiğinde inen kısmı çöpe atmak yerine `video (eksik %73).mp4` adıyla kaydeder.
Linki tarayıcıdan yenileyip tekrar eklerseniz kaldığı yerden devam eder.

**Dosya `.mp4` yerine `.ts` çıktı**
ffmpeg bulunamamış ya da dönüşüm başarısız olmuş demektir. Bkz. 6. bölüm.

**Ses gelmiyor**
`m3u8_studio` klasöründeki dört mp3 dosyasının (`Pop_app.mp3`, `Download.mp3`,
`Downloaded.mp3`, `Error.mp3`) yerinde olduğundan emin olun.

**Program hiç açılmıyor**
Komut isteminden çalıştırıp hata mesajını okuyun; `m3u8_studio.log` dosyasında da
yakalanmamış hatalar tam ayrıntısıyla kayıtlıdır.

---

## 9. Proje yapısı

```
m3u8_studio/
├── m3u8_downloader.py      Başlatıcı
├── requirements.txt
└── m3u8_studio/
    ├── app.py              Uygulama girişi
    ├── config.py           Ayarlar, günlük, ffmpeg bulma
    ├── theme.py            Renkler ve stil sayfası
    ├── i18n.py             Çeviri sözlüğü (EN / TR)
    ├── hls.py              M3U8 ayrıştırma
    ├── downloader.py       İndirme motoru (turlu yeniden deneme, soğuma)
    ├── cache.py            Segment önbelleği
    ├── thumbnail.py        Önizleme karesi çıkarma
    ├── widgets.py          Özel çizilen arayüz bileşenleri
    ├── dialogs.py          Toplu ekleme, pano bildirimi
    ├── about.py            Geliştirici sayfası
    ├── models.py           Görev modeli
    ├── mainwindow.py       Ana pencere
    ├── sounds.py           Ses efektleri
    └── *.mp3               Ses dosyaları
```

---

## 10. Sorumluluk

Bu araç, erişim hakkına sahip olduğunuz içerikleri indirmeniz için yapılmıştır. Telif hakkıyla
korunan materyalin izinsiz indirilmesi ve dağıtılması bulunduğunuz ülkenin yasalarına aykırı
olabilir. Sorumluluk kullanıcıya aittir.

---

## İletişim

Hata ve geri bildirimler için mail yoluyla iletişime geçebilirsiniz.

**By espin0**
Gmail: kayhankafali@gmail.com
GitHub: <https://github.com/espincom>
