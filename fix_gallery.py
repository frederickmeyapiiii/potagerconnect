# -*- coding: utf-8 -*-
with open(r'c:\Users\frede\OneDrive - Ecole-IT\Bureau\GoPotager\app\templates\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Améliorer la section photos d'évolution
content = content.replace("Photos d'évolution", "Photos d'evolution")

with open(r'c:\Users\frede\OneDrive - Ecole-IT\Bureau\GoPotager\app\templates\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Modifications de la galerie appliquees avec succes")
