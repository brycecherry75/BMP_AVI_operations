#
# Error codes for CheckValidFormat()
#

ERROR_NONE = 0
ERROR_NOT_BMP = 1
ERROR_DATA_OFFSET_MISMATCH = 2
ERROR_FILE_SIZE_TO_RESOLUTION_MISMATCH = 3
ERROR_FILE_SIZE_TO_HEADER_MISMATCH = 4
ERROR_INFO_HEADER_SIZE_INCORRECT = 5
ERROR_FILE_SIZE_DATA_OFFSET_RESOLUTION_MISMATCH = 6
ERROR_PLANE_COUNT_NOT_1 = 7
ERROR_INVALID_COLOUR_DEPTH = 8
ERROR_IMAGE_IS_COMPRESSED = 9
ERROR_IMAGE_SIZE_INCORRECT = 10
ERROR_RIFF_PALETTE_SIZE_INCORRECT = 11
ERROR_RIFF_PALETTE_NO_RIFF_ID = 12
ERROR_RIFF_PALETTE_NO_DATA_ID = 13
ERROR_RIFF_PALETTE_HEADER_TABLE_SIZE_INCORRECT = 14
ERROR_RIFF_PALETTE_HEADER_SIZE_INCORRECT = 15
ERROR_RIFF_PALETTE_0x14_VALUE_INCORRECT = 16
ERROR_RIFF_PALETTE_TERMINATOR_VALUE_INCORRECT = 17



HeaderSizeBeforePaletteOrImageData = 0x36

import math

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

def ReadPaletteSizeInRIFFfile(ArrayIn):
  return ReadWordInt(0x16, ArrayIn)

def CheckValidPaletteFormat(ArrayIn):
  if len(ArrayIn) != 92 and len(ArrayIn) != 1052:
    return ERROR_RIFF_PALETTE_SIZE_INCORRECT
  if ArrayIn[0x00] != 0x52 or ArrayIn[0x01] != 0x49 or ArrayIn[0x02] != 0x46 or ArrayIn[0x03] != 0x46:
    return ERROR_RIFF_PALETTE_NO_RIFF_ID
  if ArrayIn[0x08] != 0x50 or ArrayIn[0x09] != 0x41 or ArrayIn[0x0A] != 0x4C or ArrayIn[0x0B] != 0x20 or ArrayIn[0x0C] != 0x64 or ArrayIn[0x0D] != 0x61 or ArrayIn[0x0E] != 0x74 or ArrayIn[0x0F] != 0x61:
    return ERROR_RIFF_PALETTE_NO_DATA_ID
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

def CheckValidFormat(ArrayIn):
  if ArrayIn[0x00] != 0x42 or ArrayIn[0x01] != 0x4D:
    return ERROR_NOT_BMP
  if ReadLongInt(0x02, ArrayIn) != len(ArrayIn):
    return ERROR_FILE_SIZE_TO_HEADER_MISMATCH
  DataOffset = ReadLongInt(0x0A, ArrayIn)
  X_resolution = ReadXresolution(ArrayIn)
  Y_resolution = ReadYresolution(ArrayIn)
  HeaderSize = HeaderSizeBeforePaletteOrImageData
  ColourDepth = ReadBitDepth(ArrayIn)
  if CalculateFileSize(X_resolution, Y_resolution, ColourDepth) != len(ArrayIn):
    return ERROR_FILE_SIZE_TO_RESOLUTION_MISMATCH
  if ColourDepth != 24 and ColourDepth != 16:
    HeaderSize += (4 * (1 << int(ColourDepth)))
  if DataOffset != HeaderSize:
    return ERROR_DATA_OFFSET_MISMATCH
  InfoHeaderSize = ReadLongInt(0x0E, ArrayIn)
  if (InfoHeaderSize != 40):
    return ERROR_INFO_HEADER_SIZE_INCORRECT
  if ReadWordInt(0x1A, ArrayIn) != 1:
    return ERROR_PLANE_COUNT_NOT_1
  if ColourDepth != 1 and ColourDepth != 4 and ColourDepth != 8 and ColourDepth != 16 and ColourDepth != 24:
    return ERROR_INVALID_COLOUR_DEPTH
  if ReadLongInt(0x1E, ArrayIn) != 0:
    return ERROR_IMAGE_IS_COMPRESSED
  if ReadLongInt(0x22, ArrayIn) != (len(ArrayIn) - DataOffset):
    return ERROR_IMAGE_SIZE_INCORRECT
  return ERROR_NONE

