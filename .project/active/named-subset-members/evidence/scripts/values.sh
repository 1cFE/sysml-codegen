#!/bin/bash
# usage: values.sh <src repo root> <outdir> <shape dir>...
R=$1; OUT=$2; shift 2
cd $R; set -a; . /home/reid/src/sysml-codegen/.env; set +a
E=/home/reid/src/sysml-codegen/.project/active/named-subset-members/evidence
D=/home/reid/src/sysml-codegen/.project/active/repeated-rollup-collision/evidence/double-count
for shape in "$@"; do
  n=$(basename $shape); rm -rf $OUT/$n; mkdir -p $OUT/$n
  g=$(PYTHONPATH=$R /home/reid/src/sysml-codegen/.venv/bin/python $E/scripts/gen.py $shape $OUT/$n/generated_code 2>&1 | tail -1)
  if [[ "$g" == *"generated"* ]] && [[ "$g" != *"REFUSED ["* ]]; then
    v=$(PYTHONPATH=$R/src:$R:/home/reid/src/teax/packages/teax-simkit /home/reid/src/dc3/.venv/bin/python $D/scripts/run_pkg.py $OUT/$n/generated_code generated_code $OUT/$n/run 2>&1 | grep -v -e params -e manifest | tr '\n' ' ')
    echo "$n: $v"
  else
    echo "$n: $g"
  fi
done
