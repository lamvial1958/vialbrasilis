# -*- coding: utf-8 -*-
"""Gera as paginas estaticas do site (IT na raiz, /en/, /pt/, /privacy/, /cookie/)
a partir de src/template.html. Uso: python tools/build.py
Os arquivos gerados sao versionados porque o GitHub Pages serve o repositorio como esta."""
import os, re
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://vialbrasilis.it'
LASTMOD = '2026-11-12'
LANGS = ['it', 'en', 'pt']
PATH = {'it': '/', 'en': '/en/', 'pt': '/pt/'}
HTMLLANG = {'it': 'it', 'en': 'en', 'pt': 'pt-BR'}
OGLOCALE = {'it': 'it_IT', 'en': 'en_GB', 'pt': 'pt_BR'}

META = {
    'it': ('VIAL Brasilis — Traduzione, Interpretariato e Formazione Linguistica PT·IT·EN',
           'Servizi linguistici B2B trilingui PT↔IT↔EN per aziende italiane che operano nei mercati lusofoni e anglofoni: traduzione, interpretariato fieristico e formazione linguistica aziendale.'),
    'en': ('VIAL Brasilis — Translation, Interpretation and Language Training PT·IT·EN',
           'Trilingual B2B language services PT↔IT↔EN for Italian companies operating in Lusophone and Anglophone markets: translation, trade fair interpretation and corporate language training.'),
    'pt': ('VIAL Brasilis — Tradução, Interpretação e Formação Linguística PT·IT·EN',
           'Serviços linguísticos B2B trilíngues PT↔IT↔EN para empresas italianas que atuam nos mercados lusófonos e anglófonos: tradução, interpretação em feiras e formação linguística empresarial.'),
}
I18N = {
    'nav_services': {'it': 'Servizi', 'en': 'Services', 'pt': 'Serviços'},
    'nav_pricing': {'it': 'Tariffe', 'en': 'Pricing', 'pt': 'Tarifas'},
    'nav_about': {'it': 'Chi siamo', 'en': 'About', 'pt': 'Sobre'},
    'nav_contact': {'it': 'Contatti', 'en': 'Contact', 'pt': 'Contatos'},
    'cta_quote': {'it': 'Richiedi un preventivo', 'en': 'Request a quote', 'pt': 'Solicitar orçamento'},
    'cta_services': {'it': 'Scopri i servizi', 'en': 'Our services', 'pt': 'Nossos serviços'},
    'stat_years': {'it': 'ANNI DI ESPERIENZA', 'en': 'YEARS OF EXPERIENCE', 'pt': 'ANOS DE EXPERIÊNCIA'},
    'stat_langs': {'it': 'LINGUE OPERATIVE', 'en': 'OPERATIVE LANGUAGES', 'pt': 'LÍNGUAS OPERACIONAIS'},
    'stat_pairs': {'it': 'COPPIE LINGUISTICHE', 'en': 'LANGUAGE PAIRS', 'pt': 'PARES LINGUÍSTICOS'},
    'services_eyebrow': {'it': 'I nostri servizi', 'en': 'Our services', 'pt': 'Nossos serviços'},
    'pricing_eyebrow': {'it': 'Tariffe', 'en': 'Pricing', 'pt': 'Tarifas'},
    'contact_eyebrow': {'it': 'Contatti', 'en': 'Contact', 'pt': 'Contatos'},
}
SELECT = {
    'it': ['Seleziona un servizio', 'Traduzione non giurata', 'Interpretariato fieristico', 'Corso di portoghese', 'Corso di inglese', 'Supporto export', 'Altro'],
    'en': ['Select a service', 'Non-sworn Translation', 'Trade Fair Interpretation', 'Portuguese Course', 'English Course', 'Export Support', 'Other'],
    'pt': ['Selecione um serviço', 'Tradução não juramentada', 'Interpretação em feiras', 'Curso de português', 'Curso de inglês', 'Suporte à exportação', 'Outro'],
}
SELECT_VALS = ['', 'traduzione', 'interpretariato', 'corso_pt', 'corso_en', 'export', 'altro']
UI = {
    'it': dict(
        skip='Vai al contenuto',
        consent='Ho letto l\'<a href="/privacy/">Informativa Privacy</a> e acconsento al trattamento dei miei dati per rispondere alla richiesta. *',
        oktitle='Quasi fatto: controllate la vostra e-mail',
        oktext='Il vostro programma di posta si apre con la richiesta già compilata: premete «Invia» per completare. Se non si apre, scrivete direttamente a <a href="mailto:vial@vialbrasilis.it">vial@vialbrasilis.it</a>. Risponderemo entro 24 ore lavorative.',
        fields='Compilare tutti i campi obbligatori e accettare l\'informativa.',
        subj='Richiesta da vialbrasilis.it - ',
        labels=('Nome', 'Azienda', 'Email', 'Telefono', 'Servizio', 'Messaggio'),
        piva='P.IVA in fase di attivazione', privacy='Privacy', cookie='Cookie'),
    'en': dict(
        skip='Skip to content',
        consent='I have read the <a href="/privacy/">Privacy Notice</a> (in Italian) and consent to the processing of my data to answer this request. *',
        oktitle='Almost done: check your e-mail',
        oktext='Your e-mail program opens with the request already filled in: press “Send” to complete it. If it does not open, write directly to <a href="mailto:vial@vialbrasilis.it">vial@vialbrasilis.it</a>. We will reply within 24 business hours.',
        fields='Please fill in all required fields and accept the privacy notice.',
        subj='Request from vialbrasilis.it - ',
        labels=('Name', 'Company', 'Email', 'Phone', 'Service', 'Message'),
        piva='VAT no. pending activation', privacy='Privacy', cookie='Cookies'),
    'pt': dict(
        skip='Ir para o conteúdo',
        consent='Li a <a href="/privacy/">Informativa de Privacidade</a> (em italiano) e concordo com o tratamento dos meus dados para responder a este pedido. *',
        oktitle='Quase pronto: confira o seu e-mail',
        oktext='O seu programa de e-mail deve abrir com o pedido já preenchido: clique em «Enviar» para concluir. Se não abrir, escreva diretamente para <a href="mailto:vial@vialbrasilis.it">vial@vialbrasilis.it</a>. Responderemos em até 24 horas úteis.',
        fields='Preencha todos os campos obrigatórios e aceite a informativa de privacidade.',
        subj='Pedido de vialbrasilis.it - ',
        labels=('Nome', 'Empresa', 'E-mail', 'Telefone', 'Serviço', 'Mensagem'),
        piva='P.IVA em fase de ativação', privacy='Privacidade', cookie='Cookies'),
}