def CombineRGBvalues_RGB888(r, g, b):
  return (((int(r) & 0xFF) << 16) | ((int(g) & 0xFF) << 8) | (int(b) & 0xFF))

def SeparateRGBvalues_RGB888(value):
  value = int(value)
  return ((value >> 16) & 0xFF), ((value >> 8) & 0xFF), (value & 0xFF)

def CombineRGBvalues_RGB555(r, g, b):
  return (((int(r) & 0xF8) << 7) | ((int(g) & 0xF8) << 2) | ((int(b) & 0xF8) >> 3))

def SeparateRGBvalues_RGB555(value):
  value = int(value)
  return ((value >> 7) & 0xFF), ((value >> 3) & 0xFF), ((value << 3) & 0xFF)

def CombineRGBvalues_RGB565(r, g, b):
  return (((int(r) & 0xF8) << 8) | ((int(g) & 0xFC) << 3) | ((int(b) & 0xF8) >> 3))

def SeparateRGBvalues_RGB565(value):
  value = int(value)
  return ((value >> 8) & 0xFF), ((value >> 3) & 0xFF), ((value << 3) & 0xFF)

def WriteHeader(X_resolution, Y_resolution, BitDepth, XpixelsPerMetre, YpixelsPerMetre, ArrayIn):
  if ((BitDepth == 1 or BitDepth == 4 or BitDepth == 8 or BitDepth == 16 or BitDepth == 24) and X_resolution > 0 and X_resolution < 4294967296 and Y_resolution > 0 and Y_resolution < 4294967296 and XpixelsPerMetre > 0 and XpixelsPerMetre < 4294967296 and YpixelsPerMetre > 0 and YpixelsPerMetre < 4294967296):
    DataOffset = HeaderSizeBeforePaletteOrImageData
    if BitDepth != 24 and BitDepth != 16: # 16 or 24 bit formats do not have a palette
      DataOffset += (4 * (1 << BitDepth))
    FileSize = CalculateFileSize(X_resolution, Y_resolution, BitDepth)
    if (FileSize - DataOffset) > 0 and (FileSize - DataOffset) < 4294967296:
      for ByteToClear in range (DataOffset):
        ArrayIn[ByteToClear] = 0x00

      # BM ID
      ArrayIn[0x00] = 0x42
      ArrayIn[0x01] = 0x4D

      WriteLongInt(0x02, int(FileSize), ArrayIn)
      WriteLongInt(0x06, 0, ArrayIn) # unused
      WriteLongInt(0x0A, int(DataOffset), ArrayIn)
      WriteLongInt(0x0E, 40, ArrayIn) # Info header size
      WriteLongInt(0x12, int(X_resolution), ArrayIn)
      WriteLongInt(0x16, int(Y_resolution), ArrayIn)
      WriteWordInt(0x1A, 1, ArrayIn) # plane count
      WriteWordInt(0x1C, int(BitDepth), ArrayIn)
      WriteLongInt(0x1E, 0, ArrayIn) # no compression
      WriteLongInt(0x22, int(FileSize - DataOffset), ArrayIn) # image size
      WriteLongInt(0x26, int(XpixelsPerMetre), ArrayIn)
      WriteLongInt(0x2A, int(YpixelsPerMetre), ArrayIn)
      WriteLongInt(0x2E, (1 << BitDepth), ArrayIn)
      WriteLongInt(0x32, 0, ArrayIn) # Important colours (0 = all colours are important)

  return ArrayIn

def ReadXresolution(ArrayIn):
  return ReadLongInt(0x12, ArrayIn)

def ReadYresolution(ArrayIn):
  return ReadLongInt(0x16, ArrayIn)

def ReadBitDepth(ArrayIn):
  return ReadWordInt(0x1C, ArrayIn)

def ReadXpixelsPerMetre(ArrayIn):
  return ReadLongInt(0x26, ArrayIn)

def ReadYpixelsPerMetre(ArrayIn):
  return ReadLongInt(0x2A, ArrayIn)

def GetStartOfImage(ArrayIn):
  HeaderSize = HeaderSizeBeforePaletteOrImageData
  BitDepth = ReadBitDepth(ArrayIn)
  if BitDepth != 24 and BitDepth != 16:
    HeaderSize += (4 * (1 << ReadBitDepth(ArrayIn)))
  return HeaderSize

