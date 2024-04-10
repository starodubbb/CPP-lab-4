import logging

#
# Cross Platform Virtual Machine
#
# R0 - R255 - 2 bytes, bigendian
#
# Bytecode: 0x00 - idle                             (1 byte)
#           0x01 - Load two bytes to Register B3    (4 bytes), bigendian
#           0x02 - Add B1 and B2 and place to B3    (4 bytes)
#           0x03 - Print B1                         (2 bytes)
#                  for instance 0x05 0x00 prints R1
#           0x04 - if B1 nonzero then jump to next B2 commands (3 bytes)
#           0x05 - Subtract B1 and B2 and place to B3 (4 bytes), bigendian
#           0xA0 - Define a function B1 - function ID, B2 - function length
#           0xA1 - Return from function
#           0xAA - Call function with ID stored in B1
#
################################################################################################
#
#           0xB0 - HALT (stop working) - 1 bytes
#           0xB1 - RESET (reset all memory and data) - 1 bytes
#           0xB2 - DUMP (show all memory) - 1 bytes
#           0xB3 - If Ra == Rb jump to R3 (4 bytes)
#           0xB4 - Increment (add 1 and save at the same cell) - 2 bytes
#           0xB5 - ZERO (set zero into register cell) - 2 bytes

logger = logging.getLogger('my_logger')

logging.basicConfig(
    level=logging.DEBUG  # allow DEBUG level messages to pass through the logger
)

# command count
count = 0

# number of registers
nreg = 256

# 256 functions F[0] ... F[255]
function = {'id': 0, 'length': 0, 'addr': 0, 'return_addr': 0}
F = [0] * nreg

# 256 Registers  R[0] ... R[255]
R = [0] * nreg

bytecode = [0x00,  # idle
            0x01,  # load 0xFF01  to R0 , bigendian
            0xFF,
            0x01,
            0x00,  # R0
            0x01,  # load 0x0300 to R1, bigendian
            0x03,
            0x00,
            0x01,  # R1
            0xB1,  # RESET
            0xB2,  # DUMP
            0x00,  # idle
            0x01,  # load 0x0015 (21) to R0 , bigendian
            0x00,
            0x15,
            0x00,  # R0
            0xB4,  # Increment R0 (21+1=22)
            0x00,  # R0
            0xB5,  # ZERO R0
            0x00,  # R0
            0x00,  # idle
            0x01,  # load 0x0F1F to R0
            0x0F,
            0x0F,
            0x00,  # R0
            0x01,  # load 0x0F1F to R1
            0x0F,
            0x0F,
            0x01,  # R1
            0x01,  # load 0x0001 to R2
            0x00,
            0x01,
            0x02,  # R2
            0xB3,  # If R0 == R1 jump to R2
            0x00,  # R0
            0x01,  # R1
            0x02,  # R2
            0xB0,  # HALT  (skipped)
            0xA0,  # function
            0x11,  # function ID (17)
            0x06,  # length of function in bytes
            0x05,  # Subtract (R2 = R0 - R1)
            0x00,  # R0
            0x01,  # R1
            0x02,  # R2
            0xA1,  # return (end of function)
            0x11,  # The ID of the function we are returning from
            0x01,  # load 0x0011 (17) to R5
            0x00,
            0x11,
            0x05,  # R5
            0xB2,  # DUMP
            0xAA,  # call function
            0x05,  # R5 (function id),
            0xB0,  # HALT
            0x00,  # idle
            0x00,  # idle
            0x00,  # idle
            0x00,  # idle
            0x00]  # idle
# bytecode = []

logging.debug(bytecode)


# Go through all bytes bytes


