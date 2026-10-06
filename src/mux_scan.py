#!/usr/bin/env python3
"""
Standalone ADG726 MUX scanner for a LabJack T8.

Default wiring:
    A0=FIO0, A1=FIO1, A2=FIO2, A3=FIO3
    EN=FIO4, CSA=FIO5, CSB=FIO6, WR=FIO7
    DA=AIN0, DB=AIN1

Examples:
    python mux_scan.py --mode pc
    python mux_scan.py --mode scope --dwell 5
    python mux_scan.py --channels 1,4,8,16 --mode pc
    python mux_scan.py --dry-run --channels 1,2,16
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from collections import deque
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol


LABJACK_DEVICE_TYPE = "T8"
LABJACK_CONNECTION = "USB"
LABJACK_SERIAL = "480010850"

ADDRESS_PINS = {
    "A0": "FIO0",
    "A1": "FIO1",
    "A2": "FIO2",
    "A3": "FIO3",
}

CONTROL_PINS = {
    "EN": "FIO4",
    "CSA": "FIO5",
    "CSB": "FIO6",
    "WR": "FIO7",
}

ANALOG_INPUTS = {
    "DA": "AIN0",
    "DB": "AIN1",
}

AIN_RANGE_VOLTS = 10.0
AIN_WARN_VOLTS = 9.5
DEFAULT_DWELL_SECONDS = 1.0
DEFAULT_SAMPLE_RATE_HZ = 50.0
PLOT_HISTORY_SECONDS = 20.0


@dataclass(frozen=True)
class ScanSample:
    elapsed_s: float
    channel: int
    da_v: float
    db_v: float


class LabJackLike(Protocol):
    """Subset of the LabJack LJM API used by the MUX controller."""

    def write_name(self, name: str, value: float) -> None: ...
    def read_name(self, name: str) -> float: ...
    def close(self) -> None: ...


def address_to_string(channel: int) -> str:
    return f"{channel - 1:04b}"


class DryRunLabJack:
    """LabJack-shaped object that simulates address pins and analog reads."""

    def __init__(self) -> None:
        self._address_bits: dict[str, int] = {pin: 0 for pin in ADDRESS_PINS}
        self._start_time = time.monotonic()
        print("[dry-run] LabJack not opened")

    def write_name(self, name: str, value: float) -> None:
        for pin_name, register in ADDRESS_PINS.items():
            if name == register:
                self._address_bits[pin_name] = int(value) & 0b1
                break
        print(f"[dry-run] WRITE {name} = {value:g}")

    def read_name(self, name: str) -> float:
        elapsed = time.monotonic() - self._start_time
        base = 0.1 * self._current_channel
        if name == ANALOG_INPUTS["DA"]:
            value = base + 0.25 * math.sin(elapsed * 2.0)
        elif name == ANALOG_INPUTS["DB"]:
            value = -base + 0.25 * math.cos(elapsed * 2.0)
        else:
            value = 0.0
        print(f"[dry-run] READ  {name} -> {value:.6f}")
        return value

    def close(self) -> None:
        print("[dry-run] LabJack closed")

    @property
    def _current_channel(self) -> int:
        address = (
            self._address_bits["A0"]
            | (self._address_bits["A1"] << 1)
            | (self._address_bits["A2"] << 2)
            | (self._address_bits["A3"] << 3)
        )
        return address + 1


class RealLabJack:
    """Thin wrapper around labjack.ljm for the live T8 device."""

    def __init__(self, device_type: str, connection: str, serial: str) -> None:
        try:
            from labjack import ljm
        except ImportError as exc:
            raise RuntimeError(
                "Could not import labjack.ljm. Install the LabJack LJM Python "
                "package, for example: python -m pip install labjack-ljm"
            ) from exc

        self._ljm = ljm
        self._handle = ljm.openS(device_type, connection, serial)

        for ain in ANALOG_INPUTS.values():
            ljm.eWriteName(self._handle, f"{ain}_RANGE", AIN_RANGE_VOLTS)

    def write_name(self, name: str, value: float) -> None:
        self._ljm.eWriteName(self._handle, name, float(value))

    def read_name(self, name: str) -> float:
        return float(self._ljm.eReadName(self._handle, name))

    def close(self) -> None:
        self._ljm.close(self._handle)


class ADG726Controller:
    """Drives ADG726 enable and address pins through a LabJack-like backend."""

    def __init__(self, labjack: LabJackLike) -> None:
        self._labjack = labjack

    def enable(self) -> None:
        self._labjack.write_name(CONTROL_PINS["EN"], 0)
        self._labjack.write_name(CONTROL_PINS["CSA"], 0)
        self._labjack.write_name(CONTROL_PINS["CSB"], 0)
        self._labjack.write_name(CONTROL_PINS["WR"], 0)

    def disable(self) -> None:
        self._labjack.write_name(CONTROL_PINS["EN"], 1)

    def select_channel(self, channel: int) -> str:
        address = channel - 1
        bits = {
            "A0": address & 0b0001,
            "A1": (address >> 1) & 0b0001,
            "A2": (address >> 2) & 0b0001,
            "A3": (address >> 3) & 0b0001,
        }
        for pin_name in ("A0", "A1", "A2", "A3"):
            self._labjack.write_name(ADDRESS_PINS[pin_name], bits[pin_name])
        return address_to_string(channel)

    def read_outputs(self) -> dict[str, float]:
        return {
            "DA": self._labjack.read_name(ANALOG_INPUTS["DA"]),
            "DB": self._labjack.read_name(ANALOG_INPUTS["DB"]),
        }


def parse_channels(raw_channels: str) -> list[int]:
    """Parse a comma- and range-separated channel spec like '1-4,8,12'."""
    channels: list[int] = []
    for part in raw_channels.split(","):
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            start_raw, end_raw = token.split("-", 1)
            start = int(start_raw)
            end = int(end_raw)
            step = 1 if start <= end else -1
            channels.extend(range(start, end + step, step))
        else:
            channels.append(int(token))

    if not channels:
        raise argparse.ArgumentTypeError("At least one channel is required.")

    invalid = [channel for channel in channels if channel < 1 or channel > 16]
    if invalid:
        raise argparse.ArgumentTypeError(
            "ADG726 channels must be between 1 and 16. "
            f"Invalid value(s): {invalid}"
        )
    return channels


def warn_if_near_limit(readings: dict[str, float]) -> None:
    for name, value in readings.items():
        if abs(value) >= AIN_WARN_VOLTS:
            print(
                f"WARNING: {name} is {value:.3f} V, close to the "
                f"+/-{AIN_RANGE_VOLTS:g} V LabJack input range.",
                file=sys.stderr,
            )


def sleep_interruptibly(seconds: float) -> None:
    """Sleep in short slices so KeyboardInterrupt is delivered promptly."""
    end_time = time.monotonic() + seconds
    while True:
        remaining = end_time - time.monotonic()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 0.1))


def run_scope_mode(
    mux: ADG726Controller,
    channels: Sequence[int],
    dwell_s: float,
    max_cycles: int | None,
) -> None:
    """Hold each channel for `dwell_s` seconds, suitable for scope probing."""
    cycle = 0
    while max_cycles is None or cycle < max_cycles:
        for channel in channels:
            bit_string = mux.select_channel(channel)
            print(f"Channel {channel:2d} selected, A3..A0={bit_string}")
            sleep_interruptibly(dwell_s)
        cycle += 1


def run_pc_mode(
    mux: ADG726Controller,
    channels: Sequence[int],
    dwell_s: float,
    sample_rate_hz: float,
    max_cycles: int | None,
) -> None:
    """Cycle through `channels`, sample DA/DB, and update a live plot."""
    import matplotlib.pyplot as plt

    sample_interval_s = 1.0 / sample_rate_hz
    samples: deque[ScanSample] = deque()
    start_time = time.monotonic()

    plt.ion()
    fig, ax = plt.subplots()
    da_line, = ax.plot([], [], label="DA")
    db_line, = ax.plot([], [], label="DB")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (V)")
    ax.set_ylim(-AIN_RANGE_VOLTS, AIN_RANGE_VOLTS)
    ax.grid(True)
    ax.legend(loc="upper right")

    cycle = 0
    while max_cycles is None or cycle < max_cycles:
        for channel in channels:
            bit_string = mux.select_channel(channel)
            channel_end = time.monotonic() + dwell_s

            while time.monotonic() < channel_end:
                readings = mux.read_outputs()
                warn_if_near_limit(readings)

                elapsed = time.monotonic() - start_time
                samples.append(
                    ScanSample(
                        elapsed_s=elapsed,
                        channel=channel,
                        da_v=readings["DA"],
                        db_v=readings["DB"],
                    )
                )

                cutoff = elapsed - PLOT_HISTORY_SECONDS
                while samples and samples[0].elapsed_s < cutoff:
                    samples.popleft()

                x_vals = [sample.elapsed_s for sample in samples]
                da_vals = [sample.da_v for sample in samples]
                db_vals = [sample.db_v for sample in samples]

                da_line.set_data(x_vals, da_vals)
                db_line.set_data(x_vals, db_vals)
                ax.set_xlim(max(0.0, elapsed - PLOT_HISTORY_SECONDS), elapsed + 0.1)
                ax.set_title(f"ADG726 channel {channel}, A3..A0={bit_string}")
                fig.canvas.draw_idle()
                plt.pause(0.001)

                time.sleep(sample_interval_s)

        cycle += 1


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Auto-scan ADG726 MUX channels with a LabJack T8."
    )
    parser.add_argument(
        "--mode",
        choices=("pc", "scope"),
        default="pc",
        help="pc shows a live DA/DB plot; scope holds each channel for probing.",
    )
    parser.add_argument(
        "--channels",
        type=parse_channels,
        default=parse_channels("1-16"),
        help="Channels to scan, e.g. 1-16 or 1,4,8,16.",
    )
    parser.add_argument(
        "--dwell",
        type=float,
        default=DEFAULT_DWELL_SECONDS,
        help="Seconds to stay on each channel.",
    )
    parser.add_argument(
        "--sample-rate",
        type=float,
        default=DEFAULT_SAMPLE_RATE_HZ,
        help="PC display reads per second.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print LabJack writes/reads without opening hardware.",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=None,
        help="Optional number of scan cycles before exiting.",
    )
    return parser


def validate_args(args: argparse.Namespace) -> None:
    if args.dwell <= 0:
        raise SystemExit("--dwell must be greater than 0.")
    if args.sample_rate <= 0:
        raise SystemExit("--sample-rate must be greater than 0.")
    if args.cycles is not None and args.cycles <= 0:
        raise SystemExit("--cycles must be greater than 0 when provided.")


def open_labjack(dry_run: bool) -> LabJackLike:
    if dry_run:
        return DryRunLabJack()
    return RealLabJack(LABJACK_DEVICE_TYPE, LABJACK_CONNECTION, LABJACK_SERIAL)


def print_startup(args: argparse.Namespace) -> None:
    channel_text = ", ".join(str(channel) for channel in args.channels)
    print("ADG726 MUX scanner")
    print(f"Mode: {args.mode}")
    print(f"Channels: {channel_text}")
    print(f"Dwell: {args.dwell:g} s/channel")
    if args.mode == "pc":
        print(f"Sample rate: {args.sample_rate:g} Hz")
        print(
            f"Reading {ANALOG_INPUTS['DA']} as DA and "
            f"{ANALOG_INPUTS['DB']} as DB."
        )
    print("Press Ctrl+C to stop.")


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    validate_args(args)
    print_startup(args)

    labjack = open_labjack(args.dry_run)
    mux = ADG726Controller(labjack)

    try:
        mux.enable()
        if args.mode == "scope":
            run_scope_mode(mux, args.channels, args.dwell, args.cycles)
        else:
            run_pc_mode(
                mux,
                args.channels,
                args.dwell,
                args.sample_rate,
                args.cycles,
            )
    except KeyboardInterrupt:
        print("\nStopping scan.")
    finally:
        try:
            mux.disable()
        finally:
            labjack.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
