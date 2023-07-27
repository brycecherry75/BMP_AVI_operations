import argparse, struct, sys, os, ctypes, BMPoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--bmpfile", help="bmp file to generate")
  parser.add_argument("--xres", type=int, default=0, help="X resolution in pixels")
  parser.add_argument("--yres", type=int, default=0, help="Y resolution in pixels")
  parser.add_argument("--xpixelsperm", type=int, default=2835, help="X pixels per metre (default: 2835)")
  parser.add_argument("--ypixelsperm", type=int, default=2835, help="Y pixels per metre (default: 2835)")
  parser.add_argument("--bitdepth", type=int, default=24, help="Colour bit depth (default: 24)")

  args = parser.parse_args()
  bmpfilename = args.bmpfile
  X_resolution = args.xres
  Y_resolution = args.yres
  BitDepth = args.bitdepth
  XpixelsPerMetre = args.xpixelsperm
  YpixelsPerMetre = args.ypixelsperm

  ValidParameters = True

  if not args.bmpfile:
    ValidParameters = False
    print("ERROR: BMP output file not specified")
  if X_resolution < 1 or X_resolution > 65535:
    ValidParameters = False
    print("ERROR: X resolution is out of range")
  if Y_resolution < 1 or Y_resolution > 65535:
    ValidParameters = False
    print("ERROR: Y resolution is out of range")
  if BitDepth != 24 and BitDepth != 16 and BitDepth != 8 and BitDepth != 4 and BitDepth != 1:
    ValidParameters = False
    print("ERROR: Bit depth is invalid")
  if XpixelsPerMetre < 1 or XpixelsPerMetre > 4294967295:
    ValidParameters = False
    print("ERROR: X pixels per metre is out of range")
  if YpixelsPerMetre < 1 or YpixelsPerMetre > 4294967295:
    ValidParameters = False
    print("ERROR: Y pixels per metre is out of range")

  if ValidParameters == True:
    FileSize = BMPoperations.CalculateFileSize(X_resolution, Y_resolution, BitDepth)
    if FileSize > 0:
      bmpbuffer = (ctypes.c_byte * FileSize)()
      bmpbuffer = BMPoperations.WriteHeader(X_resolution, Y_resolution, BitDepth, XpixelsPerMetre, YpixelsPerMetre, bmpbuffer)
      PaletteSize = BMPoperations.CalculatePaletteSize(BitDepth)
      print("Expected file size:", FileSize)
      print("Expected palette size:", PaletteSize)
      X_resolution = BMPoperations.ReadXresolution(bmpbuffer)
      Y_resolution =  BMPoperations.ReadYresolution(bmpbuffer)
      XpixelsPerMetre = BMPoperations.ReadXpixelsPerMetre(bmpbuffer)
      YpixelsPerMetre = BMPoperations.ReadYpixelsPerMetre(bmpbuffer)
      BitDepth = BMPoperations.ReadBitDepth(bmpbuffer)
      PaletteSize = BMPoperations.CalculatePaletteSize(BitDepth)
      print("X resolution readback:", X_resolution)
      print("Y resolution readback:", Y_resolution)
      print("X pixels per metre readback:", XpixelsPerMetre)
      print("Y pixels per metre readback:", YpixelsPerMetre)
      print("Bits per pixel readback:", BitDepth)
      ErrorCode = BMPoperations.CheckValidFormat(bmpbuffer)
      bmpfile = open(bmpfilename, 'wb')
      bmpfile.write(bmpbuffer)
      bmpfile.close()
      if ErrorCode == BMPoperations.ERROR_NONE:
        print("No errors found")
      else:
        print("Error code", ErrorCode, "- refer to BMPoperations.py for definition")

    else:
      print("ERROR: Attempt to generate file larger than 4294967295 bytes")