def head(lang):
    t, d = META[lang]
    url = BASE + PATH[lang]
    alt = ''.join('<link rel="alternate" hreflang="%s" href="%s%s">\n' % (HTMLLANG[l], BASE, PATH[l]) for l in LANGS)
    alt += '<link rel="alternate" hreflang="x-default" href="%s/">\n' % BASE
    og = ''.join('<meta property="og:locale:alternate" content="%s">\n' % OGLOCALE[l] for l in LANGS if l != lang)
    return (
        '<title>%s</title>\n<meta name="description" content="%s">\n'
        '<link rel="canonical" href="%s">\n%s'
        '<meta property="og:type" content="website">\n<meta property="og:site_name" content="VIAL Brasilis">\n'
        '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n'
        '<meta property="og:url" content="%s">\n<meta property="og:locale" content="%s">\n%s'
        '<meta property="og:image" content="%s/img/logo.png">\n<meta name="twitter:card" content="summary">\n'
        '<link rel="icon" type="image/png" href="/img/logo.png">'
    ) % (t, d, url, alt, t, d, url, OGLOCALE[lang], og, BASE)


NAVBRASIL = {
    'it': '<a href="/brasile/">Brasile</a>',
    'pt': '<a href="/pt/brasil/">Brasil</a>',
}
BRASIL_PATH = {'it': '/brasile/', 'pt': '/pt/brasil/'}
BRASIL_META = {
    'it': ('Italia e Brasile — Supporto linguistico e commerciale | VIAL Brasilis',
           "Supporto linguistico e commerciale per le aziende italiane che esportano in Brasile e per le imprese brasiliane che importano dall'Italia: traduzione, interpretariato e affiancamento nelle trattative."),
    'pt': ('Itália e Brasil — Apoio linguístico e comercial | VIAL Brasilis',
           'Apoio linguístico e comercial a empresas italianas que exportam para o Brasil e a empresas brasileiras que importam da Itália: tradução, interpretação e acompanhamento de negociações.'),
}


def switch(lang, paths=None):
    paths = paths or PATH
    out = []
    for l in LANGS:
        cls = 'lang-btn active' if l == lang else 'lang-btn'
        cur = ' aria-current="true"' if l == lang else ''
        out.append('<a class="%s" href="%s" hreflang="%s" lang="%s"%s>%s</a>' % (cls, paths[l], HTMLLANG[l], HTMLLANG[l], cur, l.upper()))
    return ''.join(out)


