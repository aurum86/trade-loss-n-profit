# trade-loss-n-profit
A project to calculate the Loss and Profit using FIFO.
This comes handy if the government demands to declare profit and loss.

## Features
Currently, supported reports:
* Kraken trade report file

## How to run
1. Export trade report from Kraken platform.
2. Place `trades.csv` file into `imports/kraken` folder in project's root dir.
3. Run the following in terminal:
```bash
docker-compose -f docker/docker-compose.yml up
```
4. Enjoy the output:
* in Terminal
* in csv files in `output` dir.

## Donation

If you like this project, and it helped you to save your precious time,
please, don't hesitate to donate some of your assets.
You can donate to these addresses:
* BITCOIN: bc1qpzgtjrdw04ry2kz9ex6g5ygap3qlp7nx38wgge