def CalculateFileSize(X_resolution, Y_resolution, BitDepth):
  HeaderSize = HeaderSizeBeforePaletteOrImageData
  if BitDepth != 24 and BitDepth != 16:
    HeaderSize += (4 * (1 << BitDepth))
  if BitDepth == 1:
    X_resolutionRemainder = (X_resolution % 32) # 71 % 32 = 7
    if X_resolutionRemainder != 0:
      X_resolution += (32 - X_resolutionRemainder) # now 96
    FileSize = int(HeaderSize + ((X_resolution * Y_resolution) / 8))
    if FileSize <= 4294967295:
      return FileSize
    else:
      return 0
  elif BitDepth == 4:
    X_resolutionRemainder = (X_resolution % 8) # 26 % 8 = 2
    if X_resolutionRemainder != 0:
      X_resolution += (8 - X_resolutionRemainder) # now 32
    FileSize = int(HeaderSize + ((X_resolution * Y_resolution) / 2))
    if FileSize <= 4294967295:
      return FileSize
    else:
      return 0
  elif BitDepth == 8:
    X_resolutionRemainder = (X_resolution % 4)
    if X_resolutionRemainder != 0:
      X_resolution += int(4 - X_resolutionRemainder)
    FileSize = int(HeaderSize + (X_resolution * Y_resolution))
    if FileSize <= 4294967295:
      return FileSize
    else:
      return 0
  elif BitDepth == 16:
    X_resolutionRemainder = ((X_resolution * 2) % 4)
    if X_resolutionRemainder != 0:
      X_resolution += int(2 - X_resolutionRemainder)
    FileSize = int(HeaderSize + (((X_resolution * 2) + X_resolutionRemainder) * Y_resolution))
    if FileSize <= 4294967295:
      return FileSize
    else:
      return 0
  elif BitDepth == 24:
    X_resolutionRemainder = ((X_resolution * 3) % 4)
    if X_resolutionRemainder != 0:
      X_resolutionRemainder = int(4 - X_resolutionRemainder)
    FileSize = int(HeaderSize + (((X_resolution * 3) + X_resolutionRemainder) * Y_resolution))
    if FileSize <= 4294967295:
      return FileSize
    else:
      return 0
  else:
    return 0

def CalculatePaletteSize(BitDepth):
  if BitDepth == 1 or BitDepth == 4 or BitDepth == 8:
    return ((1 << BitDepth) * 4)
  else:
    return 0

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

def ReadRIFFpalette(PaletteIn, ArrayIn):
  if CheckValidPaletteFormat(ArrayIn) == ERROR_NONE:
    PaletteEntries = ReadWordInt(0x16, ArrayIn)
    if PaletteEntries == 16 or PaletteEntries == 256:
      for PaletteEntryToWrite in range (PaletteEntries):
        for Subpixel in range (3):
          PaletteIn[((PaletteEntryToWrite * 3) + Subpixel)] = ArrayIn[(0x18 + (PaletteEntryToWrite * 4) + Subpixel)]
  return PaletteIn

def WritePalette(PaletteIn, ArrayIn):
  BitDepth = ReadLongInt(0x1C, ArrayIn)
  if BitDepth == 1 or BitDepth == 4 or BitDepth == 8:
    PaletteEntries = (1 << BitDepth)
    for PaletteEntryToWrite in range (PaletteEntries):
      for Subpixel in range (4):
        if (Subpixel != 3):
          ArrayIn[(HeaderSizeBeforePaletteOrImageData + (PaletteEntryToWrite * 4) + (2 - Subpixel))] = PaletteIn[((PaletteEntryToWrite * 3) + Subpixel)]
        else:
          ArrayIn[(HeaderSizeBeforePaletteOrImageData + (PaletteEntryToWrite * 4) + Subpixel)] = 0
  return ArrayIn

def ReadPalette(PaletteIn, ArrayIn):
  BitDepth = ReadLongInt(0x1C, ArrayIn)
  if BitDepth == 1 or BitDepth == 4 or BitDepth == 8:
    PaletteEntries = (1 << BitDepth)
    for PaletteEntryToWrite in range (PaletteEntries):
      for Subpixel in range (3):
        PaletteIn[((PaletteEntryToWrite * 3) + (2 - Subpixel))] = ArrayIn[(HeaderSizeBeforePaletteOrImageData + (PaletteEntryToWrite * 4) + Subpixel)]
  return PaletteIn

