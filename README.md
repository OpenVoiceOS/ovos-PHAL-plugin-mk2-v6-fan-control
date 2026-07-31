# ovos-PHAL-plugin-mk2-v6-fan-control

This is an OVOS PHAL plugin. It controls the fan on the Mark2 dev kit hardware.

**Compatible with**
* Mycroft Mark2 dev kit

## Install

```console
pip install ovos-PHAL-plugin-mk2-fan-control
```

## Usage

The plugin activates in one of three ways.

* Enable manually

Add this to your `~/.config/mycroft/mycroft.conf`.

```json
{
    "PHAL": {
        "ovos-PHAL-plugin-mk2-v6-fan-control": {
            "enabled": true
        }
    }
}
```

With this configuration, the plugin makes no other validation checks. It assumes you have a compatible HAT installed.

* Automatically with [OpenVoiceOS/ovos-i2csound](https://github.com/OpenVoiceOS/ovos-i2csound)

When `ovos-i2csound` is installed and running, it creates a file at `/etc/OpenVoiceOS/i2c_platform` with the name of the HAT it detected. This plugin then reads that file. If it finds a compatible HAT, it activates.

* Automatically with hardware detection

If the two options above do not work, the plugin tries to detect a compatible HAT with `i2c-detect`. If it finds a compatible device address, it activates.

Once active on a Mark2 dev kit, the plugin controls your fan automatically.

### Configuration

You can set the temperature at which the fan turns on.

```json
{
    "PHAL": {
        "ovos-PHAL-plugin-mk2-v6-fan-control": {
            "max_fanless_temp": 60.0,
            "max_fan_temp": 80.0
        }
    }
}
```

* `max_fanless_temp` — the temperature at which the fan turns on.
* `max_fan_temp` — the temperature at which the fan runs at 100%.

## Related projects

* [OpenVoiceOS/ovos-i2csound](https://github.com/OpenVoiceOS/ovos-i2csound) — detects the installed HAT and triggers this plugin automatically.

## License

This project is licensed under the MIT license. See [LICENSE](LICENSE) for the full text.
