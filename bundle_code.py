#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

DEFAULT_EXTS = {".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".yml", ".yaml", ".css", ".scss", ".html", ".txt"}

def normalize_patterns(patterns):
    out = []
    for p in patterns or []:
        p = p.strip()
        if not p:
            continue
        out.append(p.replace("\\", "/"))
    return out

def collect_files(root: Path, includes, excludes, exts, from_list):
    files = set()
    if from_list:
        for line in from_list.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            p = (root / line).resolve()
            if p.is_file():
                files.add(p)
        return sorted(files)

    if not includes:
        includes = ["**/*"]

    for inc in includes:
        for p in root.glob(inc):
            if p.is_file():
                files.add(p.resolve())

    # filter by extension if provided
    if exts:
        files = {p for p in files if p.suffix.lower() in exts}

    # apply excludes
    for exc in excludes or []:
        for p in list(files):
            try:
                if Path(os.path.relpath(p, root)).as_posix().startswith(exc.rstrip("*")):
                    files.discard(p)
            except Exception:
                pass

    return sorted(files)

def read_text_safe(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # fallback with errors replaced to avoid choking
        return path.read_text(encoding="utf-8", errors="replace")

def write_single_txt(out_path: Path, root: Path, files, comment_header=False, max_lines=None, fence=False):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    total_lines = 0
    part_idx = 1
    current = out_path.open("w", encoding="utf-8")

    def roll_now():
        nonlocal total_lines, part_idx, current
        if current:
            current.close()
        part_idx += 1
        total_lines = 0
        new_path = out_path.with_name(f"{out_path.stem}.part{part_idx}{out_path.suffix}")
        current = new_path.open("w", encoding="utf-8")
        return new_path

    for fp in files:
        rel = Path(os.path.relpath(fp, root)).as_posix()
        header = f"{'// ' if comment_header else ''}=== {rel} ===\n"
        begin = f"{'// ' if comment_header else ''}--- BEGIN ---\n"
        end = f"\n{'// ' if comment_header else ''}--- END ---\n\n"
        body = read_text_safe(fp)

        block = header + begin
        if fence:
            lang = fp.suffix.lstrip(".") or ""
            block += f"```{lang}\n{body}\n```\n"
        else:
            block += body + "\n"
        block += end

        lines = block.count("\n")
        if max_lines and total_lines > 0 and (total_lines + lines) > max_lines:
            roll_now()
        current.write(block)
        total_lines += lines
        # if we exactly hit the limit, roll for the next file
        if max_lines and total_lines >= max_lines:
            roll_now()

    current.close()

def write_tree_zip(out_zip: Path, root: Path, files, to_txt=True, comment_header=False):
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(out_zip, "w", compression=ZIP_DEFLATED) as zf:
        for fp in files:
            rel = Path(os.path.relpath(fp, root)).as_posix()
            target_rel = rel + (".txt" if to_txt else "")
            content = read_text_safe(fp)
            header = f"{'// ' if comment_header else ''}=== {rel} ===\n"
            data = header + content
            zf.writestr(target_rel, data)

def main():
    ap = argparse.ArgumentParser(description="Empacotar arquivos de código em TXT único ou ZIP com estrutura.")
    ap.add_argument("--root", default=".", help="Diretório raiz do projeto (onde estão backend/ e frontend/)")
    ap.add_argument("--include", "-i", action="append", help="Glob para incluir (pode repetir). Ex: backend/src/controllers/**/*.ts")
    ap.add_argument("--exclude", "-x", action="append", help="Prefixo relativo para excluir. Ex: node_modules/ ou dist/")
    ap.add_argument("--ext", action="append", help="Extensões permitidas. Ex: .ts .tsx .json (default foco em texto/código)")
    ap.add_argument("--list", help="Arquivo com lista de paths relativos para incluir, um por linha")
    ap.add_argument("--mode", choices=["single", "tree"], default="single", help="single = 1 TXT; tree = ZIP espelhando pastas")
    ap.add_argument("--out", "-o", required=True, help="Saída: .txt para single; .zip para tree")
    ap.add_argument("--comment-header", action="store_true", help="Prefixa cabeçalhos com // para ficar amigável a TypeScript")
    ap.add_argument("--fence", action="store_true", help="No modo single, envolve cada arquivo em bloco ```lang```")
    ap.add_argument("--max-lines", type=int, help="No modo single, limite de linhas por arquivo de saída; gera partes .partN")
    ap.add_argument("--no-to-txt", action="store_true", help="No modo tree, não converte extensão; só adiciona cabeçalho e mantém ext")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Root não encontrado: {root}")

    includes = normalize_patterns(args.include)
    excludes = normalize_patterns(args.exclude)
    exts = set(e.lower() if e.startswith(".") else f".{e.lower()}" for e in (args.ext or []))
    if not exts:
        exts = DEFAULT_EXTS

    from_list = Path(args.list).resolve() if args.list else None
    files = collect_files(root, includes, excludes, exts, from_list)

    if not files:
        raise SystemExit("Nenhum arquivo encontrado. Ajuste --include/--list/--ext.")

    out = Path(args.out).resolve()
    if args.mode == "single":
        if out.suffix.lower() != ".txt":
            out = out.with_suffix(".txt")
        write_single_txt(out, root, files, comment_header=args.comment_header, max_lines=args.max_lines, fence=args.fence)
        print(f"[ok] Gerado: {out}")
    else:
        if out.suffix.lower() != ".zip":
            out = out.with_suffix(".zip")
        write_tree_zip(out, root, files, to_txt=not args.no_to_txt, comment_header=args.comment_header)
        print(f"[ok] Gerado: {out}")

if __name__ == "__main__":
    main()