def WritePixel(X_pixel, Y_pixel, value, ArrayIn):
  X_resolution = ReadXresolution(ArrayIn)
  Y_resolution = ReadYresolution(ArrayIn)
  BitDepth = ReadBitDepth(ArrayIn)
  ArraySize = len(ArrayIn)
  if X_pixel >= 0 and X_pixel < X_resolution and Y_pixel >= 0 and Y_pixel < Y_resolution:
    if BitDepth == 1:
      X_resolutionRemainder = (X_resolution % 32) # 639 % 32 = 31
      if X_resolutionRemainder != 0:
        X_resolution += (32 - X_resolutionRemainder) # now 640
      X_resolution /= 8 # now 80
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int((X_pixel / 8)))
      remainder = (X_pixel % 8)
      mask = 0x01
      value <<= (7 - remainder)
      mask <<= (7 - remainder)
      ArrayIn[ElementToChange] &= ~mask
      ArrayIn[ElementToChange] |= value
    elif BitDepth == 4:
      X_resolutionRemainder = (X_resolution % 4) # 639 % 4 = 3
      if X_resolutionRemainder != 0:
        X_resolution += (4 - X_resolutionRemainder) # now 640
      X_resolution /= 2 # now 320
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int((X_pixel / 2)))
      mask = 0x0F
      if (X_pixel % 2) == 0:
        value <<= 4
        mask <<= 4
      ArrayIn[ElementToChange] &= ~mask
      ArrayIn[ElementToChange] |= value
    elif BitDepth == 8:
      X_resolutionRemainder = (X_resolution % 4)
      if X_resolutionRemainder != 0:
        X_resolution += int(4 - X_resolutionRemainder)
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int(X_pixel))
      ArrayIn[ElementToChange] = (value & 0xFF)
    elif BitDepth == 16:
      X_resolutionRemainder = ((X_resolution * 2) % 4)
      ElementToChange = int(ArraySize - ((Y_pixel + 1) * ((X_resolution * 2) + X_resolutionRemainder))) + int(X_pixel * 2)
      ArrayIn[(ElementToChange)] = (value & 0xFF)
      ArrayIn[(ElementToChange + 1)] = ((value >> 8) & 0xFF)
    elif BitDepth == 24:
      X_resolutionRemainder = ((X_resolution * 3) % 4)
      if X_resolutionRemainder != 0:
        X_resolutionRemainder = int(4 - X_resolutionRemainder)
      ElementToChange = int(ArraySize - ((Y_pixel + 1) * ((X_resolution * 3) + X_resolutionRemainder))) + int(X_pixel * 3)
      ArrayIn[ElementToChange] = (value & 0xFF)
      ArrayIn[(ElementToChange + 1)] = ((value >> 8) & 0xFF)
      ArrayIn[(ElementToChange + 2)] = ((value >> 16) & 0xFF)
  return ArrayIn

def ReadPixel(X_pixel, Y_pixel, ArrayIn):
  X_resolution = ReadXresolution(ArrayIn)
  Y_resolution = ReadYresolution(ArrayIn)
  BitDepth = ReadBitDepth(ArrayIn)
  PixelValue = 0
  ArraySize = len(ArrayIn)
  if X_pixel >= 0 and X_pixel < X_resolution and Y_pixel >= 0 and Y_pixel < Y_resolution:
    if BitDepth == 1:
      X_resolutionRemainder = (X_resolution % 4) # 639 % 4 = 3
      if X_resolutionRemainder != 0:
        X_resolution += (4 - X_resolutionRemainder) # now 640
      X_resolution /= 8 # now 80
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int((X_pixel / 8)))
      PixelValue = ArrayIn[ElementToChange]
      remainder = (X_pixel % 8)
      PixelValue >>= (7 - remainder)
      PixelValue &= 0x01
    elif BitDepth == 4:
      X_resolutionRemainder = (X_resolution % 4) # 639 % 4 = 3
      if X_resolutionRemainder != 0:
        X_resolution += (4 - X_resolutionRemainder) # now 640
      X_resolution /= 2 # now 320
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int((X_pixel / 2)))
      PixelValue = ArrayIn[ElementToChange]
      #deal with unwanted sign bit
      if PixelValue > 0:
        PixelValue += 256
      if (X_pixel % 2) == 0:
        PixelValue >>= 4
      PixelValue &= 0x0F
    elif BitDepth == 8:
      X_resolutionRemainder = (X_resolution % 4)
      if X_resolutionRemainder != 0:
        X_resolution += int(4 - X_resolutionRemainder)
      ElementToRead = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int(X_pixel))
      # deal with unwanted sign bit
      PixelValue = ArrayIn[ElementToRead]
      if PixelValue < 0:
        PixelValue += 256
    elif BitDepth == 16:
      X_resolutionRemainder = ((X_resolution * 2) % 4)
      if X_resolutionRemainder != 0:
        X_resolution += int(2 - X_resolutionRemainder)
      ElementToRead = int(ArraySize - ((Y_pixel + 1) * ((X_resolution * 2) + X_resolutionRemainder))) + int(X_pixel * 2)
      # deal with unwanted sign bit
      Element1 = ArrayIn[ElementToRead + 1]
      Element2 = ArrayIn[ElementToRead]
      if Element1 < 0:
        Element1 += 256
      if Element2 < 0:
        Element2 += 256
      PixelValue = ((Element1 << 8) | Element2)
    elif BitDepth == 24:
      X_resolutionRemainder = ((X_resolution * 3) % 4)
      if X_resolutionRemainder != 0:
        X_resolutionRemainder = int(4 - X_resolutionRemainder)
      ElementToRead = int(ArraySize - ((Y_pixel + 1) * ((X_resolution * 3) + X_resolutionRemainder))) + int(X_pixel * 3)
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

