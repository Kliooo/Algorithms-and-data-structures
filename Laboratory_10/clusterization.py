import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import fowlkes_mallows_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
import time

class ClusteringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Кластеризация данных")
        self.root.geometry("1000x600")

        self.original_df = None
        self.true_labels = None
        self.n_features = tk.IntVar(value=15)
        self.n_anonymize = tk.IntVar(value=10)

        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        tk.Button(control_frame, text="Загрузить CSV", command=self.load_csv).pack(fill=tk.X)
        tk.Button(control_frame, text="Обычная кластеризация", command=self.cluster_and_evaluate).pack(fill=tk.X, pady=(5, 0))

        tk.Label(control_frame, text="Признаков для отбора:").pack(anchor='w', pady=(10, 0))
        tk.Entry(control_frame, textvariable=self.n_features).pack(fill=tk.X)
        tk.Button(control_frame, text="Отбор признаков", command=self.select_features_cluster_evaluate).pack(fill=tk.X, pady=(5, 0))

        tk.Label(control_frame, text="Признаков для обезличивания:").pack(anchor='w', pady=(10, 0))
        tk.Entry(control_frame, textvariable=self.n_anonymize).pack(fill=tk.X)
        tk.Button(control_frame, text="Обезличивание", command=self.anonymize_cluster_evaluate).pack(fill=tk.X, pady=(5, 0))

        self.output = tk.Text(root)
        self.output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV файлы", "*.csv")])
        if not path:
            return
        try:
            df = pd.read_csv(path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")
            return

        df = df.drop(columns=['Index'], errors='ignore')
        if len(df) > 50_000:
            df = df.sample(n=50_000, random_state=42).reset_index(drop=True)

        if 'Target' in df.columns:
            self.true_labels = LabelEncoder().fit_transform(df['Target'])
            df = df.drop(columns=['Target'])

        num_cols = df.select_dtypes(include=['number']).columns
        df[num_cols] = SimpleImputer(strategy='mean').fit_transform(df[num_cols])
        cat_cols = df.select_dtypes(include=['object', 'bool']).columns
        for col in cat_cols:
            df[col] = LabelEncoder().fit_transform(df[col].astype(str))

        self.original_df = df.copy()
        self.output.insert(tk.END, f"Загружен файл {path}\n")
        self.output.insert(tk.END, f"Объектов: {df.shape[0]}, Признаков: {df.shape[1]}\n\n")

    def cluster_and_evaluate(self):
        df = self.original_df.copy() if self.original_df is not None else None
        if df is None:
            messagebox.showwarning("Внимание", "Сначала загрузите CSV-файл.")
            return
        self.output.insert(tk.END, "=== Кластеризация ===\n")
        start_time = time.perf_counter()
        labels = self.isodata(df.values, k=2)
        elapsed_time = time.perf_counter() - start_time
        score = self.evaluate(df.values, labels)
        self.output.insert(tk.END, f"Объектов: {df.shape[0]}, Признаков: {df.shape[1]}\n")
        self.output.insert(tk.END, f"Количество кластеров: 2\nИндекс Фоулкса-Мэллоуза: {score:.4f}\n")
        self.output.insert(tk.END, f"Время расчета: {elapsed_time:.2f} сек.\n\n")

    def select_features_cluster_evaluate(self):
        df = self.original_df.copy() if self.original_df is not None else None
        if df is None or self.true_labels is None:
            messagebox.showwarning("Внимание", "Загрузите CSV с меткой Target для отбора признаков.")
            return
        n = self.n_features.get()
        self.output.insert(tk.END, "=== Отбор признаков ===\n")
        start_time = time.perf_counter()
        selected_idx = self.feature_selection_add(df, self.true_labels, n)
        selected_cols = df.columns[selected_idx]
        self.output.insert(tk.END, f"Выбрано признаков: {len(selected_cols)} ({', '.join(selected_cols)})\n")
        df_sel = df.iloc[:, selected_idx]
        labels = self.isodata(df_sel.values, k=2)
        elapsed_time = time.perf_counter() - start_time
        score = self.evaluate(df_sel.values, labels)
        self.output.insert(tk.END, f"Индекс Фоулкса-Мэллоуза: {score:.4f}\n")
        self.output.insert(tk.END, f"Время расчета: {elapsed_time:.2f} сек.\n\n")

    def anonymize_cluster_evaluate(self):
        df = self.original_df.copy() if self.original_df is not None else None
        if df is None or self.true_labels is None:
            messagebox.showwarning("Внимание", "Сначала загрузите CSV с target.")
            return
        self.output.insert(tk.END, "=== Обезличивание ===\n")
        start_time = time.perf_counter()

        top_k = 3
        top_idx = self.feature_selection_add(df, self.true_labels, top_k)
        df = df.drop(columns=df.columns[top_idx])
        self.output.insert(tk.END, f"Удалены признаки: {', '.join(self.original_df.columns[top_idx])}\n")

        m = min(self.n_anonymize.get(), df.shape[1])
        selected_idx = self.feature_selection_add(df, self.true_labels, m)
        df_sel = df.iloc[:, selected_idx].copy()

        for col in df_sel.select_dtypes(include=['number']).columns:
            min_val = df_sel[col].min()
            max_val = df_sel[col].max()
            bins = np.linspace(min_val, max_val, 6)
            df_sel[col] = np.digitize(df_sel[col], bins[1:-1], right=True)

        df_enc = df_sel.copy()
        for col in df_enc.columns:
            df_enc[col] = LabelEncoder().fit_transform(df_enc[col])

        group_sizes = df_sel.groupby(list(df_sel.columns), observed=True).size()
        most_common_key = group_sizes.idxmax()
        keys_per_row = df_sel.apply(lambda row: tuple(row), axis=1)
        row_group_sizes = keys_per_row.map(group_sizes)
        low_size_mask = row_group_sizes < 5
        if low_size_mask.any():
            replacement_df = pd.DataFrame(
                [most_common_key] * low_size_mask.sum(),
                columns=df_sel.columns,
                index=df_sel[low_size_mask].index
            )
            df_sel.loc[low_size_mask, df_sel.columns] = replacement_df
            df_enc = df_sel.copy()
            for col in df_enc.columns:
                df_enc[col] = LabelEncoder().fit_transform(df_enc[col])

        labels = self.isodata(df_enc.values, k=2)
        score = self.evaluate(df_enc.values, labels)
        elapsed_time = time.perf_counter() - start_time
        self.output.insert(tk.END, f"Осталось признаков: {df_enc.shape[1]}\n")
        self.output.insert(tk.END, f"Индекс Фоулкса-Мэллоуза: {score:.4f}\n")

        group_sizes = df_sel.groupby(list(df_sel.columns), observed=True).size()
        k_anon = group_sizes.min()
        self.output.insert(tk.END, f"Минимальная k-анонимность: {k_anon}\n")

        k_counts = group_sizes.value_counts().sort_index()
        self.output.insert(tk.END, "Распределение по группам (первые 5):\n")
        for k_val, count in list(k_counts.items())[:5]:
            self.output.insert(tk.END, f"  k = {k_val}: {count * k_val} строк ({count} групп)\n")
        self.output.insert(tk.END, f"Время расчета: {elapsed_time:.2f} сек.\n\n")

    def show_confusion_matrix(self, true_labels, pred_labels):
        cm = confusion_matrix(true_labels, pred_labels)
        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=np.unique(pred_labels),
                    yticklabels=np.unique(true_labels))
        plt.xlabel("Предсказанные метки")
        plt.ylabel("Истинные метки")
        plt.title("Матрица ошибок")
        plt.tight_layout()
        plt.show()

    def show_clusters_plot(self, features, labels):
        pca = PCA(n_components=2)
        reduced = pca.fit_transform(features)

        plt.figure(figsize=(6, 5))
        colors = ['blue', 'orange']
        for cluster in [0, 1]:
            mask = labels == cluster
            plt.scatter(reduced[mask, 0], reduced[mask, 1], c=colors[cluster], label=f'Кластер {cluster}')

        plt.xlabel("PCA 1")
        plt.ylabel("PCA 2")
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.show()

    def evaluate(self, features, labels):
        score = fowlkes_mallows_score(self.true_labels, labels)
        self.show_clusters_plot(features, labels)
        self.show_confusion_matrix(self.true_labels, labels)
        return score

    def isodata(self, data, k=2):
        centers_idx = [np.random.randint(0, len(data))]
        for _ in range(1, k):
            centers_matrix = data[centers_idx]
            distance_matrix = np.max(np.abs(data[:, np.newaxis] - centers_matrix), axis=2)
            min_distances = distance_matrix.min(axis=1)
            next_center_idx = int(np.argmax(min_distances))
            centers_idx.append(next_center_idx)

        centers_matrix = data[centers_idx]
        distance_matrix = np.max(np.abs(data[:, np.newaxis] - centers_matrix), axis=2)
        labels = np.argmin(distance_matrix, axis=1)
        return labels

    def feature_selection_add(self, X, y, n_features):
        remaining = list(range(X.shape[1]))
        selected = []
        while len(selected) < n_features and remaining:
            best_score = -1
            best_idx = None
            for i in remaining:
                cols = selected + [i]
                labels_pred = self.isodata(X.iloc[:, cols].values, k=2)
                score = fowlkes_mallows_score(y, labels_pred)
                if score > best_score:
                    best_score, best_idx = score, i
            if best_idx is None:
                break
            selected.append(best_idx)
            remaining.remove(best_idx)
        return selected

if __name__ == "__main__":
    root = tk.Tk()
    app = ClusteringApp(root)
    root.mainloop()
