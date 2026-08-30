"""
python_exporter.py
──────────────────
NumeriPlot — Bağımsız Python Kodu Olarak Dışa Aktarma

Kullanım (MainWindow içinden):
    from python_exporter import export_as_python
    code = export_as_python(canvas, data_manager, fit_list)
    with open("figure.py", "w", encoding="utf-8") as f:
        f.write(code)
"""

from __future__ import annotations
import inspect
import textwrap
import numpy as np
from typing import TYPE_CHECKING

from src.version import APP_NAME

if TYPE_CHECKING:
    from src.plotting.canvas import MplCanvas
    from src.analysis.data_manager import DataManager


# ── Yardımcı: numpy array'i satır satır güzel formatlı string'e çevir ────────

def _array_repr(arr, indent: int = 4) -> str:
    """1-D numpy array'i okunabilir Python listesine dönüştürür."""
    if arr is None or len(arr) == 0:
        return "np.array([])"
    pad = " " * indent
    vals = ", ".join(f"{v:.6g}" for v in arr)
    # Uzun dizileri satırlara böl (80 karakter)
    if len(vals) > 72:
        rows = []
        chunk = []
        line_len = 0
        for v in arr:
            tok = f"{v:.6g}"
            if line_len + len(tok) + 2 > 72:
                rows.append(pad + "    " + ", ".join(chunk) + ",")
                chunk = [tok]
                line_len = len(tok)
            else:
                chunk.append(tok)
                line_len += len(tok) + 2
        if chunk:
            rows.append(pad + "    " + ", ".join(chunk))
        return "np.array([\n" + "\n".join(rows) + "\n" + pad + "])"
    return f"np.array([{vals}])"


def _repr(val) -> str:
    """Python repr — string, sayı, None için."""
    if val is None:
        return "None"
    if isinstance(val, str):
        return repr(val)
    if isinstance(val, float):
        return f"{val:.6g}"
    return repr(val)


# ── Model kaynak kodunu bul ───────────────────────────────────────────────────

def _rename_func_in_source(source: str, old_name: str, new_name: str) -> str:
    """Kaynak koddaki fonksiyon adını yenisiyle değiştirir."""
    import re
    # 'def old_name(' → 'def new_name('
    source = re.sub(rf'\bdef\s+{re.escape(old_name)}\s*\(', f'def {new_name}(', source)
    # Özyinelemeli çağrılar varsa onları da değiştir
    source = re.sub(rf'\b{re.escape(old_name)}\s*\(', f'{new_name}(', source)
    return source


def _to_safe_name(name: str) -> str:
    """Model adını geçerli Python fonksiyon adına dönüştürür (Türkçe dahil)."""
    import unicodedata
    # Unicode normalize et, ardından ASCII'ye çevir
    nfkd = unicodedata.normalize('NFKD', name)
    ascii_name = nfkd.encode('ascii', 'ignore').decode('ascii')
    # Boşluk ve tire → alt çizgi, küçük harf, non-word → kaldır
    import re
    safe = re.sub(r'[\s\-]+', '_', ascii_name.lower())
    safe = re.sub(r'[^\w]', '', safe)
    if safe and safe[0].isdigit():
        safe = 'model_' + safe
    return safe or 'model'


def _fallback_parameter_names(param_names) -> str:
    """Return valid placeholder identifiers for an unavailable model source."""
    count = len(param_names or ())
    return ', '.join(f'p{i + 1}' for i in range(count)) if count else 'a, b'


def _get_model_source(func) -> tuple[str, str] | tuple[None, None]:
    """
    Fit modelinin kaynak kodunu ve gerçek fonksiyon adını döndürür.
    Dönüş: (source_code, function_name) veya (None, None)
    """
    try:
        src = inspect.getsource(func)
        lines = src.splitlines()
        start = next((i for i, l in enumerate(lines) if l.strip().startswith("def ")), 0)
        source = textwrap.dedent("\n".join(lines[start:]))
        # Fonksiyon adını çıkar: "def model(x, K, n):" → "model"
        import re
        m = re.match(r"def\s+(\w+)\s*\(", source)
        func_name = m.group(1) if m else "model"
        return source, func_name
    except (OSError, TypeError):
        return None, None


# ── Ana export fonksiyonu ─────────────────────────────────────────────────────

