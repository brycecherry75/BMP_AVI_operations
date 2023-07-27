import argparse, struct, sys, os, ctypes, BMPoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--bmpfile", help="BMP file to check")
  args = parser.parse_args()
  bmpfilename = args.bmpfile
  if args.bmpfile:
    if os.path.isfile(bmpfilename):
      bmpfilesize = os.path.getsize(bmpfilename)
      bmpbuffer = (ctypes.c_byte * bmpfilesize)()
      bmpfile = open(bmpfilename, 'rb')
      bmpbuffer = bmpfile.read(bmpfilesize)
      X_resolution = BMPoperations.ReadXresolution(bmpbuffer)
      Y_resolution = BMPoperations.ReadYresolution(bmpbuffer)
      BitsPerPixel = BMPoperations.ReadBitsPerPixel(bmpbuffer)
      XpixelsPerMetre = BMPoperations.ReadXpixelsPerMetre(bmpbuffer)
      YpixelsPerMetre = BMPoperations.ReadYpixelsPerMetre(bmpbuffer)
      PaletteSize = BMPoperations.CalculatePaletteSize(BitsPerPixel)
      print("X resolution:", X_resolution)
      print("Y resolution:", Y_resolution)
      print("X pixels per metre:", XpixelsPerMetre)
      print("Y pixels per metre:", YpixelsPerMetre)
      print("Bits per pixel:", BitsPerPixel)
      print("Expected palette size:", PaletteSize)
      print("Expected file size:", BMPoperations.CalculateFileSize(X_resolution, Y_resolution, BitsPerPixel))
      ErrorCode = BMPoperations.CheckValidFormat(bmpbuffer)
      bmpfile.close()
      if ErrorCode == BMPoperations.ERROR_NONE:
        print("No errors found")
      else:
        print("Error code", ErrorCode, "- refer to BMPoperations.py for definition")
    else:
      print("ERROR:", bmpfile, "not found")
  else:
    print("ERROR: BMP file not specified")