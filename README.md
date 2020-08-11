# fake_piano
Interpreta piezas musicales en un piano digital sin saber como usarlo.

Las notas tocadas en el piano serán sustituidas por las indicadas en un archivo MIDI antes de reproducirse, permitiendo interpretar la melodía original.

Aunque el programa ha sido pensado para usar un piano digital como dispositivo de entrada y un puerto MIDI como salida, es posible usar otros medios de entrada y de salida.

## Instalación
### Requisitos mínimos
Los scripts requieren *Pyton 3* para ejecutarse. Además son necesarios ciertos módulos y herramientas para su correcto funcionamiento.

* [Mido](https://pypi.org/project/mido/) - Para trabajar con archivos MIDI
```
pip install mido
```
* [python-rtmidi](https://pypi.org/project/python-rtmidi/) - Para gestionar puertos MIDI
```
pip install python-rtmidi
```

### Requisitos opcionales
Es posible ampliar la funcionalidad en cuanto a dispositivos de entrada y salida posibles, aunque para ello puede ser necesario instalar módulos externos.

* [pyFluidSynth](https://github.com/nwhitehead/pyfluidsynth) - Para usar como salida el sintetizador FluidSynth.
```
pip install pyFluidSynth
```
* [pynput](https://pypi.org/project/pynput/) - Para usar como entrada el teclado del ordenador.
```
pip install pynput
```
* [pyPS4Controller](https://pypi.org/project/pyPS4Controller/) - Para usar como entrada un controlador DualShock 4.
```
pip install pyPS4Controller
```

## Uso básico
El programa consta de dos partes básicas, la lectura de los archivos MIDI y su reproducción. Las clases correspondientes a cada tarea principal son Reader y Player respectivamente.
<br>El objeto Reader es usado para leer un archivo MIDI y crear un objeto (Playable) que Player es capaz de reproducir. 
<br>El objeto Player se encarga de leer los mensajes enviados por el dispositivo de entrada elegido y modificarlos antes de enviarlos al dispositivo de salida.