def export_as_python(
    canvas: "MplCanvas",
    data_manager: "DataManager",
    fit_list: list,
    loaded_models: dict | None = None,
    canvas_config: dict | None = None,
    figure_width_cm: float | None = None,
    figure_height_cm: float | None = None,
) -> str:
    """
    Mevcut grafiği bağımsız çalışan bir Python scripti olarak döndürür.

    Parametreler
    ────────────
    canvas         : MplCanvas nesnesi (panel config ve layout bilgisi için)
    data_manager   : DataManager nesnesi (ham veri için)
    fit_list       : MainWindow.fit_list (fit sonuçları)
    loaded_models  : MainWindow.loaded_models dict'i (model fonksiyonları)
    figure_width_cm, figure_height_cm : Figure boyutu (cm). None ise canvas'tan alınır.
    """

    rows = canvas._layout_rows
    cols = canvas._layout_cols
    n_panels = canvas.panel_count

    # Figure boyutu
    # Boyutu önce canvas_config'den al (en doğru kaynak)
    # Sonra parametre override'ları, son olarak fig.get_size_inches() fallback
    if canvas_config is not None:
        fig_w = canvas_config.get('width_cm', 10.0) / 2.54
        fig_h = canvas_config.get('height_cm', 8.0) / 2.54
    else:
        fig_w, fig_h = canvas.fig.get_size_inches()
    if figure_width_cm is not None:
        fig_w = figure_width_cm / 2.54
    if figure_height_cm is not None:
        fig_h = figure_height_cm / 2.54

    lines: list[str] = []

    # ── BAŞLIK ────────────────────────────────────────────────────────────────
    lines += [
        '"""',
        f'{APP_NAME} — Otomatik Oluşturulmuş Python Grafiği',
        f'Bu dosya {APP_NAME} tarafından dışa aktarılmıştır.',
        'Python >= 3.9 ve şu paketler gereklidir:',
        '    pip install matplotlib numpy scipy pandas',
        '"""',
        '',
        'import numpy as np',
        'import matplotlib.pyplot as plt',
        'import matplotlib.gridspec as gridspec',
    ]

    # Fit varsa scipy import
    if fit_list:
        lines += [
            'from scipy.optimize import curve_fit',
        ]

    lines += ['', '']

    # ── MODEL FONKSİYONLARI ───────────────────────────────────────────────────
    written_models: dict[str, str] = {}  # model_name → real_function_name
    if fit_list and loaded_models:
        lines += [
            '# ════════════════════════════════════════════════════════════════',
            '# Fit Model Fonksiyonları',
            '# ════════════════════════════════════════════════════════════════',
        ]
        for fit in fit_list:
            mn = fit.get('model_name', '')
            if mn in written_models:
                continue
            written_models[mn] = mn  # geçici placeholder
            func = loaded_models.get(mn)
            src, real_fn = _get_model_source(func) if func else (None, None)
            # Unique fonksiyon adı: model adından türet, çakışmayı önle
            unique_fn = _to_safe_name(mn)
            if src:
                # Kaynak koddaki fonksiyon adını unique_fn ile değiştir
                src_renamed = _rename_func_in_source(src, real_fn, unique_fn)
                lines.append(f'# Model: {mn}')
                lines.append(src_renamed)
                lines.append('')
                written_models[mn] = unique_fn
            else:
                pnames = fit.get('param_names', [])
                args = _fallback_parameter_names(pnames)
                lines.append(f'# Model: {mn}  (kaynak bulunamadı — elle düzenleyin)')
                lines.append(f'def {unique_fn}(x, {args}):')
                lines.append(f'    raise NotImplementedError("Model fonksiyonunu buraya yazın")')
                lines.append('')
                written_models[mn] = unique_fn
        lines.append('')

    # ── VERİ ──────────────────────────────────────────────────────────────────
    lines += [
        '# ════════════════════════════════════════════════════════════════',
        '# Veri',
        '# ════════════════════════════════════════════════════════════════',
    ]

    # Her seriyi var_name → series eşlemesiyle listele
    series_varnames: dict[int, str] = {}  # id(series) → varname

    all_series = data_manager.get_all_series()
    for i, s in enumerate(all_series):
        vname = f"s{i+1}"
        series_varnames[id(s)] = vname
        label = s.get('label', f'Seri {i+1}')
        pt    = s.get('plot_type', 'scatter')
        lines.append(f'# Seri {i+1}: {label}  (panel={s.get("panel_id", 0)+1}, tip={pt})')

        x_arr = s.get('x')
        y_arr = s.get('y')
        xe_arr = s.get('x_err')
        ye_arr = s.get('y_err')

        lines.append(f'{vname}_x    = {_array_repr(x_arr)}')
        lines.append(f'{vname}_y    = {_array_repr(y_arr)}')
        if xe_arr is not None and len(xe_arr) > 0:
            lines.append(f'{vname}_xerr = {_array_repr(xe_arr)}')
        else:
            lines.append(f'{vname}_xerr = None')
        if ye_arr is not None and len(ye_arr) > 0:
            lines.append(f'{vname}_yerr = {_array_repr(ye_arr)}')
        else:
            lines.append(f'{vname}_yerr = None')
        lines.append('')

    lines.append('')

    # ── FİGURE & GRIDSPEC ─────────────────────────────────────────────────────
    lines += [
        '# ════════════════════════════════════════════════════════════════',
        '# Figure ve Panel Düzeni',
        '# ════════════════════════════════════════════════════════════════',
        f'fig = plt.figure(figsize=({fig_w:.4f}, {fig_h:.4f}))',
        f'gs  = gridspec.GridSpec({rows}, {cols}, figure=fig)',
        '',
    ]

    # Her panel için ax değişkeni
    for pid in range(n_panels):
        r_ = pid // cols
        c_ = pid % cols
        lines.append(f'ax{pid+1} = fig.add_subplot(gs[{r_}, {c_}])')
    lines.append('')
    lines.append('')

    # ── HER PANEL İÇİN ÇİZİM ─────────────────────────────────────────────────
    lines += [
        '# ════════════════════════════════════════════════════════════════',
        '# Çizim',
        '# ════════════════════════════════════════════════════════════════',
    ]

    for pid in range(n_panels):
        cfg   = canvas.panel_configs[pid]
        pname = canvas.panel_names[pid]
        axvar = f'ax{pid+1}'
        ax2var = f'ax{pid+1}r'

        lines += [
            f'# ── Panel {pid+1}: {pname} ──────────────────────────────────',
        ]

        # Bu panele ait seriler
        panel_series = [s for s in all_series if s.get('panel_id', 0) == pid]
        # Sağ eksen var mı?
        has_right = any(s.get('axis') == 'right' for s in panel_series)

        if has_right:
            lines.append(f'{ax2var} = {axvar}.twinx()')

        for s in panel_series:
            vname = series_varnames[id(s)]
            label = s.get('label', '')
            color = s.get('color', 'black')
            pt    = s.get('plot_type', 'scatter')
            axis  = s.get('axis', 'left')
            target = ax2var if axis == 'right' else axvar

            if pt == 'histogram':
                lines += [
                    f'{target}.hist(',
                    f'    {vname}_y,',
                    f'    bins={_repr(s.get("bins", 20))},',
                    f'    color={_repr(color)},',
                    f'    alpha={_repr(s.get("alpha", 0.7))},',
                    f'    edgecolor={_repr(s.get("edgecolor", "white"))},',
                    f'    label={_repr(label)},',
                    f')',
                ]

            elif pt == 'bar':
                filled     = s.get('bar_filled', True)
                bar_color  = color if filled else 'none'
                bar_edge   = s.get('edgecolor', 'none') if filled else color
                lines += [
                    f'{target}.bar(',
                    f'    {vname}_x, {vname}_y,',
                    f'    width={_repr(s.get("bar_width", 0.8))},',
                    f'    color={_repr(bar_color)},',
                    f'    edgecolor={_repr(bar_edge)},',
                    f'    linewidth={_repr(s.get("bar_edge_width", 1.0))},',
                    f'    alpha={_repr(s.get("alpha", 1.0))},',
                    f'    label={_repr(label)},',
                ]
                ye_arr = s.get('y_err')
                if ye_arr is not None and len(ye_arr) > 0:
                    lines += [
                        f'    yerr={vname}_yerr,',
                        f'    capsize={_repr(s.get("capsize", 2.0))},',
                        f'    error_kw={{"elinewidth": {_repr(s.get("elinewidth", 1.0))}, "capthick": {_repr(s.get("elinewidth", 1.0))}}},',
                    ]
                lines.append(')')

            else:
                # scatter / line / scatter+line
                mk  = s.get('marker', 'o')
                ls  = s.get('linestyle', 'None')
                fc  = color if s.get('filled', True) else 'none'
                mew = s.get('markeredgewidth', 0.5)
                has_xerr = s.get('x_err') is not None and len(s.get('x_err', [])) > 0
                has_yerr = s.get('y_err') is not None and len(s.get('y_err', [])) > 0

                if has_xerr or has_yerr:
                    lines += [
                        f'{target}.errorbar(',
                        f'    {vname}_x, {vname}_y,',
                        f'    xerr={vname}_xerr if {vname}_xerr is not None else None,',
                        f'    yerr={vname}_yerr if {vname}_yerr is not None else None,',
                        f'    fmt={_repr(mk)},',
                        f'    color={_repr(color)},',
                        f'    markerfacecolor={_repr(fc)},',
                        f'    markersize={_repr(s.get("markersize", 5))},',
                        f'    markeredgewidth={_repr(mew)},',
                        f'    linestyle={_repr(ls)},',
                        f'    linewidth={_repr(s.get("linewidth", 1.0))},',
                        f'    capsize={_repr(s.get("capsize", 2.0))},',
                        f'    elinewidth={_repr(s.get("elinewidth", 1.0))},',
                        f'    label={_repr(label)},',
                        f')',
                    ]
                else:
                    lines += [
                        f'{target}.plot(',
                        f'    {vname}_x, {vname}_y,',
                        f'    marker={_repr(mk)},',
                        f'    color={_repr(color)},',
                        f'    markerfacecolor={_repr(fc)},',
                        f'    markersize={_repr(s.get("markersize", 5))},',
                        f'    markeredgewidth={_repr(mew)},',
                        f'    linestyle={_repr(ls)},',
                        f'    linewidth={_repr(s.get("linewidth", 1.0))},',
                        f'    label={_repr(label)},',
                        f')',
                    ]

        # ── Fit çizgileri ─────────────────────────────────────────────────
        panel_fits = [f for f in fit_list if f.get('panel_id', 0) == pid]
        if panel_fits:
            lines.append('')
            lines.append(f'# Fit çizgileri — Panel {pid+1}')

        for fi, fit in enumerate(panel_fits):
            mn     = fit.get('model_name', f'fit{fi+1}')
            pnames = fit.get('param_names', [])
            pvals  = fit.get('param_values', [])
            src_s  = fit.get('source_series', '')
            axis   = fit.get('axis', 'left')
            target = ax2var if axis == 'right' else axvar
            fit_color = fit.get('color', 'red')

            # Parametre değerlerini yorum satırı olarak yaz
            if pnames and pvals:
                param_str = ',  '.join(f'{n} = {v:.6g}' for n, v in zip(pnames, pvals))
                lines.append(f'# {mn}: {param_str}')
                stats = fit.get('res_stats', {})
                r2    = fit.get('r2', None)
                if r2 is not None:
                    lines.append(f'# R² = {r2:.6f},  RMSE = {stats.get("rmse", 0):.6g}')

            # Fit için x aralığı
            fx = fit.get('x')
            fy = fit.get('y')
            fvname = f'fit{pid+1}_{fi+1}'
            lines.append(f'{fvname}_x = {_array_repr(fx)}')

            # Scipy curve_fit ile yeniden fit
            real_fn = written_models.get(mn)  # gerçek fonksiyon adı
            func_exists = real_fn is not None and loaded_models and loaded_models.get(mn)

            if func_exists and pnames and pvals:
                args = ', '.join(pnames)
                p0_str = ', '.join(f'{v:.6g}' for v in pvals)
                lines += [
                    f'# Fit yeniden hesapla ({mn})',
                    f'# Kaynak seri: {src_s}',
                ]
                # Hangi seri bu fit'in kaynağı?
                src_series = next(
                    (s for s in panel_series if s.get('label') == src_s), None
                )
                if src_series:
                    sv = series_varnames[id(src_series)]
                    lines += [
                        f'_popt_{fvname}, _ = curve_fit(',
                        f'    {real_fn}, {sv}_x, {sv}_y,',
                        f'    p0=[{p0_str}],',
                        f'    method="trf", maxfev=5000,',
                        f')',
                        f'{fvname}_y = {real_fn}({fvname}_x, *_popt_{fvname})',
                    ]
                else:
                    # Kaynak seri bulunamadı — mevcut y değerlerini göm
                    lines.append(f'{fvname}_y = {_array_repr(fy)}')
            else:
                # Model kaynağı yoksa hesaplanmış y'yi doğrudan göm
                lines.append(f'{fvname}_y = {_array_repr(fy)}')

            lines += [
                f'{target}.plot(',
                f'    {fvname}_x, {fvname}_y,',
                f'    linestyle={_repr(fit.get("linestyle", "-"))},',
                f'    linewidth={_repr(fit.get("linewidth", 1.0))},',
                f'    color={_repr(fit_color)},',
                f'    label={_repr(fit.get("label", mn))},',
                f')',
                '',
            ]

        # ── Panel eksen ayarları ───────────────────────────────────────────
        lines.append('')
        lines.append(f'# Panel {pid+1} eksen ayarları')

        font_family = cfg.get('fontfamily', 'Times New Roman')
        size_label  = cfg.get('size_label', 10)
        size_title  = cfg.get('size_title', 12)
        size_tick   = cfg.get('size_tick', 10)

        # Etiketler
        xlabel = cfg.get('xlabel', '')
        ylabel = cfg.get('ylabel', '')
        title  = cfg.get('title', '')
        if xlabel:
            lines.append(f'{axvar}.set_xlabel({_repr(xlabel)}, fontsize={size_label}, labelpad={_repr(cfg.get("xlabel_pad", 2.0))})')
        if ylabel:
            lines.append(f'{axvar}.set_ylabel({_repr(ylabel)}, fontsize={size_label}, labelpad={_repr(cfg.get("ylabel_pad", 2.0))})')
        if title:
            lines.append(f'{axvar}.set_title({_repr(title)}, fontsize={size_title}, pad={_repr(cfg.get("title_pad", 6.0))})')

        # Sağ eksen etiketi
        if has_right:
            yr_label = cfg.get('ylabel_right', '')
            if yr_label:
                lines.append(f'{ax2var}.set_ylabel({_repr(yr_label)}, fontsize={size_label})')

        # X/Y sınırları
        if not cfg.get('x_auto', True):
            lines.append(f'{axvar}.set_xlim({_repr(cfg["x_min"])}, {_repr(cfg["x_max"])})')
        if not cfg.get('y_auto', True):
            lines.append(f'{axvar}.set_ylim({_repr(cfg["y_min"])}, {_repr(cfg["y_max"])})')

        # Log skala
        if cfg.get('logx', False):
            lines.append(f'{axvar}.set_xscale("log")')
        if cfg.get('logy', False):
            lines.append(f'{axvar}.set_yscale("log")')

        # Tick boyutu
        lines.append(f'{axvar}.tick_params(axis="both", labelsize={size_tick})')

        # Izgara
        if cfg.get('grid', False):
            gs_  = _repr(cfg.get('grid_style', ':'))
            ga_  = _repr(cfg.get('grid_alpha', 0.6))
            lines.append(f'{axvar}.grid(True, linestyle={gs_}, alpha={ga_})')

        # Çerçeve (spine)
        for side in ('top', 'bottom', 'left', 'right'):
            show = cfg.get(f'spine_{side}', True)
            if not show:
                lines.append(f'{axvar}.spines[{_repr(side)}].set_visible(False)')
        spine_w = cfg.get('spine_width', 1.0)
        lines.append(f'for sp in {axvar}.spines.values(): sp.set_linewidth({_repr(spine_w)})')

        # Lejant
        if cfg.get('legend_show', True):
            leg_fs    = cfg.get('legend_fontsize', 10)
            leg_frame = cfg.get('legend_frame', True)
            is_manual = cfg.get('legend_manual', False)
            if is_manual:
                leg_x = _repr(cfg.get('legend_x', 1.0))
                leg_y = _repr(cfg.get('legend_y', 1.0))
                leg_pos = f"bbox_to_anchor=({leg_x}, {leg_y}), loc='upper left'"
            else:
                leg_loc = _repr(cfg.get('legend_loc', 'best'))
                leg_pos = f'loc={leg_loc}'
            if has_right:
                lines += [
                    f'_h1, _l1 = {axvar}.get_legend_handles_labels()',
                    f'_h2, _l2 = {ax2var}.get_legend_handles_labels()',
                    f'{axvar}.legend(_h1 + _h2, _l1 + _l2, {leg_pos}, fontsize={leg_fs}, frameon={leg_frame})',
                ]
            else:
                lines.append(f'{axvar}.legend({leg_pos}, fontsize={leg_fs}, frameon={leg_frame})')

        lines.append('')

    # ── LAYOUT & KAYDET ───────────────────────────────────────────────────────
    # Kenar boşlukları canvas_config'den (figure-level), panel_config'den değil
    cc = canvas_config or {}
    ml = cc.get('margin_left', 0.12)
    mb = cc.get('margin_bottom', 0.12)
    mr = cc.get('margin_right', 0.95)
    mt = cc.get('margin_top', 0.95)

    adjust_args = f'left={ml:.4f}, bottom={mb:.4f}, right={mr:.4f}, top={mt:.4f}'
    if n_panels > 1:
        hs = cc.get('hspace', 0.4)
        ws = cc.get('wspace', 0.3)
        adjust_args += f', hspace={hs:.4f}, wspace={ws:.4f}'

    lines += [
        '# ════════════════════════════════════════════════════════════════',
        '# Layout ve Kaydetme',
        '# ════════════════════════════════════════════════════════════════',
        f'fig.subplots_adjust({adjust_args})',
        '',
        '# Kaydetmek için yorum satırını kaldırın:',
        '# Boyutu korumak için bbox_inches kullanmayın:',
        '# fig.savefig("figure.pdf", dpi=300)',
        '# fig.savefig("figure.png", dpi=300)',
        '',
        'plt.show()',
        '',
    ]

    return "\n".join(lines)


