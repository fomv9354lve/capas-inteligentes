/* lang.js — toggle ES/EN PERSISTENTE en todo el ecosistema KRENIQ.
   Persistencia entre los 3 sitios vía cookie a nivel de dominio padre `.krenniq.com`
   (la comparten krenniq.com + capas.krenniq.com + atlas.krenniq.com). localStorage como
   respaldo por-origen. Traducción por atributo: cada elemento traducible lleva
   data-en="<HTML en inglés>"; el español es su contenido original. Cero dependencias. */
(function () {
  var DEFAULT = 'en';  // inglés de entrada en todo el ecosistema (la cookie compartida lo cambia y persiste)
  function getCookie(n) {
    var m = document.cookie.match('(^|;)\\s*' + n + '\\s*=\\s*([^;]+)');
    return m ? decodeURIComponent(m.pop()) : '';
  }
  function curLang() {
    var c = getCookie('kq_lang');
    if (c) return c;
    try { return localStorage.getItem('kq_lang') || DEFAULT; } catch (e) { return DEFAULT; }
  }
  function setLang(l) {
    // cookie en el dominio padre -> persiste entre apex y subdominios
    document.cookie = 'kq_lang=' + l + ';domain=.krenniq.com;path=/;max-age=31536000;SameSite=Lax';
    document.cookie = 'kq_lang=' + l + ';path=/;max-age=31536000;SameSite=Lax'; // fallback host-only (FQDN azure)
    try { localStorage.setItem('kq_lang', l); } catch (e) {}
    apply(l);
  }
  function apply(l) {
    document.documentElement.lang = l;
    // Simétrico: cada elemento traducible lleva data-en y/o data-es. El contenido tal como se
    // escribió se guarda en data-base; si falta la traducción del idioma pedido, cae a data-base.
    // Así sirve igual para el landing (base ES + data-en) y CAPAS (base EN + data-es).
    document.querySelectorAll('[data-en],[data-es]').forEach(function (el) {
      if (!el.hasAttribute('data-base')) el.setAttribute('data-base', el.innerHTML);
      var t = el.getAttribute('data-' + l);
      el.innerHTML = (t !== null) ? t : el.getAttribute('data-base');
    });
    document.querySelectorAll('[data-en-attr]').forEach(function (el) {
      // formato: "attr|english"  (p.ej. placeholder|Search…)
      var spec = el.getAttribute('data-en-attr'), i = spec.indexOf('|');
      var attr = spec.slice(0, i), en = spec.slice(i + 1), keyEs = 'data-es-' + attr;
      if (!el.hasAttribute(keyEs)) el.setAttribute(keyEs, el.getAttribute(attr) || '');
      el.setAttribute(attr, (l === 'en') ? en : el.getAttribute(keyEs));
    });
    document.querySelectorAll('[data-lang-btn]').forEach(function (b) {
      b.textContent = (l === 'en') ? 'ES' : 'EN';
      b.setAttribute('aria-label', (l === 'en') ? 'Cambiar a español' : 'Switch to English');
    });
  }
  window.KQLang = {
    cur: curLang, set: setLang,
    toggle: function () { setLang(curLang() === 'en' ? 'es' : 'en'); },
    apply: function () { apply(curLang()); }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { apply(curLang()); });
  else apply(curLang());
})();