def footer(lang):
    u = UI[lang]
    return '''<footer>
  <div class="container">
    <div class="footer-inner">
      <div>&copy; 2026 <strong>VIAL Brasilis</strong> &middot; Luiz Antonio M. Vial &middot; %s &middot; Arsiero (VI), Italia</div>
      <div class="footer-links">
        <a href="mailto:vial@vialbrasilis.it">vial@vialbrasilis.it</a>
        <a href="tel:+393274341567">+39 327 4341567</a>
        <a href="mailto:machado.vial@pec.it" class="footer-pec">PEC: machado.vial@pec.it</a>
        <a href="https://www.linkedin.com/in/luiz-antonio-machado-vial-876a73278/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
        <a href="/privacy/">%s</a>
        <a href="/cookie/">%s</a>
      </div>
    </div>
  </div>
</footer>''' % (u['piva'], u['privacy'], u['cookie'])


SCRIPT = '''<script>
(function () {
  var L = [__LABELS__], MSG = '__MSG__', SUBJ = '__SUBJ__';
  window.addEventListener('scroll', function () {
    document.querySelector('nav').style.boxShadow = window.scrollY > 20 ? '0 2px 20px rgba(0,0,0,0.3)' : 'none';
  });
  var btn = document.getElementById('btnSubmit');
  if (!btn) return;
  btn.addEventListener('click', function () {
    var ids = ['nome', 'email', 'servizio', 'messaggio', 'consenso'];
    for (var i = 0; i < ids.length; i++) {
      var el = document.getElementById(ids[i]);
      var ok = el.type === 'checkbox' ? el.checked : el.value.trim() !== '';
      if (ids[i] === 'email' && ok) ok = el.checkValidity();
      if (!ok) { el.setCustomValidity(MSG); el.reportValidity(); el.setCustomValidity(''); el.focus(); return; }
    }
    function v(id) { return document.getElementById(id).value.trim() || '-'; }
    var body = L[0] + ': ' + v('nome') + '\\n' + L[1] + ': ' + v('azienda') + '\\n' + L[2] + ': ' + v('email') + '\\n' +
      L[3] + ': ' + v('telefono') + '\\n' + L[4] + ': ' + v('servizio') + '\\n\\n' + L[5] + ':\\n' + v('messaggio');
    window.location.href = 'mailto:vial@vialbrasilis.it?subject=' + encodeURIComponent(SUBJ + v('servizio')) + '&body=' + encodeURIComponent(body);
    document.getElementById('formSuccess').style.display = 'block';
  });
})();
</script>'''


def script(lang):
    u = UI[lang]
    return (SCRIPT.replace('__LABELS__', ','.join("'%s'" % x for x in u['labels']))
            .replace('__MSG__', u['fields'].replace("'", "\\'"))
            .replace('__SUBJ__', u['subj']))


def build_home(lang, tpl):
    u = UI[lang]
    soup = BeautifulSoup(tpl, 'html.parser')
    for el in soup.select('[data-lang]'):
        langs = el['data-lang'].replace('active', '').split()
        if lang not in langs:
            el.decompose()
        else:
            del el['data-lang']
    for el in soup.select('[data-i18n]'):
        el.string = I18N[el['data-i18n']][lang]
        del el['data-i18n']
    sel = soup.find('select', id='servizio')
    for val, txt in zip(SELECT_VALS, SELECT[lang]):
        o = soup.new_tag('option', value=val)
        o.string = txt
        sel.append(o)
    for lab in soup.select('.form-group label'):
        nxt = lab.find_next_sibling(['input', 'select', 'textarea'])
        if nxt is not None and nxt.get('id'):
            lab['for'] = nxt['id']
    html = str(soup)
    html = (html.replace('{{HTMLLANG}}', HTMLLANG[lang]).replace('{{HEAD}}', head(lang))
            .replace('{{SKIP}}', u['skip']).replace('{{LANGSWITCH}}', switch(lang))
            .replace('{{CONSENT}}', u['consent']).replace('{{OKTITLE}}', u['oktitle'])
            .replace('{{OKTEXT}}', u['oktext']).replace('{{FOOTER}}', footer(lang))
            .replace('{{SCRIPT}}', script(lang))
            .replace('{{NAVBRASIL}}', NAVBRASIL.get(lang, '')))
    assert '{{' not in html, re.findall(r'\{\{\w+\}\}', html)
    return html


