#!/bin/bash

echo -n "igresa el primer numero"
read num1

echo -n "igresa el segundo numero"
read num2

suma=$((num1 + num2))
resta=$((num1 - num2))

echo "La suma de $num1 y $num2 es $suma"
echo "La resta de $num1 y $num2 es $resta"
