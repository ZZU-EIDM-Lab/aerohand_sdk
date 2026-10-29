import struct
import unittest

from aero_open_sdk.aero_hand import (
    AeroHand,
    GET_CURR,
    GET_POS,
    GET_TEMP,
    GET_VEL,
)
from aero_open_sdk.aero_hand_constants import AeroHandConstants


class FakeSerial:
    def __init__(self, frame):
        self.frame = frame

    def reset_input_buffer(self):
        pass

    def read(self, size):
        assert size == 16
        return self.frame


def hand_with_frame(opcode, values, valid_mask=0x7F, signed=False, legacy=False):
    flags = 0 if legacy else 0x80 | valid_mask
    format_code = "h" if signed else "H"
    frame = struct.pack(f"<2B7{format_code}", opcode, flags, *values)
    hand = AeroHand.__new__(AeroHand)
    hand.ser = FakeSerial(frame)
    hand._send_data = lambda requested_opcode: None
    constants = AeroHandConstants()
    hand.actuation_lower_limits = constants.actuation_lower_limits
    hand.actuation_upper_limits = constants.actuation_upper_limits
    return hand


class MetricFrameTests(unittest.TestCase):
    def test_missing_servo_does_not_hide_other_readings(self):
        valid_mask = 0x7F & ~(1 << 3)
        current = hand_with_frame(GET_CURR, [1, -2, 3, 0, 5, 6, 7], valid_mask, signed=True)
        temperature = hand_with_frame(GET_TEMP, [31, 32, 33, 0, 35, 36, 37], valid_mask)
        speed = hand_with_frame(GET_VEL, [1, -2, 3, 0, 5, 6, 7], valid_mask, signed=True)
        position = hand_with_frame(GET_POS, [0, 32768, 65535, 0, 32768, 0, 65535], valid_mask)

        self.assertEqual(current.get_actuator_currents(), [6.5, -13.0, 19.5, None, 32.5, 39.0, 45.5])
        self.assertEqual(temperature.get_actuator_temperatures(), [31.0, 32.0, 33.0, None, 35.0, 36.0, 37.0])
        speeds = speed.get_actuator_speeds()
        self.assertIsNone(speeds[3])
        for index, raw_value in enumerate([1, -2, 3, 0, 5, 6, 7]):
            if index != 3:
                self.assertAlmostEqual(speeds[index], raw_value * 0.732)
        positions = position.get_actuations()
        self.assertIsNone(positions[3])
        self.assertEqual(positions[0], position.actuation_lower_limits[0])
        self.assertEqual(positions[2], position.actuation_upper_limits[2])

    def test_old_firmware_frame_without_mask_remains_supported(self):
        hand = hand_with_frame(GET_TEMP, [31, 32, 33, 0, 35, 36, 37], legacy=True)
        self.assertEqual(hand.get_actuator_temperatures()[3], 0.0)

    def test_joint_conversion_requires_all_actuators(self):
        hand = hand_with_frame(GET_POS, [0] * 7, valid_mask=0x7E)
        self.assertIsNone(hand.get_joint_positions_compact())


if __name__ == "__main__":
    unittest.main()
