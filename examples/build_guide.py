"""Build static offline HTML from reviewed bilingual guide content and UI captures."""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.version import VERSION
GUIDE = ROOT / 'docs' / 'guide'
ORDER = ['start', 'overview', 'menus', 'import', 'table', 'panels', 'layers', 'text', 'settings-axes', 'settings-appearance', 'settings-legend', 'settings-styles', 'settings-canvas', 'fit', 'data-operations', 'symbols', 'save-export', 'troubleshooting']
IMAGES = {
    'overview': ['overview'], 'menus': ['menus-file', 'menus-view', 'menus-plot', 'menus-language'],
    'import': ['import'], 'table': ['table', 'table-roles', 'table-context'],
    'panels': ['panels'], 'layers': ['layers'], 'text': ['text'],
    'settings-axes': ['settings-axes', 'notation-options'],
    'settings-appearance': ['settings-appearance'],
    'settings-legend': ['settings-legend', 'legend-options'],
    'settings-styles': ['settings-styles', 'settings-styles-global', 'settings-styles-histogram', 'settings-styles-bar'], 'settings-canvas': ['settings-canvas'],
    'fit': ['fit', 'report'], 'data-operations': ['data-operations'], 'symbols': ['symbols'],
}
CAPTIONS = {
    'overview': ('Numaralı arayüz haritası', 'Numbered interface map'),
    'menus-file': ('Dosya menüsü', 'File menu'), 'menus-view': ('Görünüm menüsü', 'View menu'),
    'menus-plot': ('Grafik menüsü', 'Plot menu'), 'menus-language': ('Dil menüsü', 'Language menu'),
    'panels': ('Paneller ve yerleşim seçimi', 'Panels and layout selection'),
    'layers': ('Katman Yönetimi ve çizim türü', 'Layer Management and plot type'),
    'text': ('Metin Yönetimi: seçili örnek yazısı ve Sil düğmesi', 'Text Management: selected example annotation and Delete'),
    'table': ('Veri Tablosu ve sütun rolleri', 'Data Table and column roles'),
    'table-roles': ('Sütun başlığının sağ tık menüsü', 'Column-header context menu'),
    'table-context': ('Seçili hücrenin sağ tık menüsü', 'Selected-cell context menu'),
    'symbols': ('Ω ile açılan gerçek sembol paleti', 'Actual symbol palette opened with Ω'),
    'report': ('Sentetik Gauss örneğinin analiz raporu', 'Analysis report for the synthetic Gaussian example'),
    'settings-axes': ('Grafik Ayarları → Eksenler', 'Plot Settings → Axes'),
    'settings-appearance': ('Grafik Ayarları → Genel Görünüm', 'Plot Settings → Appearance'),
    'settings-legend': ('Grafik Ayarları → Lejant', 'Plot Settings → Legend'),
    'settings-styles': ('Grafik Ayarları → Stiller; seçili veri serisi', 'Plot Settings → Styles; selected data series'),
    'settings-styles-global': ('Stiller: Global Mod', 'Styles: Global Mode'),
    'settings-styles-histogram': ('Stiller: histogram', 'Styles: histogram'),
    'settings-styles-bar': ('Stiller: bar', 'Styles: bar'),
    'settings-canvas': ('Grafik Ayarları → Kanvas Ayarları', 'Plot Settings → Canvas Settings'),
    'notation-options': ('Eksen sayı gösterimi seçenekleri', 'Axis number-notation options'),
    'legend-options': ('Lejant yerleşim seçenekleri', 'Legend layout options'),
    'fit': ('Başlangıç parametreleri ve ağırlıksız fit açıklaması', 'Initial parameters and unweighted-fit notice'),
    'import': ('Sentetik CSV dosyası için içe aktarma önizlemesi', 'Import preview for the synthetic CSV file'),
    'data-operations': ('Veri İşlemleri: kaynak, işlem ve çıktı seçimi', 'Data Operations: source, operation, and output selection'),
}


def escape(value):
    return html.escape(str(value), quote=True)


