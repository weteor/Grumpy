### cos(y) Kong

30 or 36 key 3row keyboards with col stagger

![top](img/both_top.png)

## Features

- single pcb with optional break off outer colums 
- Hotswap sockets (MX)
- onboard rp2040
- production files for pcba
- case files are supplied (stl, dxf, as well as cadquery files)
- QMK with vial support
- completely open source, permissive license ([CERN-OHL-P](https://cern-ohl.web.cern.ch/home))

## Want one?

All production files you need to build your own board can be found [here](./prod/).

The case has no bottom and ends right below the HS Sockets. You may either it as is, but preferably use some 2-3mm self-adhesive neopren on the whole pcb. The case may be hard to print on a FDM Printer, so maybe use a service to print it in resin. The cases on the picture are both made from white resin and were spraypainted.

It's advised to get the pcb's preassembled, since the MCU is really hard to solder per hand. Pick and place as well as BOM files can be found in the prod folder.

Apart from the pcb and optionally a case you need:
- 30-36 hotswap sockets
- 30-36 of your favourite switches

just solder the HS Socket, plug in your switches and you should be good to go.

### firmware
firmware configs for qmk and vial can be found in the [firmware folder].

The first time the pcb is plugged in, the bootloader will provide a drive to upload the firmware file. 

### the rest

Everything in this repository is free to use however you might see fit. If you want to support me and my projects, please consider linking back to this repository if you build/change/use anything.

If you would like to send me a tip, you could do it [here](https://ko-fi.com/weteor) (Please don't feel like you have to).

### more pictures

![top](img/cosy_top.png)
