# ovos-PHAL-plugin-mk2-v6-fan-control

**Compatible with**
* Mycroft Mark2 dev kit

# Usage

There are a few ways for this plugin to get enabled.

* Enable manually

Add this to your `~/.config/mycroft/mycroft.conf`

```json
{
    "PHAL": {
        "ovos-PHAL-plugin-mk2-v6-fan-control": {
            "enabled": true
        }
    }
}
```
With this configuration, no other validation checks are made.  It is assuming you have a compatible HAT installed.

* Automatically with [ovos-i2csound](https://github.com/OpenVoiceOS/ovos-i2csound)

When `ovos-i2csound` is installed and running, it creates a file at `/etc/OpenVoiceOS/i2c_platform` with the HAT name it detected.  This plugin then checks that file and if a compatible HAT is detected, the plugin is activated.

* Automatically with hardware detection

If the above two options don't work, the plugin tries to detect a compatible HAT using `i2c-detect`.  If a compatible device address is found, the plugin will activate.

From this point, if you are running OVOS on a Mark2 dev kit, your fan should be automatically controlled.
