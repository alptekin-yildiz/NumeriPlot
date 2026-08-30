import pandas as pd
import numpy as np

class DataManager:
    """
    Veri yükleme, sütunları yönetme ve 'Seri' oluşturma işlemlerinden sorumlu sınıf.
    Arayüz (UI) ile Ham Veri arasında köprü görevi görür.
    """
    def __init__(self):
        self.df = None          # Ham veri (DataFrame)
        self.series_list = []   # Grafiğe eklenmiş serilerin listesi
    
    def load_file(self, file_path):
        """
        Verilen dosya yolundan (Excel/CSV) veriyi okur.
        Dönüş: (Başarı Durumu, Hata Mesajı)
        """
        try:
            if file_path.endswith('.csv') or file_path.endswith('.txt'):
                self.df = pd.read_csv(file_path, sep=None, engine='python',
                                      encoding='utf-8-sig')  # BOM otomatik temizlenir
            else:
                self.df = pd.read_excel(file_path)

            # Sütun adlarındaki BOM, boşluk, görünmez karakter kalıntılarını temizle
            self.df.columns = [str(c).strip().lstrip('\ufeff') for c in self.df.columns]

            self.series_list.clear()
            return True, None

        except Exception as e:
            return False, str(e)

    def get_columns(self):
        """Yüklü verideki sütun isimlerini liste olarak döndürür."""
        if self.df is not None:
            return list(self.df.columns)
        return []

    def create_series(self, x_col, y_col, axis='left', style_defaults=None, panel_id=0, plot_type='scatter'):
        """
        Seçilen sütunlardan bir 'Seri Sözlüğü' oluşturur.
        plot_type: 'scatter' | 'histogram' | 'bar'
        Histogram için x_col yoksayılır, sadece y_col kullanılır.
        """
        if self.df is None:
            return None

        try:
            if plot_type == 'histogram':
                y = pd.to_numeric(self.df[y_col], errors='coerce').values
                y_clean = y[~np.isnan(y)]
                if len(y_clean) == 0:
                    return None
                series = {
                    'label': y_col,
                    'x': np.array([]),
                    'y': y_clean,
                    'x_col': None,
                    'y_col': y_col,
                    'axis': axis,
                    'plot_type': 'histogram',
                    'color': style_defaults.get('color', 'steelblue') if style_defaults else 'steelblue',
                    'alpha': style_defaults.get('alpha', 0.7) if style_defaults else 0.7,
                    'bins': style_defaults.get('bins', 20) if style_defaults else 20,
                    'edgecolor': style_defaults.get('edgecolor', 'white') if style_defaults else 'white',
                    'marker': 'None', 'linestyle': 'None', 'linewidth': 0.5,
                    'markersize': 3, 'markeredgewidth': 0.5, 'capsize': 1, 'filled': False,
                    'x_err': None, 'y_err': None,
                }
            elif plot_type == 'bar':
                subset = self.df[[x_col, y_col]].copy()
                x = subset[x_col].values          # Metin/kategori korunur
                y = pd.to_numeric(subset[y_col], errors='coerce').values
                mask = ~pd.isna(x) & ~np.isnan(y)
                x_clean, y_clean = x[mask], y[mask]
                if len(x_clean) == 0:
                    return None
                series = {
                    'label': y_col,
                    'x': x_clean,
                    'y': y_clean,
                    'x_col': x_col,
                    'y_col': y_col,
                    'axis': axis,
                    'plot_type': 'bar',
                    'color': style_defaults.get('color', 'steelblue') if style_defaults else 'steelblue',
                    'alpha': style_defaults.get('alpha', 1.0) if style_defaults else 1.0,
                    'bar_width': style_defaults.get('bar_width', 0.8) if style_defaults else 0.8,
                    'bar_filled': style_defaults.get('bar_filled', True) if style_defaults else True,
                    'bar_edge_width': style_defaults.get('bar_edge_width', 1.0) if style_defaults else 1.0,
                    'edgecolor': style_defaults.get('edgecolor', 'none') if style_defaults else 'none',
                    'ecolor': style_defaults.get('ecolor', '#000000') if style_defaults else '#000000',
                    'elinewidth': style_defaults.get('elinewidth', 1.0) if style_defaults else 1.0,
                    'capsize': style_defaults.get('capsize', 3.0) if style_defaults else 3.0,
                    'marker': 'None', 'linestyle': 'None', 'linewidth': 0.5,
                    'markersize': 3, 'markeredgewidth': 0.5, 'filled': False,
                    'x_err': None, 'y_err': None,
                }
            else:
                # scatter / line
                y = pd.to_numeric(self.df[y_col], errors='coerce').values
                if x_col is not None:
                    x = pd.to_numeric(self.df[x_col], errors='coerce').values
                    mask = ~np.isnan(x) & ~np.isnan(y)
                    x_clean = x[mask]
                else:
                    mask = ~np.isnan(y)
                    x_clean = np.arange(1, int(np.sum(mask)) + 1)
                y_clean = y[mask]
                if len(y_clean) == 0:
                    return None
                series = {
                    'label': y_col,
                    'x': x_clean,
                    'y': y_clean,
                    'x_col': x_col,
                    'y_col': y_col,
                    'axis': axis,
                    'plot_type': 'scatter',
                    'color': style_defaults.get('color', 'black') if style_defaults else 'black',
                    'marker': style_defaults.get('marker', 'o') if style_defaults else 'o',
                    'linestyle': style_defaults.get('linestyle', 'None') if style_defaults else 'None',
                    'filled': style_defaults.get('filled', False) if style_defaults else False,
                    'markersize': style_defaults.get('markersize', 3) if style_defaults else 3,
                    'markeredgewidth': style_defaults.get('markeredgewidth', 0.5) if style_defaults else 0.5,
                    'linewidth': style_defaults.get('linewidth', 0.5) if style_defaults else 0.5,
                    'capsize': style_defaults.get('capsize', 1) if style_defaults else 1,
                    'alpha': 1.0,
                    'interpolation': style_defaults.get('interpolation', 'linear') if style_defaults else 'linear',
                    'x_err': None, 'y_err': None,
                }

            series['panel_id'] = panel_id
            self.series_list.append(series)
            return series

        except Exception as e:
            print(f"Seri oluşturma hatası: {e}")
            return None

    def remove_series(self, index):
        """Listeden belirtilen indeksteki seriyi siler."""
        if 0 <= index < len(self.series_list):
            del self.series_list[index]

    def get_series_for_panel(self, panel_id: int) -> list:
        """Belirtilen panele ait serileri döndürür."""
        return [s for s in self.series_list if s.get('panel_id', 0) == panel_id]

    def remove_series_from_panel(self, panel_id: int, local_index: int):
        """Panel içindeki local index'e göre seriyi siler."""
        panel_series = self.get_series_for_panel(panel_id)
        if 0 <= local_index < len(panel_series):
            target = panel_series[local_index]
            # Dict içinde numpy array alanları bulunduğu için value-based remove
            # (eşitlik karşılaştırması) ambiguity hatası verebilir.
            # Bu yüzden kimlik (identity) bazlı silme yapıyoruz.
            for i, s in enumerate(self.series_list):
                if s is target:
                    del self.series_list[i]
                    break

    def get_all_series(self) -> list:
        return list(self.series_list)

    def clear_panel(self, panel_id: int):
        """Bir paneldeki tüm serileri siler."""
        self.series_list = [s for s in self.series_list if s.get('panel_id', 0) != panel_id]

    def reassign_panel(self, old_panel_id: int, new_panel_id: int):
        """Bir paneldeki serileri başka panele taşır."""
        for s in self.series_list:
            if s.get('panel_id', 0) == old_panel_id:
                s['panel_id'] = new_panel_id

    def reassign_orphan_series(self, orphan_panel_ids: list, target_panel_id: int = 0) -> int:
        """Artık var olmayan panellerdeki serileri hedef panele taşır."""
        moved = 0
        for s in self.series_list:
            if s.get('panel_id', 0) in orphan_panel_ids:
                s['panel_id'] = target_panel_id
                moved += 1
        return moved
