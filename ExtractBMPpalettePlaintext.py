import argparse, struct, sys, os, ctypes, csv, BMPoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--bmpfile", help="BMP file to use")
  parser.add_argument("--palettefile", help="File to store palette")
  parser.add_argument("--jasc", action='store_true', help="Include Jasc header in palette file")
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
      if PaletteSize == 256 or PaletteSize == 16 or PaletteSize == 2:
        palettebuffer = (ctypes.c_byte * (PaletteSize * 3))()
        palettebuffer = BMPoperations.ReadPalette(palettebuffer, bmpbuffer)
        with open(palettefilename, 'w', newline='') as csvfile:
          PaletteWriter = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_NONE)
          if args.jasc and (PaletteSize == 16 or PaletteSize == 256):
            PaletteWriter.writerow(["JASC-PAL"])
            PaletteWriter.writerow(["0100"])
            PaletteWriter.writerow([PaletteSize])
          for PaletteEntry in range (PaletteSize):
            RED = palettebuffer[(PaletteEntry * 3)]
            GREEN = palettebuffer[((PaletteEntry * 3) + 1)]
            BLUE = palettebuffer[((PaletteEntry * 3) + 2)]
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
      print("Error in BMP file - code", ErrorCode, "- refer to BMPoperations.py for definition")
    bmpfile.close()