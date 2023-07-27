import BMPoperations, math

#
# Error codes for CheckValidFormat()
#

ERROR_NONE = 0

# in the header
ERROR_RIFF_SIGNATURE = 1
ERROR_FILE_SIZE_OVER_4294966784_BYTES = 2
ERROR_FILE_SIZE_INCORRECT = 3
ERROR_AVI_LIST_SIGNATURE = 4
ERROR_HDRLAVIH8_SIGNATURE = 5
ERROR_FRAME_COUNT_IS_0 = 6
ERROR_FRAME_PIXEL_COUNT_OVERFLOW = 7
ERROR_ERROR_STRLSTRH8_SIGNATURE = 8
ERROR_FIRST_LIST_SIGNATURE = 9
ERROR_FRAME_SIZE = 10
ERROR_VIDSDIB_SIGNATURE = 11
ERROR_FPS_MODULUS_IS_0 = 12
ERROR_FPS_FRACTION_IS_0 = 13
ERROR_FRAME_COUNT_IS_0 = 14
ERROR_PALETTE_TYPE = 15
ERROR_FRAME_SIZE_0x3C_0x90_MISMATCH = 16
ERROR_HEIGHT_WIDTH_COMBINED_MISMATCH = 17
ERROR_WIDTH_0x40_0xB0_MISMATCH = 18
ERROR_HEIGHT_0x44_0xB4_MISMATCH = 19
ERROR_FRAME_SIZE_0x3C_0xC0_MISMATCH = 20
ERROR_STRN_SIGNATURE = 21
ERROR_AVIVIDEOSTREAM1_SIGNATURE = 22
ERROR_JUNK_SIGNATURE = 23
ERROR_SECOND_LIST_SIGNATURE_OFFSET = 24
ERROR_COMBINED_FRAMES_SIZE_INCORRECT = 25
ERROR_MOVI_SIGNATURE = 26
ERROR_SECOND_PALETTE_ENTRY_OFFSET_LAST_DWORD_OFFSET = 27
ERROR_AVI_VIDEO_STREAM_SIGNATURE_LAST_DWORD_OFFSET = 28
ERROR_VIDEO_STREAM_HEADER_SIZE = 29
ERROR_SECOND_LIST_SIGNATURE = 30
ERROR_INVALID_BITS_PER_PIXEL = 31

ERROR_0x10_VALUE = 101
ERROR_0x24_VALUE = 102
ERROR_0x28_VALUE = 103
ERROR_0x2C_VALUE = 104
ERROR_0x34_VALUE = 105
ERROR_0x38_VALUE = 106
ERROR_0x48_VALUE = 107
ERROR_0x4C_VALUE = 108
ERROR_0x50_VALUE = 109
ERROR_0x54_VALUE = 110
ERROR_0x5C_VALUE = 111
ERROR_0x74_VALUE = 113
ERROR_0x78_VALUE = 114
ERROR_0x7C_VALUE = 115
ERROR_0x88_VALUE = 116
ERROR_0x94_VALUE = 117
ERROR_0x98_VALUE = 118
ERROR_0x9C_VALUE = 119
ERROR_0xA4_VALUE = 120
ERROR_0xBC_VALUE = 121
ERROR_0xC4_VALUE = 122
ERROR_0xC8_VALUE = 123
ERROR_0xCC_VALUE = 124
ERROR_0xD0_VALUE = 125
ERROR_0x4F8_TO_0xFF0_NOT_ZERO = 126
ERROR_0xF8_TO_0x7FC_NOT_ZERO = 127

# header for each frame
ERROR_FRAME_SIGNATURE = 201
ERROR_FRAME_SIZE_IN_FRAME_HEADER = 202

# in the index after the last frame
ERROR_INDEX_SIGNATURE = 301
ERROR_INDEX_LENGTH_INCORRECT = 302
ERROR_INDEX_FRAME_SIGNATURE = 303
ERROR_INDEX_NUMBER_INCORRECT = 304
ERROR_INDEX_FRAME_OFFSET = 305
ERROR_INDEX_FRAME_SIZE = 306



ERROR_RIFF_PALETTE_SIZE_INCORRECT = 401
ERROR_RIFF_PALETTE_NO_RIFF_SIGNATURE = 402
ERROR_RIFF_PALETTE_NO_DATA_SIGNATURE = 403
ERROR_RIFF_PALETTE_HEADER_TABLE_SIZE_INCORRECT = 404
ERROR_RIFF_PALETTE_HEADER_SIZE_INCORRECT = 405
ERROR_RIFF_PALETTE_0x14_VALUE_INCORRECT = 406
ERROR_RIFF_PALETTE_TERMINATOR_VALUE_INCORRECT = 407



AVIheaderSize_24bit = 0x800
AVIheaderSize_8bit = 0x1000

IndexEntrySize = 16
FrameHeaderSize = 8
FrameLengthOffset = 4



def ReadLongInt(address, ArrayIn):
  value = 0
  for BytesToShift in range (4):
    value <<= 8
    value |= (ArrayIn[(address + (3 - BytesToShift))] & 0xFF)
  return value

def WriteLongInt(address, value, ArrayIn):
  for BytesToShift in range (4):
    ArrayIn[(address + BytesToShift)] = (value & 0xFF)
    value >>= 8
  return ArrayIn  

def ReadWordInt(address, ArrayIn):
  return ((ArrayIn[address] & 0xFF) | ((ArrayIn[(address + 1)] & 0xFF) << 8))

def WriteWordInt(address, value, ArrayIn):
  ArrayIn[address] = (value & 0xFF)
  value >>= 8
  ArrayIn[(address + 1)] = (value & 0xFF)
  return ArrayIn

def CombineRGBvalues(r, g, b):
  return (((int(r) & 0xFF) << 16) | ((int(g) & 0xFF) << 8) | (int(b) & 0xFF))

def SeparateRGBvalues(value):
  value = int(value)
  return ((value >> 16) & 0xFF), ((value >> 8) & 0xFF), (value & 0xFF)

def ReadPaletteSizeInRIFFfile(ArrayIn):
  return ReadWordInt(0x16, ArrayIn)

def CheckValidPaletteFormat(ArrayIn):
  if len(ArrayIn) != 92 and len(ArrayIn) != 1052:
    return ERROR_RIFF_PALETTE_SIZE_INCORRECT
  if ArrayIn[0x00] != 0x52 or ArrayIn[0x01] != 0x49 or ArrayIn[0x02] != 0x46 or ArrayIn[0x03] != 0x46:
    return ERROR_RIFF_PALETTE_NO_RIFF_SIGNATURE
  if ArrayIn[0x08] != 0x50 or ArrayIn[0x09] != 0x41 or ArrayIn[0x0A] != 0x4C or ArrayIn[0x0B] != 0x20 or ArrayIn[0x0C] != 0x64 or ArrayIn[0x0D] != 0x61 or ArrayIn[0x0E] != 0x74 or ArrayIn[0x0F] != 0x61:
    return ERROR_RIFF_PALETTE_NO_DATA_SIGNATURE
  PaletteSize = ReadPaletteSizeInRIFFfile(ArrayIn)
  HeaderTableSize = ReadLongInt(0x04, ArrayIn)
  HeaderTableSize -= (PaletteSize * 4)
  if HeaderTableSize != 20:
    return ERROR_RIFF_PALETTE_HEADER_TABLE_SIZE_INCORRECT
  HeaderSize = ReadLongInt(0x10, ArrayIn)
  HeaderSize -= (PaletteSize * 4)
  if HeaderSize != 8:
    return ERROR_RIFF_PALETTE_HEADER_SIZE_INCORRECT
  if ReadWordInt(0x14, ArrayIn) != 768:
    return ERROR_RIFF_PALETTE_0x14_VALUE_INCORRECT
  TerminatorValue = ReadLongInt((0x18 + (PaletteSize * 4)), ArrayIn)
  if (PaletteSize == 16 and TerminatorValue != 0) or (PaletteSize == 256 and TerminatorValue != 992495):
    return ERROR_RIFF_PALETTE_TERMINATOR_VALUE_INCORRECT
  return ERROR_NONE

def CalculateRIFFpaletteSize(BitDepth):
  return (0x1C + ((1 << BitDepth) * 4))

