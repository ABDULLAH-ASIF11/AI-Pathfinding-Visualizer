import tkinter as tk
from tkinter import ttk, messagebox
import random
import heapq
import time
import math

class PathfindingVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Pathfinding Visualizer")
        self.root.geometry("1000x750")
        self.root.configure(bg="#F8FAFC")
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()
        
        self.rows = 20
        self.cols = 25
        self.cell_size = 25
        
        self.start_node = (3, 3)
        self.goal_node = (16, 21)
        self.walls = set()
        
        self.grid = {}
        
        self.setup_ui()
        self.build_grid_ui()

    def configure_styles(self):
        self.style.configure(".", background="#F8FAFC", foreground="#1E293B", font=("Segoe UI", 10))
        self.style.configure("TLabelframe", background="#F8FAFC", bordercolor="#CBD5E1")
        self.style.configure("TLabelframe.Label", background="#F8FAFC", foreground="#475569", font=("Segoe UI", 10, "bold"))
        
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), borderwidth=1, focuscolor="none")
        self.style.configure("Run.TButton", foreground="#FFFFFF", background="#0EA5E9", bordercolor="#0284C7")
        self.style.map("Run.TButton", background=[("active", "#0284C7")])
        
        self.style.configure("Status.TLabel", font=("Segoe UI", 10, "bold"), foreground="#0F172A")

    def setup_ui(self):
        top_frame = ttk.Frame(self.root, padding="12", style="Card.TFrame")
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=10)
        
        config_frame = ttk.LabelFrame(top_frame, text=" CONFIGURATION ", padding="8")
        config_frame.pack(side=tk.LEFT, padx=8)
        
        ttk.Label(config_frame, text="R:").grid(row=0, column=0, padx=2)
        self.row_entry = ttk.Entry(config_frame, width=4, justify="center")
        self.row_entry.insert(0, str(self.rows))
        self.row_entry.grid(row=0, column=1, padx=4)
        
        ttk.Label(config_frame, text="C:").grid(row=0, column=2, padx=2)
        self.col_entry = ttk.Entry(config_frame, width=4, justify="center")
        self.col_entry.insert(0, str(self.cols))
        self.col_entry.grid(row=0, column=3, padx=4)
        
        ttk.Button(config_frame, text="Resize", command=self.resize_grid, width=7).grid(row=0, column=4, padx=4)
        
        mode_frame = ttk.LabelFrame(top_frame, text=" MOUSE MODE ", padding="8")
        mode_frame.pack(side=tk.LEFT, padx=8)
        
        self.mode_var = tk.StringVar(value="Wall")
        ttk.Radiobutton(mode_frame, text="Wall", variable=self.mode_var, value="Wall").grid(row=0, column=0, padx=6)
        ttk.Radiobutton(mode_frame, text="Start", variable=self.mode_var, value="Start").grid(row=0, column=1, padx=6)
        ttk.Radiobutton(mode_frame, text="Goal", variable=self.mode_var, value="Goal").grid(row=0, column=2, padx=6)
        
        algo_frame = ttk.LabelFrame(top_frame, text=" SEARCH STRATEGY ", padding="8")
        algo_frame.pack(side=tk.LEFT, padx=8)
        
        self.algo_var = tk.StringVar(value="A*")
        self.algo_menu = ttk.Combobox(algo_frame, textvariable=self.algo_var, values=["BFS", "UCS", "GBFS", "A*"], width=6, state="readonly")
        self.algo_menu.grid(row=0, column=0, padx=4)
        
        self.heur_var = tk.StringVar(value="Manhattan")
        self.heur_menu = ttk.Combobox(algo_frame, textvariable=self.heur_var, values=["Manhattan", "Euclidean"], width=10, state="readonly")
        self.heur_menu.grid(row=0, column=1, padx=4)
        
        gen_frame = ttk.LabelFrame(top_frame, text=" MAP SETUP ", padding="8")
        gen_frame.pack(side=tk.LEFT, padx=8)
        
        self.density_entry = ttk.Entry(gen_frame, width=4, justify="center")
        self.density_entry.insert(0, "30")
        self.density_entry.grid(row=0, column=0, padx=2)
        ttk.Label(gen_frame, text="%").grid(row=0, column=1, padx=2)
        
        ttk.Button(gen_frame, text="Maze", command=self.generate_maze, width=6).grid(row=0, column=2, padx=4)
        ttk.Button(gen_frame, text="Clear", command=self.clear_board, width=6).grid(row=0, column=3, padx=4)
        
        ttk.Button(top_frame, text="RUN SEARCH", command=self.execute_search, style="Run.TButton", width=12).pack(side=tk.LEFT, padx=20)
        
        metrics_bar = tk.Frame(self.root, bg="#0F172A", height=40)
        metrics_bar.pack(side=tk.BOTTOM, fill=tk.X)
        metrics_bar.pack_propagate(False)
        
        self.nodes_lbl = tk.Label(metrics_bar, text="Nodes Expanded: 0", fg="#94A3B8", bg="#0F172A", font=("Segoe UI", 10, "bold"))
        self.nodes_lbl.pack(side=tk.LEFT, padx=30)
        
        self.cost_lbl = tk.Label(metrics_bar, text="Path Cost: 0", fg="#94A3B8", bg="#0F172A", font=("Segoe UI", 10, "bold"))
        self.cost_lbl.pack(side=tk.LEFT, padx=30)
        
        self.time_lbl = tk.Label(metrics_bar, text="Execution Time: 0.00 ms", fg="#38BDF8", bg="#0F172A", font=("Segoe UI", 10, "bold"))
        self.time_lbl.pack(side=tk.RIGHT, padx=30)
        
        self.canvas_container = ttk.Frame(self.root, padding="10")
        self.canvas_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_container, bg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#CBD5E1")
        self.canvas.pack(anchor=tk.CENTER, expand=True)
        
        self.canvas.bind("<B1-Motion>", self.handle_mouse_drag)
        self.canvas.bind("<Button-1>", self.handle_mouse_click)

    def build_grid_ui(self):
        self.canvas.delete("all")
        self.grid.clear()
        
        c_width = self.cols * self.cell_size
        c_height = self.rows * self.cell_size
        self.canvas.config(width=c_width, height=c_height)
        
        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                tag = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#FFFFFF", outline="#F1F5F9", width=1)
                self.grid[(r, c)] = tag
                
        self.sync_node_colors()

    def sync_node_colors(self):
        for coord, tag in self.grid.items():
            if coord == self.start_node:
                self.canvas.itemconfig(tag, fill="#F59E0B", outline="#D97706")
            elif coord == self.goal_node:
                self.canvas.itemconfig(tag, fill="#EF4444", outline="#DC2626")
            elif coord in self.walls:
                self.canvas.itemconfig(tag, fill="#475569", outline="#334155")
            else:
                self.canvas.itemconfig(tag, fill="#FFFFFF", outline="#F1F5F9")

    def resize_grid(self):
        try:
            r = int(self.row_entry.get())
            c = int(self.col_entry.get())
            if 0 < r <= 26 and 0 < c <= 38:
                self.rows, self.cols = r, c
                self.start_node = (1, 1)
                self.goal_node = (r - 2, c - 2)
                self.walls.clear()
                self.build_grid_ui()
            else:
                messagebox.showwarning("Boundaries exceeded", "Please size coordinates between 5x5 and 26x38 for clean workspace display scaling.")
        except ValueError:
            pass

    def handle_mouse_click(self, event):
        c = event.x // self.cell_size
        r = event.y // self.cell_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.modify_cell(r, c)

    def handle_mouse_drag(self, event):
        c = event.x // self.cell_size
        r = event.y // self.cell_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            if self.mode_var.get() == "Wall":
                self.modify_cell(r, c)

    def modify_cell(self, r, c):
        mode = self.mode_var.get()
        coord = (r, c)
        
        if mode == "Start":
            if coord != self.goal_node and coord not in self.walls:
                self.start_node = coord
        elif mode == "Goal":
            if coord != self.start_node and coord not in self.walls:
                self.goal_node = coord
        elif mode == "Wall":
            if coord != self.start_node and coord != self.goal_node:
                if coord in self.walls:
                    self.walls.remove(coord)
                else:
                    self.walls.add(coord)
        self.sync_node_colors()

    def generate_maze(self):
        self.walls.clear()
        try:
            density = float(self.density_entry.get()) / 100.0
        except ValueError:
            density = 0.3
            
        for r in range(self.rows):
            for c in range(self.cols):
                coord = (r, c)
                if coord != self.start_node and coord != self.goal_node:
                    if random.random() < density:
                        self.walls.add(coord)
        self.sync_node_colors()

    def clear_board(self):
        self.walls.clear()
        self.sync_node_colors()

    def get_neighbors(self, node):
        r, c = node
        variants = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        valid = []
        for nr, nc in variants:
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if (nr, nc) not in self.walls:
                    valid.append((nr, nc))
        return valid

    def calculate_heuristic(self, node):
        r1, c1 = node
        r2, c2 = self.goal_node
        if self.heur_var.get() == "Manhattan":
            return abs(r1 - r2) + abs(c1 - c2)
        else:
            return math.sqrt((r1 - r2)**2 + (c1 - c2)**2)

    def execute_search(self):
        self.sync_node_colors()
        strategy = self.algo_var.get()
        
        start_time = time.perf_counter()
        
        parent = {}
        visited = set()
        frontier_set = set()
        
        g_score = {self.start_node: 0}
        expanded_count = 0
        success = False
        
        if strategy == "BFS":
            queue = [self.start_node]
            frontier_set.add(self.start_node)
            
            while queue:
                curr = queue.pop(0)
                frontier_set.discard(curr)
                
                if curr == self.goal_node:
                    success = True
                    break
                    
                if curr not in visited:
                    visited.add(curr)
                    expanded_count += 1
                    if curr != self.start_node:
                        self.canvas.itemconfig(self.grid[curr], fill="#EEF2F6", outline="#E2E8F0")
                        
                    for nxt in self.get_neighbors(curr):
                        if nxt not in visited and nxt not in frontier_set:
                            parent[nxt] = curr
                            queue.append(nxt)
                            frontier_set.add(nxt)
                            if nxt != self.goal_node:
                                self.canvas.itemconfig(self.grid[nxt], fill="#FEF08A", outline="#FDE047")
                    self.root.update()
                    
        elif strategy in ["UCS", "GBFS", "A*"]:
            pq = []
            init_h = self.calculate_heuristic(self.start_node)
            
            if strategy == "UCS":
                heapq.heappush(pq, (0, self.start_node))
            elif strategy == "GBFS":
                heapq.heappush(pq, (init_h, self.start_node))
            elif strategy == "A*":
                heapq.heappush(pq, (init_h, 0, self.start_node))
                
            frontier_set.add(self.start_node)
            
            while pq:
                item = heapq.heappop(pq)
                if strategy == "A*":
                    _, cost, curr = item
                else:
                    cost, curr = item
                    
                frontier_set.discard(curr)
                
                if curr == self.goal_node:
                    success = True
                    break
                    
                if curr not in visited:
                    visited.add(curr)
                    expanded_count += 1
                    if curr != self.start_node:
                        self.canvas.itemconfig(self.grid[curr], fill="#E0E7FF", outline="#C7D2FE")
                        
                    for nxt in self.get_neighbors(curr):
                        new_g = g_score[curr] + 1
                        if nxt not in g_score or new_g < g_score[nxt]:
                            g_score[nxt] = new_g
                            parent[nxt] = curr
                            h = self.calculate_heuristic(nxt)
                            
                            if strategy == "UCS":
                                heapq.heappush(pq, (new_g, nxt))
                            elif strategy == "GBFS":
                                heapq.heappush(pq, (h, nxt))
                            elif strategy == "A*":
                                heapq.heappush(pq, (new_g + h, new_g, nxt))
                                
                            frontier_set.add(nxt)
                            if nxt != self.goal_node:
                                self.canvas.itemconfig(self.grid[nxt], fill="#FEF08A", outline="#FDE047")
                    self.root.update()

        runtime = (time.perf_counter() - start_time) * 1000
        
        if success:
            path_cost = 0
            curr = self.goal_node
            while curr in parent:
                path_cost += 1
                curr = parent[curr]
                if curr != self.start_node:
                    self.canvas.itemconfig(self.grid[curr], fill="#10B981", outline="#059669")
            
            self.nodes_lbl.config(text=f"Nodes Expanded: {expanded_count}")
            self.cost_lbl.config(text=f"Path Cost: {path_cost}")
            self.time_lbl.config(text=f"Execution Time: {runtime:.2f} ms")
        else:
            self.nodes_lbl.config(text=f"Nodes Expanded: {expanded_count}")
            self.cost_lbl.config(text="Path Cost: N/A")
            self.time_lbl.config(text=f"Execution Time: {runtime:.2f} ms")
            messagebox.showinfo("Search Result", "No valid path exists to the target node configuration.")

if __name__ == "__main__":
    window = tk.Tk()
    app = PathfindingVisualizer(window)
    window.mainloop()