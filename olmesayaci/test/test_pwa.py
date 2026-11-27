from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8099/index.html"
ok = bad = 0
def check(name, cond, extra=""):
    global ok, bad
    if cond: ok += 1; print("  OK   ", name)
    else: bad += 1; print("  HATA ", name, extra)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page()
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE); pg.wait_for_timeout(800)
    mf = pg.evaluate("fetch('manifest.webmanifest').then(r=>r.json())")
    check("manifest okunuyor", mf["short_name"] == "Ölme Sayacı" and mf["display"] == "standalone")
    for ic in mf["icons"]:
        r = pg.evaluate("(u)=>fetch(u).then(r=>r.status)", ic["src"]); check("simge " + ic["src"], r == 200)
    sw = pg.evaluate("navigator.serviceWorker.ready.then(r=>!!r.active)")
    check("service worker etkin", sw is True)
    pg.reload(); pg.wait_for_timeout(500)
    ctx.set_offline(True)
    pg.reload(); pg.wait_for_timeout(800)
    check("cevrimdisi acilir", pg.inner_text("#num").strip() == "0" and "Ölme Sayacı" in pg.inner_text(".brand"))
    check("hata yok", not errs, errs)
    # sifirlama etiketi
    ctx.set_offline(False); pg.reload(); pg.wait_for_timeout(400)
    pg.click("#inc"); pg.click("#reset"); pg.wait_for_timeout(200); pg.click(".dlg .btn.stop"); pg.wait_for_timeout(200)
    check("sifirlama olayi 'sıfırlandı' yazar", "sıfırlandı" in pg.inner_text("#feed"))
    b.close()
print("SONUC: %d basarili, %d hatali" % (ok, bad))