def run():
    global count, R, F, bytecode, nreg

    while count < len(bytecode):
        # logging.debug(bytecode[count])

        if bytecode[count] == 0x00:  # idle
            logging.debug("IDLE"
                          + " (COUNT = " + str(count) + ")")
            count += 1
            continue

        if bytecode[count] == 0x01:  # load two bytes to R[addr] (4 bytes)
            addr = bytecode[count + 3]
            if addr < nreg:
                R[addr] = bytecode[count + 1] << 8 | bytecode[count + 2]
                logging.debug("R" + str(addr) + "=" + str(R[addr])
                              + " (COUNT = " + str(count) + ")")
            count += 4
            continue

        if bytecode[count] == 0x02:  # R3 = R1 + R2 (4 bytes)
            R[bytecode[count + 3]] = R[bytecode[count + 1]] + R[bytecode[count + 2]]
            logging.debug("Rz = Rx + Ry, Rz=" + str(R[bytecode[count + 3]])
                          + " (COUNT = " + str(count) + ")")
            count += 4
            continue

        if bytecode[count] == 0x03:  # print R* (2 bytes)
            logging.debug("PRINT"
                          + " (COUNT = " + str(count) + ")")
            addr = bytecode[count + 1]
            if addr < nreg:
                logging.debug("R " + str(addr) + "=" + str(R[addr])
                              + " (COUNT = " + str(count) + ")")
            count += 2
            continue

        if bytecode[count] == 0x04:  # If b1 is nonzero then jump to next b2 (3 bytes)
            logging.debug("Jump if B1 != 0 " + str(R[bytecode[count + 1]])
                          + " (COUNT = " + str(count) + ")")
            if R[bytecode[count + 1]]:
                logging.debug("Jump to next B2 " + str(R[bytecode[count + 2]])
                              + " (COUNT = " + str(count) + ")")
                count += R[bytecode[count + 2]]  # this code is not safe
            count += 3
            continue

        if bytecode[count] == 0x05:  # R3 = R1 - R2 (4 bytes)
            R[bytecode[count + 3]] = R[bytecode[count + 1]] - R[bytecode[count + 2]]
            logging.debug("Rz = Rx - Ry, Rz=" + str(R[bytecode[count + 3]])
                          + " (COUNT = " + str(count) + ")")
            count += 4
            continue

        if bytecode[count] == 0x06:  # If Ra > Rb jump to R3 (4 bytes)
            logging.debug("Jump if Ra > Rb " + str(R[bytecode[count + 1]]) + " " + str(R[bytecode[count + 2]])
                          + " (COUNT = " + str(count) + ")")
            if R[bytecode[count + 1]] > R[bytecode[count + 2]]:
                logging.debug("Jump to next Rc " + str(R[bytecode[count + 3]])
                              + " (COUNT = " + str(count) + ")")
                count += R[bytecode[count + 3]]  # this code is not safe
            count += 4
            continue

        if bytecode[count] == 0xA0:  # function
            logging.debug("FUNCTION " + str(bytecode[count + 1]) + " length " + str(bytecode[count + 2])
                          + " (COUNT = " + str(count) + ")")
            my_function = function
            my_function['id'] = bytecode[count + 1]
            my_function['length'] = bytecode[count + 2]
            my_function['addr'] = count
            F[my_function['id']] = my_function
            count = count + bytecode[count + 2] + 3
            continue

        if bytecode[count] == 0xA1:  # return
            logging.debug("RETURN FROM FUNCTION ID " + str(bytecode[count + 1])
                          + " (COUNT = " + str(count) + ")")
            my_function = F[bytecode[count + 1]]
            count = my_function['return_addr']
            logging.debug("RETURN " + str(my_function['return_addr'])
                          + " (COUNT = " + str(count) + ")")
            continue

        if bytecode[count] == 0xAA:  # call function
            logging.debug("CALL " + str(bytecode[1])
                          + " (COUNT = " + str(count) + ")")

            # my_function = F[bytecode[count + 1]]
            my_function = F[R[bytecode[count + 1]]]

            my_function['return_addr'] = count + 2
            logging.debug("F " + str(my_function)
                          + " (COUNT = " + str(count) + ")")
            count = my_function['addr'] + 3

            logging.debug("count " + str(count) + " bytecode " + str(bytecode[count])
                          + " (COUNT = " + str(count) + ")")
            continue

        ############################################################################################

        if bytecode[count] == 0xB0:  # HALT
            logging.debug("HALT"
                          + " (COUNT = " + str(count) + ")")
            count = len(bytecode)
            continue

        if bytecode[count] == 0xB1:  # RESET
            logging.debug("RESET"
                          + " (COUNT = " + str(count) + ")")
            F = [0] * nreg
            R = [0] * nreg
            count += 1
            continue

        if bytecode[count] == 0xB2:  # DUMP
            logging.debug("DUMP"
                          + " (COUNT = " + str(count) + ")")
            logging.debug("R = " + str(R))
            logging.debug("F = " + str(F))
            logging.debug("Count = " + str(count))
            count += 1
            continue

        if bytecode[count] == 0xB3:  # If Ra == Rb jump to R3 (4 bytes)
            logging.debug("Jump if Ra == Rb " + str(R[bytecode[count + 1]]) + " " + str(R[bytecode[count + 2]])
                          + " (COUNT = " + str(count) + ")")
            if R[bytecode[count + 1]] == R[bytecode[count + 2]]:
                logging.debug("Jump to next Rc " + str(R[bytecode[count + 3]])
                              + " (COUNT = " + str(count) + ")")
                count += R[bytecode[count + 3]]  # this code is not safe
            count += 4
            continue

        if bytecode[count] == 0xB4:  # Increment
            R[bytecode[count + 1]] += 1
            logging.debug("Rx = Rx + 1, Rx=" + str(R[bytecode[count + 1]])
                          + " (COUNT = " + str(count) + ")")
            count += 2
            continue

        if bytecode[count] == 0xB5:  # ZERO
            R[bytecode[count + 1]] = 0
            logging.debug("ZERO Rx, Rx=" + str(R[bytecode[count + 1]])
                          + " (COUNT = " + str(count) + ")")
            count += 2
            continue

    logging.debug("bytecode is completed")


run()
