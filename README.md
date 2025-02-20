# watch-calibration
Template to create Python packages

## Initial Setup

```bash
./setup.sh
```

## Update Dependencies

Add new dependencies to `requirements.in` and then run:

```bash
./update-deps.sh
```

## Container Usage

All container functionality is made available using the `./run.sh` script. The default functionality is to generate plots and other functionality is made available through passing command line arguments.

### Generate Figures

```bash
./run.sh
```

```bash
./run.sh -g
```

### Jupyter Notebook

To run jupyter notebook in the container and open up a jupyter notebook on your local port 8888, run:

```bash
./run.sh -j
```

Then navigate to the link starting with http://localhost:8888/tree?token=<token> displayed in your terminal.

### ipython Kernel

And to run an ipython kernel in the container, run:

```bash
./run.sh -i
```

Once the ipython prompt shows up, data can be loaded and analysis run with:

```bash
wc = WatchCalibration()
wc.load_audio("data_W241130_W241130.wav")
wc.generate_figures()
... TODO perform analysis command
```

## Publish Package

Get S3-like credentials from: https://archive.org/account/s3.php

TODO
