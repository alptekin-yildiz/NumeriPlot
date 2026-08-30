from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import copy
from lang import t


def _default_panel_config():
    """Her yeni panel için varsayılan ayar sözlüğü."""
    return {
        'title': "", 'xlabel': t('default_xlabel'), 'ylabel': t('default_ylabel'),
        'math_mode': False,
        'x_auto': True, 'x_min': 0, 'x_max': 10, 'x_step': 0, 'x_minor': 0,
        'y_auto': True, 'y_min': 0, 'y_max': 10, 'y_step': 0, 'y_minor': 0,
        'y_right_auto': True, 'y_right_min': 0, 'y_right_max': 10,
        'y_right_step': 0, 'y_right_minor': 0, 'logy_right': False, 'ylabel_right': "",
        'spine_width': 1.0,
        'spine_top': True, 'spine_bottom': True, 'spine_left': True, 'spine_right': True,
        'tick_top': False, 'tick_bottom': True, 'tick_left': True, 'tick_right': False,
        'grid': False, 'grid_style': ':', 'grid_alpha': 0.6,
        'logx': False, 'logy': False,
        'fontsize': 12, 'fontfamily': "Times New Roman",
        'tick_major_len': 3.0, 'tick_major_width': 1,
        'tick_minor_len': 2.0, 'tick_minor_width': 0.8,
        'title_bold': False, 'title_italic': False,
        'xlabel_bold': False, 'xlabel_italic': False,
        'ylabel_bold': False, 'ylabel_italic': False,
        'ylabel_right_bold': False, 'ylabel_right_italic': False,
        'size_title': 12, 'size_label': 10, 'size_tick': 10,
        'legend_show': True, 'legend_loc': 'best', 'legend_frame': True,
        'legend_fontsize': 10,
        'legend_layout_mode': 'auto',   # auto | vertical | horizontal | custom
        'legend_ncol': 1,
        'legend_handletextpad': 0.8,
        'legend_labelspacing': 0.5,
        'legend_columnspacing': 2.0,
        'legend_handlelength': 2.5,
        'legend_markerscale': 1.0,
        'xlabel_pad': 2.0,
        'ylabel_pad': 2.0,
        'ylabel_right_pad': 2.0,
        'title_pad': 6.0,
        'show_xticklabels': True,
        'show_yticklabels': True,
        'bar_mode': 'overlay',  # overlay | grouped
        # Kenar boşlukları (per-panel subplots_adjust değil, figure-level'da kullanılır)
        'margin_left': 0.15, 'margin_bottom': 0.15,
        'margin_right': 0.95, 'margin_top': 0.95,
    }


