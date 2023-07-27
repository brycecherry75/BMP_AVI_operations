import argparse, struct, sys, os, ctypes, BMPoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--bmpfile", help="BMP file to check")
  parser.add_argument("--palettefile", help="File to store palette")
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

  if ValidParameters == True:
    bmpfilesize = os.path.getsize(bmpfilename)
    bmpbuffer = (ctypes.c_byte * bmpfilesize)()
    bmpfile = open(bmpfilename, 'rb')
    bmpbuffer = bmpfile.read(bmpfilesize)
    PaletteSize = (1 << BMPoperations.ReadBitDepth(bmpbuffer))
    ErrorCode = BMPoperations.CheckValidFormat(bmpbuffer)
    if ErrorCode == BMPoperations.ERROR_NONE:
      if PaletteSize == 256 or PaletteSize == 16:
        palettebuffer = (ctypes.c_byte * (PaletteSize * 3))()
        palettebuffer = BMPoperations.ReadPalette(palettebuffer, bmpbuffer)
        RIFFbuffer = (ctypes.c_byte * BMPoperations.CalculateRIFFpaletteSize(BMPoperations.ReadBitDepth(bmpbuffer)))()
        RIFFbuffer = BMPoperations.WriteRIFFpalette(palettebuffer, RIFFbuffer)
        ErrorCode = BMPoperations.CheckValidPaletteFormat(RIFFbuffer)
        if ErrorCode == BMPoperations.ERROR_NONE:
          RIFFfile = open(palettefilename, 'wb')
          RIFFfile.write(RIFFbuffer)
          RIFFfile.close()
          print("Palette extraction complete")
        else:
          print("Error generating palette file - code", ErrorCode, "- refer to BMPoperations.py for definition")
      else:
        print("Palette size of", PaletteSize, "colours is unsupported")
    else:
      print("Error in BMP file - code", ErrorCode, "- refer to BMPoperations.py for definition")
    bmpfile.close()