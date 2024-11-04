import random
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Genetic algorithm")
root.geometry("1200x600")

population = []
best_solution = None
best_value = float('inf')
total_generations = 0
integer_mode = False
modified_mode = False

def set_generations(value):
    generations_entry.delete(0, tk.END)
    generations_entry.insert(0, str(value))

def toggle_integer_mode():
    global integer_mode
    integer_mode = not integer_mode
    integer_mode_btn.config(
        text="Целочисленное решение: Вкл" if integer_mode else "Целочисленное решение: Выкл"
    )

def toggle_modified_mode():
    global modified_mode
    modified_mode = not modified_mode
    modified_mode_btn.config(
        text="Модификация: Вкл" if modified_mode else "Модификация: Выкл"
    )

def create_initial_population(size, min_gene, max_gene):
    if integer_mode:
        return [[random.randint(int(min_gene), int(max_gene)) for _ in range(2)] for _ in range(size)]
    else:
        return [[random.uniform(min_gene, max_gene) for _ in range(2)] for _ in range(size)]

def evaluate_function(chromosome):
    x1, x2 = chromosome
    return 4 * (x1 - 5) ** 2 + (x2 - 6) ** 2

def selection(population):
    if modified_mode:
        population.sort(key=lambda chrom: evaluate_function(chrom))
        elite_size = int(len(population) * 0.1)
        return population[:elite_size]
    else:
        return population

def mutate(chromosome, mutation_rate, min_gene, max_gene):
    for gene_index in range(len(chromosome)):
        if random.random() < mutation_rate:
            if integer_mode:
                chromosome[gene_index] = random.randint(int(min_gene), int(max_gene))
            else:
                chromosome[gene_index] = random.uniform(min_gene, max_gene)
    return chromosome

def crossover(parent1, parent2, alpha=0.5):
    return [(alpha * p1 + (1 - alpha) * p2) for p1, p2 in zip(parent1, parent2)]

def create_new_generation(selected, mutation_rate, min_gene, max_gene):
    new_generation = selected[:]

    while len(new_generation) < len(population):
        parent1, parent2 = random.sample(selected, 2)
        child = crossover(parent1, parent2)
        new_generation.append(mutate(child, mutation_rate, min_gene, max_gene))

    return new_generation

def calculate_chromosomes():
    global population, best_solution, best_value, total_generations

    num_chromosomes = int(chromosomes_entry.get())
    min_gene = float(min_gene_entry.get())
    max_gene = float(max_gene_entry.get())
    mutation_rate = float(mutation_entry.get()) / 100

    population = create_initial_population(num_chromosomes, min_gene, max_gene)

    current_generations = int(generations_entry.get())

    for _ in range(current_generations):
        selected = selection(population)
        population = create_new_generation(selected, mutation_rate, min_gene, max_gene)

        total_generations += 1

        for chrom in population:
            value = evaluate_function(chrom)
            if modified_mode:
                value *= 0.9

            if value < best_value:
                best_value = value
                best_solution = chrom

        previous_generations_entry.delete(0, tk.END)
        previous_generations_entry.insert(0, str(total_generations))

    best_solution_text.delete(1.0, tk.END)
    if best_solution:
        best_solution_text.insert(tk.END, f"x1 = {best_solution[0]:.6f}\n")
        best_solution_text.insert(tk.END, f"x2 = {best_solution[1]:.6f}\n")

    function_value_entry.delete(0, tk.END)
    function_value_entry.insert(0, str(best_value))

    for item in tree.get_children():
        tree.delete(item)

    for i, chrom in enumerate(population):
        tree.insert("", "end", values=(i + 1, evaluate_function(chrom), *chrom))


left_frame = tk.Frame(root, padx=10, pady=10)
left_frame.pack(side="left", fill="y")

params_label = tk.LabelFrame(left_frame, text="Параметры", padx=10, pady=10)
params_label.pack(fill="x", pady=5)

params_label.grid_columnconfigure(0, weight=1)
params_label.grid_columnconfigure(1, weight=2)

tk.Label(params_label, text="Функция").grid(row=0, column=0, sticky="w")
func_combo = tk.Entry(params_label)
func_combo.grid(row=0, column=1, sticky="ew")
func_combo.insert(0, "4 * (x[1] - 5) ** 2 + (x[2] - 6) ** 2")

