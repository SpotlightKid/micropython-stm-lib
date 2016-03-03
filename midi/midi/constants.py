# -*- coding: utf-8 -*-

###################################################
## Definitions of the different midi events

# For compatibility with CPython
try:
    const
except NameError:
    const = lambda x: x

###################################################
## Midi channel events (The most usual events)
## also called "Channel Voice Messages"

# 1000cccc 0nnnnnnn 0vvvvvvv (channel, note, velocity)
NOTE_OFF = const(0x80)

# 1001cccc 0nnnnnnn 0vvvvvvv (channel, note, velocity)
NOTE_ON = const(0x90)

# 1010cccc 0nnnnnnn 0vvvvvvv (channel, note, velocity)
AFTERTOUCH = const(0xA0)
POLYPHONIC_PRESSURE = AFTERTOUCH

# 1011cccc 0ccccccc 0vvvvvvv (channel, controller, value)
# see Channel Mode Messages!
CONTROLLER_CHANGE = const(0xB0)

# 1100cccc 0ppppppp (channel, program)
PROGRAM_CHANGE = const(0xC0)

# 1101cccc 0ppppppp (channel, pressure)
CHANNEL_PRESSURE = const(0xD0)

# 1110cccc 0vvvvvvv 0wwwwwww (channel, value-lo, value-hi)
PITCH_BEND = const(0xE0)


###################################################
##  Channel Mode Messages (Continuous Controller)
##  All CCs have the same status byte (const(0xB)n).
##  The controller number is the first data byte

# High resolution continuous controllers (MSB)

BANK_SELECT = const(0x00)
MODULATION_WHEEL = const(0x01)
BREATH_CONTROLLER = const(0x02)
FOOT_CONTROLLER = const(0x04)
PORTAMENTO_TIME = const(0x05)
DATA_ENTRY = const(0x06)
DATA_ENTRY_MSB = DATA_ENTRY
VOLUME = const(0x07)
CHANNEL_VOLUME = VOLUME
BALANCE = const(0x08)
PAN = const(0x0A)
EXPRESSION_CONTROLLER = const(0x0B)
EFFECT_CONTROL_1 = const(0x0C)
EFFECT_CONTROL_2 = const(0x0D)
GENERAL_PURPOSE_CONTROLLER_1 = const(0x10)
GENERAL_PURPOSE_CONTROLLER_2 = const(0x11)
GENERAL_PURPOSE_CONTROLLER_3 = const(0x12)
GENERAL_PURPOSE_CONTROLLER_4 = const(0x13)

# High resolution continuous controllers (LSB)

BANK_SELECT_LSB = const(0x20)
MODULATION_WHEEL_LSB = const(0x21)
BREATH_CONTROLLER_LSB = const(0x22)
FOOT_CONTROLLER_LSB = const(0x24)
PORTAMENTO_TIME_LSB = const(0x25)
DATA_ENTRY_LSB = const(0x26)
CHANNEL_VOLUME_LSB = const(0x27)
BALANCE_LSB = const(0x28)
PAN_LSB = const(0x2A)
EXPRESSION_CONTROLLER_LSB = const(0x2B)
EFFECT_CONTROL_1_LSB = const(0x2C)
EFFECT_CONTROL_2_LSB = const(0x2D)
GENERAL_PURPOSE_CONTROLLER_1_LSB = const(0x30)
GENERAL_PURPOSE_CONTROLLER_2_LSB = const(0x31)
GENERAL_PURPOSE_CONTROLLER_3_LSB = const(0x32)
GENERAL_PURPOSE_CONTROLLER_4_LSB = const(0x33)

# Switches

SUSTAIN_ONOFF = const(0x40)
PORTAMENTO_ONOFF = const(0x41)
SOSTENUTO_ONOFF = const(0x42)
SOFT_PEDAL_ONOFF = const(0x43)
LEGATO_ONOFF = const(0x44)
HOLD_2_ONOFF = const(0x45)

# Low resolution continuous controllers

# TG: Sound Variation; FX: Exciter On/Off
SOUND_CONTROLLER_1 = const(0x46)
# TG: Harmonic Content; FX: Compressor On/Off
SOUND_CONTROLLER_2 = const(0x47)
# TG: Release Time; FX: Distortion On/Off
SOUND_CONTROLLER_3 = const(0x48)
# TG: Attack Time; FX: EQ On/Off
SOUND_CONTROLLER_4 = const(0x49)
# TG: Brightness; FX: Expander On/Off
SOUND_CONTROLLER_5 = const(0x4A)
# TG: Undefined; FX: Reverb On/Off
SOUND_CONTROLLER_6 = const(0x4B)
# TG: Undefined; FX: Delay On/Off
SOUND_CONTROLLER_7 = const(0x4C)
# TG: Undefined; FX: Pitch Transpose On/Off
SOUND_CONTROLLER_8 = const(0x4D)
# TG: Undefined; FX: Flange/Chorus On/Off
SOUND_CONTROLLER_9 = const(0x4E)
# TG: Undefined; FX: Special Effects On/Off
SOUND_CONTROLLER_10 = const(0x4F)
GENERAL_PURPOSE_CONTROLLER_5 = const(0x50)
GENERAL_PURPOSE_CONTROLLER_6 = const(0x51)
GENERAL_PURPOSE_CONTROLLER_7 = const(0x52)
GENERAL_PURPOSE_CONTROLLER_8 = const(0x53)
# PTC, 0vvvvvvv is the source Note number
PTC = const(0x54)
PORTAMENTO_CONTROL = PTC
# Ext. Effects Depth
EFFECTS_1 = const(0x5B)
# Tremelo Depth
EFFECTS_2 = const(0x5C)
# Chorus Depth
EFFECTS_3 = const(0x5D)
# Celeste Depth
EFFECTS_4 = const(0x5E)
# Phaser Depth
EFFECTS_5 = const(0x5F)
# controller value byte should be 0
DATA_INCREMENT = const(0x60)
# controller value byte should be 0
DATA_DECREMENT = const(0x61)
NRPN_LSB = const(0x62)
NON_REGISTERED_PARAMETER_NUMBER_LSB = NRPN_LSB
NRPN_MSB = const(0x63)
NON_REGISTERED_PARAMETER_NUMBER_MSB = NRPN_MSB
RPN_LSB = const(0x64)
REGISTERED_PARAMETER_NUMBER_LSB = RPN_LSB
RPN_MSB = const(0x65)
REGISTERED_PARAMETER_NUMBER_MSB = RPN_MSB