def WriteRIFFpalette(PaletteIn, ArrayIn):
  PaletteEntries = len(PaletteIn)
  PaletteEntries /= 3
  PaletteEntries = int(PaletteEntries)
  if PaletteEntries == 16 or PaletteEntries == 256:
    # RIFF ID
    ArrayIn[0x00] = 0x52
    ArrayIn[0x01] = 0x49
    ArrayIn[0x02] = 0x46
    ArrayIn[0x03] = 0x46

    WriteLongInt(0x04, (20 + (4 * PaletteEntries)), ArrayIn)

    # PAL data ID
    ArrayIn[0x08] = 0x50
    ArrayIn[0x09] = 0x41
    ArrayIn[0x0A] = 0x4C
    ArrayIn[0x0B] = 0x20
    ArrayIn[0x0C] = 0x64
    ArrayIn[0x0D] = 0x61
    ArrayIn[0x0E] = 0x74
    ArrayIn[0x0F] = 0x61
    WriteLongInt(0x10, (8 + (4 * PaletteEntries)), ArrayIn)
    WriteWordInt(0x14, 768, ArrayIn)
    WriteWordInt(0x16, PaletteEntries, ArrayIn)
    if PaletteEntries == 256:
      WriteLongInt((0x18 + (PaletteEntries * 4)), 992495, ArrayIn)
    elif PaletteEntries == 16:
      WriteLongInt((0x18 + (PaletteEntries * 4)), 0, ArrayIn)
    for PaletteEntryToWrite in range (PaletteEntries):
      for Subpixel in range (4):
        if (Subpixel != 3):
          ArrayIn[(0x18 + (PaletteEntryToWrite * 4) + Subpixel)] = PaletteIn[((PaletteEntryToWrite * 3) + Subpixel)]
        else:
          ArrayIn[(0x18 + (PaletteEntryToWrite * 4) + Subpixel)] = 0
  return ArrayIn


def CalculateLineLength(Width, BitDepth):
  if (BitDepth == 24):
    LineLength = (Width * 3)
    if (LineLength % 4) != 0:
      LineLength += (4 - (LineLength % 4))
    return LineLength
  elif (BitDepth == 8):
    LineLength = Width
    if (LineLength % 4) != 0:
      LineLength += (4 - (LineLength % 4))
    return LineLength
  return 0

def CalculateFrameSize(Width, Height, BitDepth):
  FrameSize = (CalculateLineLength(Width, BitDepth) * Height)
  if FrameSize > 4294966784:
    FrameSize = 0
  return FrameSize

def CalculateIndexDataSize(FrameCount, BitDepth):
  return (FrameHeaderSize + (FrameCount * IndexEntrySize))

def CalculateEOFpaddingBytes(Width, Height, BitDepth, FrameCount):
  EOFpaddingByteCount = CalculateLineLength(Width, BitDepth)
  EOFpaddingByteCount *= Height
  EOFpaddingByteCount += FrameHeaderSize
  EOFpaddingByteCount *= FrameCount
  if BitDepth == 24:
    EOFpaddingByteCount += AVIheaderSize_24bit
  elif BitDepth == 8:
    EOFpaddingByteCount += AVIheaderSize_8bit
  EOFpaddingByteCount += CalculateIndexDataSize(FrameCount, BitDepth)
  EOFpaddingByteCount %= 512
  if (EOFpaddingByteCount % 512) != 0:
    EOFpaddingByteCount = (512 - EOFpaddingByteCount)
  return EOFpaddingByteCount

def CalculateFileSize(Width, Height, BitDepth, FrameCount):
  FileSize = CalculateLineLength(Width, BitDepth)
  FileSize *= Height
  FileSize += FrameHeaderSize
  FileSize *= FrameCount
  FileSize += CalculateIndexDataSize(FrameCount, BitDepth)
  FileSize += CalculateEOFpaddingBytes(Width, Height, BitDepth, FrameCount)
  if BitDepth == 24:
    FileSize += AVIheaderSize_24bit
  elif BitDepth == 8:
    FileSize += AVIheaderSize_8bit
  if FileSize > 4294966784:
    FileSize = 0
  return FileSize

def ReadFrameCount(ArrayIn):
  return ReadLongInt(0x30, ArrayIn)

def ReadWidth(ArrayIn):
  return ReadLongInt(0x40, ArrayIn)

def ReadHeight(ArrayIn):
  return ReadLongInt(0x44, ArrayIn)

def ReadFrameRate(ArrayIn):
  Modulus = ReadLongInt(0x80, ArrayIn)
  if Modulus > 0:
    return (ReadLongInt(0x84, ArrayIn) / Modulus)
  else:
    return 0

def ReadBitDepth(ArrayIn):
  return ((ReadLongInt(0xB8, ArrayIn) >> 16) & 0xFFFF)

