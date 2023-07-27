import argparse, struct, sys, os, ctypes, AVIoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--avifile", help="AVI file to generate")
  parser.add_argument("--width", type=int, default=0, help="Width in pixels")
  parser.add_argument("--height", type=int, default=0, help="Height in pixels")
  parser.add_argument("--framecount", type=int, default=0, help="Frame count")
  parser.add_argument("--framerate", type=float, default=0, help="Frame rate")
  parser.add_argument("--bitdepth", type=int, default=24, help="Colour bit depth (default: 24)")

  args = parser.parse_args()
  avifilename = args.avifile
  Width = args.width
  Height = args.height
  FrameCount = args.framecount
  FrameRate = args.framerate
  BitsPerPixel = args.bitdepth

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
  if BitsPerPixel != 24 and BitsPerPixel != 8:
    ValidParameters = False
    print("ERROR: Bit depth is invalid")

  if ValidParameters == True:
    FileSize = AVIoperations.CalculateFileSize(Width, Height, BitsPerPixel, FrameCount)
    avibuffer = (ctypes.c_byte * FileSize)()
    avibuffer = AVIoperations.WriteAVI(Width, Height, BitsPerPixel, FrameRate, FrameCount, avibuffer)
    Width = AVIoperations.ReadWidth(avibuffer)
    Height =  AVIoperations.ReadHeight(avibuffer)
    FrameCount = AVIoperations.ReadFrameCount(avibuffer)
    FrameRate = AVIoperations.ReadFrameRate(avibuffer)
    BitDepth = AVIoperations.ReadBitDepth(avibuffer)
    print("Width readback:", Width)
    print("Height readback:", Height)
    print("Frame count readback:", FrameCount)
    print("Frame rate per second readback:", FrameRate)
    print("Bit depth:", BitDepth)
    print("Expected line length with padding:", AVIoperations.CalculateLineLength(Width, BitsPerPixel))
    print("Expected frame size without header:", AVIoperations.CalculateFrameSize(Width, Height, BitsPerPixel))
    print("Expected file size:", FileSize)
    print("Expected end of file padding byte count:", AVIoperations.CalculateEOFpaddingBytes(Width, Height, BitsPerPixel, FrameCount))
    print("Expected index data size:", AVIoperations.CalculateIndexDataSize(FrameCount, BitsPerPixel))
    ErrorCode = AVIoperations.CheckValidFormat(avibuffer)
    avifile = open(avifilename, 'wb')
    avifile.write(avibuffer)
    avifile.close()
    if ErrorCode == AVIoperations.ERROR_NONE:
      print("No errors found")
    else:
      print("Error code", ErrorCode, "- refer to AVIoperations.py for definition")