def SetSinglePixelBit(X_pixel, Y_pixel, BitToWrite, ArrayIn):
  ArraySize = len(ArrayIn)
  X_resolution = ReadXresolution(ArrayIn)
  Y_resolution = ReadYresolution(ArrayIn)
  BitDepth = ReadBitDepth(ArrayIn)
  if X_pixel >= 0 and X_pixel < X_resolution and Y_pixel >= 0 and Y_pixel < Y_resolution and BitToWrite >= 0 and BitToWrite < BitDepth:
    if BitDepth == 1:
      X_resolutionRemainder = (X_resolution % 32) # 639 % 32 = 31
      if X_resolutionRemainder != 0:
        X_resolution += (32 - X_resolutionRemainder) # now 640
      X_resolution /= 8 # now 80
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int((X_pixel / 8)))
      remainder = (X_pixel % 8)
      value = 1
      value <<= (7 - remainder)
      ArrayIn[ElementToChange] |= value
    elif BitDepth == 4:
      X_resolutionRemainder = (X_resolution % 4) # 639 % 4 = 3
      if X_resolutionRemainder != 0:
        X_resolution += (4 - X_resolutionRemainder) # now 640
      X_resolution /= 2 # now 320
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int((X_pixel / 2)))
      value = (1 << BitToWrite)
      if (X_pixel % 2) == 0:
        value <<= 4
      ArrayIn[ElementToChange] |= value
    elif BitDepth == 8:
      X_resolutionRemainder = (X_resolution % 4)
      if X_resolutionRemainder != 0:
        X_resolution += int(4 - X_resolutionRemainder)
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int(X_pixel))
      ArrayIn[ElementToChange] |= (1 << BitToWrite)
    elif BitDepth == 16:
      X_resolutionRemainder = ((X_resolution * 2) % 4)
      if X_resolutionRemainder != 0:
        X_resolution += int(2 - X_resolutionRemainder)
      ElementToChange = int(ArraySize - ((Y_pixel + 1) * ((X_resolution * 2) + X_resolutionRemainder))) + int(X_pixel * 2)
      if BitToWrite <= 7:
        ArrayIn[(ElementToChange)] |= (1 << (BitToWrite % 8))
      else:
        ArrayIn[(ElementToChange + 1)] |= (1 << (BitToWrite % 8))
    elif BitDepth == 24:
      X_resolutionRemainder = ((X_resolution * 3) % 4)
      if X_resolutionRemainder != 0:
        X_resolutionRemainder = int(4 - X_resolutionRemainder)
      ElementToChange = int(ArraySize - ((Y_pixel + 1) * ((X_resolution * 3) + X_resolutionRemainder))) + int(X_pixel * 3)
      if BitToWrite <= 7:
        ArrayIn[(ElementToChange)] |= (1 << (BitToWrite % 8))
      elif BitToWrite <= 15:
        ArrayIn[(ElementToChange + 1)] |= (1 << (BitToWrite % 8))
      else:
        ArrayIn[(ElementToChange + 2)] |= (1 << (BitToWrite % 8))
  return ArrayIn