tk.Label(params_label, text="Вероятность мутации, %:").grid(row=1, column=0, sticky="w")
mutation_entry = tk.Entry(params_label)
mutation_entry.grid(row=1, column=1, sticky="ew")
mutation_entry.insert(0, "25")

tk.Label(params_label, text="Количество хромосом:").grid(row=2, column=0, sticky="w")
chromosomes_entry = tk.Entry(params_label)
chromosomes_entry.grid(row=2, column=1, sticky="ew")
chromosomes_entry.insert(0, "50")

tk.Label(params_label, text="Минимальное значение гена:").grid(row=3, column=0, sticky="w")
min_gene_entry = tk.Entry(params_label)
min_gene_entry.grid(row=3, column=1, sticky="ew")
min_gene_entry.insert(0, "-50")

tk.Label(params_label, text="Максимальное значение гена:").grid(row=4, column=0, sticky="w")
max_gene_entry = tk.Entry(params_label)
max_gene_entry.grid(row=4, column=1, sticky="ew")
max_gene_entry.insert(0, "50")

control_label = tk.LabelFrame(left_frame, text="Управление", padx=10, pady=10)
control_label.pack(fill="x", pady=5)

tk.Label(control_label, text="Количество поколений:").grid(row=1, column=0, sticky="w", pady=0)
generations_entry = tk.Entry(control_label)
generations_entry.grid(row=1, column=1, sticky="ew", pady=0)
generations_entry.insert(0, "5")

tk.Label(control_label, text="Количество прошлых поколений:").grid(row=2, column=0, sticky="w", pady=0)
previous_generations_entry = tk.Entry(control_label)
previous_generations_entry.grid(row=2, column=1, sticky="ew", pady=0)
previous_generations_entry.insert(0, "0")

buttons_frame = tk.Frame(control_label)
buttons_frame.grid(row=3, column=0, columnspan=2, pady=5)
tk.Button(buttons_frame, text="1", width=13, command=lambda: set_generations(1)).pack(side="left", padx=0)
tk.Button(buttons_frame, text="10", width=13, command=lambda: set_generations(10)).pack(side="left", padx=0)
tk.Button(buttons_frame, text="100", width=13, command=lambda: set_generations(100)).pack(side="left", padx=0)
tk.Button(buttons_frame, text="1000", width=13, command=lambda: set_generations(1000)).pack(side="left", padx=0)

integer_mode_btn = tk.Button(control_label, text="Целочисленное решение: Выкл", command=toggle_integer_mode)
integer_mode_btn.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

modified_mode_btn = tk.Button(control_label, text="Модификация: Выкл", command=toggle_modified_mode)
modified_mode_btn.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)

calculate_btn = tk.Button(control_label, text="Рассчитать", command=calculate_chromosomes)
calculate_btn.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)

results_label = tk.LabelFrame(left_frame, text="Результаты", padx=10, pady=10)
results_label.pack(fill="x", pady=5)

results_label.grid_columnconfigure(0, weight=1)
results_label.grid_columnconfigure(1, weight=1)

best_solution_label = tk.Label(results_label, text="Лучшее решение:")
best_solution_label.grid(row=0, column=0, sticky="w", columnspan=2)

best_solution_text = tk.Text(results_label, width=30, height=5)
best_solution_text.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

function_value_label = tk.Label(results_label, text="Значение функции:")
function_value_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)

function_value_entry = tk.Entry(results_label)
function_value_entry.grid(row=2, column=1, sticky="ew", pady=5)

table_label_frame = tk.LabelFrame(root, text="Хромосомы данного поколения", padx=10, pady=10)
table_label_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=(0, 0))

columns = ("Номер", "Значение функции", "Ген 1", "Ген 2")
tree = ttk.Treeview(table_label_frame, columns=columns, show="headings")
tree.heading("Номер", text="Номер")
tree.heading("Значение функции", text="Значение функции")
tree.heading("Ген 1", text="Ген 1")
tree.heading("Ген 2", text="Ген 2")

tree.column("Номер", width=50)
tree.column("Значение функции", width=150)
tree.column("Ген 1", width=150)
tree.column("Ген 2", width=150)

tree.pack(fill="both", expand=True)

root.mainloop()
