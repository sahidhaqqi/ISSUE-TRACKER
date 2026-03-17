# rapihin_indent_saja.py
import sys

filename = sys.argv[1]

with open(filename, "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Hitung level indent berdasarkan tab/spasi
    stripped = line.lstrip()
    if not stripped:  # baris kosong
        new_lines.append("\n")
        continue

    # Hitung jumlah indentasi level
    indent_level = (len(line) - len(stripped)) // 4
    new_line = " " * (indent_level * 4) + stripped
    new_lines.append(new_line)

with open(filename, "w") as f:
    f.writelines(new_lines)

print(f"{filename} sudah dirapihkan indentasinya.")
