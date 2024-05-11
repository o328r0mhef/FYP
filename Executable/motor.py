from pyb import I2C, Pin, Timer
import machine

# Define addresses
DRV2605_REG_MODE = 0x01           # Mode register
DRV2605_MODE_INTTRIG = 0x00       # Internal trigger mode
DRV2605_MODE_EXTTRIGEDGE = 0x01   # External edge trigger mode
DRV2605_MODE_EXTTRIGLVL = 0x02    # External level trigger mode
DRV2605_MODE_PWMANALOG = 0x03     # PWM/Analog input mode
DRV2605_MODE_AUDIOVIBE = 0x04     # Audio-to-vibe mode
DRV2605_MODE_REALTIME = 0x05      # Real-time playback (RTP) mode
DRV2605_MODE_DIAGNOS = 0x06       # Diagnostics mode
DRV2605_MODE_AUTOCAL = 0x07       # Auto calibration mode

DRV2605_REG_RTPIN = 0x02      # Real-time playback input register
DRV2605_REG_LIBRARY = 0x03    # Waveform library selection register
DRV2605_REG_WAVESEQ1 = 0x04   # Waveform sequence register 1
DRV2605_REG_WAVESEQ2 = 0x05   # Waveform sequence register 2
DRV2605_REG_WAVESEQ3 = 0x06   # Waveform sequence register 3
DRV2605_REG_WAVESEQ4 = 0x07   # Waveform sequence register 4
DRV2605_REG_WAVESEQ5 = 0x08   # Waveform sequence register 5
DRV2605_REG_WAVESEQ6 = 0x09   # Waveform sequence register 6
DRV2605_REG_WAVESEQ7 = 0x0A   # Waveform sequence register 7
DRV2605_REG_WAVESEQ8 = 0x0B   # Waveform sequence register 8

DRV2605_REG_GO = 0x0C         # Go register
DRV2605_REG_OVERDRIVE = 0x0D  # Overdrive time offset register
DRV2605_REG_SUSTAINPOS = 0x0E # Sustain time offset, positive register
DRV2605_REG_SUSTAINNEG = 0x0F # Sustain time offset, negative register
DRV2605_REG_BREAK = 0x10      # Brake time offset register
DRV2605_REG_AUDIOCTRL = 0x11  # Audio-to-vibe control register
DRV2605_REG_AUDIOLVL = 0x12   # Audio-to-vibe minimum input level register
DRV2605_REG_AUDIOMAX = 0x13   # Audio-to-vibe maximum input level register
DRV2605_REG_AUDIOOUTMIN = 0x14 # Audio-to-vibe minimum output drive register
DRV2605_REG_AUDIOOUTMAX = 0x15 # Audio-to-vibe maximum output drive register
DRV2605_REG_RATEDV = 0x16     # Rated voltage register
DRV2605_REG_CLAMPV = 0x17     # Overdrive clamp voltage register
DRV2605_REG_AUTOCALCOMP = 0x18 # Auto-calibration compensation result register
DRV2605_REG_AUTOCALEMP = 0x19  # Auto-calibration back-EMF result register
DRV2605_REG_FEEDBACK = 0x1A    # Feedback control register
DRV2605_REG_CONTROL1 = 0x1B    # Control1 Register
DRV2605_REG_CONTROL2 = 0x1C    # Control2 Register
DRV2605_REG_CONTROL3 = 0x1D    # Control3 Register
DRV2605_REG_CONTROL4 = 0x1E    # Control4 Register
DRV2605_REG_VBAT = 0x21        # Vbat voltage-monitor register
DRV2605_REG_LRARESON = 0x22    # LRA resonance-period register


i2c = I2C(1, I2C.MASTER)

def writeRegister8(reg, val):
    buf = bytearray(2)
    buf[0] = reg
    buf[1] = val
    i2c.send(buf, 0x5a)

def readRegister8(reg):
    rx = i2c.recv(reg, 0x5a)
    return rx[0]

def setMode(mode):
    writeRegister8(DRV2605_REG_MODE, mode)

def setRealtimeValue(rtp):
    writeRegister8(DRV2605_REG_RTPIN, rtp)

def useERM():
    writeRegister8(DRV2605_REG_FEEDBACK, readRegister8(DRV2605_REG_FEEDBACK) & 0x7F)

def useLRA():
    writeRegister8(DRV2605_REG_FEEDBACK, readRegister8(DRV2605_REG_FEEDBACK) | 0x80)

def setWaveform(slot, w):
    writeRegister8(DRV2605_REG_WAVESEQ1 + slot, w)

def selectLibrary(lib):
    writeRegister8(DRV2605_REG_LIBRARY, lib)

def go():
    writeRegister8(DRV2605_REG_GO, 1) # Set EN high

def stop():
    writeRegister8(DRV2605_REG_GO, 0)

def select_multipexer(reg, val):
    buf = bytearray(2)
    buf[0] = reg
    buf[1] = val
    i2c.send(buf, 0x70)

def initialise_motor(): # Using LRA - Linear Resonant Actuators, library 6 is for LRA
    writeRegister8(DRV2605_REG_MODE, 0x00) # out of standby
    writeRegister8(DRV2605_REG_RTPIN, 0x00) # no real-time-playback
    writeRegister8(DRV2605_REG_WAVESEQ1, 1) # strong click
    writeRegister8(DRV2605_REG_WAVESEQ2, 0) # end sequence
    writeRegister8(DRV2605_REG_OVERDRIVE, 0) # no overdrive
    writeRegister8(DRV2605_REG_SUSTAINPOS, 0)
    writeRegister8(DRV2605_REG_SUSTAINNEG, 0)
    writeRegister8(DRV2605_REG_BREAK, 0)
    writeRegister8(DRV2605_REG_AUDIOMAX, 0x64)
    writeRegister8(DRV2605_REG_FEEDBACK, readRegister8(DRV2605_REG_FEEDBACK) & 0x7F) # turn off N_ERM_LRA || ORiGINAL
    writeRegister8(DRV2605_REG_CONTROL3, readRegister8(DRV2605_REG_CONTROL3) | 0x20) # turn on ERM_OPEN_LOOP

def rampUp():
    setMode(0)
    go()
    setWaveform(0, 17)
    time.sleep_ms(1000)
    stop()

def click(intensity):
    setMode(3)
    go()
    writeRegister8(DRV2605_REG_CLAMPV, intensity)
    time.sleep_ms(800)
    setMode(0)

    # After driving the motor via PWM, the controller is unable to execute library waveforms. Therefore, a power cycle resets the bits.
    writeRegister8(0x01, 0b10000000) # Reset
    time.sleep(0.00001)
    initialise_motor()
