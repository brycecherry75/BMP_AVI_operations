import argparse, struct, sys, os, ctypes, BMPoperations, PlaintextPaletteToBinaryArray

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--bmpfile", help="BMP file to patch")
  parser.add_argument("--palettefile", help="BMP palette file")
  args = parser.parse_args()
  bmpfilename = args.bmpfile
  palettefilename = args.palettefile

  ValidParameters = True

  if not args.bmpfile:
    ValidParameters = False
    print("BMP file not specified")
  elif not os.path.isfile(bmpfilename):
    ValidParameters = False
    print("BMP file not found")
  if not args.palettefile:
    ValidParameters = False
    print("Palette file not specified")
  elif not os.path.isfile(palettefilename):
    ValidParameters = False
    print("Plaintext palette file not found")

  if ValidParameters == True:
    bmpfilesize = os.path.getsize(bmpfilename)
    bmpbuffer = (ctypes.c_byte * bmpfilesize)()
    bmpfile = open(bmpfilename, 'rb')
    bmpbuffer = bmpfile.read(bmpfilesize)

    ColoursCounted = PlaintextPaletteToBinaryArray.CountRGBvalues(palettefilename)
    if (ColoursCounted == 256 or ColoursCounted == 16):
      PaletteArray = (ctypes.c_byte * (ColoursCounted * 3))()
      PlaintextPaletteToBinaryArray.ConvertPlaintextPaletteFileToBinaryArray(palettefilename, ColoursCounted, PaletteArray)
      BitDepth = 8
      if (ColoursCounted == 16):
        BitDepth = 4
      ErrorCode = BMPoperations.CheckValidFormat(bmpbuffer)
      if ErrorCode == BMPoperations.ERROR_NONE:
        PaletteSize = (1 << BMPoperations.ReadBitDepth(bmpbuffer))
        if PaletteSize == ColoursCounted:
          PatchedFileBuffer = (ctypes.c_byte * bmpfilesize)()
          for ByteToTransfer in range (bmpfilesize):
            PatchedFileBuffer[ByteToTransfer] = bmpbuffer[ByteToTransfer]
          PatchedFileBuffer = BMPoperations.WritePalette(PaletteArray, PatchedFileBuffer)
          bmpfile.close()
          bmpfile = open(bmpfilename, 'wb')
          bmpfile.write(PatchedFileBuffer)
          bmpfile.close()
          print("Palette patch complete")
        else:
          print("BMP file does not have a palette or palette size of BMP file and palette file mismatch")
      else:
        print("BMP file error code", ErrorCode, "- refer to BMPoperations.py for definition")
    else:
      print("Plaintext palette file does not have 16 or 256 colours or format is invalid")
    bmpfile.close()