def CheckValidFormat(ArrayIn):
  BitDepth = ReadBitDepth(ArrayIn)
  if (BitDepth == 24 or BitDepth == 8):
    Width = ReadWidth(ArrayIn)
    Height = ReadHeight(ArrayIn)
    FrameCount = ReadFrameCount(ArrayIn)
    FrameSize = CalculateFrameSize(Width, Height, BitDepth)
    LineLength = CalculateLineLength(Width, BitDepth)
    if CalculateFileSize(Width, Height, BitDepth, FrameCount) > 4294966784:
      return ERROR_FILE_SIZE_OVER_4294966784_BYTES
    if len(ArrayIn) != CalculateFileSize(Width, Height, BitDepth, FrameCount):
      return ERROR_FILE_SIZE_INCORRECT

    if ArrayIn[0x00] != 0x52 or ArrayIn[0x01] != 0x49 or ArrayIn[0x02] != 0x46 or ArrayIn[0x46]:
      return ERROR_RIFF_SIGNATURE
    IndexHeaderPointer = ReadLongInt(0x04, ArrayIn)
    if ArrayIn[0x08] != 0x41 or ArrayIn[0x09] != 0x56 or ArrayIn[0x0A] != 0x49 or ArrayIn[0x0B] != 0x20 or ArrayIn[0x0C] != 0x4C or ArrayIn[0x0D] != 0x49 or ArrayIn[0x0E] != 0x53 or ArrayIn[0x0F] != 0x54:
      return ERROR_AVI_LIST_SIGNATURE
    if (BitDepth == 24 and ReadLongInt(0x10, ArrayIn) != 220) or (BitDepth == 8 and ReadLongInt(0x10, ArrayIn) != 1244):
      return ERROR_0x10_VALUE
    if ArrayIn[0x14] != 0x68 or ArrayIn[0x15] != 0x64 or ArrayIn[0x16] != 0x72 or ArrayIn[0x17] != 0x6C or ArrayIn[0x18] != 0x61 or ArrayIn[0x19] != 0x76 or ArrayIn[0x1A] != 0x69 or ArrayIn[0x1B] != 0x68 or ArrayIn[0x1C] != 0x38 or ArrayIn[0x1D] != 0x00 or ArrayIn[0x1E] != 0x00 or ArrayIn[0x1F] != 0x00:
      return ERROR_HDRLAVIH8_SIGNATURE
    if ReadLongInt(0x24, ArrayIn) != 0:
      return ERROR_0x24_VALUE
    if ReadLongInt(0x28, ArrayIn) != 0:
      return ERROR_0x28_VALUE
    if ReadLongInt(0x2C, ArrayIn) != 2064:
      return ERROR_0x2C_VALUE
    if ReadLongInt(0x30, ArrayIn) == 0:
      return ERROR_FRAME_COUNT_IS_0
    if ReadLongInt(0x34, ArrayIn) != 0:
      return ERROR_0x34_VALUE
    if ReadLongInt(0x38, ArrayIn) != 1:
      return ERROR_0x38_VALUE
    if ReadLongInt(0x3C, ArrayIn) != FrameSize:
      return ERROR_FRAME_SIZE
    if (Width * Height) > 4294966784:
      return ERROR_FRAME_PIXEL_COUNT_OVERFLOW
    if ReadLongInt(0x48, ArrayIn) != 0:
      return ERROR_0x48_VALUE
    if ReadLongInt(0x4C, ArrayIn) != 0:
      return ERROR_0x4C_VALUE
    if ReadLongInt(0x50, ArrayIn) != 0:
      return ERROR_0x50_VALUE
    if ReadLongInt(0x54, ArrayIn) != 0:
      return ERROR_0x54_VALUE
    if ArrayIn[0x58] != 0x4C or ArrayIn[0x59] != 0x49 or ArrayIn[0x5A] != 0x53 or ArrayIn[0x5B] != 0x54:
      return ERROR_FIRST_LIST_SIGNATURE
    if (BitDepth == 24 and ReadLongInt(0x5C, ArrayIn) != 144) or (BitDepth == 8 and ReadLongInt(0x5C, ArrayIn) != 1168):
      return ERROR_0x5C_VALUE
    if ArrayIn[0x60] != 0x73 or ArrayIn[0x61] != 0x74 or ArrayIn[0x62] != 0x72 or ArrayIn[0x63] != 0x6C or ArrayIn[0x64] != 0x73 or ArrayIn[0x65] != 0x74 or ArrayIn[0x66] != 0x72 or ArrayIn[0x67] != 0x68 or ArrayIn[0x68] != 0x38 or ArrayIn[0x69] != 0x00 or ArrayIn[0x6A] != 0x00 or ArrayIn[0x6B] != 0x00:
      return ERROR_STRLSTRH8_SIGNATURE
    if ArrayIn[0x6C] != 0x76 or ArrayIn[0x6D] != 0x69 or ArrayIn[0x6E] != 0x64 or ArrayIn[0x6F] != 0x73 or ArrayIn[0x70] != 0x44 or ArrayIn[0x71] != 0x49 or ArrayIn[0x72] != 0x42 or ArrayIn[0x73] != 0x20:
      return ERROR_VIDSDIB_SIGNATURE
    if ReadLongInt(0x74, ArrayIn) != 0:
      return ERROR_0x74_VALUE
    if ReadLongInt(0x78, ArrayIn) != 0:
      return ERROR_0x78_VALUE
    if ReadLongInt(0x7C, ArrayIn) != 0:
      return ERROR_0x7C_VALUE
    if ReadLongInt(0x80, ArrayIn) == 0:
      return ERROR_FPS_MODULUS_IS_0
    if ReadLongInt(0x84, ArrayIn) == 0:
      return ERROR_FPS_FRACTION_IS_0
    if ReadLongInt(0x88, ArrayIn) != 0:
      return ERROR_0x88_VALUE
    if ReadFrameCount(ArrayIn) == 0:
      return ERROR_FRAME_COUNT_IS_0
    if ReadLongInt(0x90, ArrayIn) != ReadLongInt(0x3C, ArrayIn):
      return ERROR_FRAME_SIZE_0x3C_0x90_MISMATCH
    if ReadLongInt(0x94, ArrayIn) != 900:
      return ERROR_0x94_VALUE
    if ReadLongInt(0x98, ArrayIn) != 0:
      return ERROR_0x98_VALUE
    if ReadLongInt(0x9C, ArrayIn) != 0:
      return ERROR_0x9C_VALUE
    SeparatedWidth = ReadLongInt(0xA0, ArrayIn)
    SeparatedHeight = SeparatedWidth
    SeparatedHeight >>= 16
    SeparatedHeight &= 0xFFFF
    SeparatedWidth &= 0xFFFF
    if SeparatedWidth != Width or SeparatedHeight != Height:
      return ERROR_HEIGHT_WIDTH_COMBINED_MISMATCH
    if ReadLongInt(0xA4, ArrayIn) != 1718776947:
      return ERROR_0xA4_VALUE
    if (BitDepth == 24 and ReadLongInt(0xA8, ArrayIn) != 40) or (BitDepth == 8 and ReadLongInt(0xA8, ArrayIn) != 1064):
      return ERROR_SECOND_PALETTE_ENTRY_OFFSET_LAST_DWORD_OFFSET
    if (BitDepth == 24 and ReadLongInt(0xAC, ArrayIn) != 40) or (BitDepth == 8 and ReadLongInt(0xAC, ArrayIn) != 40):
      return ERROR_AVI_VIDEO_STREAM_SIGNATURE_LAST_DWORD_OFFSET
    if ReadLongInt(0xB0, ArrayIn) != ReadLongInt(0x40, ArrayIn):
      return ERROR_WIDTH_0x40_0xB0_MISMATCH
    if ReadLongInt(0xB4, ArrayIn) != ReadLongInt(0x44, ArrayIn):
      return ERROR_HEIGHT_0x44_0xB4_MISMATCH
    PaletteType = (ReadLongInt(0xB8, ArrayIn) & 0xFFFF)
    if (BitDepth == 24 and PaletteType != 1) or (BitDepth == 8 and PaletteType != 1):
      return ERROR_PALETTE_TYPE
    if ReadLongInt(0xBC, ArrayIn) != 0:
      return ERROR_0xBC_VALUE
    if ReadLongInt(0xC0, ArrayIn) != ReadLongInt(0x3C, ArrayIn):
      return ERROR_FRAME_SIZE_0x3C_0xC0_MISMATCH
    if ReadLongInt(0xC4, ArrayIn) != 0:
      return ERROR_0xC4_VALUE
    if ReadLongInt(0xC8, ArrayIn) != 0:
      return ERROR_0xC8_VALUE
    if BitDepth == 24:
      if ReadLongInt(0xCC, ArrayIn) != 0:
        return ERROR_0xCC_VALUE
      if ReadLongInt(0xD0, ArrayIn) != 0:
        return ERROR_0xD0_VALUE
      if ArrayIn[0xD4] != 0x73 or ArrayIn[0xD5] != 0x74 or ArrayIn[0xD6] != 0x72 or ArrayIn[0xD7] != 0x6E:
        return ERROR_STRN_SIGNATURE
      if ReadLongInt(0xD8, ArrayIn) != 20:
        return ERROR_VIDEO_STREAM_HEADER_SIZE
      if ArrayIn[0xDC] != 0x41 or ArrayIn[0xDD] != 0x56 or ArrayIn[0xDE] != 0x49 or ArrayIn[0xDF] != 0x20 or ArrayIn[0xE0] != 0x56 or ArrayIn[0xE1] != 0x69 or ArrayIn[0xE2] != 0x64 or ArrayIn[0xE3] != 0x65 or ArrayIn[0xE4] != 0x6F or ArrayIn[0xE5] != 0x20 or ArrayIn[0xE6] != 0x53 or ArrayIn[0xE7] != 0x74 or ArrayIn[0xE8] != 0x72 or ArrayIn[0xE9] != 0x65 or ArrayIn[0xEA] != 0x61 or ArrayIn[0xEB] != 0x6D or ArrayIn[0xEC] != 0x20 or ArrayIn[0xED] != 0x23 or ArrayIn[0xEE] != 0x31 or ArrayIn[0xEF] != 0x00:
        return ERROR_AVIVIDEOSTREAM1_SIGNATURE
      if ArrayIn[0xF0] != 0x4A or ArrayIn[0xF1] != 0x55 or ArrayIn[0xF2] != 0x4E or ArrayIn[0xF3] != 0x4B:
        return ERROR_JUNK_SIGNATURE
      if ReadLongInt(0xF4, ArrayIn) != 1788:
        return ERROR_SECOND_LIST_SIGNATURE_OFFSET
      NotZero = False
      for ValuesToCheck in range (int((0x7F4 - 0xF8) / 4)):
        if ReadLongInt(int(0xF8 + (ValuesToCheck * 4)), ArrayIn) != 0:
          NotZero = True
          break
      if NotZero == True:
        return ERROR_0xF8_TO_0x7FC_NOT_ZERO
      if ArrayIn[0x7F4] != 0x4C or ArrayIn[0x7F5] != 0x49 or ArrayIn[0x7F6] != 0x53 or ArrayIn[0x7F7] != 0x54:
        return ERROR_SECOND_LIST_SIGNATURE
      if ReadLongInt(0x7F8, ArrayIn) != (FrameCount * (FrameSize + FrameHeaderSize) + FrameLengthOffset):
        return ERROR_COMBINED_FRAMES_SIZE_INCORRECT
      if ArrayIn[0x7FC] != 0x6D or ArrayIn[0x7FD] != 0x6F or ArrayIn[0x7FE] != 0x76 or ArrayIn[0x7FF] != 0x69:
        return ERROR_MOVI_SIGNATURE
    elif BitDepth == 8:
      if ReadLongInt(0xCC, ArrayIn) != 256:
        return ERROR_0xCC_VALUE
      if ReadLongInt(0xD0, ArrayIn) != 256:
        return ERROR_0xD0_VALUE
      if ArrayIn[0x4D4] != 0x73 or ArrayIn[0x4D5] != 0x74 or ArrayIn[0x4D6] != 0x72 or ArrayIn[0x4D7] != 0x6E:
        return ERROR_STRN_SIGNATURE
      if ReadLongInt(0x4D8, ArrayIn) != 20:
        return ERROR_VIDEO_STREAM_HEADER_SIZE
      if ArrayIn[0x4DC] != 0x41 or ArrayIn[0x4DD] != 0x56 or ArrayIn[0x4DE] != 0x49 or ArrayIn[0x4DF] != 0x20 or ArrayIn[0x4E0] != 0x56 or ArrayIn[0x4E1] != 0x69 or ArrayIn[0x4E2] != 0x64 or ArrayIn[0x4E3] != 0x65 or ArrayIn[0x4E4] != 0x6F or ArrayIn[0x4E5] != 0x20 or ArrayIn[0x4E6] != 0x53 or ArrayIn[0x4E7] != 0x74 or ArrayIn[0x4E8] != 0x72 or ArrayIn[0x4E9] != 0x65 or ArrayIn[0x4EA] != 0x61 or ArrayIn[0x4EB] != 0x6D or ArrayIn[0x4EC] != 0x20 or ArrayIn[0x4ED] != 0x23 or ArrayIn[0x4EE] != 0x31 or ArrayIn[0x4EF] != 0x00:
        return ERROR_AVIVIDEOSTREAM1_SIGNATURE
      if ArrayIn[0x4F0] != 0x4A or ArrayIn[0x4F1] != 0x55 or ArrayIn[0x4F2] != 0x4E or ArrayIn[0x4F3] != 0x4B:
        return ERROR_JUNK_SIGNATURE
      if ReadLongInt(0x4F4, ArrayIn) != 2812:
        return ERROR_SECOND_LIST_SIGNATURE_OFFSET
      NotZero = False
      for ValuesToCheck in range (int((0xFF4 - 0xAFC) / 4)):
        if ReadLongInt(int(0x4F8 + (ValuesToCheck * 4)), ArrayIn) != 0:
          NotZero = True
          break
      if NotZero == True:
        return ERROR_0x4F8_TO_0FF0_NOT_ZERO
      if ArrayIn[0xFF4] != 0x4C or ArrayIn[0xFF5] != 0x49 or ArrayIn[0xFF6] != 0x53 or ArrayIn[0xFF7] != 0x54:
        return ERROR_SECOND_LIST_SIGNATURE
      if ReadLongInt(0xFF8, ArrayIn) != (FrameCount * (FrameSize + FrameHeaderSize) + FrameLengthOffset):
        return ERROR_COMBINED_FRAMES_SIZE_INCORRECT
      if ArrayIn[0xFFC] != 0x6D or ArrayIn[0xFFD] != 0x6F or ArrayIn[0xFFE] != 0x76 or ArrayIn[0xFFF] != 0x69:
        return ERROR_MOVI_SIGNATURE

    AVIheaderSize = AVIheaderSize_24bit
    if BitDepth == 8:
      AVIheaderSize = AVIheaderSize_8bit
    FrameIDok = True
    for Frames in range (FrameCount):
      if ArrayIn[(AVIheaderSize + (Frames * (FrameSize + FrameHeaderSize)))] != 0x30 or ArrayIn[((AVIheaderSize + (Frames * (FrameSize + FrameHeaderSize))) + 1)] != 0x30 or ArrayIn[((AVIheaderSize + (Frames * (FrameSize + FrameHeaderSize))) + 2)] != 0x64 or ArrayIn[((AVIheaderSize + (Frames * (FrameSize + FrameHeaderSize))) + 3)] != 0x62:
        FrameIDok = False
    if FrameIDok == False:
      return ERROR_FRAME_SIGNATURE
    FrameIDok == True
    for Frames in range (FrameCount):
      if ReadLongInt((AVIheaderSize + (Frames * (FrameSize + FrameHeaderSize)) + FrameLengthOffset), ArrayIn) != FrameSize:
        FrameIDok = False
        break
    if FrameIDok == False:
      return ERROR_FRAME_SIZE_IN_FRAME_HEADER

    IndexHeaderPointer -= (IndexEntrySize * FrameCount)
    if ArrayIn[IndexHeaderPointer] != 0x69 or ArrayIn[(IndexHeaderPointer + 1)] != 0x64 or ArrayIn[(IndexHeaderPointer + 2)] != 0x78 or ArrayIn[(IndexHeaderPointer + 3)] != 0x31:
      return ERROR_INDEX_SIGNATURE
    if ReadLongInt((IndexHeaderPointer + FrameLengthOffset), ArrayIn) != (IndexEntrySize * FrameCount):
      return ERROR_INDEX_LENGTH_INCORRECT
    FrameIDok = True
    for Frames in range (FrameCount):
      if ArrayIn[(IndexHeaderPointer + (Frames * IndexEntrySize) + FrameHeaderSize)] != 0x30 or ArrayIn[(IndexHeaderPointer + (Frames * IndexEntrySize) + FrameHeaderSize + 1)] != 0x30 or ArrayIn[(IndexHeaderPointer + (Frames * IndexEntrySize) + FrameHeaderSize + 2)] != 0x64 or ArrayIn[(IndexHeaderPointer + (Frames * IndexEntrySize) + FrameHeaderSize + 3)] != 0x62:
        FrameIDok = False
        break
    if FrameIDok == False:
      return ERROR_INDEX_FRAME_SIGNATURE
    NumberCorrect = True
    for Frames in range (FrameCount):
      if ReadLongInt(((IndexHeaderPointer + (Frames * IndexEntrySize) + FrameHeaderSize + FrameLengthOffset)), ArrayIn) != IndexEntrySize:
        NumberCorrect = False
        break
    if NumberCorrect == False:
      return ERROR_INDEX_NUMBER_INCORRECT
    FrameOffsetCorrect = True
    for Frames in range (FrameCount):
      if ReadLongInt(((IndexHeaderPointer + (Frames * IndexEntrySize) + IndexEntrySize)), ArrayIn) != ((Frames * (FrameSize + FrameHeaderSize)) + FrameLengthOffset):
        NumberCorrect = False
        break
    if FrameOffsetCorrect == False:
      return ERROR_INDEX_FRAME_OFFSET
    FrameSizeCorrect = True
    for Frames in range (FrameCount):
      if ReadLongInt(((IndexHeaderPointer + (Frames * IndexEntrySize) + IndexEntrySize + FrameLengthOffset)), ArrayIn) != FrameSize:
        NumberCorrect = False
        break
    if FrameSizeCorrect == False:
      return ERROR_INDEX_FRAME_SIZE

    return ERROR_NONE # all checks OK

  return ERROR_INVALID_BITS_PER_PIXEL