# Channel Mode messages

ALL_SOUND_OFF = const(0x78)
RESET_ALL_CONTROLLERS = const(0x79)
LOCAL_CONTROL_ONOFF = const(0x7A)
ALL_NOTES_OFF = const(0x7B)
# also causes All Notes Off
OMNI_MODE_OFF = const(0x7C)
# also causes All Notes Off
OMNI_MODE_ON = const(0x7D)
# Mono Mode on / Poly Off; also causes All Notes Off
# 1011nnnn 01111110 0000vvvv
# vvvv > 0 : Number of channels to use (Omni Off).
# vvvv = 0 : Use all available channels (Omni On)
MONO_MODE_ON = const(0x7E)
# Poly Mode On / Mono Off; also causes All Notes Off
POLY_MODE_ON = const(0x7F)


###################################################
## System Common Messages, for all channels

# 11110000 0iiiiiii 0ddddddd ... 11110111
SYSTEM_EXCLUSIVE = const(0xF0)

# MIDI Time Code Quarter Frame
# 11110001
MTC = const(0xF1)
MIDI_TIME_CODE = MTC

# 11110010 0vvvvvvv 0wwwwwww (lo-position, hi-position)
SPP = const(0xF2)
SONG_POSITION_POINTER = SPP

# 11110011 0sssssss (songnumber)
SONG_SELECT = const(0xF3)

# 11110100
#UNDEFINED = const(0xF4)

# 11110101
#UNDEFINED = const(0xF5)

# 11110110
TUNING_REQUEST = const(0xF6)

# End of system exclusive
# 11110111
END_OF_EXCLUSIVE = const(0xF7)

# MIDI Time Code Formats
MTC_FRAME_RATE_24 = const(0)
MTC_FRAME_RATE_25 = const(1)
MTC_FRAME_RATE_30_DROP = const(2)
MTC_FRAME_RATE_30 = const(3)


###################################################
## Midifile meta-events

# 00 02 ss ss (seq-number)
SEQUENCE_NUMBER = const(0x00)
# 01 len text...
TEXT            = const(0x01)
# 02 len text...
COPYRIGHT       = const(0x02)
# 03 len text...
SEQUENCE_NAME   = const(0x03)
# 04 len text...
INSTRUMENT_NAME = const(0x04)
# 05 len text...
LYRIC           = const(0x05)
# 06 len text...
MARKER          = const(0x06)
# 07 len text...
CUEPOINT        = const(0x07)
# 08 len text...
PROGRAM_NAME    = const(0x08)
# 09 len text...
DEVICE_NAME     = const(0x09)

# MIDI channel prefix assignment (deprecated)
MIDI_CH_PREFIX  = const(0x20)
# 21 01 port, deprecated but still used
MIDI_PORT       = const(0x21)
# 2f 00
END_OF_TRACK    = const(0x2F)
# 51 03 tt tt tt (tempo in µs/quarternote)
TEMPO           = const(0x51)
# 54 05 hh mm ss ff xx
SMTP_OFFSET     = const(0x54)
# 58 04 nn dd cc bb
TIME_SIGNATURE  = const(0x58)
# 59 02 sf mi
# sf = number of sharps(+) or flats(-), mi = major(0) or minor (1)
KEY_SIGNATURE   = const(0x59)
# Sequencer specific event
SPECIFIC        = const(0x7F)


###################################################
## System Realtime messages
## These should not occur in midi files

TIMING_CLOCK   = const(0xF8)
# undefined    = const(0xF9)
SONG_START     = const(0xFA)
SONG_CONTINUE  = const(0xFB)
SONG_STOP      = const(0xFC)
# undefined    = const(0xFD)
ACTIVE_SENSING = const(0xFE)
SYSTEM_RESET   = const(0xFF)


###################################################
## META EVENT, it is used only in midi files.
## In transmitted data it means system reset!!!

# 11111111
META_EVENT      = const(0xFF)
ESCAPE_SEQUENCE = const(0xF7)


###################################################
## Misc constants

FILE_HEADER  = 'MThd'
TRACK_HEADER = 'MTrk'

# Timecode resolution: frames per second
FPS_24 = const(0xE8)
FPS_25 = const(0xE7)
FPS_29 = const(0xE3)
FPS_30 = const(0xE2)
