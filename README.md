# SupRISE Linear Langmuir Probe Array — Control & Display

Real-time data acquisition, display, and logging for a 5-probe linear Langmuir probe array on the SupRISE experiment using a LabJack T8.

---

## Requirements

- Python 3.9+
- LabJack T8 connected via USB (serial `480010850`)
- Python packages:

```
pip install pyqt5 pyqtgraph numpy scipy labjack-ljm seabreeze openpyxl ujson pandas
```

---

## File Structure

```
.
├── main.py              Entry point — launches the GUI
├── mux_scan.py          Launcher for the standalone MUX scanner
├── src/                 Application and analysis source code
│   ├── paths.py         Project-relative paths to Data/ (no machine-specific paths)
│   ├── GUImain.py       Qt application and main window
│   ├── GUIcontrol.py    Left panel: probe control widgets
│   ├── GUIdisplay.py    Right panel: live pyqtgraph IV plots
│   ├── GUIthreads.py    Background plot polling thread
│   ├── IO.py            LabJack acquisition, data manager, GUI signals
│   ├── IODevice.py      Device abstraction (LabJack, etc.)
│   ├── LJ_DAQ.py        Low-level LabJack LJM port wrapper
│   ├── DataManager.py   Shot directories, CSV logging, Excel summary, settings JSON
│   ├── Utils.py         Signal processing utilities
│   ├── mux_scan.py      MUX scanner implementation
│   └── analysis/        Offline Langmuir analysis scripts
│       ├── runShotAnalysis.py
│       ├── langmuir_support_functions.py
│       └── callibration.py
└── Data/
    ├── supRISEshots.xlsx     Excel log of all recorded shots
    └── SHOT_DATA/            One subdirectory per shot
        └── {SHOT_NUM}/
            ├── settings.json
            └── RAW_DATA/
                ├── LAB_JACK_INPUT.csv
                └── LAB_JACK_OUTPUT.csv
```

---

## LabJack T8 Pin Assignments (Main Application)

| Channel  | LabJack Pin | Signal        |
|----------|-------------|---------------|
| AIN0     | Analog in   | Langmuir sweep voltage |
| AIN1     | Analog in   | Probe 1 current (shunt voltage) |
| AIN2     | Analog in   | Probe 2 current |
| AIN3     | Analog in   | Probe 3 current |
| AIN4     | Analog in   | Probe 4 current |
| AIN5     | Analog in   | Probe 5 current |

Range: ±10 V on all channels. Resolution index: 5.

The voltage channel is converted to physical voltage by `LANG_VOL × 10.417`. Current channels are converted by dividing the shunt voltage by the entered shunt resistance.

---

## Running the Main Application

```bash
python main.py
```

The GUI opens two panels:

**Left — Control panel**
- **Resistance (ohms):** Enter the shunt resistor value used to measure probe current, then click **Change resistance**. Defaults to 50 Ω.
- **Shot number:** Five-digit identifier for the logging session. Leave blank to auto-increment from the last saved shot.
- **Comment:** Free-text annotation saved with the shot metadata.
- **Start logging / Stop logging:** Begins or ends data capture to disk.

**Right — Display panel**
Six live scatter plots update at ~10 FPS:
1. All 5 probes overlaid (current vs. applied voltage)
2–6. Individual IV curves for probes 1–5

---

## Data Output

Each logging session creates:

```
Data/SHOT_DATA/{SHOT_NUM}/
    settings.json           Shot metadata (shot number, date, time, resistance, comment, duration)
    RAW_DATA/
        LAB_JACK_INPUT.csv  TIME, LANG_VOL, LANG_CUR_1 … LANG_CUR_5 (raw voltages, unprocessed)
        LAB_JACK_OUTPUT.csv Output device log
```

`Data/supRISEshots.xlsx` is updated with one row per shot containing: shot number, date, time, comment, resistance, log duration, start time, and end time.

Shot data and the Excel log live under `Data/` at the project root. Paths are resolved in `src/paths.py` relative to the repository, so no per-machine path edits are required.

---

## Standalone MUX Scanner (`mux_scan.py`)

Scans all 16 channels of an ADG726 multiplexer independently of the main GUI.

### Wiring

| ADG726 Pin | LabJack Pin |
|------------|-------------|
| A0         | FIO0        |
| A1         | FIO1        |
| A2         | FIO2        |
| A3         | FIO3        |
| EN         | FIO4        |
| CSA        | FIO5        |
| CSB        | FIO6        |
| WR         | FIO7        |
| DA (out)   | AIN0        |
| DB (out)   | AIN1        |

### Usage

```bash
python mux_scan.py [options]
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--mode` | `pc` \| `scope` | `pc` | `pc` shows a live matplotlib DA/DB voltage plot. `scope` holds each channel for the dwell period and prints the address bits — intended for oscilloscope probing. |
| `--channels` | string | `1-16` | Channels to scan. Accepts comma-separated values (`1,4,8,16`), ranges (`1-8`), or a mix (`1-4,8,16`). Valid range: 1–16. |
| `--dwell` | float (s) | `1.0` | Time in seconds to hold each channel before advancing. |
| `--sample-rate` | float (Hz) | `50.0` | Samples per second in `pc` mode. Has no effect in `scope` mode. |
| `--cycles` | int | unlimited | Number of full channel-list sweeps before exiting. Omit to run indefinitely. |
| `--dry-run` | flag | off | Simulates hardware writes and reads without opening the LabJack. Useful for verifying channel logic. |

### Examples

```bash
# Live plot, all channels, 1 s dwell
python mux_scan.py --mode pc

# Scope mode, 5 s per channel
python mux_scan.py --mode scope --dwell 5

# Live plot, selected channels only
python mux_scan.py --channels 1,4,8,16 --mode pc

# Verify channel logic without hardware
python mux_scan.py --dry-run --channels 1,2,16
```

Press **Ctrl+C** to stop at any time.
