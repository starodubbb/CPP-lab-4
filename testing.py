import unittest

import main

class TestVirtualMachine(unittest.TestCase):
    def setUp(self):
        # global R, F, bytecode, nreg, count
        main.count = 0
        main.nreg = 256
        main.F = [0] * main.nreg
        main.R = [0] * main.nreg
        main.bytecode = []

    def test_idle(self):
        main.bytecode = [0x00,  # IDLE
                         0x00,  # IDLE
                         0x00]  # IDLE

        main.run()
        flag = all(value == 0 for (value) in main.F)
        if not flag:
            self.assertTrue(flag)

        flag = all(value == 0 for (value) in main.R)
        if not flag:
            self.assertTrue(flag)

        flag = True if main.count == 3 else False
        self.assertTrue(flag)

    def test_load(self):
        main.bytecode = [0x01,  # load 0xFF00 (65280) to R0 , bigendian
                         0xFF,
                         0x00,
                         0x00]
        main.run()
        self.assertEqual(main.R[0x00], 0xFF00)

    def test_add(self):
        main.bytecode = [
            0x01,  # load 0xFF00 (65280) to R0 , bigendian
              0xFF,
              0x00,
              0x00,  # R0
            0x01,  # load 0x0003 to R1, bigendian
              0x00,
              0x03,
              0x01,  # R1
            0x02,  # add R0 to R1 and place to R2
              0x00,  # R0
              0x01,  # R1
              0x02]  # R2  /// R2 = R1 + R0
        main.run()
        self.assertEqual(main.R[0x02], 65283)

    def test_jump_if_not_zero(self):
        main.bytecode = [
        0x01,  # load
            0x00,  # 0x0001
            0x01,
            0x00,  # R0
        0x01,  # load
            0x00,  # 0x0003
            0x03,
            0x01,  # R0
        0x04,
            0x00,  # if R0 != 0
            0x01]  # R1 where to jump

        main.run()
        self.assertEqual(main.count, 14)

    def test_subtract(self):
        main.bytecode = [0x01,  # load 0xFF00 (65280) to R0 , bigendian
              0xFF,
              0x00,
              0x00,  # R0
            0x01,  # load 0x0003 to R1, bigendian
              0x00,
              0x03,
              0x01,  # R1
            0x05,  # sub R0 to R1 and place to R2
              0x00,  # R0
              0x01,  # R1
              0x02]  # R2  /// R2 = R1 - R0
        main.run()
        self.assertEqual(main.R[0x02], 65277)

    def test_jump_if_more(self):
        main.bytecode = [0x01,  # load 0xFF00 (65280) to R0 , bigendian
              0xFF,
              0x00,
              0x00,  # R0
            0x01,  # load 0x0003 to R1, bigendian
              0x00,
              0x03,
              0x01,  # R1
            0x01, # load
              0x00, # 0x0001
              0x01,
              0x03, # R3
            0x06, # Jump Ra > Rb
              0x00, # if R0 > R1
              0x01,
              0x03]
        main.run()
        self.assertEqual(main.count, 17)

    def test_halt(self):
        main.bytecode = [
            0x00,
            0x00,
            0x00,
            0xB0,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00]

        main.run()
        self.assertEqual(main.count, 13)

    def test_reset(self):
        main.bytecode = [0x01,  # load 0xFF00 (65280) to R0 , bigendian
              0xFF,
              0x00,
              0x00,  # R0
            0x01,  # load 0x0003 to R1, bigendian
              0x00,
              0x03,
              0x01,  # R1
            0x05,  # sub R0 to R1 and place to R2
              0x00,  # R0
              0x01,  # R1
              0x02,  # R2  /// R2 = R1 - R0
            0x01, # load
              0x00, # 0x0001
              0x01,
              0x03, # R3,
            0xB1]

        main.run()

        flag = all(value == 0 for (value) in main.F)
        if not flag:
            self.assertTrue(flag)

        flag = all(value == 0 for (value) in main.R)
        if not flag:
            self.assertTrue(flag)

        flag = True if main.count == 17 else False
        self.assertTrue(flag)

    def test_jump_if_equal(self):
        main.bytecode = [0x01,  # load 0xFF00 (65280) to R0 , bigendian
              0xFF,
              0x00,
              0x00,  # R0
            0x01,  # load 0xFF00 (65280) to R1, bigendian
              0xFF,
              0x00,
              0x01,  # R1
            0x01, # load
              0x00, # 0x0001
              0x01,
              0x03, # R3
            0xB3, # Jump Ra == Rb
              0x00,
              0x01,
              0x03]
        main.run()
        self.assertEqual(main.count, 17)

    def test_increment(self):
        main.bytecode = [
            0x01,  # load 0xFF00 (65280) to R0 , bigendian
              0xFF,
              0x00,
              0x00,  # R0
            0xB4,
              0x00]
        main.run()
        self.assertEqual(main.R[0x00], 0xFF01)

    def test_zero(self):
        main.bytecode = [
            0x01,  # load 0xFF00 (65280) to R0 , bigendian
              0xFF,
              0x00,
              0x00,  # R0
            0xB5,
              0x00]
        main.run()
        self.assertEqual(main.R[0x00], 0)