def build():
    sections = {}
    for filename in ('essentials.json', 'workflows.json', 'settings.json'):
        for section in json.loads((GUIDE / filename).read_text(encoding='utf-8')):
            if section['id'] in sections:
                raise ValueError(f'Duplicate section: {section["id"]}')
            sections[section['id']] = section
    assert set(sections) == set(ORDER)
    manifest = json.loads((GUIDE / 'assets' / 'manifest.json').read_text(encoding='utf-8'))
    for language in ('tr', 'en'):
        def tr(a, b):
            return a if language == 'tr' else b

        def localized(value):
            return escape(value[language])

        def figure(name):
            info = manifest[name][language]
            assert (GUIDE / info['src']).is_file()
            caption = CAPTIONS[name][0 if language == 'tr' else 1]
            enlarge = tr('Görseli büyüt', 'Enlarge image')
            pins = ''.join(f'<a class="pin" href="#{p["target"]}" style="left:{p["x"]:.3f}%;top:{p["y"]:.3f}%" aria-label="{p["number"]}: {localized(sections[p["target"]]["title"])}">{p["number"]}</a>' for p in info.get('pins', []))
            return f'<figure><div class="image-wrap"><button class="image-button" aria-label="{enlarge}: {escape(caption)}"><img src="{info["src"]}" width="{info["width"]}" height="{info["height"]}" alt="{escape(caption)}" loading="lazy"></button>{pins}</div><figcaption>{escape(caption)} · {enlarge}</figcaption></figure>'

        nav = ''.join(f'<a href="#{key}"><span class="nav-num">{i:02}</span>{localized(sections[key]["title"])}</a>' for i, key in enumerate(ORDER, 1))
        articles = []
        for i, key in enumerate(ORDER, 1):
            s = sections[key]
            out = [f'<article class="section" id="{key}"><div class="section-head"><span class="section-number">{i:02}</span><h2>{localized(s["title"])}</h2></div><p class="intro">{localized(s["intro"])}</p>']
            images = IMAGES.get(key, [])
            if images:
                cls = 'gallery single' if key == 'overview' else 'gallery'
                out.append(f'<div class="{cls}">' + ''.join(figure(name) for name in images) + '</div>')
            for block_index, block in enumerate(s['blocks']):
                out.append(f'<details id="{key}-detail-{block_index + 1}" open><summary>{localized(block["heading"])}</summary><div class="block-body">')
                if block.get('text'):
                    out.append(f'<p>{localized(block["text"])}</p>')
                if block.get('rows'):
                    out.append('<table><tbody>')
                    for row in block['rows']:
                        out.append(f'<tr><th scope="row">{localized(row["label"])}</th><td>{localized(row["description"])}</td></tr>')
                    out.append('</tbody></table>')
                if block.get('steps'):
                    out.append('<ol>' + ''.join(f'<li>{escape(step)}</li>' for step in block['steps'][language]) + '</ol>')
                out.append('</div></details>')
            out.append('</article>')
            articles.append(''.join(out))
        title = tr('Kullanım kılavuzu', 'User guide')
        other = 'en.html' if language == 'tr' else 'index.html'
        page = f'''<!doctype html>
<html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="NumeriPlot {VERSION}: {title}"><title>NumeriPlot · {title}</title><link rel="stylesheet" href="guide.css"><script src="guide.js" defer></script></head>
<body><a class="skip" href="#content">{tr('İçeriğe geç', 'Skip to content')}</a>
<aside class="sidebar" id="contents"><a class="brand" href="#start">NumeriPlot<span class="brand-dot">.</span></a><p class="edition">{VERSION} · {tr('Kullanım kılavuzu','Field guide')}</p><nav aria-label="{tr('İçindekiler','Contents')}">{nav}</nav><p class="side-foot">{tr('Gerçek arayüz. Sentetik veri. Çevrim dışı erişim.','Real interface. Synthetic data. Offline access.')}<br>Public Beta · {tr('Proje şeması','Project schema')} 1.0</p></aside>
<header class="topbar"><button class="mobile-menu" aria-controls="contents" aria-expanded="false">☰ <span class="sr">{tr('İçindekiler','Contents')}</span></button><div class="search-wrap"><label for="search">{tr('Kılavuzda ara','Search guide')}</label><input id="search" type="search" placeholder="{tr('Örn. metin sil, lejant, R²…','Try delete text, legend, R²…')}" autocomplete="off"></div><button class="expand" aria-expanded="true">{tr('Bölümleri daralt','Collapse sections')}</button><button class="print">{tr('Yazdır','Print')}</button><a class="language" data-page="{other}" href="{other}" hreflang="{tr('en','tr')}">{tr('English','Türkçe')}</a></header>
<main id="content"><div class="hero"><span class="eyebrow">{tr('Öğrenciler ve araştırmacılar için','For students and researchers')}</span><h1>{tr('Veriyi görün.<br>İşlemi anlayın.','See the data.<br>Understand the steps.')}</h1><p>{tr('İlk grafikten ayrıntılı eksen ayarlarına: NumeriPlot’u gerçek ekranlar, açıklamalı seçenekler ve uygulanabilir örneklerle keşfedin.','From your first plot to detailed axis settings: explore NumeriPlot through real screens, explained controls, and practical examples.')}</p><span class="pill">18 {tr('bölüm','sections')}</span><span class="pill">{len(manifest)} × 2 {tr('arayüz görüntüsü','UI captures')}</span><span class="pill">TR / EN</span><div class="quicklinks"><a href="../../docs/SOURCE_INSTALL{tr('_TR','')}.md">{tr('Kurulum','Installation')} ↗</a><a href="#start">{tr('İlk grafiğimi oluştur','Create my first plot')} ↗</a><a href="#text">{tr('Grafikteki yazıyı kaldır','Remove plot text')} ↗</a><a href="#settings-axes">{tr('Grafik ayarlarını öğren','Explore plot settings')} ↗</a></div></div>
<section class="first-install" aria-labelledby="install-title"><h2 id="install-title">{tr('İlk kez mi kullanıyorsunuz?', 'First time here?')}</h2><p>{tr('Kod yazmanız veya uygulamayı derlemeniz gerekmez. Mac’te üç adımda başlayın:', 'No coding or application build is required. Start on Mac in three steps:')}</p><ol><li>{tr('Kaynak kodu indirin ve ZIP’i açın.', 'Download the source code and extract the ZIP.')}</li><li>{tr('Kurulum kılavuzundaki bir defalık Python ve bağımlılık kurulumunu tamamlayın.', 'Follow the installation guide for the one-time Python and dependency setup.')}</li><li>{tr('Sonraki açılışlarda Finder’da NumeriPlot.command dosyasına çift tıklayın.', 'On later launches, double-click NumeriPlot.command in Finder.')}</li></ol><p><a href="../../docs/SOURCE_INSTALL{tr('_TR','')}.md"><strong>{tr('Mac’te kur ve kullan →', 'Install and use on Mac →')}</strong></a></p></section>
<noscript><p class="note">{tr('Tüm içerik JavaScript olmadan okunabilir. Arama ve görsel büyütme için JavaScript gerekir.','All content is readable without JavaScript. Search and image enlargement require JavaScript.')}</p></noscript><p class="status" id="status" role="status" aria-live="polite"></p><p id="empty" class="empty" hidden>{tr('Eşleşme bulunamadı. Daha kısa bir sözcük deneyin veya aramayı temizleyin.','No match. Try a shorter term or clear the search.')}</p>
{''.join(articles)}
<footer><p>NumeriPlot {VERSION} · Public Beta · {tr('Bağımsız akademik proje. Kurumsal destek veya bilimsel doğrulama iddiası değildir.','Independent academic project. No institutional endorsement or scientific validation is implied.')}</p><p><a href="../../README{tr('_TR','')}.md">README</a><a href="../../SUPPORT{tr('_TR','')}.md">{tr('Destek','Support')}</a><a href="../../SECURITY.md">{tr('Güvenlik','Security')}</a><a href="https://github.com/alptekin-yildiz/NumeriPlot">GitHub ↗</a></p></footer></main>
<dialog id="viewer" aria-labelledby="viewer-title"><div class="viewer-bar"><span id="viewer-title"></span><a id="full-image" target="_blank" rel="noopener">{tr('Tam boyut','Full size')}</a><button id="close-viewer">{tr('Kapat','Close')} ×</button></div><img id="viewer-image" alt=""></dialog></body></html>'''
        (GUIDE / ('index.html' if language == 'tr' else 'en.html')).write_text(page + '\n', encoding='utf-8')
    print(f'Built {len(sections)} sections in Turkish and English.')


if __name__ == '__main__':
    build()