def ReadRIFFpalette(PaletteIn, ArrayIn):
  if CheckValidPaletteFormat(ArrayIn) == ERROR_NONE:
    PaletteEntries = ReadWordInt(0x16, ArrayIn)
    if PaletteEntries == 16 or PaletteEntries == 256:
      for PaletteEntryToWrite in range (PaletteEntries):
        for Subpixel in range (4):
          if (Subpixel != 3):
            PaletteIn[((PaletteEntryToWrite * 3) + Subpixel)] = ArrayIn[(0x18 + (PaletteEntryToWrite * 4) + Subpixel)]
  return PaletteIn

def WritePalette(PaletteIn, ArrayIn):
  BitsPerPixel = ReadBitDepth(ArrayIn)
  if BitsPerPixel == 8:
    PaletteSize = (1 << BitsPerPixel)
    for PaletteEntryToWrite in range (PaletteSize):
      for Subpixel in range (4):
        if (Subpixel != 3):
          ArrayIn[(0xD4 + (PaletteEntryToWrite * 4) + (2 - Subpixel))] = PaletteIn[((PaletteEntryToWrite * 3) + Subpixel)]
        else:
          ArrayIn[(0xD4 + (PaletteEntryToWrite * 4) + Subpixel)] = 0
  return ArrayIn

def ReadPalette(PaletteIn, ArrayIn):
  BitsPerPixel = ReadBitDepth(ArrayIn)
  if BitsPerPixel == 8:
    PaletteSize = (1 << BitsPerPixel)
    for PaletteEntryToWrite in range (PaletteSize):
      for Subpixel in range (4):
        if (Subpixel != 3):
          PaletteIn[((PaletteEntryToWrite * 3) + (2 - Subpixel))] = ArrayIn[(0xD4 + (PaletteEntryToWrite * 4) + Subpixel)]
  return PaletteIn

