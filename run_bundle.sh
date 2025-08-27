#!/bin/bash
# gerar txt único
python bundle_code.py \
  --root ../../space-sales \
  --mode single -o ../../space-sales/export-single.txt \
  -i "backend/src/**/*.ts" \
  -i "frontend/src/**/*.tsx" \
  -x "backend/node_modules/" -x "frontend/node_modules/" \
  --comment-header --fence --max-lines 4000

# gerar zip com estrutura
python bundle_code.py \
  --root ../../space-sales \
  --mode tree -o ../../space-sales/export-zip.zip \
  -i "backend/src/**/*.ts" \
  -i "frontend/src/**/*.tsx" \
  -x "backend/node_modules/" -x "frontend/node_modules/"

# cd projects/testes/utils/bundle-code
# chmod +x run_bundle.sh
# ./run_bundle.sh
