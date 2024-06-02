import subprocess
from threading import Event
from os.path import exists

from ovos_plugin_manager.phal import PHALPlugin
from ovos_plugin_manager.templates.phal import PHALValidator
from ovos_utils.log import LOG
from ovos_i2c_detection import is_sj201_v6

I2C_PLATFORM_FILE = "/etc/OpenVoiceOS/i2c_platform"


class Mk2Rev6FanValidator(PHALValidator):
    @staticmethod
    def validate(config=None):
        config = config or {}
        # If the user enabled the plugin no need to go further
        if config.get("enabled"):
            return True
        # Check for a file created by ovos-i2csound
        # https://github.com/OpenVoiceOS/ovos-i2csound/blob/dev/ovos-i2csound#L76
        LOG.debug(f"checking file {I2C_PLATFORM_FILE}")
        if exists(I2C_PLATFORM_FILE):
            with open(I2C_PLATFORM_FILE) as f:
                platform = f.readline().strip().lower()
            LOG.debug(f"detected platform {platform}")
            if platform == "sj201v6":
                return True
            # Try a direct hardware check
        if is_sj201_v6():
            LOG.debug("direct hardware check found v6")
            return True
        LOG.debug("No Validation")
        return False


class Mk2Rev6FanControls(PHALPlugin):
    validator = Mk2Rev6FanValidator

    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-phal-plugin-mk2-devkit-fan", config=config)
        self.fan = R6FanControl()
        self.exit_flag = Event()
        self._max_fanless_temp = self.config.get(
            "max_fanless_temp", 60.0)  # Highest fan-less temp allowed
        self._max_fan_temp = self.config.get(
            "max_fan_temp", 80.0)  # Thermal throttle temp max fan

        if self.config.get("min_fan_temp"):
            self.set_min_fan_temp(float(self.config.get("min_fan_temp")))

    def get_cpu_temp(self):
        cmd = ["cat", "/sys/class/thermal/thermal_zone0/temp"]
        out, err = self.fan.execute_cmd(cmd)
        return float(out.strip()) / 1000

    def set_min_fan_temp(self, new_temp: float):
        """
        Set the temperature at which the fan will turn on.
        @param new_temp: Float temperature in degrees Celsius at which the fan
            will start running. Recommended values are 30.0-60.0
        """
        if new_temp > 80.0:
            LOG.error("Fan will run at maximum speed at 80C; "
                      "min temp must be lower. Setting unchanged.")
            return
        if new_temp < 0.0:
            LOG.error("Requested temperature is below operating range; "
                      "min temp must be more than 0C. Setting unchanged.")
            return
        LOG.info(f"Set fan to turn on at {new_temp}C")
        self._max_fanless_temp = new_temp

    def run(self):
        self.exit_flag = False
        LOG.debug("temperature monitor thread started")
        while not self.exit_flag.wait(30):
            LOG.debug(f"CPU temperature is {self.get_cpu_temp()}")

            current_temp = self.get_cpu_temp()
            if current_temp < self._max_fanless_temp:
                # Below specified fanless temperature
                fan_speed = 0
                LOG.debug(f"Temp below {self._max_fanless_temp}")
            elif current_temp > self._max_fan_temp:
                LOG.warning(f"Thermal Throttling, temp={current_temp}C")
                fan_speed = 100
            else:
                # Specify linear fan curve inside normal operating temp range
                speed_const = 100 / (self._max_fan_temp -
                                     self._max_fanless_temp)
                fan_speed = speed_const * (current_temp -
                                           self._max_fanless_temp)
                LOG.debug(f"temp={current_temp}")

            LOG.debug(f"Setting fan speed to: {fan_speed}")
            self.fan.set_fan_speed(fan_speed)
        LOG.debug("Fan thread received exit signal")

    def shutdown(self):
        self.exit_flag.set()
        self.fan.shutdown()
        try:
            # Turn on Mark2 fan to prevent thermal throttling
            import RPi.GPIO as GPIO
            GPIO.output(self.fan.fan_pin, 0)
        except Exception as e:
            LOG.debug(e)


class R6FanControl:
    # hardware speed range is appx 30-255
    # we convert from 0 to 100
    HDW_MIN = 0
    HDW_MAX = 255
    SFW_MIN = 0
    SFW_MAX = 100

    def __init__(self):
        self.fan_speed = 0
        # self.set_fan_speed(self.fan_speed)

    @staticmethod
    def execute_cmd(cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, )
        out, err = process.communicate()
        try:
            out = out.decode("utf8")
        except Exception as e:
            LOG.exception(e)

        try:
            err = err.decode("utf8")
        except Exception as e:
            LOG.exception(e)

        return out, err

    @staticmethod
    def celcius_to_fahrenheit(temp):
        return (temp * 1.8) + 32

    def speed_to_hdw_val(self, speed):
        out_steps = self.HDW_MAX - self.HDW_MIN
        in_steps = self.SFW_MAX - self.SFW_MIN
        ratio = out_steps / in_steps
        # force compliance
        if speed > self.SFW_MAX:
            speed = self.SFW_MAX
        if speed < self.SFW_MIN:
            speed = self.SFW_MIN

        return int((speed * ratio) + self.HDW_MIN)

    def hdw_val_to_speed(self, hdw_val):
        out_steps = self.SFW_MAX - self.SFW_MIN
        in_steps = self.HDW_MAX - self.HDW_MIN
        ratio = out_steps / in_steps
        # force compliance
        if hdw_val > self.HDW_MAX:
            hdw_val = self.HDW_MAX
        if hdw_val < self.HDW_MIN:
            hdw_val = self.HDW_MIN

        return int(round(((hdw_val - self.HDW_MIN) * ratio) + self.SFW_MIN, 0))

    def hdw_set_speed(self, hdw_speed):
        # force compliance
        if hdw_speed > self.HDW_MAX:
            hdw_speed = self.HDW_MAX
        if hdw_speed < self.HDW_MIN:
            hdw_speed = self.HDW_MIN

        hdw_speed = str(hdw_speed)
        cmd = ["i2cset", "-a", "-y", "1", "0x04", "101", hdw_speed, "i"]
        out, err = self.execute_cmd(cmd)
        LOG.debug(f'out={out}')
        LOG.debug(f'err={err}')

    def set_fan_speed(self, speed):
        self.fan_speed = self.speed_to_hdw_val(speed)
        self.hdw_set_speed(self.fan_speed)

    def get_fan_speed(self):
        return self.hdw_val_to_speed(self.fan_speed)

    def shutdown(self):
        self.set_fan_speed(0)
