import argparse, struct, sys, os, ctypes, AVIoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--avifile", help="AVI file to use")
  parser.add_argument("--palettefile", help="File to store palette")
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

  if ValidParameters == True:
    avifilesize = os.path.getsize(avifilename)
    avibuffer = (ctypes.c_byte * avifilesize)()
    avifile = open(avifilename, 'rb')
    avibuffer = avifile.read(avifilesize)
    PaletteSize = (1 << AVIoperations.ReadBitDepth(avibuffer))
    ErrorCode = AVIoperations.CheckValidFormat(avibuffer)
    if ErrorCode == AVIoperations.ERROR_NONE:
      if PaletteSize == 256 or PaletteSize == 16:
        palettebuffer = (ctypes.c_byte * (PaletteSize * 3))()
        palettebuffer = AVIoperations.ReadPalette(palettebuffer, avibuffer)
        RIFFbuffer = (ctypes.c_byte * AVIoperations.CalculateRIFFpaletteSize(AVIoperations.ReadBitDepth(avibuffer)))()
        RIFFbuffer = AVIoperations.WriteRIFFpalette(palettebuffer, RIFFbuffer)
        ErrorCode = AVIoperations.CheckValidPaletteFormat(RIFFbuffer)
        if ErrorCode == AVIoperations.ERROR_NONE:
          RIFFfile = open(palettefilename, 'wb')
          RIFFfile.write(RIFFbuffer)
          RIFFfile.close()
          print("Palette extraction complete")
        else:
          print("Error generating palette file - code", ErrorCode, "- refer to AVIoperations.py for definition")
      else:
        print("Palette size of", PaletteSize, "colours is unsupported")
    else:
      print("Error in AVI file - code", ErrorCode, "- refer to AVIoperations.py for definition")
    avifile.close()