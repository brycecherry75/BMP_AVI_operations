import argparse, struct, sys, os, ctypes, BMPoperations, PlaintextPaletteToBinaryArray

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--palettefile", help="Plaintext palatte to convert")
  parser.add_argument("--rifffile", help="File to store palette")
  args = parser.parse_args()
  plaintextpalettefilename = args.palettefile
  palettefilename = args.rifffile

  ValidParameters = True

  if not args.palettefile:
    ValidParameters = False
    print("Plaintext palette file not specified")
  elif not os.path.isfile(plaintextpalettefilename):
    ValidParameters = False
    print("Plaintext palette file not found")
  if not args.palettefile:
    ValidParameters = False
    print("RIFF palette file not specified")

  if ValidParameters == True:
    ColoursCounted = PlaintextPaletteToBinaryArray.CountRGBvalues(plaintextpalettefilename)
    if (ColoursCounted == 256 or ColoursCounted == 16):
      PaletteArray = (ctypes.c_byte * (ColoursCounted * 3))()
      PlaintextPaletteToBinaryArray.ConvertPlaintextPaletteFileToBinaryArray(plaintextpalettefilename, ColoursCounted, PaletteArray)
      BitDepth = 8
      if (ColoursCounted == 16):
        BitDepth = 4
      RIFFbuffer = (ctypes.c_byte * BMPoperations.CalculateRIFFpaletteSize(BitDepth))()
      BMPoperations.WriteRIFFpalette(PaletteArray, RIFFbuffer)
      RIFFfile = open(palettefilename, 'wb')
      RIFFfile.write(RIFFbuffer)
      RIFFfile.close()
      print("Palette conversion complete")
    else:
      print("Plaintext palette file does not have 16 or 256 colours or format is invalid")