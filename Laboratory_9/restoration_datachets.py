import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import nan_euclidean_distances


def create_gui():
    root = tk.Tk()
    root.title("Data Restoration")
    root.geometry("1000x355")

    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(row=0, column=0, sticky="nsew")
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    form_frame = ttk.Frame(main_frame, padding=10, borderwidth=2, relief="groove")
    form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    form_frame.columnconfigure(1, weight=1)

    output_frame = ttk.Frame(main_frame, padding=10, borderwidth=2, relief="groove")
    output_frame.grid(row=0, column=1, sticky="nsew")
    output_frame.columnconfigure(0, weight=1)
    output_frame.rowconfigure(0, weight=1)

    output_text = tk.Text(output_frame, wrap=tk.WORD, height=18, width=40)
    output_text.grid(row=0, column=0, sticky="nsew")

    ttk.Label(form_frame, text="Исходный файл:").grid(row=0, column=0, sticky=tk.W, pady=5)
    source_file_entry = ttk.Entry(form_frame, state='readonly')
    source_file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

    def select_source_file():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            filename = os.path.basename(file_path)
            source_file_entry.configure(state='normal')
            source_file_entry.delete(0, tk.END)
            source_file_entry.insert(0, filename)
            source_file_entry.configure(state='readonly')
            root.source_file_path = file_path

    source_select_button = ttk.Button(form_frame, text="Выбрать", command=select_source_file)
    source_select_button.grid(row=0, column=2, sticky=tk.W, pady=5)

    ttk.Label(form_frame, text="Удалить (%):").grid(row=1, column=0, sticky=tk.W, pady=0)
    percent_entry = ttk.Entry(form_frame)
    percent_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(5, 2))

    def delete_data():
        if not hasattr(root, 'source_file_path'):
            messagebox.showerror("Ошибка", "Исходный файл не выбран")
            return
        try:
            pct = float(percent_entry.get())
            assert 0 < pct < 50
        except:
            messagebox.showerror("Ошибка", "Введите корректный процент (0-50)")
            return

        df = pd.read_excel(root.source_file_path)
        arr = df.values.copy()
        h, w = arr.shape
        total_cells = h * w
        target = int(total_cells * pct / 100)

        mask = np.zeros_like(arr, dtype=bool)
        removed = 0

        cells_per_sq = 4 * 4
        positions = [(i, j) for i in range(h - 3) for j in range(w - 3)]
        np.random.shuffle(positions)
        for (i, j) in positions:
            if removed + cells_per_sq > target:
                break
            if not mask[i:i+4, j:j+4].any():
                mask[i:i+4, j:j+4] = True
                removed += cells_per_sq

        still = target - removed
        if still > 0:
            candidates = np.argwhere(~mask)
            np.random.shuffle(candidates)
            row_counts = mask.sum(axis=1)
            max_per_row = w // 2
            added = 0
            for (i, j) in candidates:
                if added >= still:
                    break
                if row_counts[i] < max_per_row:
                    mask[i, j] = True
                    row_counts[i] += 1
                    added += 1
            removed += added

        arr[mask] = np.nan
        df2 = pd.DataFrame(arr, columns=df.columns)

        base, ext = os.path.splitext(root.source_file_path)
        out_path_gaps = base + "_nan" + ext
        df2.to_excel(out_path_gaps, index=False)

        messagebox.showinfo(
            "Готово",
            f"Удалено {removed} из {total_cells} ячеек ({removed/total_cells*100:.2f}%)\n"
            f"Файл с пропусками сохранён как:\n{out_path_gaps}"
        )

    delete_button = ttk.Button(form_frame, text="Удалить", command=delete_data)
    delete_button.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

    ttk.Label(form_frame, text="Файл для восстановления:").grid(row=3, column=0, sticky=tk.W, pady=5)
    restore_file_entry = ttk.Entry(form_frame, state='readonly')
    restore_file_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

    def select_restore_file():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            filename = os.path.basename(file_path)
            restore_file_entry.configure(state='normal')
            restore_file_entry.delete(0, tk.END)
            restore_file_entry.insert(0, filename)
            restore_file_entry.configure(state='readonly')
            root.restore_file_path = file_path

    restore_select_button = ttk.Button(form_frame, text="Выбрать", command=select_restore_file)
    restore_select_button.grid(row=3, column=2, sticky=tk.W, pady=5)

    ttk.Label(form_frame, text="Метод восстановления:").grid(row=4, column=0, sticky=tk.W, pady=5)
    method_var = tk.StringVar()
    method_combobox = ttk.Combobox(form_frame, textvariable=method_var, state='readonly')
    method_combobox['values'] = (
        'Попарное удаление',
        'Метод заполнения моды',
        'На основе Zet-алгоритма'
    )
    method_combobox.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(5, 1))
    method_combobox.current(0)

    def recover_data(df, method):
        df_recovered = df.copy()

        if method == 'На основе Zet-алгоритма':
            encoders = {}
            df_encoded = df_recovered.copy()
            categorical_cols = df_recovered.select_dtypes(include=['object', 'category']).columns
            numeric_cols = df_recovered.select_dtypes(include=['int64', 'float64']).columns

            for col in categorical_cols:
                encoders[col] = LabelEncoder()
                df_encoded[col] = df_encoded[col].fillna('__NAN__')
                df_encoded[col] = encoders[col].fit_transform(df_encoded[col])
                df_encoded[col] = df_encoded[col].where(
                    df_encoded[col] != encoders[col].transform(['__NAN__'])[0], np.nan
                )

            nan_rows = df_recovered.isna().any(axis=1)
            for idx in df_recovered[nan_rows].index:
                nan_cols = df_recovered.columns[df_recovered.loc[idx].isna()]
                valid_rows = df_recovered[~df_recovered[nan_cols].isna().any(axis=1)]
                
                if valid_rows.empty:
                    continue

                row_encoded = df_encoded.loc[idx].values.reshape(1, -1)
                valid_encoded = df_encoded.loc[valid_rows.index].values
                distances = nan_euclidean_distances(row_encoded, valid_encoded)[0]

                k = min(10, len(valid_rows))
                nearest_indices = np.argsort(distances)[:k]
                nearest_rows = valid_rows.iloc[nearest_indices]

                for col in nan_cols:
                    if col in numeric_cols:
                        df_recovered.loc[idx, col] = nearest_rows[col].mean()
                    else:
                        mode_val = nearest_rows[col].mode()[0]
                        df_recovered.loc[idx, col] = mode_val

        elif method == 'Попарное удаление':
            nan_rows = df_recovered.isna().any(axis=1)
            df_recovered.loc[nan_rows, :] = np.nan
        elif method == 'Метод заполнения моды':
            for column in df_recovered.columns:
                mode_val = df_recovered[column].mode()[0]
                df_recovered[column] = df_recovered[column].fillna(mode_val)

        return df_recovered

    def restore_data():
        if not hasattr(root, 'restore_file_path'):
            messagebox.showerror("Ошибка", "Файл для восстановления не выбран")
            return

        df = pd.read_excel(root.restore_file_path)
        selected_method = method_var.get()
        df_recovered = recover_data(df, selected_method)

        base, ext = os.path.splitext(root.restore_file_path)
        method_name_map = {
            'Попарное удаление': 'pairwise',
            'Метод заполнения моды': 'modefill',
            'На основе Zet-алгоритма': 'zetalgo'
        }
        method_suffix = method_name_map.get(selected_method, "recovered")
        out_path_recovered = base + f"_{method_suffix}" + ext
        df_recovered.to_excel(out_path_recovered, index=False)

        messagebox.showinfo(
            "Готово",
            f"Восстановленный файл сохранён как:\n{out_path_recovered}"
        )

    restore_button = ttk.Button(form_frame, text="Восстановить", command=restore_data)
    restore_button.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

    ttk.Label(form_frame, text="Исходный файл:").grid(row=6, column=0, sticky=tk.W, pady=5)
    input_file_name_entry = ttk.Entry(form_frame, state='readonly')
    input_file_name_entry.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

    def select_input_file_name():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            filename = os.path.basename(file_path)
            input_file_name_entry.configure(state='normal')
            input_file_name_entry.delete(0, tk.END)
            input_file_name_entry.insert(0, filename)
            input_file_name_entry.configure(state='readonly')
            root.input_file_path = file_path

    select_input_button = ttk.Button(form_frame, text="Выбрать", command=select_input_file_name)
    select_input_button.grid(row=6, column=2, sticky=tk.W, pady=5)

    ttk.Label(form_frame, text="Получившийся файл:").grid(row=7, column=0, sticky=tk.W, pady=5)
    output_file_name_entry = ttk.Entry(form_frame, state='readonly')
    output_file_name_entry.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

    def select_output_file_name():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            filename = os.path.basename(file_path)
            output_file_name_entry.configure(state='normal')
            output_file_name_entry.delete(0, tk.END)
            output_file_name_entry.insert(0, filename)
            output_file_name_entry.configure(state='readonly')
            root.output_file_path = file_path

    select_output_button = ttk.Button(form_frame, text="Выбрать", command=select_output_file_name)
    select_output_button.grid(row=7, column=2, sticky=tk.W, pady=5)

    def calculate_error():
        if not hasattr(root, 'input_file_path') or not hasattr(root, 'output_file_path'):
            messagebox.showerror("Ошибка", "Выберите оба файла: исходный и восстановленный")
            return

        df_original = pd.read_excel(root.input_file_path)
        df_restored = pd.read_excel(root.output_file_path)

        categorical_cols = df_original.select_dtypes(include=['object', 'category']).columns
        numeric_cols = df_original.select_dtypes(include=['int64', 'float64']).columns

        numeric_errors = []
        categorical_errors = []
        output_text.delete(1.0, tk.END)

        #output_text.insert(tk.END, "Ошибка по столбцам:\n\n")

        for col in numeric_cols:
            numeric_error = 0
            numeric_count = 0
            original_values = df_original[col].values
            restored_values = df_restored[col].values
            for orig, rest in zip(original_values, restored_values):
                if pd.isna(orig):
                    continue
                numeric_count += 1
                if pd.isna(rest):
                    numeric_error += 1
                elif orig == 0:
                    continue
                else:
                    numeric_error += abs(orig - rest) / abs(orig)
            if numeric_count > 0:
                error_percent = (numeric_error / numeric_count) * 100
                numeric_errors.append(error_percent)
                output_text.insert(tk.END, f"Столбец '{col}' (числовой): {error_percent:.2f}%\n")
            else:
                output_text.insert(tk.END, f"Столбец '{col}' (числовой): Нет данных для расчета\n")

        for col in categorical_cols:
            categorical_errors_col = 0
            categorical_total = 0
            original_values = df_original[col].values
            restored_values = df_restored[col].values
            for orig, rest in zip(original_values, restored_values):
                if pd.isna(orig):
                    continue
                categorical_total += 1
                if pd.isna(rest) or orig != rest:
                    categorical_errors_col += 1
            if categorical_total > 0:
                error_percent = (categorical_errors_col / categorical_total) * 100
                categorical_errors.append(error_percent)
                output_text.insert(tk.END, f"Столбец '{col}' (категориальный): {error_percent:.2f}%\n")
            else:
                output_text.insert(tk.END, f"Столбец '{col}' (категориальный): Нет данных для расчета\n")


        #output_text.insert(tk.END, "\nИтоговые значения:\n")
        numeric_avg_error = sum(numeric_errors) / len(numeric_errors) if numeric_errors else 0
        categorical_avg_error = sum(categorical_errors) / len(categorical_errors) if categorical_errors else 0

        if numeric_errors:
            output_text.insert(tk.END, f"Средняя ошибка для числовых данных: {numeric_avg_error:.2f}%\n")
        else:
            output_text.insert(tk.END, "Средняя ошибка для числовых данных: Нет числовых данных\n")

        if categorical_errors:
            output_text.insert(tk.END, f"Средняя ошибка для категориальных данных: {categorical_avg_error:.2f}%\n")
        else:
            output_text.insert(tk.END, "Средняя ошибка для категориальных данных: Нет категориальных данных\n")

        if numeric_errors and categorical_errors:
            overall_error = (numeric_avg_error + categorical_avg_error) / 2
            output_text.insert(tk.END, f"Общая ошибка: {overall_error:.2f}%\n")
        elif numeric_errors:
            output_text.insert(tk.END, f"Общая ошибка: {numeric_avg_error:.2f}% (только числовые данные)\n")
        elif categorical_errors:
            output_text.insert(tk.END, f"Общая ошибка: {categorical_avg_error:.2f}% (только категориальные данные)\n")
        else:
            output_text.insert(tk.END, "Общая ошибка: Нет данных для расчета\n")
        print(output_text.get("1.0", tk.END))

    calc_error_button = ttk.Button(form_frame, text="Рассчитать ошибку", command=calculate_error)
    calc_error_button.grid(row=8, column=0, columnspan=3, sticky="nsew", pady=(5,0))

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    root.mainloop()

if __name__ == "__main__":
    create_gui()