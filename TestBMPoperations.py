import argparse, struct, sys, os, ctypes, BMPoperations

if __name__ == "__main__":

  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--bmpfile", help="BMP file to generate")
  parser.add_argument("--xres", type=int, default=0, help="X resolution in pixels")
  parser.add_argument("--yres", type=int, default=0, help="Y resolution in pixels")
  parser.add_argument("--xpixelsperm", type=int, default=2835, help="X pixels per metre (default: 2835)")
  parser.add_argument("--ypixelsperm", type=int, default=2835, help="Y pixels per metre (default: 2835)")
  parser.add_argument("--bitdepth", type=int, default=24, help="Colour bit depth (default: 24)")
  parser.add_argument("--gfxtest", action='store_true', help="Test GFX operations")

  args = parser.parse_args()
  bmpfilename = args.bmpfile
  X_resolution = args.xres
  Y_resolution = args.yres
  BitDepth = args.bitdepth
  XpixelsPerMetre = args.xpixelsperm
  YpixelsPerMetre = args.ypixelsperm
  GFXtest = False

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
  if args.gfxtest:
    GFXtest = True

  if ValidParameters == True:

    FileSize = BMPoperations.CalculateFileSize(X_resolution, Y_resolution, BitDepth)
    if FileSize > 0:
      bmpbuffer = (ctypes.c_byte * FileSize)()
      for ByteToClear in range (len(bmpbuffer)):
        bmpbuffer[ByteToClear] = 0x00
      bmpbuffer = BMPoperations.WriteHeader(X_resolution, Y_resolution, BitDepth, XpixelsPerMetre, YpixelsPerMetre, bmpbuffer)

      if BitDepth != 24 and BitDepth != 16:
        ColoursInPalette = (1 << BitDepth)
        PaletteBuffer = (ctypes.c_byte * (ColoursInPalette * 3))()
        for PaletteEntry in range (ColoursInPalette):
          PaletteBuffer[(PaletteEntry * 3)] = ((0x20 + PaletteEntry) & 0xFF)
          PaletteBuffer[((PaletteEntry * 3) + 1)] = ((0x90 + PaletteEntry) & 0xFF)
          PaletteBuffer[((PaletteEntry * 3) + 2)] = ((0xE0 + PaletteEntry) & 0xFF)
        BMPoperations.WritePalette(PaletteBuffer, bmpbuffer)

      if BitDepth == 24:
        BMPoperations.WritePixel(200, 19, 0xA1B2C3, bmpbuffer)
        print("Read of 200, 19 is", hex(BMPoperations.ReadPixel(200, 19, bmpbuffer)))
        print("Read of 190, 12 is", hex(BMPoperations.ReadPixel(190, 12, bmpbuffer)))
        BMPoperations.SetSinglePixelBit(190, 12, 5, bmpbuffer)
        BMPoperations.SetSinglePixelBit(190, 12, 12, bmpbuffer)
        BMPoperations.SetSinglePixelBit(190, 12, 22, bmpbuffer)
        print("Read of 190, 12 is", hex(BMPoperations.ReadPixel(190, 12, bmpbuffer)))
        BMPoperations.ClearSinglePixelBit(190, 12, 12, bmpbuffer)
        print("Read of 190, 12 is", hex(BMPoperations.ReadPixel(190, 12, bmpbuffer)))
        BMPoperations.ToggleSinglePixelBit(190, 12, 5, bmpbuffer)
        print("Read of 190, 12 is", hex(BMPoperations.ReadPixel(190, 12, bmpbuffer)))

      elif BitDepth == 16:
        BMPoperations.WritePixel(200, 19, 0x7C00, bmpbuffer)
        print("Read of 200, 19 is", hex(BMPoperations.ReadPixel(200, 19, bmpbuffer)))
        print("Read of 200, 20 is", hex(BMPoperations.ReadPixel(200, 20, bmpbuffer)))
        BMPoperations.SetSinglePixelBit(190, 12, 10, bmpbuffer)
        print("Read of 190, 12 is", hex(BMPoperations.ReadPixel(190, 12, bmpbuffer)))
        BMPoperations.ClearSinglePixelBit(190, 12, 10, bmpbuffer)
        print("Read of 190, 12 is", hex(BMPoperations.ReadPixel(190, 12, bmpbuffer)))
        BMPoperations.ToggleSinglePixelBit(190, 40, 6, bmpbuffer)
        print("Read of 190, 40 is", hex(BMPoperations.ReadPixel(190, 40, bmpbuffer)))
        BMPoperations.ToggleSinglePixelBit(190, 40, 6, bmpbuffer)
        print("Read of 190, 40 is", hex(BMPoperations.ReadPixel(190, 40, bmpbuffer)))

      elif BitDepth == 8:
        BMPoperations.WritePixel(200, 19, 0x90, bmpbuffer)
        print("Read of 200, 19 is", hex(BMPoperations.ReadPixel(200, 19, bmpbuffer)))
        print("Read of 200, 20 is", hex(BMPoperations.ReadPixel(200, 20, bmpbuffer)))
        BMPoperations.SetSinglePixelBit(190, 12, 6, bmpbuffer)
        print("Read of 190, 12 is", hex(BMPoperations.ReadPixel(190, 12, bmpbuffer)))
        BMPoperations.ClearSinglePixelBit(190, 12, 6, bmpbuffer)
        print("Read of 190, 12 is", hex(BMPoperations.ReadPixel(190, 12, bmpbuffer)))
        BMPoperations.ToggleSinglePixelBit(190, 40, 4, bmpbuffer)
        print("Read of 190, 40 is", hex(BMPoperations.ReadPixel(190, 40, bmpbuffer)))
        BMPoperations.ToggleSinglePixelBit(190, 40, 4, bmpbuffer)
        print("Read of 190, 40 is", hex(BMPoperations.ReadPixel(190, 40, bmpbuffer)))

      elif BitDepth == 4:
        BMPoperations.WritePixel(200, 19, 0x9, bmpbuffer)
        print("Read of 200, 19 is", hex(BMPoperations.ReadPixel(200, 19, bmpbuffer)))
        print("Read of 200, 20 is", hex(BMPoperations.ReadPixel(200, 20, bmpbuffer)))
        BMPoperations.SetSinglePixelBit(190, 12, 3, bmpbuffer)
        print("Read of 190, 12 is", hex(BMPoperations.ReadPixel(190, 12, bmpbuffer)))
        BMPoperations.ClearSinglePixelBit(190, 12, 3, bmpbuffer)
        print("Read of 190, 12 is", hex(BMPoperations.ReadPixel(190, 12, bmpbuffer)))
        BMPoperations.ToggleSinglePixelBit(190, 40, 1, bmpbuffer)
        print("Read of 190, 40 is", hex(BMPoperations.ReadPixel(190, 40, bmpbuffer)))
        BMPoperations.ToggleSinglePixelBit(190, 40, 1, bmpbuffer)
        print("Read of 190, 40 is", hex(BMPoperations.ReadPixel(190, 40, bmpbuffer)))

      elif BitDepth == 1:
        BMPoperations.WritePixel(200, 19, 0x1, bmpbuffer)
        print("Read of 200, 19 is", hex(BMPoperations.ReadPixel(200, 19, bmpbuffer)))
        print("Read of 200, 20 is", hex(BMPoperations.ReadPixel(200, 20, bmpbuffer)))
        BMPoperations.SetSinglePixelBit(190, 12, 0, bmpbuffer)
        print("Read of 190, 12 is", hex(BMPoperations.ReadPixel(190, 12, bmpbuffer)))
        BMPoperations.ClearSinglePixelBit(190, 12, 0, bmpbuffer)
        print("Read of 190, 12 is", hex(BMPoperations.ReadPixel(190, 12, bmpbuffer)))
        BMPoperations.ToggleSinglePixelBit(190, 40, 0, bmpbuffer)
        print("Read of 190, 40 is", hex(BMPoperations.ReadPixel(190, 40, bmpbuffer)))
        BMPoperations.ToggleSinglePixelBit(190, 40, 0, bmpbuffer)
        print("Read of 190, 40 is", hex(BMPoperations.ReadPixel(190, 40, bmpbuffer)))

      if GFXtest == True:
        BMPoperations.FillScreen(0xFF8080, bmpbuffer)

        # no need to use separate DrawFast(H/V)Line/WriteLine functions
        BMPoperations.DrawLine(100, 50, 300, 25, 0xFF0000, bmpbuffer)
        BMPoperations.DrawLine(100, 50, 150, 50, 0x00FF00, bmpbuffer)
        BMPoperations.DrawLine(100, 50, 100, 150, 0x0000FF, bmpbuffer)

        BMPoperations.FillRect(400, 300, 50, 100, 0xFFFF00, bmpbuffer)
        BMPoperations.DrawCircle(200, 200, 50, 0xFF8000, bmpbuffer)
        BMPoperations.FillCircle(500, 200, 80, 0xFF80FF, bmpbuffer)
        BMPoperations.DrawRect(50, 50, 25, 40, 0xFFFF00, bmpbuffer)
        BMPoperations.DrawRoundRect(350, 50, 100, 100, 20, 0xFFFFFF, bmpbuffer)
        BMPoperations.FillRoundRect(600, 100, 50, 50, 10, 0x80FFFF, bmpbuffer)
        BMPoperations.DrawTriangle(550, 400, 500, 400, 550, 450, 0xFF0000, bmpbuffer)
        BMPoperations.FillTriangle(750, 600, 750, 650, 650, 600, 0x808080, bmpbuffer)

      bmpfile = open(bmpfilename, 'wb')
      bmpfile.write(bmpbuffer)
      bmpfile.close()
      print("BMP file write complete")

    else:
      print("ERROR: File size is over 4294967295 bytes")