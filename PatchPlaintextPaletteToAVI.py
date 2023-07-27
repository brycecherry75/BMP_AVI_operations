import argparse, struct, sys, os, ctypes, AVIoperations, PlaintextPaletteToBinaryArray

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--avifile", help="AVI file to patch")
  parser.add_argument("--palettefile", help="BMP palette file")
  args = parser.parse_args()
  avifilename = args.avifile
  palettefilename = args.palettefile

  ValidParameters = True

  if not args.avifile:
    ValidParameters = False
    print("AVI file not specified")
  elif not os.path.isfile(avifilename):
    ValidParameters = False
    print("AVI file not found")
  if not args.palettefile:
    ValidParameters = False
    print("Palette file not specified")
  elif not os.path.isfile(palettefilename):
    ValidParameters = False
    print("Plaintext palette file not found")

  if ValidParameters == True:
    avifilesize = os.path.getsize(avifilename)
    avibuffer = (ctypes.c_byte * avifilesize)()
    avifile = open(avifilename, 'rb')
    avibuffer = avifile.read(avifilesize)

    ColoursCounted = PlaintextPaletteToBinaryArray.CountRGBvalues(palettefilename)
    if (ColoursCounted == 256 or ColoursCounted == 16):
      PaletteArray = (ctypes.c_byte * (ColoursCounted * 3))()
      PlaintextPaletteToBinaryArray.ConvertPlaintextPaletteFileToBinaryArray(palettefilename, ColoursCounted, PaletteArray)
      BitDepth = 8
      if (ColoursCounted == 16):
        BitDepth = 4
      ErrorCode = AVIoperations.CheckValidFormat(avibuffer)
      if ErrorCode == AVIoperations.ERROR_NONE:
        PaletteSize = (1 << AVIoperations.ReadBitDepth(avibuffer))
        if PaletteSize == ColoursCounted:
          PatchedFileBuffer = (ctypes.c_byte * avifilesize)()
          for ByteToTransfer in range (avifilesize):
            PatchedFileBuffer[ByteToTransfer] = avibuffer[ByteToTransfer]
          PatchedFileBuffer = AVIoperations.WritePalette(PaletteArray, PatchedFileBuffer)
          avifile.close()
          avifile = open(avifilename, 'wb')
          avifile.write(PatchedFileBuffer)
          avifile.close()
          print("Palette patch complete")
        else:
          print("AVI file does not have a paleette or palette size of AVI file and palette file mismatch")
      else:
        print("AVI file error code", ErrorCode, "- refer to AVIoperations.py for definition")
    else:
      print("Plaintext palette file does not have 16 or 256 colours or format is invalid")
    avifile.close()