def WriteAVI(Width, Height, BitDepth, FrameRate, FrameCount, ArrayIn):
  if (BitDepth == 24 or BitDepth == 8) and FrameRate > 0 and FrameCount >= 1 and Width >= 1 and Width <= 65535 and Height >= 1 and Height <= 65535 and len(ArrayIn) == CalculateFileSize(Width, Height, BitDepth, FrameCount):
    AVIheaderSize = AVIheaderSize_24bit
    if BitDepth == 8:
      AVIheaderSize = AVIheaderSize_8bit
    FrameSize = CalculateFrameSize(Width, Height, BitDepth)
    for ByteToClear in range(len(ArrayIn)):
      ArrayIn[ByteToClear] = 0x00

    # RIFF ID
    ArrayIn[0x00] = 0x52
    ArrayIn[0x01] = 0x49
    ArrayIn[0x02] = 0x46
    ArrayIn[0x03] = 0x46

    IndexHeaderLocation = CalculateLineLength(Width, BitDepth)
    IndexHeaderLocation *= Height
    IndexHeaderLocation += FrameHeaderSize
    IndexHeaderLocation *= FrameCount
    if BitDepth == 24:
      IndexHeaderLocation += AVIheaderSize_24bit
    elif BitDepth == 8:
      IndexHeaderLocation += AVIheaderSize_8bit

    WriteLongInt(0x04, (IndexHeaderLocation + (IndexEntrySize * FrameCount)), ArrayIn)

    # AVI LIST ID
    ArrayIn[0x08] = 0x41
    ArrayIn[0x09] = 0x56
    ArrayIn[0x0A] = 0x49
    ArrayIn[0x0B] = 0x20
    ArrayIn[0x0C] = 0x4C
    ArrayIn[0x0D] = 0x49
    ArrayIn[0x0E] = 0x53
    ArrayIn[0x0F] = 0x54

    if BitDepth == 24:
      WriteLongInt(0x10, 220, ArrayIn)
    elif BitDepth == 8:
      WriteLongInt(0x10, 1244, ArrayIn)

    # hdrlavih8 ID
    ArrayIn[0x14] = 0x68
    ArrayIn[0x15] = 0x64
    ArrayIn[0x16] = 0x72
    ArrayIn[0x17] = 0x6C
    ArrayIn[0x18] = 0x61
    ArrayIn[0x19] = 0x76
    ArrayIn[0x1A] = 0x69
    ArrayIn[0x1B] = 0x68
    ArrayIn[0x1C] = 0x38
    ArrayIn[0x1D] = 0x00
    ArrayIn[0x1E] = 0x00
    ArrayIn[0x1F] = 0x00

    WriteLongInt(0x20, int(1000000 / FrameRate), ArrayIn)
    WriteLongInt(0x24, 0, ArrayIn)
    WriteLongInt(0x28, 0, ArrayIn)
    WriteLongInt(0x2C, 2064, ArrayIn)
    WriteLongInt(0x30, FrameCount, ArrayIn)
    WriteLongInt(0x34, 0, ArrayIn)
    WriteLongInt(0x38, 1, ArrayIn)
    WriteLongInt(0x3C, CalculateFrameSize(Width, Height, BitDepth), ArrayIn)
    WriteLongInt(0x40, Width, ArrayIn)
    WriteLongInt(0x44, Height, ArrayIn)
    WriteLongInt(0x48, 0, ArrayIn)
    WriteLongInt(0x4C, 0, ArrayIn)
    WriteLongInt(0x50, 0, ArrayIn)
    WriteLongInt(0x54, 0, ArrayIn)

    # LIST ID
    ArrayIn[0x58] = 0x4C
    ArrayIn[0x59] = 0x49
    ArrayIn[0x5A] = 0x53
    ArrayIn[0x5B] = 0x54

    if BitDepth == 24:
      WriteLongInt(0x5C, 144, ArrayIn)
    elif BitDepth == 8:
      WriteLongInt(0x5C, 1168, ArrayIn)

    # strlstrh8 ID
    ArrayIn[0x60] = 0x73
    ArrayIn[0x61] = 0x74
    ArrayIn[0x62] = 0x72
    ArrayIn[0x63] = 0x6c
    ArrayIn[0x64] = 0x73
    ArrayIn[0x65] = 0x74
    ArrayIn[0x66] = 0x72
    ArrayIn[0x67] = 0x68
    ArrayIn[0x68] = 0x38
    ArrayIn[0x69] = 0x00
    ArrayIn[0x6A] = 0x00
    ArrayIn[0x6B] = 0x00

    # vidsDIB ID
    ArrayIn[0x6C] = 0x76
    ArrayIn[0x6D] = 0x69
    ArrayIn[0x6E] = 0x64
    ArrayIn[0x6F] = 0x73
    ArrayIn[0x70] = 0x44
    ArrayIn[0x71] = 0x49
    ArrayIn[0x72] = 0x42
    ArrayIn[0x73] = 0x20

    WriteLongInt(0x74, 0, ArrayIn)
    WriteLongInt(0x78, 0, ArrayIn)
    WriteLongInt(0x7C, 0, ArrayIn)
    WriteLongInt(0x80, 1000, ArrayIn) # Frames per second Modulus
    WriteLongInt(0x84, int(FrameRate * 1000), ArrayIn)
    WriteLongInt(0x88, 0, ArrayIn)
    WriteLongInt(0x8C, FrameCount, ArrayIn)
    ArrayIn[0x90] = ArrayIn[0x3C]
    ArrayIn[0x91] = ArrayIn[0x3D]
    ArrayIn[0x92] = ArrayIn[0x3E]
    ArrayIn[0x93] = ArrayIn[0x3F]
    WriteLongInt(0x94, 900, ArrayIn)
    WriteLongInt(0x98, 0, ArrayIn)
    WriteLongInt(0x9C, 0, ArrayIn)
    WriteLongInt(0xA0, (((Height & 0xFFFF) << 16) | (Width & 0xFFFF)), ArrayIn)
    WriteLongInt(0xA4, 1718776947, ArrayIn)
    if BitDepth == 24:
      WriteLongInt(0xA8, 40, ArrayIn)
    elif BitDepth == 8:
      WriteLongInt(0xA8, 1064, ArrayIn)
    if BitDepth == 24:
      WriteLongInt(0xAC, 40, ArrayIn)
    elif BitDepth == 8:
      WriteLongInt(0xAC, 40, ArrayIn)
    WriteLongInt(0xB0, Width, ArrayIn)
    WriteLongInt(0xB4, Height, ArrayIn)
    PaletteType = 1
    if BitDepth == 8:
      PaletteType = 1  
    WriteLongInt(0xB8, (PaletteType | (BitDepth << 16)), ArrayIn)
    WriteLongInt(0xBC, 0, ArrayIn)
    ArrayIn[0xC0] = ArrayIn[0x3C]
    ArrayIn[0xC1] = ArrayIn[0x3D]
    ArrayIn[0xC2] = ArrayIn[0x3E]
    ArrayIn[0xC3] = ArrayIn[0x3F]
    WriteLongInt(0xC4, 0, ArrayIn)
    WriteLongInt(0xC8, 0, ArrayIn)

    if BitDepth == 24:
      WriteLongInt(0xCC, 0, ArrayIn)
      WriteLongInt(0xD0, 0, ArrayIn)

      # strn ID
      ArrayIn[0xD4] = 0x73
      ArrayIn[0xD5] = 0x74
      ArrayIn[0xD6] = 0x72
      ArrayIn[0xD7] = 0x6E

      WriteLongInt(0xD8, 20, ArrayIn)

      # AVI Video Stream #1 ID
      ArrayIn[0xDC] = 0x41
      ArrayIn[0xDD] = 0x56
      ArrayIn[0xDE] = 0x49
      ArrayIn[0xDF] = 0x20
      ArrayIn[0xE0] = 0x56
      ArrayIn[0xE1] = 0x69
      ArrayIn[0xE2] = 0x64
      ArrayIn[0xE3] = 0x65
      ArrayIn[0xE4] = 0x6F
      ArrayIn[0xE5] = 0x20
      ArrayIn[0xE6] = 0x53
      ArrayIn[0xE7] = 0x74
      ArrayIn[0xE8] = 0x72
      ArrayIn[0xE9] = 0x65
      ArrayIn[0xEA] = 0x61
      ArrayIn[0xEB] = 0x6D
      ArrayIn[0xEC] = 0x20
      ArrayIn[0xED] = 0x23
      ArrayIn[0xEE] = 0x31
      ArrayIn[0xEF] = 0x00

      # JUNK ID
      ArrayIn[0xF0] = 0x4A
      ArrayIn[0xF1] = 0x55
      ArrayIn[0xF2] = 0x4E
      ArrayIn[0xF3] = 0x4B

      WriteLongInt(0xF4, 1788, ArrayIn)

      # LIST ID
      ArrayIn[0x7F4] = 0x4C
      ArrayIn[0x7F5] = 0x49
      ArrayIn[0x7F6] = 0x53
      ArrayIn[0x7F7] = 0x54

      WriteLongInt(0x7F8, (FrameLengthOffset + (FrameCount * (FrameSize + FrameHeaderSize))), ArrayIn)

      # movi ID
      ArrayIn[0x7FC] = 0x6D
      ArrayIn[0x7FD] = 0x6F
      ArrayIn[0x7FE] = 0x76
      ArrayIn[0x7FF] = 0x69

    elif BitDepth == 8:
      WriteLongInt(0xCC, 256, ArrayIn)
      WriteLongInt(0xD0, 256, ArrayIn)

      # strn ID
      ArrayIn[0x4D4] = 0x73
      ArrayIn[0x4D5] = 0x74
      ArrayIn[0x4D6] = 0x72
      ArrayIn[0x4D7] = 0x6E

      WriteLongInt(0x4D8, 20, ArrayIn)

      # AVI Video Stream #1 ID
      ArrayIn[0x4DC] = 0x41
      ArrayIn[0x4DD] = 0x56
      ArrayIn[0x4DE] = 0x49
      ArrayIn[0x4DF] = 0x20
      ArrayIn[0x4E0] = 0x56
      ArrayIn[0x4E1] = 0x69
      ArrayIn[0x4E2] = 0x64
      ArrayIn[0x4E3] = 0x65
      ArrayIn[0x4E4] = 0x6F
      ArrayIn[0x4E5] = 0x20
      ArrayIn[0x4E6] = 0x53
      ArrayIn[0x4E7] = 0x74
      ArrayIn[0x4E8] = 0x72
      ArrayIn[0x4E9] = 0x65
      ArrayIn[0x4EA] = 0x61
      ArrayIn[0x4EB] = 0x6D
      ArrayIn[0x4EC] = 0x20
      ArrayIn[0x4ED] = 0x23
      ArrayIn[0x4EE] = 0x31
      ArrayIn[0x4EF] = 0x00

      # JUNK ID
      ArrayIn[0x4F0] = 0x4A
      ArrayIn[0x4F1] = 0x55
      ArrayIn[0x4F2] = 0x4E
      ArrayIn[0x4F3] = 0x4B

      WriteLongInt(0x4F4, 2812, ArrayIn)

      # LIST ID
      ArrayIn[0xFF4] = 0x4C
      ArrayIn[0xFF5] = 0x49
      ArrayIn[0xFF6] = 0x53
      ArrayIn[0xFF7] = 0x54

      WriteLongInt(0xFF8, (FrameLengthOffset + (FrameCount * (FrameSize + FrameHeaderSize))), ArrayIn)

      # movi ID
      ArrayIn[0xFFC] = 0x6D
      ArrayIn[0xFFD] = 0x6F
      ArrayIn[0xFFE] = 0x76
      ArrayIn[0xFFF] = 0x69

    for Frames in range (FrameCount):
      # 00db ID
      ArrayIn[(AVIheaderSize + (Frames * (FrameSize + FrameHeaderSize)))] = 0x30
      ArrayIn[(AVIheaderSize + (Frames * (FrameSize + FrameHeaderSize)) + 1)] = 0x30
      ArrayIn[(AVIheaderSize + (Frames * (FrameSize + FrameHeaderSize)) + 2)] = 0x64
      ArrayIn[(AVIheaderSize + (Frames * (FrameSize + FrameHeaderSize)) + 3)] = 0x62

      WriteLongInt((AVIheaderSize + (Frames * (FrameSize + FrameHeaderSize) + FrameLengthOffset)), FrameSize, ArrayIn)

    # idx1 ID
    ArrayIn[IndexHeaderLocation] = 0x69
    ArrayIn[(IndexHeaderLocation + 1)] = 0x64
    ArrayIn[(IndexHeaderLocation + 2)] = 0x78
    ArrayIn[(IndexHeaderLocation + 3)] = 0x31

    WriteLongInt((IndexHeaderLocation + FrameLengthOffset), (FrameCount * IndexEntrySize), ArrayIn)

    for Frames in range (FrameCount):
      # 00db ID
      ArrayIn[(IndexHeaderLocation + (Frames * IndexEntrySize) + FrameHeaderSize)] = 0x30
      ArrayIn[(IndexHeaderLocation + (Frames * IndexEntrySize) + FrameHeaderSize + 1)] = 0x30
      ArrayIn[(IndexHeaderLocation + (Frames * IndexEntrySize) + FrameHeaderSize + 2)] = 0x64
      ArrayIn[(IndexHeaderLocation + (Frames * IndexEntrySize) + FrameHeaderSize + 3)] = 0x62

      WriteLongInt(((IndexHeaderLocation + (Frames * IndexEntrySize) + FrameHeaderSize + FrameLengthOffset)), IndexEntrySize, ArrayIn)
      WriteLongInt(((IndexHeaderLocation + (Frames * IndexEntrySize) + FrameHeaderSize + FrameLengthOffset)), IndexEntrySize, ArrayIn)      
      WriteLongInt(((IndexHeaderLocation + (Frames * IndexEntrySize) + IndexEntrySize)), ((Frames * (FrameSize + FrameHeaderSize)) + FrameLengthOffset), ArrayIn)
      WriteLongInt(((IndexHeaderLocation + (Frames * IndexEntrySize) + IndexEntrySize + FrameLengthOffset)), FrameSize, ArrayIn)

  return ArrayIn