# ── Jupyter Notebook Export ───────────────────────────────────────────────────

import json as _json


def _nb_code_cell(source: str) -> dict:
    """Kod hücresi oluştur."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def _nb_markdown_cell(source: str) -> dict:
    """Markdown hücresi oluştur."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source,
    }



# ── Jupyter Notebook Export ───────────────────────────────────────────────────

import json as _json


def _nb_code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def _nb_markdown_cell(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source,
    }


def export_as_notebook(
    canvas: "MplCanvas",
    data_manager: "DataManager",
    fit_list: list,
    loaded_models: dict | None = None,
    canvas_config: dict | None = None,
    figure_width_cm: float | None = None,
    figure_height_cm: float | None = None,
) -> str:
    """
    Mevcut grafiği Jupyter Notebook (.ipynb) olarak döndürür.

    Hücre yapısı:
      1. Markdown başlık
      2. Import'lar
      3. Model fonksiyonları (varsa)
      4+. Panel başına veri (np.array'ler) — ayrı hücreler
      Son. Figure + GridSpec + TÜM çizim + eksen ayarları + plt.show() — tek hücre
    """

    rows = canvas._layout_rows
    cols = canvas._layout_cols
    n_panels = canvas.panel_count

    if canvas_config is not None:
        fig_w = canvas_config.get('width_cm', 10.0) / 2.54
        fig_h = canvas_config.get('height_cm', 8.0) / 2.54
    else:
        fig_w, fig_h = canvas.fig.get_size_inches()
    if figure_width_cm is not None:
        fig_w = figure_width_cm / 2.54
    if figure_height_cm is not None:
        fig_h = figure_height_cm / 2.54

    cells = []

    # ── HÜCRE 1: Başlık ───────────────────────────────────────────────────────
    cells.append(_nb_code_cell(
        f"# {APP_NAME} — Otomatik Oluşturulmuş Grafik\n"
        f"# Bu notebook {APP_NAME} tarafından dışa aktarılmıştır.\n"
        "# Gereksinimler: pip install matplotlib numpy scipy pandas"
    ))

    # ── HÜCRE 2: Import'lar ───────────────────────────────────────────────────
    imports = [
        "import numpy as np",
        "import matplotlib.pyplot as plt",
        "import matplotlib.gridspec as gridspec",
        "%matplotlib inline",
    ]
    if fit_list:
        imports.append("from scipy.optimize import curve_fit")
    cells.append(_nb_code_cell("\n".join(imports)))

    # ── HÜCRE 3: Model fonksiyonları (varsa) ──────────────────────────────────
    written_models: dict[str, str] = {}  # model_name → real_function_name
    if fit_list and loaded_models:
        model_lines = ["# Fit Model Fonksiyonları"]
        for fit in fit_list:
            mn = fit.get('model_name', '')
            if mn in written_models:
                continue
            written_models[mn] = mn  # geçici placeholder
            func = loaded_models.get(mn)
            src, real_fn = _get_model_source(func) if func else (None, None)
            unique_fn = _to_safe_name(mn)
            if src:
                src_renamed = _rename_func_in_source(src, real_fn, unique_fn)
                model_lines += ["", f"# {mn}", src_renamed]
                written_models[mn] = unique_fn
            else:
                pnames = fit.get('param_names', [])
                args = _fallback_parameter_names(pnames)
                model_lines += [
                    f"# {mn}  (kaynak bulunamadı — elle düzenleyin)",
                    f"def {unique_fn}(x, {args}):",
                    f"    raise NotImplementedError('Model fonksiyonunu buraya yazın')",
                ]
                written_models[mn] = unique_fn
        cells.append(_nb_code_cell("\n".join(model_lines)))

    # ── HÜCRE 4: Tüm veri — tek hücre (panel bölümü yorum satırıyla) ──────────
    all_series = data_manager.get_all_series()
    series_varnames: dict[int, str] = {}

    data_lines = ["# ── Veri ──────────────────────────────────────────────"]
    for pid in range(n_panels):
        panel_series = [s for s in all_series if s.get('panel_id', 0) == pid]
        if not panel_series:
            continue

        pname = canvas.panel_names[pid]
        data_lines.append(f"\n# Panel {pid+1}: {pname}")

        for s in panel_series:
            gi = all_series.index(s)
            vname = f"s{gi+1}"
            series_varnames[id(s)] = vname
            label = s.get('label', f'Seri {gi+1}')
            pt = s.get('plot_type', 'scatter')

            data_lines.append(f"# {label}  (tip={pt})")
            data_lines.append(f"{vname}_x    = {_array_repr(s.get('x'))}")
            data_lines.append(f"{vname}_y    = {_array_repr(s.get('y'))}")
            xe = s.get('x_err')
            ye = s.get('y_err')
            data_lines.append(f"{vname}_xerr = {_array_repr(xe) if xe is not None and len(xe) > 0 else 'None'}")
            data_lines.append(f"{vname}_yerr = {_array_repr(ye) if ye is not None and len(ye) > 0 else 'None'}")
            data_lines.append("")

    cells.append(_nb_code_cell("\n".join(data_lines)))

    # ── SON HÜCRE: Figure + TÜM çizim + plt.show() — TEK HÜCRE ───────────────
    # Grafik hücresi — markdown kaldırıldı

    draw = []

    # Figure ve GridSpec
    draw += [
        f"fig = plt.figure(figsize=({fig_w:.4f}, {fig_h:.4f}))",
        f"gs  = gridspec.GridSpec({rows}, {cols}, figure=fig)",
        "",
    ]
    for pid in range(n_panels):
        r_ = pid // cols
        c_ = pid % cols
        draw.append(f"ax{pid+1} = fig.add_subplot(gs[{r_}, {c_}])")
    draw.append("")

    # Her panel için çizim
    for pid in range(n_panels):
        cfg = canvas.panel_configs[pid]
        pname = canvas.panel_names[pid]
        axvar = f"ax{pid+1}"
        ax2var = f"ax{pid+1}r"

        panel_series = [s for s in all_series if s.get('panel_id', 0) == pid]
        has_right = any(s.get('axis') == 'right' for s in panel_series)
        panel_fits = [f for f in fit_list if f.get('panel_id', 0) == pid]

        draw.append(f"# ── Panel {pid+1}: {pname} ──────────────────────────")

        if has_right:
            draw.append(f"{ax2var} = {axvar}.twinx()")
            draw.append("")

        # Seriler
        for s in panel_series:
            vname = series_varnames.get(id(s), "s?")
            label = s.get('label', '')
            color = s.get('color', 'black')
            pt    = s.get('plot_type', 'scatter')
            axis  = s.get('axis', 'left')
            target = ax2var if axis == 'right' else axvar

            if pt == 'histogram':
                draw += [
                    f"{target}.hist(",
                    f"    {vname}_y,",
                    f"    bins={_repr(s.get('bins', 20))},",
                    f"    color={_repr(color)},",
                    f"    alpha={_repr(s.get('alpha', 0.7))},",
                    f"    edgecolor={_repr(s.get('edgecolor', 'white'))},",
                    f"    label={_repr(label)},",
                    f")",
                ]
            elif pt == 'bar':
                filled    = s.get('bar_filled', True)
                bar_color = color if filled else 'none'
                bar_edge  = s.get('edgecolor', 'none') if filled else color
                ye_arr = s.get('y_err')
                draw += [
                    f"{target}.bar(",
                    f"    {vname}_x, {vname}_y,",
                    f"    width={_repr(s.get('bar_width', 0.8))},",
                    f"    color={_repr(bar_color)},",
                    f"    edgecolor={_repr(bar_edge)},",
                    f"    linewidth={_repr(s.get('bar_edge_width', 1.0))},",
                    f"    alpha={_repr(s.get('alpha', 1.0))},",
                    f"    label={_repr(label)},",
                ]
                if ye_arr is not None and len(ye_arr) > 0:
                    draw += [
                        f"    yerr={vname}_yerr,",
                        f"    capsize={_repr(s.get('capsize', 2.0))},",
                        f"    error_kw={{'elinewidth': {_repr(s.get('elinewidth', 1.0))}}},",
                    ]
                draw.append(")")
            else:
                mk  = s.get('marker', 'o')
                ls  = s.get('linestyle', 'None')
                fc  = color if s.get('filled', True) else 'none'
                mew = s.get('markeredgewidth', 0.5)
                has_xe = s.get('x_err') is not None and len(s.get('x_err', [])) > 0
                has_ye = s.get('y_err') is not None and len(s.get('y_err', [])) > 0

                if has_xe or has_ye:
                    draw += [
                        f"{target}.errorbar(",
                        f"    {vname}_x, {vname}_y,",
                        f"    xerr={vname}_xerr if {vname}_xerr is not None else None,",
                        f"    yerr={vname}_yerr if {vname}_yerr is not None else None,",
                        f"    fmt={_repr(mk)},",
                        f"    color={_repr(color)},",
                        f"    markerfacecolor={_repr(fc)},",
                        f"    markersize={_repr(s.get('markersize', 5))},",
                        f"    markeredgewidth={_repr(mew)},",
                        f"    linestyle={_repr(ls)},",
                        f"    linewidth={_repr(s.get('linewidth', 1.0))},",
                        f"    capsize={_repr(s.get('capsize', 2.0))},",
                        f"    elinewidth={_repr(s.get('elinewidth', 1.0))},",
                        f"    label={_repr(label)},",
                        f")",
                    ]
                else:
                    draw += [
                        f"{target}.plot(",
                        f"    {vname}_x, {vname}_y,",
                        f"    marker={_repr(mk)},",
                        f"    color={_repr(color)},",
                        f"    markerfacecolor={_repr(fc)},",
                        f"    markersize={_repr(s.get('markersize', 5))},",
                        f"    markeredgewidth={_repr(mew)},",
                        f"    linestyle={_repr(ls)},",
                        f"    linewidth={_repr(s.get('linewidth', 1.0))},",
                        f"    label={_repr(label)},",
                        f")",
                    ]

        # Fit çizgileri
        for fi, fit in enumerate(panel_fits):
            mn     = fit.get('model_name', f'fit{fi+1}')
            pnames = fit.get('param_names', [])
            pvals  = fit.get('param_values', [])
            src_s  = fit.get('source_series', '')
            axis   = fit.get('axis', 'left')
            target = ax2var if axis == 'right' else axvar
            fvname = f"fit{pid+1}_{fi+1}"
            real_fn = written_models.get(mn)
            func_exists = real_fn is not None and loaded_models and loaded_models.get(mn)

            if pnames and pvals:
                param_str = ',  '.join(f'{n}={v:.6g}' for n, v in zip(pnames, pvals))
                draw.append(f"# {mn}: {param_str}")
                r2 = fit.get('r2')
                if r2 is not None:
                    stats = fit.get('res_stats', {})
                    draw.append(f"# R²={r2:.6f},  RMSE={stats.get('rmse', 0):.6g}")

            draw.append(f"{fvname}_x = {_array_repr(fit.get('x'))}")

            src_series = next((s for s in panel_series if s.get('label') == src_s), None)

            if func_exists and pnames and pvals and src_series:
                sv = series_varnames[id(src_series)]
                p0_str = ', '.join(f'{v:.6g}' for v in pvals)
                draw += [
                    f"_popt_{fvname}, _ = curve_fit(",
                    f"    {real_fn}, {sv}_x, {sv}_y,",
                    f"    p0=[{p0_str}], method='trf', maxfev=5000,",
                    f")",
                    f"{fvname}_y = {real_fn}({fvname}_x, *_popt_{fvname})",
                ]
            else:
                draw.append(f"{fvname}_y = {_array_repr(fit.get('y'))}")

            draw += [
                f"{target}.plot(",
                f"    {fvname}_x, {fvname}_y,",
                f"    linestyle={_repr(fit.get('linestyle', '-'))},",
                f"    linewidth={_repr(fit.get('linewidth', 1.0))},",
                f"    color={_repr(fit.get('color', 'red'))},",
                f"    label={_repr(fit.get('label', mn))},",
                f")",
            ]

        # Eksen ayarları
        size_label = cfg.get('size_label', 10)
        size_title = cfg.get('size_title', 12)
        size_tick  = cfg.get('size_tick', 10)

        draw.append("")
        if cfg.get('xlabel', ''):
            draw.append(f"{axvar}.set_xlabel({_repr(cfg['xlabel'])}, fontsize={size_label}, labelpad={_repr(cfg.get('xlabel_pad', 2.0))})")
        if cfg.get('ylabel', ''):
            draw.append(f"{axvar}.set_ylabel({_repr(cfg['ylabel'])}, fontsize={size_label}, labelpad={_repr(cfg.get('ylabel_pad', 2.0))})")
        if cfg.get('title', ''):
            draw.append(f"{axvar}.set_title({_repr(cfg['title'])}, fontsize={size_title})")
        if has_right and cfg.get('ylabel_right', ''):
            draw.append(f"{ax2var}.set_ylabel({_repr(cfg['ylabel_right'])}, fontsize={size_label})")
        if not cfg.get('x_auto', True):
            draw.append(f"{axvar}.set_xlim({_repr(cfg['x_min'])}, {_repr(cfg['x_max'])})")
        if not cfg.get('y_auto', True):
            draw.append(f"{axvar}.set_ylim({_repr(cfg['y_min'])}, {_repr(cfg['y_max'])})")
        if cfg.get('logx', False):
            draw.append(f"{axvar}.set_xscale('log')")
        if cfg.get('logy', False):
            draw.append(f"{axvar}.set_yscale('log')")
        draw.append(f"{axvar}.tick_params(axis='both', labelsize={size_tick})")
        if cfg.get('grid', False):
            draw.append(f"{axvar}.grid(True, linestyle={_repr(cfg.get('grid_style', ':'))}, alpha={_repr(cfg.get('grid_alpha', 0.6))})")
        spine_w = cfg.get('spine_width', 1.0)
        draw.append(f"for sp in {axvar}.spines.values(): sp.set_linewidth({_repr(spine_w)})")

        if cfg.get('legend_show', True):
            leg_fs    = cfg.get('legend_fontsize', 10)
            leg_frame = cfg.get('legend_frame', True)
            is_manual = cfg.get('legend_manual', False)
            if is_manual:
                leg_x = _repr(cfg.get('legend_x', 1.0))
                leg_y = _repr(cfg.get('legend_y', 1.0))
                leg_pos = f"bbox_to_anchor=({leg_x}, {leg_y}), loc='upper left'"
            else:
                leg_loc = _repr(cfg.get('legend_loc', 'best'))
                leg_pos = f'loc={leg_loc}'
            if has_right:
                draw += [
                    f"_h1, _l1 = {axvar}.get_legend_handles_labels()",
                    f"_h2, _l2 = {ax2var}.get_legend_handles_labels()",
                    f"{axvar}.legend(_h1+_h2, _l1+_l2, {leg_pos}, fontsize={leg_fs}, frameon={leg_frame})",
                ]
            else:
                draw.append(f"{axvar}.legend({leg_pos}, fontsize={leg_fs}, frameon={leg_frame})")

        draw.append("")

    # Layout & kaydet — canvas_config'den al (figure-level)
    cc = canvas_config or {}
    ml = cc.get('margin_left', 0.12)
    mb = cc.get('margin_bottom', 0.12)
    mr = cc.get('margin_right', 0.95)
    mt = cc.get('margin_top', 0.95)

    nb_adjust = f'left={ml:.4f}, bottom={mb:.4f}, right={mr:.4f}, top={mt:.4f}'
    if n_panels > 1:
        hs = cc.get('hspace', 0.4)
        ws = cc.get('wspace', 0.3)
        nb_adjust += f', hspace={hs:.4f}, wspace={ws:.4f}'

    draw += [
        f"fig.subplots_adjust({nb_adjust})",
        "",
        "# Kaydetmek için yorum satırını kaldırın:",
        "# Boyutu korumak için bbox_inches kullanmayın:",
        "# fig.savefig('figure.pdf', dpi=300)",
        "# fig.savefig('figure.png', dpi=300)",
        "",
        "plt.show()",
    ]

    cells.append(_nb_code_cell("\n".join(draw)))

    # ── Notebook JSON ─────────────────────────────────────────────────────────
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.9.0",
            },
        },
        "cells": cells,
    }

    return _json.dumps(notebook, ensure_ascii=False, indent=1)
