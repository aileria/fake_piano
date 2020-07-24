# fake_piano
Interpreta piezas musicales almacenadas como archivos MIDI con un piano digital, sin saber cómo usarlo.
## Instalación
### Requisitos previos
Los scipts requieren *Pyton 3* para ejecutarse. Además son necesarios ciertos módulos y herramientas para un correcto funcionamiento.

* [pyFluidSynth](https://github.com/nwhitehead/pyfluidsynth) - Envoltorio de FluidSynth para Python
```
pip3 install pyFluidSynth
```
* [Mido](https://pypi.org/project/mido/) - Librería para trabajar con mensajes y puertos MIDI
```
pip3 install mido
```
### Requisitos funcionales
Adicionalmente, serán necesarios archivos MIDI y SF2 (soundfont o instrumentos virtuales) no proporcionados en este repositorio.

## Uso básico
Ejecuta el archivo *fake_piano.py*, previamente indicando en este la ruta al archivo MIDI, la ruta al archivo de instrumento virtual .sf2 y el nombre del puerto del piano digital.

Cada tecla pulsada en el piano digital producirá un mensaje MIDI que recibirá el script, el cual sustituirá el valor de la nota tocada por el de la nota siguiente en el MIDI cargado, enviando finalmente este mensaje modificado al sintetizador, que reproducirá el sonido.