def GetEndOfFrame(frame, ArrayIn):
  AVIheaderSize = AVIheaderSize_24bit
  if ReadBitDepth(ArrayIn) == 8:
    AVIheaderSize = AVIheaderSize_8bit
  FrameSize = (ReadLongInt(0x3C, ArrayIn) + FrameHeaderSize)
  return (AVIheaderSize + ((frame + 1) * FrameSize))

def GetStartOfFrame(frame, ArrayIn):
  return (GetEndOfFrame(frame, ArrayIn) - ReadLongInt(0x3C, ArrayIn))

def WritePixel(X_pixel, Y_pixel, frame, value, ArrayIn):
  Width = ReadWidth(ArrayIn)
  Height = ReadHeight(ArrayIn)
  BitDepth = ReadBitDepth(ArrayIn)
  if X_pixel >= 0 and X_pixel < Width and Y_pixel >= 0 and Y_pixel < Height and frame >=0 and frame < ReadFrameCount(ArrayIn):
    EndOfFrame = GetEndOfFrame(frame, ArrayIn)
    if BitDepth == 8:
      WidthRemainder = (Width % 4)
      if WidthRemainder != 0:
        Width += int(4 - WidthRemainder)
      ElementToChange = int((EndOfFrame - (Y_pixel * (Width)) - int(Width)) + int(X_pixel))
      ArrayIn[ElementToChange] = (value & 0xFF)
    elif BitDepth == 24:
      WidthRemainder = ((Width * 3) % 4)
      if WidthRemainder != 0:
        WidthRemainder = int(4 - WidthRemainder)
      ElementToChange = int(EndOfFrame - ((Y_pixel + 1) * ((Width * 3) + WidthRemainder))) + int(X_pixel * 3)
      ArrayIn[ElementToChange] = (value & 0xFF)
      ArrayIn[(ElementToChange + 1)] = ((value >> 8) & 0xFF)
      ArrayIn[(ElementToChange + 2)] = ((value >> 16) & 0xFF)
  return ArrayIn

def ReadPixel(X_pixel, Y_pixel, frame, ArrayIn):
  Width = ReadWidth(ArrayIn)
  Height = ReadHeight(ArrayIn)
  BitDepth = ReadBitDepth(ArrayIn)
  PixelValue = 0
  if X_pixel >= 0 and X_pixel < Width and Y_pixel >= 0 and Y_pixel < Height and frame >=0 and frame < ReadFrameCount(ArrayIn):
    EndOfFrame = GetEndOfFrame(frame, ArrayIn)
    if BitDepth == 8:
      WidthRemainder = (Width % 4)
      if WidthRemainder != 0:
        Width += int(4 - WidthRemainder)
      ElementToRead = int((EndOfFrame - (Y_pixel * (Width)) - int(Width)) + int(X_pixel))
      # deal with unwanted sign bit
      PixelValue = ArrayIn[ElementToRead]
      if PixelValue < 0:
        PixelValue += 256
    elif BitDepth == 24:
      WidthRemainder = ((Width * 3) % 4)
      if WidthRemainder != 0:
        WidthRemainder = int(4 - WidthRemainder)
      ElementToRead = int(EndOfFrame - ((Y_pixel + 1) * ((Width * 3) + WidthRemainder))) + int(X_pixel * 3)
      # deal with unwanted sign bit
      RED = ArrayIn[ElementToRead + 2]
      GREEN = ArrayIn[ElementToRead + 1]
      BLUE = ArrayIn[ElementToRead]
      if RED < 0:
        RED += 256
      if GREEN < 0:
        GREEN += 256
      if BLUE < 0:
        BLUE += 256
      PixelValue = ((RED << 16) | (GREEN << 8) | BLUE)

  return PixelValue