def ClearSinglePixelBit(X_pixel, Y_pixel, BitToWrite, ArrayIn):
  ArraySize = len(ArrayIn)
  X_resolution = ReadXresolution(ArrayIn)
  Y_resolution = ReadYresolution(ArrayIn)
  BitDepth = ReadBitDepth(ArrayIn)
  if X_pixel >= 0 and X_pixel < X_resolution and Y_pixel >= 0 and Y_pixel < Y_resolution and BitToWrite >= 0 and BitToWrite < BitDepth:
    if BitDepth == 1:
      X_resolutionRemainder = (X_resolution % 32) # 639 % 32 = 1
      if X_resolutionRemainder != 0:
        X_resolution += (32 - X_resolutionRemainder) # now 640
      X_resolution /= 8 # now 80
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int((X_pixel / 8)))
      remainder = (X_pixel % 8)
      value = 1
      value <<= (7 - remainder)
      ArrayIn[ElementToChange] &= ~value
    elif BitDepth == 4:
      X_resolutionRemainder = (X_resolution % 4) # 639 % 4 = 3
      if X_resolutionRemainder != 0:
        X_resolution += (4 - X_resolutionRemainder) # now 640
      X_resolution /= 2 # now 320
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int((X_pixel / 2)))
      value = (1 << BitToWrite)
      mask = 0x0F
      if (X_pixel % 2) == 0:
        value <<= 4
        mask <<= 4
      ArrayIn[ElementToChange] &= ~value
    elif BitDepth == 8:
      X_resolutionRemainder = (X_resolution % 4)
      if X_resolutionRemainder != 0:
        X_resolution += int(4 - X_resolutionRemainder)
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int(X_pixel))
      ArrayIn[ElementToChange] &= ~(1 << BitToWrite)
    elif BitDepth == 16:
      X_resolutionRemainder = ((X_resolution * 2) % 4)
      if X_resolutionRemainder != 0:
        X_resolution += int(2 - X_resolutionRemainder)
      ElementToChange = int(ArraySize - ((Y_pixel + 1) * ((X_resolution * 2) + X_resolutionRemainder))) + int(X_pixel * 2)
      if BitToWrite <= 7:
        ArrayIn[(ElementToChange)] &= ~(1 << (BitToWrite % 8))
      else:
        ArrayIn[(ElementToChange + 1)] &= ~(1 << (BitToWrite % 8))
    elif BitDepth == 24:
      X_resolutionRemainder = ((X_resolution * 3) % 4)
      if X_resolutionRemainder != 0:
        X_resolutionRemainder = int(4 - X_resolutionRemainder)
      ElementToChange = int(ArraySize - ((Y_pixel + 1) * ((X_resolution * 3) + X_resolutionRemainder))) + int(X_pixel * 3)
      if BitToWrite <= 7:
        ArrayIn[(ElementToChange)] &= ~ (1 << (BitToWrite % 8))
      elif BitToWrite <= 15:
        ArrayIn[(ElementToChange + 1)] &= ~ (1 << (BitToWrite % 8))
      else:
        ArrayIn[(ElementToChange + 2)] &= ~ (1 << (BitToWrite % 8))
  return ArrayIn