BRASIL_TPL = '''<!DOCTYPE html>
<html lang="%(hl)s">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(t)s</title>
<meta name="description" content="%(d)s">
<link rel="canonical" href="%(url)s">
%(alt)s<meta property="og:type" content="website">
<meta property="og:site_name" content="VIAL Brasilis">
<meta property="og:title" content="%(t)s">
<meta property="og:description" content="%(d)s">
<meta property="og:url" content="%(url)s">
<meta property="og:locale" content="%(og)s">
<meta property="og:image" content="%(base)s/img/logo.png">
<link rel="icon" type="image/png" href="/img/logo.png">
<link rel="stylesheet" href="/css/style.css">
</head>
<body class="legal">
<a class="skip-link" href="#main">%(skip)s</a>
<nav>
  <a class="nav-brand" href="%(home)s"><img class="nav-logo" src="/img/logo.png" alt="VIAL Brasilis"><span class="nav-name">VIAL Brasilis</span></a>
  <div class="nav-links">
    <a href="%(home)s">&larr; Home</a>
    <div class="lang-switcher" role="group" aria-label="Lingua / Language / Idioma">%(sw)s</div>
  </div>
</nav>
<main id="main" class="legal-main"><div class="container legal-container">
%(body)s
</div></main>
%(footer)s
</body>
</html>
'''


def brasil_page(lang):
    t, d = BRASIL_META[lang]
    url = BASE + BRASIL_PATH[lang]
    body = open(os.path.join(ROOT, 'src', 'brasil.%s.body.html' % lang), encoding='utf-8').read()
    alt = ''.join('<link rel="alternate" hreflang="%s" href="%s%s">\n' % (HTMLLANG[l], BASE, BRASIL_PATH[l]) for l in BRASIL_PATH)
    alt += '<link rel="alternate" hreflang="x-default" href="%s%s">\n' % (BASE, BRASIL_PATH['it'])
    sw_paths = {'it': BRASIL_PATH['it'], 'en': PATH['en'], 'pt': BRASIL_PATH['pt']}
    return BRASIL_TPL % dict(hl=HTMLLANG[lang], t=t, d=d, url=url, alt=alt, og=OGLOCALE[lang], base=BASE,
                             skip=UI[lang]['skip'], home=PATH[lang], sw=switch(lang, sw_paths), body=body,
                             footer=footer(lang))


def write(rel, content):
    path = os.path.join(ROOT, rel.lstrip('/'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


def legal_page(title, desc, path, body):
    return '''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(title)s — VIAL Brasilis</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(base)s%(path)s">
<link rel="icon" type="image/png" href="/img/logo.png">
<link rel="stylesheet" href="/css/style.css">
</head>
<body class="legal">
<nav>
  <a class="nav-brand" href="/"><img class="nav-logo" src="/img/logo.png" alt="VIAL Brasilis"><span class="nav-name">VIAL Brasilis</span></a>
  <div class="nav-links"><a href="/">&larr; Home</a></div>
</nav>
<main id="main" class="legal-main"><div class="container legal-container">
%(body)s
</div></main>
%(footer)s
</body>
</html>
''' % dict(title=title, desc=desc, base=BASE, path=path, body=body, footer=footer('it'))


LEGAL = {
    'privacy': ('Informativa Privacy', 'Informativa sul trattamento dei dati personali ai sensi degli artt. 13-14 del Regolamento (UE) 2016/679 (GDPR).'),
    'cookie': ('Cookie Policy', "Informazioni sull'uso di cookie e tecnologie analoghe sul sito vialbrasilis.it."),
}


def main():
    tpl = open(os.path.join(ROOT, 'src', 'template.html'), encoding='utf-8').read()
    for lang in LANGS:
        write(PATH[lang] + 'index.html', build_home(lang, tpl))
    for lang in BRASIL_PATH:
        write(BRASIL_PATH[lang] + 'index.html', brasil_page(lang))
    for page, (title, desc) in LEGAL.items():
        src = open(os.path.join(ROOT, 'src', page + '.body.html'), encoding='utf-8').read()
        write('/%s/index.html' % page, legal_page(title, desc, '/%s/' % page, src))
    alts = ''.join('    <xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>\n' % (HTMLLANG[l], BASE, PATH[l]) for l in LANGS)
    alts += '    <xhtml:link rel="alternate" hreflang="x-default" href="%s/"/>\n' % BASE
    urls = ''
    for l in LANGS:
        urls += '  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n%s  </url>\n' % (BASE, PATH[l], LASTMOD, alts)
    balts = ''.join('    <xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>\n' % (HTMLLANG[l], BASE, BRASIL_PATH[l]) for l in BRASIL_PATH)
    balts += '    <xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>\n' % (BASE, BRASIL_PATH['it'])
    for l in BRASIL_PATH:
        urls += '  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n%s  </url>\n' % (BASE, BRASIL_PATH[l], LASTMOD, balts)
    for p in LEGAL:
        urls += '  <url>\n    <loc>%s/%s/</loc>\n    <lastmod>%s</lastmod>\n  </url>\n' % (BASE, p, LASTMOD)
    write('/sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + '</urlset>\n')
    write('/robots.txt', 'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % BASE)


if __name__ == '__main__':
    main()
