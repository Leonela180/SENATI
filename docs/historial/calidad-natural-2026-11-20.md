# Corrección de ampliación y edición por etapas

La usuaria rechazó el aspecto de pintura de la ampliación y del ejemplo de la
artesana. La cadena anterior combinaba reducción de ruido completa, CLAHE y
enfoque RGB; el ejemplo x4 además partía de una copia reducida a 256 px.

## Cambios

- Se retiró CLAHE de la ampliación y se conserva el tono del original.
- La limpieza es opcional y mezcla solo un 20 % de la señal limpiada.
- Ampliación bicúbica y enfoque de luminancia, con corrección limitada a ±3
  niveles por canal. No se enfoca cada canal de color por separado.
- Valores iniciales más suaves: nitidez 0,35 y reducción de ruido desmarcada.
- Versión de resultados identificada como `opencv-4.14.0-natural-v2`.
- Se aclara que x4 no significa 4K ni superresolución generativa.

## Nuevos trabajos reales

- 220: entrada 512×640, salida 2048×2560, x4 sin limpieza y enfoque 0,3.
- 221: ajuste leve de luz y contraste de la artesana, sin cambiar el fondo.
- 222: ampliación x2 de la etapa anterior, de 640×640 a 1280×1280.

Se guardaron las salidas nuevas en la cuenta individual1, álbum
«05 · Ampliacion natural y etapas DEMO». Los trabajos y archivos anteriores
no se borraron ni se modificaron como si hubieran usado el motor nuevo.

La portada y el comparador apuntan a los ejemplos nuevos. El registro privado
está en `private_data/demo_senati/calidad_natural_v2/trabajos.json`, con respaldo
del manifiesto anterior. `corregir_ejemplos_calidad.py` permite reproducir la carga.

## Límite pendiente

Comprobación realizada: 124 pruebas backend aprobadas en 49,18 s, compilación
TypeScript/Vite correcta y verificación de ambos ejemplos en el comparador,
incluidas dimensiones reales y enlaces directos.
Los seis recorridos de navegador afectados también aprobaron en 29,6 s.

Esta corrección reduce artefactos; no transforma una foto borrosa en una foto
con información nueva. La recuperación generativa requeriría otro modelo de
superresolución y una evaluación propia. No se anuncia como implementada.
