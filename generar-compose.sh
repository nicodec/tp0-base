#!/bin/bash
echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Uso: $0 <nombre_del_archivo> <cantidad_de_clientes>"
  exit 1
fi
python3 compose_generator.py --filename $1 --clients $2