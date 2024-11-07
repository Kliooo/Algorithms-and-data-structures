import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

particles = []
velocities = []
personal_best_positions = []
personal_best_scores = []
global_best_position = None
global_best_score = float('inf')
iteration_count = 0
is_modified_mode = False

def toggle_modified_mode():
    global is_modified_mode, mode_toggle_button
    is_modified_mode = not is_modified_mode
    mode_toggle_button.config(
        text="Модификация: Вкл" if is_modified_mode else "Модификация: Выкл"
    )

def objective_function(x):
    return 4 * (x[0] - 5) ** 2 + (x[1] - 6) ** 2

def initialize_particles():
    global particles, velocities, personal_best_positions, personal_best_scores, global_best_position, global_best_score
    num_particles = int(particle_count_entry.get())
    x_min, x_max, y_min, y_max = -10, 10, -10, 10

    particles = np.random.uniform([x_min, y_min], [x_max, y_max], (num_particles, 2))
    velocities = np.random.uniform(-1, 1, (num_particles, 2))
    personal_best_positions = np.copy(particles)
    personal_best_scores = np.array([objective_function(p) for p in particles])
    global_best_position = personal_best_positions[np.argmin(personal_best_scores)]
    global_best_score = min(personal_best_scores)

    ax.clear()
    ax.scatter(particles[:, 0], particles[:, 1], color='blue', label='Particles')
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xticks(np.arange(-10, 11, 2))
    ax.set_yticks(np.arange(-10, 11, 2))
    ax.set_xlabel('X0-coordinate')
    ax.set_ylabel('X1-coordinate', labelpad=-3)

    ax.grid(True)
    canvas.draw()

def run_pso():
    global particles, velocities, personal_best_positions, personal_best_scores, global_best_position, global_best_score, iteration_count

    if len(particles) == 0:
        messagebox.showerror("Ошибка", "Частицы не инициализированы. Пожалуйста, сначала инициализируйте частицы.")
        return
    
    inertia_factor = float(inertia_entry.get())
    cognitive_factor = float(personal_best_factor_entry.get())
    social_factor = float(global_best_factor_entry.get())
    compression_factor = 0.729
    num_iterations = int(iterations_entry.get())

    for _ in range(num_iterations):
        iteration_count += 1

        for i in range(len(particles)):
            inertia = inertia_factor * velocities[i]
            cognitive = cognitive_factor * np.random.rand() * (personal_best_positions[i] - particles[i])
            social = social_factor * np.random.rand() * (global_best_position - particles[i])

            velocities[i] = compression_factor * (inertia + cognitive + social) if is_modified_mode else inertia + cognitive + social
            particles[i] += velocities[i]

            score = objective_function(particles[i])
            if score < personal_best_scores[i]:
                personal_best_scores[i] = score
                personal_best_positions[i] = particles[i]

        best_particle_index = np.argmin(personal_best_scores)
        if personal_best_scores[best_particle_index] < global_best_score:
            global_best_score = personal_best_scores[best_particle_index]
            global_best_position = personal_best_positions[best_particle_index]

        ax.clear()
        ax.scatter(particles[:, 0], particles[:, 1], color='blue', label='Particles')
        ax.scatter(global_best_position[0], global_best_position[1], color='red', marker='*', s=100, label='Global Best')
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        ax.set_xticks(np.arange(-10, 11, 2))
        ax.set_yticks(np.arange(-10, 11, 2))
        ax.set_xlabel('X0-coordinate')
        ax.set_ylabel('X1-coordinate', labelpad=-3)
        ax.grid(True)
        ax.legend(loc='lower right')
        canvas.draw()

    best_position_text.delete("1.0", tk.END)
    best_position_text.insert(tk.END, f"{global_best_position}")
    objective_value_entry.delete(0, tk.END)
    objective_value_entry.insert(0, f"{global_best_score}")
    iteration_count_entry.delete(0, tk.END)
    iteration_count_entry.insert(0, str(iteration_count))


root = tk.Tk()
root.title("Particle Swarm Optimization")
root.geometry("1000x545")

left_frame = tk.Frame(root, padx=10, pady=10)
left_frame.pack(side="left", fill="y")

parameters_frame = tk.LabelFrame(left_frame, text="Параметры", padx=10, pady=10)
parameters_frame.pack(fill="x", pady=5)