def SetSinglePixelBit(X_pixel, Y_pixel, frame, BitToWrite, ArrayIn):
  Width = ReadWidth(ArrayIn)
  Height = ReadHeight(ArrayIn)
  BitDepth = ReadBitDepth(ArrayIn)
  if X_pixel >= 0 and X_pixel < Width and Y_pixel >= 0 and Y_pixel < Height and BitToWrite >= 0 and BitToWrite < BitDepth and frame >=0 and frame < ReadFrameCount(ArrayIn):
    EndOfFrame = GetEndOfFrame(frame, ArrayIn)
    if BitDepth == 8:
      WidthRemainder = (Width % 4)
      if WidthRemainder != 0:
        Width += int(4 - WidthRemainder)
      ElementToChange = int((EndOfFrame - (Y_pixel * (Width)) - int(Width)) + int(X_pixel))
      ArrayIn[ElementToChange] |= (1 << BitToWrite)
    elif BitDepth == 24:
      WidthRemainder = ((Width * 3) % 4)
      if WidthRemainder != 0:
        WidthRemainder = int(4 - WidthRemainder)
      ElementToChange = int(EndOfFrame - ((Y_pixel + 1) * ((Width * 3) + WidthRemainder))) + int(X_pixel * 3)
      if BitToWrite <= 7:
        ArrayIn[(ElementToChange)] |= (1 << (BitToWrite % 8))
      elif BitToWrite <= 15:
        ArrayIn[(ElementToChange + 1)] |= (1 << (BitToWrite % 8))
      else:
        ArrayIn[(ElementToChange + 2)] |= (1 << (BitToWrite % 8))
  return ArrayIn

def ClearSinglePixelBit(X_pixel, Y_pixel, frame, BitToWrite, ArrayIn):
  Width = ReadWidth(ArrayIn)
  Height = ReadHeight(ArrayIn)
  BitDepth = ReadBitDepth(ArrayIn)
  if X_pixel >= 0 and X_pixel < Width and Y_pixel >= 0 and Y_pixel < Height and BitToWrite >= 0 and BitToWrite < BitDepth and frame >=0 and frame < ReadFrameCount(ArrayIn):
    EndOfFrame = GetEndOfFrame(frame, ArrayIn)
    if BitDepth == 8:
      WidthRemainder = (Width % 4)
      if WidthRemainder != 0:
        Width += int(4 - WidthRemainder)
      ElementToChange = int((EndOfFrame - (Y_pixel * (Width)) - int(Width)) + int(X_pixel))
      ArrayIn[ElementToChange] &= ~(1 << BitToWrite)
    elif BitDepth == 24:
      WidthRemainder = ((Width * 3) % 4)
      if WidthRemainder != 0:
        WidthRemainder = int(4 - WidthRemainder)
      ElementToChange = int(EndOfFrame - ((Y_pixel + 1) * ((Width * 3) + WidthRemainder))) + int(X_pixel * 3)
      if BitToWrite <= 7:
        ArrayIn[(ElementToChange)] &= ~ (1 << (BitToWrite % 8))
      elif BitToWrite <= 15:
        ArrayIn[(ElementToChange + 1)] &= ~ (1 << (BitToWrite % 8))
      else:
        ArrayIn[(ElementToChange + 2)] &= ~ (1 << (BitToWrite % 8))
  return ArrayIn

def ToggleSinglePixelBit(X_pixel, Y_pixel, frame, BitToWrite, ArrayIn):
  Width = ReadWidth(ArrayIn)
  Height = ReadHeight(ArrayIn)
  BitDepth = ReadBitDepth(ArrayIn)
  if X_pixel >= 0 and X_pixel < Width and Y_pixel >= 0 and Y_pixel < Height and BitToWrite >= 0 and BitToWrite < BitDepth and frame >=0 and frame < ReadFrameCount(ArrayIn):
    EndOfFrame = GetEndOfFrame(frame, ArrayIn)
    if BitDepth == 8:
      WidthRemainder = (Width % 4)
      if WidthRemainder != 0:
        Width += int(4 - WidthRemainder)
      ElementToChange = int((EndOfFrame - (Y_pixel * (Width)) - int(Width)) + int(X_pixel))
      ArrayIn[ElementToChange] ^= (1 << BitToWrite)
    elif BitDepth == 24:
      WidthRemainder = ((Width * 3) % 4)
      if WidthRemainder != 0:
        WidthRemainder = int(4 - WidthRemainder)
      ElementToChange = int(EndOfFrame - ((Y_pixel + 1) * ((Width * 3) + WidthRemainder))) + int(X_pixel * 3)
      if BitToWrite <= 7:
        ArrayIn[(ElementToChange)] ^= (1 << (BitToWrite % 8))
      elif BitToWrite <= 15:
        ArrayIn[(ElementToChange + 1)] ^= (1 << (BitToWrite % 8))
      else:
        ArrayIn[(ElementToChange + 2)] ^= (1 << (BitToWrite % 8))
  return ArrayIn

def WriteBMP(frame, BMParray, ArrayIn):
  Width = ReadWidth(ArrayIn)
  Height = ReadHeight(ArrayIn)
  BitDepth = ReadBitDepth(ArrayIn)
  if frame < ReadFrameCount(ArrayIn) and BMPoperations.ReadXresolution(BMParray) == Width and BMPoperations.ReadYresolution(BMParray) == Height and BMPoperations.ReadBitDepth(BMParray) == BitDepth:
    StartOfImage = BMPoperations.GetStartOfImage(BMParray)
    StartOfFrame = GetStartOfFrame(frame, ArrayIn)
    FrameSize = CalculateFrameSize(Width, Height, BitDepth)
    for ByteToWrite in range (FrameSize):
      ArrayIn[(StartOfFrame + ByteToWrite)] = BMParray[(StartOfImage + ByteToWrite)]
  return ArrayIn

def ExtractBMP(frame, BMParray, ArrayIn):
  Width = ReadWidth(ArrayIn)
  Height = ReadHeight(ArrayIn)
  BitDepth = ReadBitDepth(ArrayIn)
  if frame < ReadFrameCount(ArrayIn) and BMPoperations.ReadXresolution(BMParray) == Width and BMPoperations.ReadYresolution(BMParray) == Height and BMPoperations.ReadBitDepth(BMParray) == BitDepth:
    StartOfImage = BMPoperations.GetStartOfImage(BMParray)
    StartOfFrame = GetStartOfFrame(frame, ArrayIn)
    FrameSize = CalculateFrameSize(Width, Height, BitDepth)
    for ByteToWrite in range (FrameSize):
      BMParray[(StartOfImage + ByteToWrite)] = ArrayIn[(StartOfFrame + ByteToWrite)]
  return BMParray

# The following is based on the Adafruit GFX library Copyright (c) 2013 Adafruit Industries. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

def WriteLine(x0, y0, x1, y1, frame, colour, ArrayIn):
  steep = False
  if math.fabs(y1 - y0) > math.fabs(x1 - x0):
    temp = x0
    x0 = y0
    y0 = temp
    temp = x1
    x1 = y1
    y1 = temp
    steep = True

  if (x0 > x1):
    temp = x0
    x0 = x1
    x1 = temp
    temp = y0
    y0 = y1
    y1 = temp

  dx = x1 - x0
  dy = math.fabs(y1 - y0)

  err = int(dx / 2)
  ystep = -1

  if (y0 < y1):
    ystep = 1

  while True:
    if x0 > x1:
      break
    if steep == True:
      WritePixel(y0, x0, frame, colour, ArrayIn)
    else:
      WritePixel(x0, y0, frame, colour, ArrayIn)

    err -= dy
    if (err < 0):
      y0 += ystep
      err += dx

    x0 += 1

def DrawFastVLine(x, y, h, frame, colour, ArrayIn):
  WriteLine(x, y, x, y + h - 1, frame, colour, ArrayIn)

def DrawFastHLine(x, y, w, frame, colour, ArrayIn):
  WriteLine(x, y, x + w - 1, y, frame, colour, ArrayIn)

def FillRect(x, y, w, h, frame, colour, ArrayIn):
  i = x
  PixelLimit = x + w

  while True:
    if i >= PixelLimit:
      break
    DrawFastVLine(i, y, h, frame, colour, ArrayIn)
    i += 1

def FillScreen(frame, colour, ArrayIn):
  FillRect(0, 0, ReadWidth(ArrayIn), ReadHeight(ArrayIn), frame, colour, ArrayIn)

def DrawLine(x0, y0, x1, y1, frame, colour, ArrayIn):
  if (x0 == x1):
    if (y0 > y1):
      temp = y0
      y0 = y1
      y1 = temp
    DrawFastVLine(x0, y0, y1 - y0 + 1, frame, colour, ArrayIn)
  elif (y0 == y1):
    if (x0 > x1):
      temp = x0
      x0 = x1
      x1 = temp
    DrawFastHLine(x0, y0, x1 - x0 + 1, frame, colour, ArrayIn)
  else:
    WriteLine(x0, y0, x1, y1, frame, colour, ArrayIn)