class MplCanvas(FigureCanvas):
    """
    Matplotlib çizim alanını (Canvas) yöneten sınıf.
    GridSpec tabanlı çoklu panel (subplot) desteği içerir.
    Akademik yayın kalitesi için gerekli varsayılan ayarlar korunmuştur.
    """

    def __init__(self, parent=None, width=5, height=4, dpi=150):
        # 1. Akademik Varsayılanları Yükle
        self._setup_academic_style()

        # 2. Figure Oluştur
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        # 3. Panel Durumu
        self._layout_rows = 1
        self._layout_cols = 1
        self.axes_list = []    # Ana (sol Y) axes, panel sırasına göre
        self.axes2_list = []   # İkincil (sağ Y) axes, panel sırasına göre (None olabilir)
        self.active_index = 0  # Seçili (aktif) panel indeksi
        self.panel_names = []  # Her panelin kullanıcı tarafından verilmiş ismi
        self.panel_configs = []  # Her panele ait plot_config kopyası

        # İlk layout'u oluştur (1×1)
        self._build_layout(1, 1)

        super().__init__(self.fig)

    # --------------------------------------------------
    # Akademik Stil
    # --------------------------------------------------
    def _setup_academic_style(self):
        """OriginPro tarzı ayarlar: Times New Roman font ve dış bakan tick'ler."""
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["font.serif"] = ["Times New Roman"]
        plt.rcParams["font.size"] = 12

        plt.rcParams['xtick.direction'] = 'out'
        plt.rcParams['ytick.direction'] = 'out'
        plt.rcParams['xtick.top'] = False
        plt.rcParams['ytick.right'] = False

        plt.rcParams['xtick.major.size'] = 4.0
        plt.rcParams['xtick.major.width'] = 1
        plt.rcParams['ytick.major.size'] = 4.0
        plt.rcParams['ytick.major.width'] = 1

        plt.rcParams['xtick.minor.size'] = 2.0
        plt.rcParams['xtick.minor.width'] = 1.0
        plt.rcParams['ytick.minor.size'] = 2.0
        plt.rcParams['ytick.minor.width'] = 1.0

    # --------------------------------------------------
    # Layout Yönetimi
    # --------------------------------------------------
    def _build_layout(self, rows: int, cols: int):
        """
        GridSpec'i yeniden kurar. Mevcut panel sayısından fazla panel varsa
        Ax1'e taşınmak üzere bilgi döndürür (MainWindow halleder).
        """
        n_new = rows * cols
        n_old = len(self.axes_list)

        # Mevcut figure içeriğini temizle
        self.fig.clf()

        self._layout_rows = rows
        self._layout_cols = cols

        gs = GridSpec(rows, cols, figure=self.fig)

        new_axes = []
        new_axes2 = []
        new_names = []
        new_configs = []

        for i in range(n_new):
            ax = self.fig.add_subplot(gs[i // cols, i % cols])
            for spine in ax.spines.values():
                spine.set_linewidth(1)
            new_axes.append(ax)
            new_axes2.append(None)

            # Mevcut panel varsa config ve ismi koru, yoksa varsayılan yap
            if i < n_old:
                new_names.append(self.panel_names[i])
                new_configs.append(self.panel_configs[i])
            else:
                new_names.append(f"Ax{i + 1}")
                new_configs.append(_default_panel_config())

        self.axes_list = new_axes
        self.axes2_list = new_axes2
        self.panel_names = new_names
        self.panel_configs = new_configs

        # Aktif indeks sınır dışına çıkmasın
        if self.active_index >= n_new:
            self.active_index = 0

    def apply_layout(self, rows: int, cols: int):
        """
        Dışarıdan (MainWindow) çağrılır. Layout'u değiştirir,
        fazla panel_id'leri Ax0'a taşımak için gereken bilgiyi döndürür.
        Dönüş: (orphan_panel_ids: list[int])  — sahipsiz kalan eski panel indeksleri
        """
        n_new = rows * cols
        n_old = len(self.axes_list)
        orphan_ids = list(range(n_new, n_old)) if n_new < n_old else []
        self._build_layout(rows, cols)
        return orphan_ids

    # --------------------------------------------------
    # Aktif Panel Erişimi
    # --------------------------------------------------
    @property
    def axes(self):
        """Geriye dönük uyumluluk: aktif panelin sol Y eksenini döndürür."""
        if not self.axes_list:
            return None
        return self.axes_list[self.active_index]

    @property
    def ax2(self):
        """Geriye dönük uyumluluk: aktif panelin sağ Y eksenini döndürür."""
        if not self.axes2_list:
            return None
        return self.axes2_list[self.active_index]

    @ax2.setter
    def ax2(self, value):
        """Geriye dönük uyumluluk: aktif panelin ax2'sini set eder."""
        if self.axes2_list:
            self.axes2_list[self.active_index] = value

    def get_axes(self, panel_id: int):
        """Belirli bir panel_id için (ax, ax2) tuple döndürür."""
        if 0 <= panel_id < len(self.axes_list):
            return self.axes_list[panel_id], self.axes2_list[panel_id]
        return None, None

    def set_ax2(self, panel_id: int, ax2):
        """Belirli bir panelin ikincil eksenini atar."""
        if 0 <= panel_id < len(self.axes2_list):
            self.axes2_list[panel_id] = ax2

    def get_active_config(self):
        """Aktif panelin config sözlüğünü döndürür."""
        if self.panel_configs:
            return self.panel_configs[self.active_index]
        return _default_panel_config()

    def set_active(self, index: int):
        """Aktif panel indeksini değiştirir."""
        if 0 <= index < len(self.axes_list):
            self.active_index = index

    @property
    def panel_count(self):
        return len(self.axes_list)

    # --------------------------------------------------
    # Temizleme
    # --------------------------------------------------
    def clear_panel(self, panel_id: int):
        """Belirli bir paneli temizler (axes içeriği)."""
        if 0 <= panel_id < len(self.axes_list):
            self.axes_list[panel_id].cla()
            if self.axes2_list[panel_id]:
                try:
                    self.axes2_list[panel_id].remove()
                except Exception:
                    pass
                self.axes2_list[panel_id] = None
        self.draw()

    def clear_plot(self):
        """
        Tüm figure'ı temizler (geriye dönük uyumluluk).
        Layout'u korur, sadece çizim içeriğini siler.
        """
        for i in range(len(self.axes_list)):
            self.axes_list[i].cla()
            if self.axes2_list[i]:
                try:
                    self.axes2_list[i].remove()
                except Exception:
                    pass
                self.axes2_list[i] = None
        self.draw()

    # --------------------------------------------------
    # Yardımcı
    # --------------------------------------------------
    def get_panel_config_copy(self, panel_id: int) -> dict:
        """Belirli bir panelin config'inin derin kopyasını döndürür."""
        if 0 <= panel_id < len(self.panel_configs):
            return copy.deepcopy(self.panel_configs[panel_id])
        return _default_panel_config()

    def set_panel_config(self, panel_id: int, cfg: dict):
        """Belirli bir panelin config'ini günceller."""
        if 0 <= panel_id < len(self.panel_configs):
            self.panel_configs[panel_id].update(cfg)

    # --------------------------------------------------
    # Qt Çift Tıklama — SpanSelector ile çakışmaz
    # --------------------------------------------------
    # Callback: MainWindow tarafından atanır
    dblclick_callback = None

    def mouseDoubleClickEvent(self, event):
        """
        Qt mouse event'i — matplotlib event loop'undan tamamen bağımsız.
        SpanSelector'ı hiç etkilemez çünkü farklı event sistemi.
        """
        if not self.axes_list or not callable(self.dblclick_callback):
            super().mouseDoubleClickEvent(event)
            return

        x_qt = event.position().x()
        y_qt = event.position().y()
        dpr   = self.devicePixelRatio()

        # Qt: (0,0) sol-üst. Mpl display: (0,0) sol-alt.
        x_mpl = x_qt * dpr
        y_mpl = (self.height() - y_qt) * dpr

        # Renderer'lı bbox (draw() sonrası geçerli)
        try:
            renderer = self.fig.canvas.get_renderer()
        except Exception:
            renderer = None

        found = None
        for i, ax in enumerate(self.axes_list):
            try:
                bb = ax.get_window_extent(renderer)
            except Exception:
                bb = ax.get_window_extent()
            if bb.contains(x_mpl, y_mpl):
                found = i
                break
            ax2 = self.axes2_list[i]
            if ax2 is not None:
                try:
                    bb2 = ax2.get_window_extent(renderer)
                except Exception:
                    bb2 = ax2.get_window_extent()
                if bb2.contains(x_mpl, y_mpl):
                    found = i
                    break

        if found is not None:
            self.dblclick_callback(found)
            return

        # Eksen dışındaki figure boşluğu: MainWindow kanvas ayarlarını açabilir.
        self.dblclick_callback(None)
