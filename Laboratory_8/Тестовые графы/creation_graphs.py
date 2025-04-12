import random
import openpyxl
import math

num_vertices = 40


def generate_complete_graph(num_vertices, min_distance=100, grid_size=None):
    if not grid_size:
        cols = int(math.ceil(math.sqrt(num_vertices)))
    else:
        cols = grid_size

    vertices = []
    for i in range(num_vertices):
        row = i // cols
        col = i % cols
        x = col * min_distance
        y = row * min_distance
        vertices.append((i + 1, x + 30, y + 30))
    
    edges = []
    for i in range(num_vertices):
        for j in range(num_vertices):
            if i != j:
                weight_ij = random.randint(1, 2000)
                weight_ji = random.randint(1, 2000)
                edges.append((i + 1, j + 1, weight_ij))
                edges.append((j + 1, i + 1, weight_ji))

    return vertices, edges

def save_graph_to_excel(vertices, edges, num_vertices):
    wb = openpyxl.Workbook()

    ws_vertices = wb.active
    ws_vertices.title = "Vertices"
    ws_vertices.append(("ID", "X", "Y"))
    for vertex in vertices:
        ws_vertices.append(vertex)

    ws_edges = wb.create_sheet(title="Edges")
    ws_edges.append(("Vertex 1", "Vertex 2", "Weight"))
    for edge in edges:
        ws_edges.append(edge)

    filename = f"{num_vertices}.xlsx"
    wb.save(filename)
    print(f"Файл '{filename}' успешно создан.")

vertices, edges = generate_complete_graph(num_vertices)

save_graph_to_excel(vertices, edges, num_vertices)
