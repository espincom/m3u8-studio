LANG = "en"


STRINGS = {
    "app_title":        ("M3U8 Studio - Video Downloader", "M3U8 Studio - Video İndirici"),
    "tagline":          ("Download HLS streams at the highest quality",
                         "HLS akışlarını en yüksek kalitede indirin"),
    "tab_downloader":   ("M3U8", "M3U8"),
    "tab_about":        ("Developer", "Geliştirici"),
    "clip_watch":       ("Clipboard watcher", "Pano izleyici"),
    "clip_watch_tip":   ("Shows a notification when you copy an .m3u8 link from your browser.",
                         "Tarayıcıdan bir .m3u8 linki kopyaladığınızda bildirim gösterir."),
    "lang_tip_en":      ("Switch to English", "İngilizceye geç"),
    "lang_tip_tr":      ("Türkçeye geç", "Türkçeye geç"),

    "url_placeholder":  ("Paste an M3U8 link and press Enter...",
                         "M3U8 linkini yapıştırın ve Enter'a basın..."),
    "add_queue":        ("Add to Queue", "Kuyruğa Ekle"),
    "download_now":     ("Download Now", "Hemen İndir"),
    "bulk_add":         ("Bulk Add", "Toplu Ekle"),
    "save_folder":      ("Save folder:", "Kayıt klasörü:"),
    "browse":           ("Browse", "Gözat"),

    "referer":          ("Referer:", "Referer:"),
    "referer_ph":       ("On 403 errors: the address of the video page",
                         "403 hatasında: video sayfasının adresi"),
    "cookie":           ("Cookie:", "Cookie:"),
    "cookie_ph":        ("Cookie header, if required", "Gerekirse Cookie başlığı"),
    "seg_conn":         ("Segment connections:", "Segment bağlantısı:"),
    "parallel_video":   ("Parallel videos:", "Eş zamanlı video:"),
    "autostart":        ("Start automatically when added", "Eklenince otomatik başlat"),
    "remux":            ("Convert to MP4 with ffmpeg", "ffmpeg ile MP4'e dönüştür"),
    "ffmpeg_found":     ("ffmpeg: %s", "ffmpeg: %s"),
    "ffmpeg_missing":   ("ffmpeg not found - saving as .ts",
                         "ffmpeg bulunamadı - .ts kaydedilir"),
    "ffmpeg_btn_tip":   ("Choose ffmpeg.exe or see installation help",
                         "ffmpeg.exe yolunu seç veya kurulum yardımını gör"),

    "queue_title":      ("Download Queue", "İndirme Kuyruğu"),
    "download_all":     ("Download All", "Tümünü İndir"),
    "clear_done":       ("Clear Completed", "Tamamlananları Temizle"),
    "clear_all":        ("Empty List", "Listeyi Boşalt"),
    "queue_empty":      ("The queue is empty.\nPaste an M3U8 link or copy one from your browser.",
                         "Kuyruk boş.\nBir M3U8 linki yapıştırın veya tarayıcıdan kopyalayın."),

    "tip_start":        ("Download", "İndir"),
    "tip_stop":         ("Stop", "Durdur"),
    "tip_open":         ("Show in folder", "Klasörde göster"),
    "tip_remove":       ("Remove from list", "Listeden kaldır"),

    "st_queued":        ("Waiting in queue", "Sırada bekliyor"),
    "st_starting":      ("Starting...", "Başlatılıyor..."),
    "st_reading":       ("Reading playlist", "Playlist okunuyor"),
    "st_downloading":   ("Downloading", "İndiriliyor"),
    "st_retrying_n":    ("Downloading (retrying %d segments)",
                         "İndiriliyor (%d segment yeniden deneniyor)"),
    "st_waiting_n":     ("Waiting for %d segments (%.0f s)",
                         "%d segment için bekleniyor (%.0f sn)"),
    "st_no_response":   ("Server not responding - waiting %.0f s",
                         "Sunucu yanıt vermiyor - %.0f sn bekleniyor"),
    "st_merging":       ("Merging", "Birleştiriliyor"),
    "st_converting":    ("Converting to MP4", "MP4'e dönüştürülüyor"),
    "st_stopping":      ("Stopping...", "Durduruluyor..."),
    "st_stopped":       ("Stopped", "Durduruldu"),
    "st_error":         ("Error: %s", "Hata: %s"),

    "pr_line":          ("%d/%d segments - %.0f%% - %.1f MB - %.1f MB/s (avg %.1f)",
                         "%d/%d segment - %%%.0f - %.1f MB - %.1f MB/s (ort %.1f)"),
    "pr_stuck":         (" - %d segments stuck, retrying",
                         " - %d segment takıldı, yeniden deneniyor"),
    "pr_retries":       (" - %d retries", " - %d yeniden deneme"),
    "pr_skipped":       (" - %d skipped", " - %d atlandı"),
    "pr_last":          (" - final segments", " - son segmentler"),
    "done_line":        ("Completed - %.1f MB - %s", "Tamamlandı - %.1f MB - %s"),
    "done_missing":     ("Completed with gaps - %d segments skipped - %.1f MB - %s",
                         "Eksik tamamlandı - %d segment atlandı - %.1f MB - %s"),
    "done_partial":     ("PARTIAL %d%% - %.1f MB - %s - re-add to resume",
                         "EKSİK %%%d indirildi - %.1f MB - %s - tekrar eklerseniz devam eder"),

    "ready":            ("Ready", "Hazır"),
    "footer_stats":     ("%d downloading - %d queued - %d completed - %d failed",
                         "%d indiriliyor - %d sırada - %d tamamlandı - %d hatalı"),

    "bulk_title":       ("Bulk Add Links", "Toplu Link Ekle"),
    "bulk_info":        ("Paste one M3U8 link per line.\nTo set a name:  <link> | <file name>",
                         "Her satıra bir M3U8 linki yapıştırın.\n"
                         "İsim vermek isterseniz:  <link> | <dosya adı>"),
    "bulk_count":       ("%d valid links", "%d geçerli link"),
    "bulk_ok":          ("Add to Queue", "Kuyruğa Ekle"),
    "bulk_cancel":      ("Cancel", "Vazgeç"),
    "bulk_added":       ("%d links added to the queue (%d skipped)",
                         "%d link kuyruğa eklendi (%d atlandı)"),

    "toast_title":      ("M3U8 link found in clipboard", "Panoda M3U8 linki bulundu"),

    "msg_invalid_title": ("Invalid link", "Geçersiz link"),
    "msg_invalid":      ("Enter a valid http(s) M3U8 link.",
                         "Geçerli bir http(s) M3U8 linki girin."),
    "msg_dup":          ("This link is already in the queue.", "Bu link zaten kuyrukta."),
    "msg_folder_err":   ("Folder error", "Klasör hatası"),
    "msg_clear_title":  ("Empty list", "Listeyi boşalt"),
    "msg_clear_body":   ("Remove all tasks from the list?",
                         "Tüm görevler listeden kaldırılsın mı?"),
    "msg_fail_title":   ("Download failed", "İndirme başarısız"),

    "ff_title":         ("ffmpeg", "ffmpeg"),
    "ff_found_body":    ("ffmpeg found:\n%s", "ffmpeg bulundu:\n%s"),
    "ff_pick_other":    ("Choose Another File", "Başka Dosya Seç"),
    "ff_ok":            ("OK", "Tamam"),
    "ff_setup_title":   ("ffmpeg setup", "ffmpeg kurulumu"),
    "ff_setup_body":    ("ffmpeg was not found. The easiest way is to install it as a "
                         "Python package:\n\n    pip install imageio-ffmpeg\n\n"
                         "That package ships the ffmpeg binary; after installing it just "
                         "press 'Search Again'.\n\nAlternatives:\n"
                         "  winget install Gyan.FFmpeg\n"
                         "  or pick ffmpeg.exe manually.",
                         "ffmpeg bulunamadı. En kolay yol Python paketi olarak kurmaktır:"
                         "\n\n    pip install imageio-ffmpeg\n\n"
                         "Bu paket ffmpeg ikilisini birlikte getirir; kurduktan sonra "
                         "'Yeniden Ara' butonuna basmanız yeterli.\n\nAlternatifler:\n"
                         "  winget install Gyan.FFmpeg\n"
                         "  veya ffmpeg.exe dosyasını elle seçin."),
    "ff_search_again":  ("Search Again", "Yeniden Ara"),
    "ff_pick":          ("Pick File", "Dosya Seç"),
    "ff_close":         ("Close", "Kapat"),
    "ff_dialog_pick":   ("Select ffmpeg.exe", "ffmpeg.exe dosyasını seçin"),
    "ff_set":           ("ffmpeg set: %s", "ffmpeg ayarlandı: %s"),
    "ff_still_missing": ("ffmpeg still not found.", "ffmpeg hâlâ bulunamadı."),
    "ff_now_found":     ("ffmpeg found: %s", "ffmpeg bulundu: %s"),

    "dlg_pick_folder":  ("Select save folder", "Kayıt klasörü seç"),
    "dlg_exists_title": ("File exists", "Dosya var"),
    "dlg_exists_body":  ("%s already exists. Overwrite?", "%s zaten var. Üzerine yazılsın mı?"),

    "w_quality":        ("Auto-selected quality: %s", "Otomatik seçilen kalite: %s"),
    "w_duration":       ("Duration: ~%.1f minutes", "Süre: ~%.1f dakika"),
    "w_segments":       ("%d segments / %d parallel connections",
                         "%d segment / %d paralel bağlantı"),
    "w_resume":         ("Found %d segments from a previous attempt, resuming.",
                         "Önceki denemeden %d segment bulundu, kaldığı yerden devam ediliyor."),
    "w_ratelimit":      ("Server is rate limiting (HTTP %d). Lowering 'Segment connections' "
                         "may help.",
                         "Sunucu hız sınırı uyguluyor (HTTP %d). 'Segment bağlantısı' "
                         "değerini düşürmek işe yarayabilir."),
    "w_retry_wait":     ("%d segments failed; retrying in %.0f seconds.",
                         "%d segment inmedi; %.0f saniye sonra tekrar denenecek."),
    "w_unreachable":    ("%d segments cannot be fetched at all (first index: %d). That part "
                         "is unavailable at the source; retrying will not help.",
                         "%d segment sunucudan hiç alınamıyor (ilk sırası: %d). Bu bölge "
                         "kaynakta erişilemez durumda; yeniden denemek sonuç vermiyor."),
    "w_stalled":        ("No progress for %.0f seconds; the server is not responding. Saving "
                         "what was downloaded - re-add to resume.",
                         "%.0f saniyedir ilerleme yok; sunucu yanıt vermiyor. İnen kısım "
                         "kaydediliyor, tekrar denerseniz kaldığı yerden devam eder."),
    "w_partial_save":   ("Video downloaded %d%%; saving as partial. Re-adding resumes from "
                         "where it stopped.",
                         "Video %%%d oranında indi; eksik olarak kaydediliyor. Sonraki "
                         "denemede kaldığı yerden devam edilir."),
    "w_gaps":           ("WARNING: %d segments are missing; the video may skip briefly there.",
                         "UYARI: %d segment eksik; video o noktalarda kısa atlamalar "
                         "içerebilir."),
    "w_ffmpeg_fail":    ("ffmpeg failed - keeping the raw file.",
                         "ffmpeg başarısız - ham dosya korunuyor."),
    "w_finished":       ("Finished - %.1f MB", "Tamamlandı - %.1f MB"),
    "w_cancelled":      ("Download cancelled.", "İndirme iptal edildi."),
    "e_not_m3u8":       ("Not a valid M3U8 playlist.", "Geçerli bir M3U8 playlist değil."),
    "e_no_variant":     ("No stream found in the master playlist.",
                         "Master playlist içinde akış bulunamadı."),
    "e_no_segment":     ("No segments found in the playlist.",
                         "Playlist içinde segment bulunamadı."),
    "e_too_few":        ("Only %d%% of the segments could be downloaded (%d/%d). Refresh the "
                         "link in your browser and try again. Downloaded segments were kept, "
                         "so a retry resumes where it stopped.",
                         "Segmentlerin yalnızca %%%d'i indirilebildi (%d/%d). Linki "
                         "tarayıcıdan yenileyip tekrar deneyin. İnen segmentler saklandı, "
                         "tekrar denerseniz kaldığı yerden devam eder."),
    "e_encrypted":      ("pycryptodome is required for encrypted streams: "
                         "pip install pycryptodome",
                         "Şifreli yayın için pycryptodome gerekli: pip install pycryptodome"),
    "e_unsupported":    ("Unsupported encryption: %s", "Desteklenmeyen şifreleme: %s"),

    "ab_heading":       ("Developer", "Geliştirici"),
    "ab_message":       ("For bugs and feedback, please get in touch by mail.",
                         "Hata ve geri bildirimler için lütfen mail yoluyla "
                         "iletişime geçiniz."),
    "ab_by":            ("By espin0", "By espin0"),
    "ab_mail_label":    ("Gmail", "Gmail"),
    "ab_github_label":  ("GitHub", "GitHub"),
    "ab_mail_hint":     ("Click to compose an e-mail", "Tıklayınca mail penceresi açılır"),
    "ab_github_hint":   ("Click to open in your browser", "Tıklayınca tarayıcıda açılır"),
    "ab_copied":        ("Copied to clipboard", "Panoya kopyalandı"),
}


def tr(key, *args):
    pair = STRINGS.get(key)
    if pair is None:
        return key
    text = pair[1] if LANG == "tr" else pair[0]
    if args:
        try:
            return text % args
        except (TypeError, ValueError):
            return text
    return text


def set_language(code):
    global LANG
    LANG = "tr" if code == "tr" else "en"


def current_language():
    return LANG
