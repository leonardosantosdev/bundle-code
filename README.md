# bundle-code — Guia de Uso

Este projeto empacota arquivos de código em um **TXT único** ou em um **ZIP com estrutura de pastas**, facilitando o envio de contexto em chats e revisões.

## Sumário

- [Visão geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Estrutura recomendada de pastas](#estrutura-recomendada-de-pastas)
- [Como o script funciona](#como-o-script-funciona)
- [Opções da CLI](#opções-da-cli)
- [Modos de operação](#modos-de-operação)
- [Exemplos de uso no terminal (Git Bash / PowerShell / CMD)](#exemplos-de-uso-no-terminal-git-bash--powershell--cmd)
- [Uso via script `run_bundle.sh` (Git Bash)](#uso-via-script-run_bundlesh-git-bash)
- [Uso via script `run_bundle.bat` (Windows)](#uso-via-script-run_bundlebat-windows)
- [Casos avançados e dicas](#casos-avançados-e-dicas)
- [Erros comuns](#erros-comuns)

---

## Visão geral

O script principal é o `bundle_code.py`. Ele:

- Recolhe arquivos a partir de um **diretório raiz**.
- Permite **incluir** arquivos por **glob** e **excluir** pastas.
- Filtra por **extensões** de arquivo.
- Gera:
  - **`single`**: um TXT único (com partes `partN` se ultrapassar `--max-lines`), ou
  - **`tree`**: um ZIP espelhando a estrutura de pastas, opcionalmente convertendo cada arquivo para `.txt`.

Uso típico:

- **TXT único** quando você quer colar conteúdo ou enviar um único arquivo agregando vários fontes.
- **ZIP com estrutura** quando você quer manter hierarquia real e isolar arquivos.

## Pré-requisitos

- Python 3.8+ instalado e acessível no PATH.
- Terminal:
  - **Git Bash** (recomendado no Windows) ou
  - **PowerShell/CMD**.
- Permissão de leitura nos diretórios que serão varridos.

## Estrutura recomendada de pastas

Exemplo (ajuste para a sua realidade):

```
projects/
  services/bundle-code/
    bundle_code.py
    run_bundle.sh
    run_bundle.bat
  seu-projeto/
    backend/
      src/...
    frontend/
      src/...
```

## Como o script funciona

Fluxo resumido:

1. Define o **`--root`** (diretório base do projeto).
2. Aplica **includes** (`--include/-i`) com globs para encontrar arquivos.
3. Remove o que bater nos **excludes** (`--exclude/-x`), como `node_modules/`.
4. Restringe por **extensões** (`--ext`), se informado. Se não informar, usa um conjunto padrão apropriado para código/texto.
5. Gera a saída conforme o **modo**:
   - `single`: concatenando blocos, cada um com cabeçalho do caminho e conteúdo do arquivo. Se atingir `--max-lines`, cria `arquivo.part2.txt`, `part3`, etc. **Nunca corta um arquivo no meio da parte**.
   - `tree`: cria `.zip` replicando a árvore de pastas. Por padrão converte cada arquivo para `.txt` com cabeçalho. Com `--no-to-txt`, mantém a extensão original.

## Opções da CLI

````
--root DIR              Diretório raiz do projeto.
--include, -i GLOB      Glob para incluir (pode repetir).
--exclude, -x PREFIXO   Prefixo relativo para excluir (pode repetir). Ex: node_modules/ dist/
--ext EXT               Extensões permitidas (.ts .tsx .json etc). Pode repetir.
--list ARQUIVO          Lista de paths relativos (um por linha) para incluir.
--mode {single,tree}    Modo de saída: single (TXT) ou tree (ZIP).
--out, -o ARQUIVO       Caminho do arquivo de saída.
--comment-header        Prefixa cabeçalhos com // (amigável para TypeScript).
--fence                 No modo single, usa blocos de código ```lang.
--max-lines N           No modo single, limita linhas por arquivo de saída (gera partes).
--no-to-txt             No modo tree, NÃO converte para .txt (mantém extensão original).
````

## Modos de operação

### single (TXT único)

- Concatena todos os arquivos em um único TXT.
- Insere cabeçalho com o caminho relativo de cada arquivo.
- Com `--fence`, envolve cada arquivo em bloco markdown ```lang.
- Com `--max-lines`, limita o tamanho do TXT e cria partes; não divide arquivo ao meio.

### tree (ZIP com estrutura)

- Mantém a hierarquia de pastas.
- Por padrão, cada arquivo é gravado como `.txt` com cabeçalho de caminho.
- Use `--no-to-txt` para manter a extensão original (.ts, .tsx etc.).

## Exemplos de uso no terminal (Git Bash / PowerShell / CMD)

### Git Bash (dentro de `projects/`)

**TXT único:**

```bash
python services/bundle-code/bundle_code.py \
  --root seu-projeto \
  --mode single -o export-single.txt \
  -i "backend/src/**/*.ts" \
  -i "frontend/src/**/*.tsx" \
  -x "backend/node_modules/" -x "frontend/node_modules/" \
  --comment-header --fence --max-lines 4000
```

**ZIP com estrutura:**

```bash
python services/bundle-code/bundle_code.py \
  --root seu-projeto \
  --mode tree -o export-zip.zip \
  -i "backend/src/**/*.ts" \
  -i "frontend/src/**/*.tsx" \
  -x "backend/node_modules/" -x "frontend/node_modules/"
```

### PowerShell (Windows)

Troque as quebras de linha com `\` por acentuação de linha do PowerShell, ou coloque tudo em uma linha:

```powershell
python .\services\bundle-code\bundle_code.py --root .\seu-projeto --mode single -o .\export-single.txt -i "backend/src/**/*.ts" -i "frontend/src/**/*.tsx" -x "backend/node_modules/" -x "frontend/node_modules/" --comment-header --fence --max-lines 4000
```

### CMD (Windows)

Use o acento circunflexo `^` para quebras de linha:

```bat
python services\bundle-code\bundle_code.py ^
  --root seu-projeto ^
  --mode single -o export-single.txt ^
  -i "backend/src/**/*.ts" ^
  -i "frontend/src/**/*.tsx" ^
  -x "backend/node_modules/" -x "frontend/node_modules/" ^
  --comment-header --fence --max-lines 4000
```

## Uso via script `run_bundle.sh` (Git Bash)

Crie `run_bundle.sh` ao lado do `bundle_code.py`:

```bash
#!/bin/bash
# gerar txt único
python bundle_code.py \
  --root ../../seu-projeto \
  --mode single -o ../../seu-projeto/export-single.txt \
  -i "backend/src/**/*.ts" \
  -i "frontend/src/**/*.tsx" \
  -x "backend/node_modules/" -x "frontend/node_modules/" \
  --comment-header --fence --max-lines 4000

# gerar zip com estrutura
python bundle_code.py \
  --root ../../seu-projeto \
  --mode tree -o ../../seu-projeto/export-zip.zip \
  -i "backend/src/**/*.ts" \
  -i "frontend/src/**/*.tsx" \
  -x "backend/node_modules/" -x "frontend/node_modules/"
```

Depois:

```bash
cd projects/services/bundle-code
chmod +x run_bundle.sh
./run_bundle.sh
```

## Uso via script `run_bundle.bat` (Windows)

Crie `run_bundle.bat` ao lado do `bundle_code.py`:

```bat
@echo off
REM gerar txt único
python bundle_code.py ^
  --root ..\..\seu-projeto ^
  --mode single -o ..\..\seu-projeto\export-single.txt ^
  -i "backend/src/**/*.ts" ^
  -i "frontend/src/**/*.tsx" ^
  -x "backend/node_modules/" -x "frontend/node_modules/" ^
  --comment-header --fence --max-lines 4000

REM gerar zip com estrutura
python bundle_code.py ^
  --root ..\..\seu-projeto ^
  --mode tree -o ..\..\seu-projeto\export-zip.zip ^
  -i "backend/src/**/*.ts" ^
  -i "frontend/src/**/*.tsx" ^
  -x "backend/node_modules/" -x "frontend/node_modules/"
```

Execute com duplo clique ou pelo terminal:

```bat
cd projects\services\bundle-code
run_bundle.bat
```

## Casos avançados e dicas

### Selecionar por lista (`--list`)

Crie `lista.txt` com caminhos relativos (um por linha):

```
backend/src/controllers/UserController.ts
backend/src/services/UserService.ts
frontend/src/pages/AiAgentsPage.tsx
```

Rode:

```bash
python bundle_code.py --root seu-projeto --mode single -o pacote.txt --list lista.txt --fence --comment-header
```

### Extensões

Por padrão, o script já considera várias extensões de texto/código. Para restringir:

```bash
--ext .ts --ext .tsx --ext .json
```

### Excluir pastas

Use prefixos relativos ao `--root`:

```bash
-x "backend/node_modules/" -x "frontend/node_modules/" -x "backend/dist/"
```

### Nunca cortar arquivo ao trocar de parte

Com `--max-lines`, o script só faz a troca de parte **antes** de escrever um arquivo que ultrapassaria o limite, garantindo integridade do bloco.

### Cabeçalho e fences

- `--comment-header` prefixa os cabeçalhos com `//`, útil para TS/JS.
- `--fence` envolve o conteúdo em blocos markdown com linguagem inferida pela extensão.

### Manter extensão no ZIP

Se preferir não converter para `.txt` no modo `tree`:

```bash
--no-to-txt --comment-header
```

## Erros comuns

- **“Nenhum arquivo encontrado”**: ajuste `--include`/`--list`/`--ext`.
- **Caminhos de exclusão não funcionando**: confirme se o prefixo está relativo ao `--root`.
- **Python não encontrado**: verifique `python --version` e o PATH.
- **Barra invertida vs barra normal**: no Git Bash, prefira `/` nas paths e globs.

---

Pronto. Com isso você consegue reproduzir os dois modos de empacote e tem comandos prontos para Git Bash, PowerShell e CMD.