def ToggleSinglePixelBit(X_pixel, Y_pixel, BitToWrite, ArrayIn):
  ArraySize = len(ArrayIn)
  X_resolution = ReadXresolution(ArrayIn)
  Y_resolution = ReadYresolution(ArrayIn)
  BitDepth = ReadBitDepth(ArrayIn)
  if X_pixel >= 0 and X_pixel < X_resolution and Y_pixel >= 0 and Y_pixel < Y_resolution and BitToWrite >= 0 and BitToWrite < BitDepth:
    if BitDepth == 1:
      X_resolutionRemainder = (X_resolution % 32) # 639 % 32 = 31
      if X_resolutionRemainder != 0:
        X_resolution += (32 - X_resolutionRemainder) # now 640
      X_resolution /= 8 # now 80
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int((X_pixel / 8)))
      value = 1
      remainder = (X_pixel % 8)
      value <<= (7 - remainder)
      ArrayIn[ElementToChange] ^= value
    elif BitDepth == 4:
      X_resolutionRemainder = (X_resolution % 4) # 639 % 4 = 3
      if X_resolutionRemainder != 0:
        X_resolution += (4 - X_resolutionRemainder) # now 640
      X_resolution /= 2 # now 320
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int((X_pixel / 2)))
      value = (1 << BitToWrite)
      mask = 0x0F
      if (X_pixel % 2) == 0:
        value <<= 4
        mask <<= 4
      ArrayIn[ElementToChange] ^= value
    elif BitDepth == 8:
      X_resolutionRemainder = (X_resolution % 4)
      if X_resolutionRemainder != 0:
        X_resolution += int(4 - X_resolutionRemainder)
      ElementToChange = int((ArraySize - (Y_pixel * (X_resolution)) - int(X_resolution)) + int(X_pixel))
      ArrayIn[ElementToChange] ^= (1 << BitToWrite)
    elif BitDepth == 16:
      X_resolutionRemainder = ((X_resolution * 2) % 4)
      if X_resolutionRemainder != 0:
        X_resolution += int(2 - X_resolutionRemainder)
      ElementToChange = int(ArraySize - ((Y_pixel + 1) * ((X_resolution * 2) + X_resolutionRemainder))) + int(X_pixel * 2)
      if BitToWrite <= 7:
        ArrayIn[(ElementToChange)] ^= (1 << (BitToWrite % 8))
      else:
        ArrayIn[(ElementToChange + 1)] ^= (1 << (BitToWrite % 8))
    elif BitDepth == 24:
      X_resolutionRemainder = ((X_resolution * 3) % 4)
      if X_resolutionRemainder != 0:
        X_resolutionRemainder = int(4 - X_resolutionRemainder)
      ElementToChange = int(ArraySize - ((Y_pixel + 1) * ((X_resolution * 3) + X_resolutionRemainder))) + int(X_pixel * 3)
      if BitToWrite <= 7:
        ArrayIn[(ElementToChange)] ^= (1 << (BitToWrite % 8))
      elif BitToWrite <= 15:
        ArrayIn[(ElementToChange + 1)] ^= (1 << (BitToWrite % 8))
      else:
        ArrayIn[(ElementToChange + 2)] ^= (1 << (BitToWrite % 8))
  return ArrayIn

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

def WriteLine(x0, y0, x1, y1, colour, ArrayIn):
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
      WritePixel(y0, x0, colour, ArrayIn)
    else:
      WritePixel(x0, y0, colour, ArrayIn)

    err -= dy
    if (err < 0):
      y0 += ystep
      err += dx

    x0 += 1

def DrawFastVLine(x, y, h, colour, ArrayIn):
  WriteLine(x, y, x, y + h - 1, colour, ArrayIn)

def DrawFastHLine(x, y, w, colour, ArrayIn):
  WriteLine(x, y, x + w - 1, y, colour, ArrayIn)

def FillRect(x, y, w, h, colour, ArrayIn):
  i = x
  PixelLimit = x + w

  while True:
    if i >= PixelLimit:
      break
    DrawFastVLine(i, y, h, colour, ArrayIn)
    i += 1

def FillScreen(colour, ArrayIn):
  FillRect(0, 0, ReadXresolution(ArrayIn), ReadYresolution(ArrayIn), colour, ArrayIn)

def DrawLine(x0, y0, x1, y1, colour, ArrayIn):
  if (x0 == x1):
    if (y0 > y1):
      temp = y0
      y0 = y1
      y1 = temp
    DrawFastVLine(x0, y0, y1 - y0 + 1, colour, ArrayIn)
  elif (y0 == y1):
    if (x0 > x1):
      temp = x0
      x0 = x1
      x1 = temp
    DrawFastHLine(x0, y0, x1 - x0 + 1, colour, ArrayIn)
  else:
    WriteLine(x0, y0, x1, y1, colour, ArrayIn)

def DrawCircle(x0, y0, r, colour, ArrayIn):
  f = 1 - r
  ddF_x = 1
  ddF_y = -2 * r
  x = 0
  y = r

  WritePixel(x0, y0 + r, colour, ArrayIn)
  WritePixel(x0, y0 - r, colour, ArrayIn)
  WritePixel(x0 + r, y0, colour, ArrayIn)
  WritePixel(x0 - r, y0, colour, ArrayIn)

  while (x < y):
    if (f >= 0):
      y -= 1
      ddF_y += 2
      f += ddF_y
    x += 1
    ddF_x += 2
    f += ddF_x

    WritePixel(x0 + x, y0 + y, colour, ArrayIn)
    WritePixel(x0 - x, y0 + y, colour, ArrayIn)
    WritePixel(x0 + x, y0 - y, colour, ArrayIn)
    WritePixel(x0 - x, y0 - y, colour, ArrayIn)
    WritePixel(x0 + y, y0 + x, colour, ArrayIn)
    WritePixel(x0 - y, y0 + x, colour, ArrayIn)
    WritePixel(x0 + y, y0 - x, colour, ArrayIn)
    WritePixel(x0 - y, y0 - x, colour, ArrayIn)

