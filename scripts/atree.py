import os
import sys


SIZE_THRESHOLD = 1024 ** 3  # 1 GB


def format_size(size_bytes):
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024


def analyze_directory(path):
    total_size = 0
    total_files = 0
    children = []
    
    if path[:5] == "/proc":
        return 0, 0, []
    
    print( "%s%s\r" % (path[:60],path[-10:]), end="", file=sys.stderr )

    try:
        entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
    except (PermissionError,FileNotFoundError,OSError):
        return 0, 0, []

    for entry in entries:
        full_path = entry.path

        if entry.is_dir(follow_symlinks=False):
            dir_size, dir_files, sub_children = analyze_directory(full_path)

            total_size += dir_size
            total_files += dir_files

            children.append({
                "name": entry.name,
                "size": dir_size,
                "files": dir_files,
                "children": sub_children,
            })

        elif entry.is_file(follow_symlinks=False):
            try:
                file_size = entry.stat().st_size
                total_size += file_size
                total_files += 1
            except OSError:
                pass

    return total_size, total_files, children


def print_tree(nodes, prefix=""):
    visible_nodes = [n for n in nodes if n["size"] >= SIZE_THRESHOLD]

    for index, node in enumerate(visible_nodes):
        is_last = index == len(visible_nodes) - 1

        branch = "+-- " if is_last else "+-- "
        next_prefix = prefix + ("    " if is_last else "|  ")

        print(
            f"{prefix}{branch}{node['name']} "
            f"[{node['files']} files - {format_size(node['size'])}]"
        )

        print_tree(node["children"], next_prefix)


def main():
    
    # idee: on affiche dans la sortie d'erreur les textes d'avancement
    # ainsi la redirection dans un fichier est propre !
    
    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(sys.argv[0])} <directory>")
        sys.exit(1)

    root_path = sys.argv[1]

    if not os.path.isdir(root_path):
        print("Invalid directory")
        sys.exit(1)
        
    print( "Please wait...", file=sys.stderr )

    total_size, total_files, tree = analyze_directory(root_path)
    
    # nettoie l'ecran
    print( "%s\r", " "*80, file=sys.stderr )
    print("")

    print(
        f"{os.path.basename(os.path.abspath(root_path))} "
        f"[{total_files} files - {format_size(total_size)}]"
    )
    print_tree(tree)


if __name__ == "__main__":
    main()