# %%
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 09:10:54 2025
@author: MZs
"""

import os
import re
from collections import defaultdict
from graphviz import Digraph

# Több könyvtár támogatása
MODULE_DIRS = ["modulok", "gui"]

# Bővített regex: modulok + gui
IMPORT_PATTERN = re.compile(
    r"from\s+(modulok|gui)(?:\.([a-zA-Z0-9_]+))?\s+import\s+([a-zA-Z0-9_,\s]+)"
    r"|import\s+(modulok|gui)\.([a-zA-Z0-9_\.]+)"
)


def find_imports_in_file(filepath):
    imports = set()
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            match = IMPORT_PATTERN.search(line)
            if match:
                pkg1, submodule, imported_items, pkg2, direct_import = match.groups()

                if submodule:
                    imports.add(f"{pkg1}.{submodule}".strip())

                elif imported_items:
                    for item in imported_items.split(","):
                        imports.add(f"{pkg1}.{item.strip()}")

                elif direct_import:
                    imports.add(f"{pkg2}.{direct_import.split('.')[0]}")

    return imports


def detect_cycles(graph):
    visited = set()
    stack = set()
    cycles = []

    def visit(node, path):
        if node in stack:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        for neighbor in graph.get(node, []):
            visit(neighbor, path + [neighbor])
        stack.remove(node)

    for node in graph:
        visit(node, [node])

    return cycles


def build_dependency_graph():
    graph = defaultdict(set)

    for base_dir in MODULE_DIRS:
        for root, _, files in os.walk(base_dir):
            for filename in files:
                if filename.endswith(".py"):
                    filepath = os.path.join(root, filename)

                    rel_path = os.path.relpath(filepath, base_dir).replace("\\", "/")
                    module_name = f"{base_dir}." + rel_path[:-3].replace("/", ".")

                    imports = find_imports_in_file(filepath)
                    graph[module_name].update(imports)

    return graph


def print_dependency_graph(graph):
    print("📦 Modulkapcsolati térkép:")
    for module, dependencies in graph.items():
        if dependencies:
            print(f"  🔹 {module} → {', '.join(dependencies)}")
        else:
            print(f"  ⚪ {module} → (nincs belső import)")


def visualize_dependency_graph(graph, output_file="modulok_terkep", jupyter_base_url="http://localhost:8888/notebooks"):
    dot = Digraph(comment="Modulkapcsolati térkép", format="svg")
    dot.attr(rankdir="LR", size="10")

    for module in graph:
        rel_path = module.replace(".", "/") + ".py"
        # modulok/ vagy gui/ alapján linkel
        dot.node(module, href=f"{jupyter_base_url}/{rel_path}", target="_blank")

    for module, deps in graph.items():
        for dep in deps:
            dot.edge(module, dep)

    dot.render(output_file, cleanup=True)
    print(f"📊 Interaktív Jupyter-linkes gráf mentve: {output_file}.svg")


if __name__ == "__main__":
    graph = build_dependency_graph()
    print_dependency_graph(graph)
    visualize_dependency_graph(graph)
# %%
