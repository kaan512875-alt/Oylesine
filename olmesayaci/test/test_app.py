import json
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8099/index.html"
ok = bad = 0
def check(name, cond, extra=""):
    global ok, bad
    if cond: ok += 1; print("  OK   ", name)
    else: bad += 1; print("  HATA ", name, extra)
def gift(user, name, count, ended, gtype=1, gid=0, shape="data", img=None):
    d = {"user": {"uniqueId": user, "nickname": user.upper()}, "giftName": name, "giftId": gid, "repeatCount": count,
         "repeatEnd": 1 if ended else 0, "giftType": gtype, "diamondCount": 1}
    if img: d["giftDetails"] = {"giftImage": {"giftPictureUrl": img}}
    if shape == "data": return json.dumps({"event": "gift", "data": d})
    if shape == "messages": return json.dumps({"messages": [{"type": "WebcastChatMessage", "data": {"comment": "selam"}}, {"type": "WebcastGiftMessage", "data": d}]})
    return json.dumps({"type": "gift", "user": d["user"], "gift": {"name": name, "diamondCount": 1, "repeatCount": count}})

errors = []; urls = []; socks = []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    pg.on("console", lambda m: errors.append("console." + m.type + ": " + m.text) if m.type == "error" else None)
    def ws_handler(ws):
        urls.append(ws.url); socks.append(ws)
    pg.route_web_socket("wss://ws.eulerstream.com/**", ws_handler)
    pg.route("https://cdn.example/**", lambda r: r.fulfill(status=200, content_type="image/png", body=open("../app/icon-192.png", "rb").read()))
    pg.goto(BASE); pg.wait_for_timeout(500)
    txt = lambda sel: pg.inner_text(sel).strip()

    print("[baslangic]")
    check("sayac 0 ve ÖLME", txt("#num") == "0" and txt("#lab") == "ÖLME")

    print("[link ayristirma]")
    pg.fill("#link", ""); pg.click("#go")
    check("bos link uyari verir", "yaz" in txt("#ctxt") and not socks)
    pg.fill("#link", "https://vm.tiktok.com/ZMabcdef/"); pg.click("#go")
    check("kisa link reddedilir", "Kısa link" in txt("#ctxt") and not socks)
    pg.fill("#link", "https://www.tiktok.com/@deneme.hesap/live?enter_from=x"); pg.click("#go"); pg.wait_for_timeout(600)
    check("tam link baglanir", len(socks) == 1 and "uniqueId=deneme.hesap" in urls[0], urls)
    check("api anahtari yoksa parametre dusurulur", "apiKey" not in urls[0], urls[0])
    check("durum: bagli", "Bağlı · @deneme.hesap" in txt("#stxt") and txt("#go") == "Durdur")

    print("[sayac mantigi]")
    ws = socks[0]
    for r in (1, 2, 3): ws.send(gift("ali", "Rose", r, False))          # seri: 1,2,3
    ws.send(gift("ali", "Rose", 3, True))                                 # seri kapanisi (tekrar sayilmamali)
    pg.wait_for_timeout(400)
    check("gul serisi 1,2,3 -> +3 (cift sayim yok)", txt("#num") == "3" and txt("#lab") == "ÖLME", txt("#num"))
    check("durum sinifi pos", "pos" in pg.get_attribute("#counter", "class"))
    ws.send(gift("veli", "TikTok", 1, True, gtype=2, shape="messages"))   # messages dizisi + sohbet mesaji
    ws.send(gift("veli", "TikTok", 1, True, gtype=2, shape="gift"))       # farkli bicim, art arda ayni hediye
    pg.wait_for_timeout(400)
    check("2 TikTok hediyesi -> -2 (3-2=1)", txt("#num") == "1" and txt("#lab") == "ÖLME", txt("#num"))
    ws.send(gift("ayse", "TikTok", 1, True, gtype=2)); pg.wait_for_timeout(300)
    check("0'a iniyor", txt("#num") == "0" and "zero" in pg.get_attribute("#counter", "class"))
    ws.send(gift("ayse", "TikTok", 2, True, gtype=2)); pg.wait_for_timeout(300)
    check("-2 -> '2 KORUMA' yazar", txt("#num") == "2" and txt("#lab") == "KORUMA" and "neg" in pg.get_attribute("#counter", "class"), (txt("#num"), txt("#lab")))
    check("alt satir: olme 0 · koruma 2", "ölme 0" in txt("#sub") and "koruma 2" in txt("#sub"), txt("#sub"))
    ws.send(gift("can", "Rose", 1, True, gtype=2)); pg.wait_for_timeout(300)
    check("koruma varken gul gelirse koruma azalir (-2+1=-1)", txt("#num") == "1" and txt("#lab") == "KORUMA")
    ws.send(gift("zeynep", "Heart Me", 4, True, gtype=2)); pg.wait_for_timeout(300)
    check("kurali olmayan hediye sayilmaz", txt("#num") == "1" and "sayılmadı" in txt("#feed"))
    ws.send(gift("img", "Rose", 1, True, gtype=2, img="https://cdn.example/rose.png")); pg.wait_for_timeout(500)
    check("hediye resmi gosterilir", pg.locator("#feed .thumb img").count() >= 1)
    ws.send("bozuk json {{{"); ws.send(json.dumps({"type": "chat", "comment": "x"})); pg.wait_for_timeout(200)
    check("bozuk/ilgisiz mesajlar yok sayilir", txt("#num") == "0")   # -1 +1 = 0

    print("[elle kontroller]")
    pg.click("#inc"); pg.click("#inc"); pg.click("#dec"); pg.wait_for_timeout(200)
    check("+1 +1 -1 -> 1", txt("#num") == "1")
    pg.click("#undo"); pg.wait_for_timeout(200)
    check("geri al (son -1 geri alinir: 0 -> 1 -> 2)", txt("#num") == "2", txt("#num"))
    pg.click("#reset"); pg.wait_for_timeout(200); pg.click(".dlg .btn.stop"); pg.wait_for_timeout(200)
    check("sifirla (onay penceresiyle)", txt("#num") == "0" and "zero" in pg.get_attribute("#counter", "class"))

    print("[kalicilik]")
    ws.send(gift("k1", "Rose", 5, True, gtype=2)); pg.wait_for_timeout(300)   # gtype=2: seri degil, tek olay x5
    check("seri olmayan x5 gul -> +5", txt("#num") == "5", txt("#num"))
    pg.screenshot(path="shot_main.png")
    pg.reload(); pg.wait_for_timeout(600)
    check("yenileyince sayac korunur", txt("#num") == "5" and "deneme.hesap" in pg.input_value("#link"))
    check("yenileyince gecmis korunur", pg.locator("#feed .ev").count() >= 5)
    check("yenileyince son bagliysa otomatik baglanir", len(socks) == 2 and "Bağlı · @deneme.hesap" in txt("#stxt"), (len(socks), txt("#stxt")))

    print("[ayarlar]")
    pg.click("#btn-set"); pg.wait_for_timeout(400)
    check("ayar sayfasi acildi", pg.is_visible(".sheet"))
    pg.screenshot(path="shot_settings.png")
    rules = pg.locator(".rule")
    check("varsayilan 2 kural", rules.count() == 2)
    pg.click("text=+ Kural ekle")
    last = pg.locator(".rule").last
    last.locator("input").first.fill("Heart Me"); last.locator("input").nth(1).fill("2")
    pg.click(".sheet >> text=Gül gönder"); pg.wait_for_timeout(200)
    pg.click(".sheet >> text=TikTok ×3"); pg.wait_for_timeout(200)
    pg.click(".sheet .x >> nth=-1") if False else None
    pg.go_back(); pg.wait_for_timeout(400)          # geri tusu ayar sayfasini kapatir
    check("geri tusu ayarlari kapatir", not pg.is_visible(".sheet"))
    check("test butonlari sayaci degistirdi (5+1-3=3)", txt("#num") == "3", txt("#num"))
    ws2 = socks[-1]
    ws2.send(gift("yeni", "Heart Me", 1, True, gtype=2)); pg.wait_for_timeout(300)
    check("yeni eklenen kural calisti (+2)", txt("#num") == "5", txt("#num"))
    pg.reload(); pg.wait_for_timeout(600)
    pg.click("#btn-set"); pg.wait_for_timeout(300)
    check("kurallar kalici", pg.locator(".rule").count() == 3 and pg.locator(".rule").nth(2).locator("input").first.input_value() == "Heart Me")
    pg.go_back(); pg.wait_for_timeout(300)

    print("[yeniden baglanma]")
    n0 = len(socks)
    check("reload sonrasi otomatik baglandi", "Bağlı" in txt("#stxt"))
    socks[-1].close(); pg.wait_for_timeout(600)
    check("kopunca 'Yeniden deneniyor'", "Yeniden" in txt("#stxt"), txt("#stxt"))
    pg.wait_for_timeout(2600)
    check("otomatik yeniden baglandi", len(socks) == n0 + 1 and "Bağlı" in txt("#stxt"), (len(socks), txt("#stxt")))
    pg.click("#go"); pg.wait_for_timeout(400)
    check("Durdur -> bagli degil", txt("#stxt") == "Bağlı değil" and txt("#go") == "Bağlan")
    pg.wait_for_timeout(3000)
    check("durdurunca yeniden baglanmaz", len(socks) == n0 + 1)
    pg.reload(); pg.wait_for_timeout(600)
    check("Durdur dediysen yeniden aciliste baglanmaz", len(socks) == n0 + 1 and txt("#stxt") == "Bağlı değil")

    print("[api anahtari]")
    pg.click("#btn-set"); pg.wait_for_timeout(300)
    pg.locator(".sheet input[type=password]").fill("ANAHTAR123")
    pg.go_back(); pg.wait_for_timeout(300)
    pg.click("#go"); pg.wait_for_timeout(600)
    check("anahtar URL'ye eklenir", "apiKey=ANAHTAR123" in urls[-1], urls[-1])
    pg.click("#go")
    pg.screenshot(path="shot_after.png")
    check("tarayici hatasi yok", not errors, errors)
    b.close()
print("\nSONUC: %d basarili, %d hatali" % (ok, bad))
