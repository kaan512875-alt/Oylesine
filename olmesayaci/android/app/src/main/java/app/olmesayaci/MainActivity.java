package app.olmesayaci;

import android.app.Activity;
import android.os.Bundle;
import android.view.WindowManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.webkit.WebViewAssetLoader;

/**
 * Ölme Sayacı: web uygulamasını (assets/index.html) tam ekran bir WebView içinde çalıştırır.
 * Sayaç ve ayarlar WebView'in localStorage'ında saklanır.
 */
public class MainActivity extends Activity {

    private static final String START_URL = "https://appassets.androidplatform.net/assets/index.html";

    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Sayaç ekranı yayın sırasında kararmasın
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        web = new WebView(this);
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setMediaPlaybackRequiresUserGesture(false);

        // Sayfa https://appassets.androidplatform.net altından sunulur (WebSocket ve localStorage için güvenli kaynak)
        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return loader.shouldInterceptRequest(request.getUrl());
            }
        });

        // Sayaç ve ayarlar localStorage'da saklandığı için sayfa her açılışta baştan yüklenebilir
        web.loadUrl(START_URL);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) web.onResume();
    }

    @Override
    public void onBackPressed() {
        // Ayarlar penceresi açıksa web uygulaması kapatır; değilse uygulamayı arka plana al
        if (web != null && web.canGoBack()) {
            web.goBack();
        } else {
            moveTaskToBack(true);
        }
    }

    @Override
    protected void onDestroy() {
        if (web != null) {
            web.destroy();
            web = null;
        }
        super.onDestroy();
    }
}
