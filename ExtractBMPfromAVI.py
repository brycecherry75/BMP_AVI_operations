import argparse, struct, sys, os, ctypes, BMPoperations, AVIoperations

if __name__ == "__main__":

  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--bmpfile", help="BMP file to save")
  parser.add_argument("--avifile", help="AVI file")
  parser.add_argument("--frame", type=int, default=0, help="Frame to convert to BMP file (default: 0)")

  args = parser.parse_args()
  bmpfilename = args.bmpfile
  avifilename = args.avifile

  ValidParameters = True

  if not args.bmpfile:
    ValidParameters = False
    print("ERROR: BMP input file not specified") 
  if not args.avifile:
    ValidParameters = False
    print("ERROR: AVI output file not specified")
  elif not os.path.isfile(avifilename):
    ValidParameters = False
    print("ERROR: AVI file not found")

  if ValidParameters == True:
    frame = args.frame
    avifilesize = os.path.getsize(avifilename)
    avibuffer = (ctypes.c_byte * avifilesize)()
    avifile = open(avifilename, 'rb')
    avibuffer = avifile.read(avifilesize)
    ErrorCode = AVIoperations.CheckValidFormat(avibuffer)
    if ErrorCode != AVIoperations.ERROR_NONE:
      ValidParemters = False
      print("Error in AVI file - code", ErrorCode, "- refer to AVIoperations.py for definition")
    FrameCount = AVIoperations.ReadFrameCount(avibuffer)
    if frame < 0 or frame >= FrameCount:
      ValidParameters = False
      print("Frame is not within 0 to", (FrameCount - 1))
    if ValidParameters == True:
      BitDepth = AVIoperations.ReadBitDepth(avibuffer)
      Width = AVIoperations.ReadWidth(avibuffer)
      Height = AVIoperations.ReadHeight(avibuffer)
      bmpbuffer = (ctypes.c_byte * BMPoperations.CalculateFileSize(Width, Height, BitDepth))()
      bmpbuffer = BMPoperations.WriteHeader(Width, Height, BitDepth, 2835, 2835, bmpbuffer)
      bmpbuffer = AVIoperations.ExtractBMP(frame, bmpbuffer, avibuffer)
      if BitDepth == 8:
        PaletteSize = (1 << BMPoperations.ReadBitDepth(bmpbuffer))
        bmppalette = (ctypes.c_byte * (PaletteSize * 3))()
        bmppalette = AVIoperations.ReadPalette(bmppalette, avibuffer)
        bmpbuffer = BMPoperations.WritePalette(bmppalette, bmpbuffer)
      bmpfile = open(bmpfilename, 'wb')
      bmpfile.write(bmpbuffer)
      bmpfile.close()
      print("Frame extraction complete")