def DrawCircle(x0, y0, r, frame, colour, ArrayIn):
  f = 1 - r
  ddF_x = 1
  ddF_y = -2 * r
  x = 0
  y = r

  WritePixel(x0, y0 + r, frame, colour, ArrayIn)
  WritePixel(x0, y0 - r, frame, colour, ArrayIn)
  WritePixel(x0 + r, y0, frame, colour, ArrayIn)
  WritePixel(x0 - r, y0, frame, colour, ArrayIn)

  while (x < y):
    if (f >= 0):
      y -= 1
      ddF_y += 2
      f += ddF_y
    x += 1
    ddF_x += 2
    f += ddF_x

    WritePixel(x0 + x, y0 + y, frame, colour, ArrayIn)
    WritePixel(x0 - x, y0 + y, frame, colour, ArrayIn)
    WritePixel(x0 + x, y0 - y, frame, colour, ArrayIn)
    WritePixel(x0 - x, y0 - y, frame, colour, ArrayIn)
    WritePixel(x0 + y, y0 + x, frame, colour, ArrayIn)
    WritePixel(x0 - y, y0 + x, frame, colour, ArrayIn)
    WritePixel(x0 + y, y0 - x, frame, colour, ArrayIn)
    WritePixel(x0 - y, y0 - x, frame, colour, ArrayIn)

def DrawCircleHelper(x0, y0, r, cornername, frame, colour, ArrayIn):

  f = 1 - r
  ddF_x = 1
  ddF_y = -2 * r
  x = 0
  y = r

  while (x < y):
    if (f >= 0):
      y -= 1
      ddF_y += 2
      f += ddF_y

    x += 1
    ddF_x += 2
    f += ddF_x
    if (cornername & 0x4) != 0:
      WritePixel(x0 + x, y0 + y, frame, colour, ArrayIn)
      WritePixel(x0 + y, y0 + x, frame, colour, ArrayIn)

    if (cornername & 0x2) != 0:
      WritePixel(x0 + x, y0 - y, frame, colour, ArrayIn)
      WritePixel(x0 + y, y0 - x, frame, colour, ArrayIn)

    if (cornername & 0x8) != 0:
      WritePixel(x0 - y, y0 + x, frame, colour, ArrayIn)
      WritePixel(x0 - x, y0 + y, frame, colour, ArrayIn)

    if (cornername & 0x1) != 0:
      WritePixel(x0 - y, y0 - x, frame, colour, ArrayIn)
      WritePixel(x0 - x, y0 - y, frame, colour, ArrayIn)

def FillCircle(x0, y0, r, frame, colour, ArrayIn):
  DrawFastVLine(x0, y0 - r, 2 * r + 1, frame, colour, ArrayIn)
  FillCircleHelper(x0, y0, r, 3, 0, frame, colour, ArrayIn)

def FillCircleHelper(x0, y0, r, corners, delta, frame, colour, ArrayIn):
  f = 1 - r
  ddF_x = 1
  ddF_y = -2 * r
  x = 0
  y = r
  px = x
  py = y

  delta += 1 # Avoid some +1's in the loop

  while (x < y):
    if (f >= 0):
      y -= 1
      ddF_y += 2
      f += ddF_y
    x += 1
    ddF_x += 2
    f += ddF_x

    if (x < (y + 1)):
      if (corners & 1 != 0):
        DrawFastVLine(x0 + x, y0 - y, 2 * y + delta, frame, colour, ArrayIn)
      if (corners & 2 != 0):
        DrawFastVLine(x0 - x, y0 - y, 2 * y + delta, frame, colour, ArrayIn)

    if (y != py):
      if (corners & 1 != 0):
        DrawFastVLine(x0 + py, y0 - px, 2 * px + delta, frame, colour, ArrayIn)
      if (corners & 2 != 0):
        DrawFastVLine(x0 - py, y0 - px, 2 * px + delta, frame, colour, ArrayIn)
      py = y

    px = x

def DrawRect(x, y, w, h, frame, colour, ArrayIn):
  DrawFastHLine(x, y, w, frame, colour, ArrayIn)
  DrawFastHLine(x, y + h - 1, w, frame, colour, ArrayIn)
  DrawFastVLine(x, y, h, frame, colour, ArrayIn)
  DrawFastVLine(x + w - 1, y, h, frame, colour, ArrayIn)

def DrawRoundRect(x, y, w, h, r, frame, colour, ArrayIn):
  max_radius = h # 1/2 minor axis
  
  if (w < h):
    max_radius = w

  max_radius /= 2

  if (r > max_radius):
    r = max_radius
  # smarter version
  DrawFastHLine(x + r, y, w - 2 * r, frame, colour, ArrayIn)         # Top
  DrawFastHLine(x + r, y + h - 1, w - 2 * r, frame, colour, ArrayIn) # Bottom
  DrawFastVLine(x, y + r, h - 2 * r, frame, colour, ArrayIn)         # Left
  DrawFastVLine(x + w - 1, y + r, h - 2 * r, frame, colour, ArrayIn) # Right
  # draw four corners
  DrawCircleHelper(x + r, y + r, r, 1, frame, colour, ArrayIn)
  DrawCircleHelper(x + w - r - 1, y + r, r, 2, frame, colour, ArrayIn)
  DrawCircleHelper(x + w - r - 1, y + h - r - 1, r, 4, frame, colour, ArrayIn)
  DrawCircleHelper(x + r, y + h - r - 1, r, 8, frame, colour, ArrayIn)

def FillRoundRect(x, y, w, h, r, frame, colour, ArrayIn):
  max_radius = h # 1/2 minor axis
  
  if (w < h):
    max_radius = w

  max_radius /= 2

  if (r > max_radius):
    r = max_radius
  # smarter version
  FillRect(x + r, y, w - 2 * r, h, frame, colour, ArrayIn)
  # draw four corners
  FillCircleHelper(x + w - r - 1, y + r, r, 1, h - 2 * r - 1, frame, colour, ArrayIn)
  FillCircleHelper(x + r, y + r, r, 2, h - 2 * r - 1, frame, colour, ArrayIn)

def DrawTriangle(x0, y0, x1, y1, x2, y2, frame, colour, ArrayIn):
  DrawLine(x0, y0, x1, y1, frame, colour, ArrayIn)
  DrawLine(x1, y1, x2, y2, frame, colour, ArrayIn)
  DrawLine(x2, y2, x0, y0, frame, colour, ArrayIn)

def FillTriangle(x0, y0, x1, y1, x2, y2, frame, colour, ArrayIn):
  a = x0
  b = y0
  y = 0
  last = y1

  # Sort coordinates by Y order (y2 >= y1 >= y0)
  if (y0 > y1):
     temp = y0
     y0 = y1
     y1 = temp
     temp = x0
     x0 = x1
     x1 = temp
  if (y1 > y2):
     temp = y2
     y2 = y1
     y1 = temp
     temp = x2
     x2 = x1
     x1 = temp
  if (y0 > y1):
     temp = y0
     y0 = y1
     y1 = temp
     temp = x0
     x0 = x1
     x1 = temp

  if (y0 == y2): # Handle awkward all-on-same-line case as its own thing
    a = x0
    b = x0
    if (x1 < a):
      a = x1
    elif (x1 > b):
      b = x1
    if (x2 < a):
      a = x2
    elif (x2 > b):
      b = x2
    DrawFastHLine(a, y0, b - a + 1, frame, colour, ArrayIn)
    return

  dx01 = x1 - x0
  dy01 = y1 - y0
  dx02 = x2 - x0
  dy02 = y2 - y0
  dx12 = x2 - x1
  dy12 = y2 - y1
  sa = 0
  sb = 0

  # For upper part of triangle, find scanline crossings for segments
  # 0-1 and 0-2.  If y1=y2 (flat-bottomed triangle), the scanline y1
  # is included here (and second loop will be skipped, avoiding a /0
  # error there), otherwise scanline y1 is skipped here and handled
  # in the second loop...which also avoids a /0 error here if y0=y1
  # (flat-topped triangle).
  if (y1 != y2):
    last = y1 - 1 # Skip it

  y = y0
  while True:
    if y > last:
      break
    a = int(x0 + sa / dy01)
    b = int(x0 + sb / dy02)
    sa += dx01
    sb += dx02
    a = int(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
    b = int(x0 + (x2 - x0) * (y - y0) / (y2 - y0))
    if (a > b):
      temp = a
      a = b
      b = temp
    DrawFastHLine(a, y, b - a + 1, frame, colour, ArrayIn)
    y += 1

  # For lower part of triangle, find scanline crossings for segments
  # 0-2 and 1-2.  This loop is skipped if y1=y2.
  sa = dx12 * (y - y1)
  sb = dx02 * (y - y0)
  y = y0
  while True:
    if y > y2:
      break
    a = int(x1 + sa / dy12)
    b = int(x0 + sb / dy02)
    sa += dx12
    sb += dx02
    # longhand:
    a = int(x1 + (x2 - x1) * (y - y1) / (y2 - y1))
    b = int(x0 + (x2 - x0) * (y - y0) / (y2 - y0))
    if (a > b):
      temp = a
      a = b
      b = temp
    DrawFastHLine(a, y, b - a + 1, frame, colour, ArrayIn)
    y += 1