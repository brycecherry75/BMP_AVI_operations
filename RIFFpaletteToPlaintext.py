import argparse, struct, sys, os, ctypes, csv, BMPoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--riffpalette", help="RIFF palatte to convert")
  parser.add_argument("--palettefile", help="File to store palette")
  parser.add_argument("--jasc", action='store_true', help="Include Jasc header in palette file")
  args = parser.parse_args()
  riffpalettefilename = args.riffpalette
  palettefilename = args.palettefile

  ValidParameters = True

  if not args.riffpalette:
    ValidParameters = False
    print("RIFF palette file not specified")
  elif not os.path.isfile(riffpalettefilename):
    ValidParameters = False
    print("RIFF palette file not found")
  if not args.palettefile:
    ValidParameters = False
    print("Palette file not specified")

  if ValidParameters == True:
    riffpalettefilesize = os.path.getsize(riffpalettefilename)
    riffpalettebuffer = (ctypes.c_byte * riffpalettefilesize)()
    riffpalettefile = open(riffpalettefilename, 'rb')
    riffpalettebuffer = riffpalettefile.read(riffpalettefilesize)

    ErrorCode = BMPoperations.CheckValidPaletteFormat(riffpalettebuffer)
    if ErrorCode == BMPoperations.ERROR_NONE:
      PaletteSize = BMPoperations.ReadPaletteSizeInRIFFfile(riffpalettebuffer)
      if PaletteSize == 256 or PaletteSize == 16:
        palettebuffer = (ctypes.c_byte * (PaletteSize * 3))()
        palettebuffer = BMPoperations.ReadRIFFpalette(palettebuffer, riffpalettebuffer)
        with open(palettefilename, 'w', newline='') as csvfile:
          PaletteWriter = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_NONE)
          if args.jasc and (PaletteSize == 16 or PaletteSize == 256):
            PaletteWriter.writerow(["JASC-PAL"])
            PaletteWriter.writerow(["0100"])
            PaletteWriter.writerow([PaletteSize])
          for PaletteEntry in range (PaletteSize):           
            RED = riffpalettebuffer[(0x18 + (PaletteEntry * 4))]
            GREEN = riffpalettebuffer[(0x18 + (PaletteEntry * 4) + 1)]
            BLUE = riffpalettebuffer[(0x18 + (PaletteEntry * 4) + 2)]
            if RED < 0:
              RED += 256
            if GREEN < 0:
              GREEN += 256
            if BLUE < 0:
              BLUE += 256
            PaletteWriter.writerow([RED] + [GREEN] + [BLUE])
        print("Palette extraction complete")
      else:
        print("Palette size of", PaletteSize, "colours is unsupported")
    else:
      print("RIFF palette error code", ErrorCode, "- refer to BMPoperations.py for definition")
    riffpalettefile.close()