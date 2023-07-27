import argparse, struct, sys, os, ctypes, AVIoperations

if __name__ == "__main__":

  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--avifile", help="AVI file to generate")
  parser.add_argument("--width", type=int, default=0, help="Width in pixels")
  parser.add_argument("--height", type=int, default=0, help="Height in pixels")
  parser.add_argument("--framecount", type=int, default=0, help="Frame count")
  parser.add_argument("--framerate", type=float, default=0, help="Frame rate")
  parser.add_argument("--bitdepth", type=int, default=24, help="Colour bit depth (default: 24)")
  parser.add_argument("--gfxtest", action='store_true', help="Test GFX operations")

  args = parser.parse_args()
  avifilename = args.avifile
  Width = args.width
  Height = args.height
  FrameCount = args.framecount
  FrameRate = args.framerate
  BitDepth = args.bitdepth
  GFXtest = False

  ValidParameters = True

  if not args.avifile:
    ValidParameters = False
    print("ERROR: AVI output file not specified")
  if Height < 1 or Height > 65535:
    ValidParameters = False
    print("ERROR: Height is out of range")
  if Width < 1 or Width > 65535:
    ValidParameters = False
    print("ERROR: Width is out of range")
  if FrameCount < 1:
    ValidParameters = False
    print("ERROR: Frame count is out of range")
  if FrameRate <= 0:
    ValidParameters = False
    print("ERROR: Frame rate is out of range")
  if BitDepth != 24 and BitDepth != 8:
    ValidParameters = False
    print("ERROR: Bit depth is invalid")
  if args.gfxtest:
    GFXtest = True

  if ValidParameters == True:
    FileSize = AVIoperations.CalculateFileSize(Width, Height, BitDepth, FrameCount)
    if FileSize > 0:
      avibuffer = (ctypes.c_byte * FileSize)()
      for ByteToClear in range (len(avibuffer)):
        avibuffer[ByteToClear] = 0x00
      avibuffer = AVIoperations.WriteAVI(Width, Height, BitDepth, FrameRate, FrameCount, avibuffer)

      if BitDepth != 24 and BitDepth != 16:
        ColoursInPalette = (1 << BitDepth)
        PaletteBuffer = (ctypes.c_byte * (ColoursInPalette * 3))()
        for PaletteEntry in range (ColoursInPalette):
          PaletteBuffer[(PaletteEntry * 3)] = ((0x20 + PaletteEntry) & 0xFF)
          PaletteBuffer[((PaletteEntry * 3) + 1)] = ((0x90 + PaletteEntry) & 0xFF)
          PaletteBuffer[((PaletteEntry * 3) + 2)] = ((0xE0 + PaletteEntry) & 0xFF)
        AVIoperations.WritePalette(PaletteBuffer, avibuffer)

      if BitDepth == 24:
        AVIoperations.WritePixel(200, 19, 1, 0xA1B2C3, avibuffer)
        print("Read of 200, 19 in frame 1 is", hex(AVIoperations.ReadPixel(200, 19, 1,avibuffer)))
        print("Read of 190, 12 in frame 1 is", hex(AVIoperations.ReadPixel(190, 12, 1,avibuffer)))
        AVIoperations.SetSinglePixelBit(190, 12, 1, 5, avibuffer)
        AVIoperations.SetSinglePixelBit(190, 12, 1, 12, avibuffer)
        AVIoperations.SetSinglePixelBit(190, 12, 1, 22, avibuffer)
        print("Read of 190, 12 in frame 1 is", hex(AVIoperations.ReadPixel(190, 12, 1,avibuffer)))
        AVIoperations.ClearSinglePixelBit(190, 12, 1, 12, avibuffer)
        print("Read of 190, 12 in frame 1 is", hex(AVIoperations.ReadPixel(190, 12, 1,avibuffer)))
        AVIoperations.ToggleSinglePixelBit(190, 12, 1, 5, avibuffer)
        print("Read of 190, 12 in frame 1 is", hex(AVIoperations.ReadPixel(190, 12, 1,avibuffer)))

        if GFXtest == True:
          AVIoperations.FillScreen(0, 0xFF8080, avibuffer) # Frame 0
          AVIoperations.FillScreen(1, 0x003FFF, avibuffer) # Frame 1
          AVIoperations.FillScreen(2, 0x7F00FF, avibuffer) # Frame 2

          # no need to use separate DrawFast(H/V)Line/WriteLine functions
          AVIoperations.DrawLine(100, 50, 300, 25, 0, 0xFF0000, avibuffer) # Frame 0
          AVIoperations.DrawLine(100, 50, 150, 50, 1, 0x00FF00, avibuffer) # Frame 1
          AVIoperations.DrawLine(100, 50, 100, 150, 2, 0x0000FF, avibuffer) # Frame 2

          # Frame 0
          AVIoperations.FillRect(400, 300, 50, 100, 0, 0xFFFF00, avibuffer)
          AVIoperations.DrawCircle(200, 200, 50, 0, 0xFF8000, avibuffer)
          AVIoperations.FillCircle(500, 200, 80, 0, 0xFF80FF, avibuffer)

          # Frame 1
          AVIoperations.DrawRect(50, 50, 25, 40, 1, 0xFFFF00, avibuffer)
          AVIoperations.DrawRoundRect(350, 50, 100, 100, 20, 1, 0xFFFFFF, avibuffer)
          AVIoperations.FillRoundRect(600, 100, 50, 50, 10, 1, 0x80FFFF, avibuffer)

          # Frame 2
          AVIoperations.DrawTriangle(550, 400, 500, 400, 550, 450, 2, 0xFF0000, avibuffer)
          AVIoperations.FillTriangle(750, 600, 750, 650, 650, 600, 2, 0x808080, avibuffer)

      elif BitDepth == 8:
        AVIoperations.WritePixel(200, 19, 1, 0x90, avibuffer)
        print("Read of 200, 19 in frame 1 is", hex(AVIoperations.ReadPixel(200, 19, 1, avibuffer)))
        print("Read of 200, 20 in frame 1 is", hex(AVIoperations.ReadPixel(200, 20, 1, avibuffer)))
        AVIoperations.SetSinglePixelBit(190, 12, 1, 6, avibuffer)
        print("Read of 190, 12 in frame 1 is", hex(AVIoperations.ReadPixel(190, 12, 1, avibuffer)))
        AVIoperations.ClearSinglePixelBit(190, 12, 1, 6, avibuffer)
        print("Read of 190, 12 in frame 1 is", hex(AVIoperations.ReadPixel(190, 12, 1, avibuffer)))
        AVIoperations.ToggleSinglePixelBit(190, 40, 1, 4, avibuffer)
        print("Read of 190, 40 in frame 1 is", hex(AVIoperations.ReadPixel(190, 40, 1, avibuffer)))
        AVIoperations.ToggleSinglePixelBit(190, 40, 1, 4, avibuffer)
        print("Read of 190, 40 in frame 1 is", hex(AVIoperations.ReadPixel(190, 40, 1, avibuffer)))

        if GFXtest == True:
          AVIoperations.FillScreen(0, 30, avibuffer) # Frame 0
          AVIoperations.FillScreen(1, 90, avibuffer) # Frame 1
          AVIoperations.FillScreen(2, 180, avibuffer) # Frame 2

          # no need to use separate DrawFast(H/V)Line/WriteLine functions
          AVIoperations.DrawLine(100, 50, 300, 25, 0, 64, avibuffer) # Frame 0
          AVIoperations.DrawLine(100, 50, 150, 50, 1, 128, avibuffer) # Frame 1
          AVIoperations.DrawLine(100, 50, 100, 150, 2, 192, avibuffer) # Frame 2

          # Frame 0
          AVIoperations.FillRect(400, 300, 50, 100, 0, 15, avibuffer)
          AVIoperations.DrawCircle(200, 200, 50, 0, 45, avibuffer)
          AVIoperations.FillCircle(500, 200, 80, 0, 75, avibuffer)

          # Frame 1
          AVIoperations.DrawRect(50, 50, 25, 40, 1, 105, avibuffer)
          AVIoperations.DrawRoundRect(350, 50, 100, 100, 20, 1, 135, avibuffer)
          AVIoperations.FillRoundRect(600, 100, 50, 50, 10, 1, 165, avibuffer)

          # Frame 2
          AVIoperations.DrawTriangle(550, 400, 500, 400, 550, 450, 2, 195, avibuffer)
          AVIoperations.FillTriangle(750, 600, 750, 650, 650, 600, 2, 225, avibuffer)

      avifile = open(avifilename, 'wb')
      avifile.write(avibuffer)
      avifile.close()
      print("AVI file write complete")

    else:
      print("ERROR: Attempt to generate file larger than 4294967295 bytes")