def DrawCircleHelper(x0, y0, r, cornername, colour, ArrayIn):

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
      WritePixel(x0 + x, y0 + y, colour, ArrayIn)
      WritePixel(x0 + y, y0 + x, colour, ArrayIn)

    if (cornername & 0x2) != 0:
      WritePixel(x0 + x, y0 - y, colour, ArrayIn)
      WritePixel(x0 + y, y0 - x, colour, ArrayIn)

    if (cornername & 0x8) != 0:
      WritePixel(x0 - y, y0 + x, colour, ArrayIn)
      WritePixel(x0 - x, y0 + y, colour, ArrayIn)

    if (cornername & 0x1) != 0:
      WritePixel(x0 - y, y0 - x, colour, ArrayIn)
      WritePixel(x0 - x, y0 - y, colour, ArrayIn)

def FillCircle(x0, y0, r, colour, ArrayIn):
  DrawFastVLine(x0, y0 - r, 2 * r + 1, colour, ArrayIn)
  FillCircleHelper(x0, y0, r, 3, 0, colour, ArrayIn)

def FillCircleHelper(x0, y0, r, corners, delta, colour, ArrayIn):
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
        DrawFastVLine(x0 + x, y0 - y, 2 * y + delta, colour, ArrayIn)
      if (corners & 2 != 0):
        DrawFastVLine(x0 - x, y0 - y, 2 * y + delta, colour, ArrayIn)

    if (y != py):
      if (corners & 1 != 0):
        DrawFastVLine(x0 + py, y0 - px, 2 * px + delta, colour, ArrayIn)
      if (corners & 2 != 0):
        DrawFastVLine(x0 - py, y0 - px, 2 * px + delta, colour, ArrayIn)
      py = y

    px = x

def DrawRect(x, y, w, h, colour, ArrayIn):
  DrawFastHLine(x, y, w, colour, ArrayIn)
  DrawFastHLine(x, y + h - 1, w, colour, ArrayIn)
  DrawFastVLine(x, y, h, colour, ArrayIn)
  DrawFastVLine(x + w - 1, y, h, colour, ArrayIn)

def DrawRoundRect(x, y, w, h, r, colour, ArrayIn):
  max_radius = h # 1/2 minor axis
  
  if (w < h):
    max_radius = w

  max_radius /= 2

  if (r > max_radius):
    r = max_radius
  # smarter version
  DrawFastHLine(x + r, y, w - 2 * r, colour, ArrayIn)         # Top
  DrawFastHLine(x + r, y + h - 1, w - 2 * r, colour, ArrayIn) # Bottom
  DrawFastVLine(x, y + r, h - 2 * r, colour, ArrayIn)         # Left
  DrawFastVLine(x + w - 1, y + r, h - 2 * r, colour, ArrayIn) # Right
  # draw four corners
  DrawCircleHelper(x + r, y + r, r, 1, colour, ArrayIn)
  DrawCircleHelper(x + w - r - 1, y + r, r, 2, colour, ArrayIn)
  DrawCircleHelper(x + w - r - 1, y + h - r - 1, r, 4, colour, ArrayIn)
  DrawCircleHelper(x + r, y + h - r - 1, r, 8, colour, ArrayIn)

def FillRoundRect(x, y, w, h, r, colour, ArrayIn):
  max_radius = h # 1/2 minor axis
  
  if (w < h):
    max_radius = w

  max_radius /= 2

  if (r > max_radius):
    r = max_radius
  # smarter version
  FillRect(x + r, y, w - 2 * r, h, colour, ArrayIn)
  # draw four corners
  FillCircleHelper(x + w - r - 1, y + r, r, 1, h - 2 * r - 1, colour, ArrayIn)
  FillCircleHelper(x + r, y + r, r, 2, h - 2 * r - 1, colour, ArrayIn)

def DrawTriangle(x0, y0, x1, y1, x2, y2, colour, ArrayIn):
  DrawLine(x0, y0, x1, y1, colour, ArrayIn)
  DrawLine(x1, y1, x2, y2, colour, ArrayIn)
  DrawLine(x2, y2, x0, y0, colour, ArrayIn)

def FillTriangle(x0, y0, x1, y1, x2, y2, colour, ArrayIn):
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
    DrawFastHLine(a, y0, b - a + 1, colour, ArrayIn)
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
    DrawFastHLine(a, y, b - a + 1, colour, ArrayIn)
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
    DrawFastHLine(a, y, b - a + 1, colour, ArrayIn)
    y += 1