parameters_frame.grid_columnconfigure(0, weight=1)
parameters_frame.grid_columnconfigure(1, weight=2)

tk.Label(parameters_frame, text="Функция").grid(row=0, column=0, sticky="w")
objective_function_entry = tk.Entry(parameters_frame, width=30)
objective_function_entry.grid(row=0, column=1, sticky="ew")
objective_function_entry.insert(0, "4 * (x[0] - 5) ** 2 + (x[1] - 6) ** 2")

tk.Label(parameters_frame, text="Коэфф. инерции:").grid(row=1, column=0, sticky="w")
inertia_entry = tk.Entry(parameters_frame, width=30)
inertia_entry.grid(row=1, column=1, sticky="ew")
inertia_entry.insert(0, "0.3")

tk.Label(parameters_frame, text="Коэфф. личного лучшего значения:").grid(row=2, column=0, sticky="w", padx=(0, 5))
personal_best_factor_entry = tk.Entry(parameters_frame, width=30)
personal_best_factor_entry.grid(row=2, column=1, sticky="ew")
personal_best_factor_entry.insert(0, "1.5")

tk.Label(parameters_frame, text="Коэфф. глобального лучшего значения:").grid(row=3, column=0, sticky="w")
global_best_factor_entry = tk.Entry(parameters_frame, width=30)
global_best_factor_entry.grid(row=3, column=1, sticky="ew")
global_best_factor_entry.insert(0, "2.5")

tk.Label(parameters_frame, text="Количество частиц:").grid(row=9, column=0, sticky="w")
particle_count_entry = tk.Entry(parameters_frame, width=30)
particle_count_entry.grid(row=9, column=1, sticky="ew")
particle_count_entry.insert(0, "200")

control_frame = tk.LabelFrame(left_frame, text="Управление", padx=10, pady=11)
control_frame.pack(fill="x", pady=5)

control_frame.grid_columnconfigure(0, weight=1)

tk.Label(control_frame, text="Число итераций:").grid(row=1, column=0, sticky="w")
iterations_entry = tk.Entry(control_frame, width=30)
iterations_entry.grid(row=1, column=1, sticky="ew")
iterations_entry.insert(0, "1")

tk.Label(control_frame, text="Предыдущие итерации:").grid(row=2, column=0, sticky="w")
iteration_count_entry = tk.Entry(control_frame, width=30)
iteration_count_entry.grid(row=2, column=1, sticky="ew")
iteration_count_entry.insert(0, str(iteration_count))

tk.Button(control_frame, text="Инициализировать частицы", command=initialize_particles).grid(row=6, column=0, columnspan=2, sticky="ew", pady=(5,0))
mode_toggle_button = tk.Button(control_frame, text="Модификация: Выкл", command=toggle_modified_mode)
mode_toggle_button.grid(row=7, column=0, columnspan=2, sticky="ew", pady=5)
tk.Button(control_frame, text="Выполнить PSO", command=run_pso).grid(row=8, column=0, columnspan=2, sticky="ew", pady=0)

results_frame = tk.LabelFrame(left_frame, text="Результаты", padx=10, pady=11)
results_frame.pack(fill="x", pady=4)

results_frame.grid_columnconfigure(0, weight=1)
results_frame.grid_columnconfigure(1, weight=1)

best_position_label = tk.Label(results_frame, text="Лучшее положение:")
best_position_label.grid(row=0, column=0, sticky="w", columnspan=2)

best_position_text = tk.Text(results_frame, width=30, height=5)
best_position_text.grid(row=1, column=0, columnspan=2, sticky="ew")

objective_value_label = tk.Label(results_frame, text="Значение функции:", pady=11)
objective_value_label.grid(row=2, column=0, sticky="w")
objective_value_entry = tk.Entry(results_frame, width=30)
objective_value_entry.grid(row=2, column=1, sticky="ew")

right_frame = tk.Frame(root, padx=10, pady=14)
right_frame.pack(side="right", fill="both", expand=True)

graph_frame = tk.LabelFrame(right_frame, text="График", padx=10, pady=10)
graph_frame.pack(fill="both", expand=True)

fig, ax = plt.subplots(figsize=(4, 4))
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)

def centerWindow(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2) + 150
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

centerWindow(root)
root.mainloop()
