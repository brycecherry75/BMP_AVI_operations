import argparse, struct, sys, os, ctypes, BMPoperations, AVIoperations

if __name__ == "__main__":

  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--bmpfile", help="BMP file to patch AVI with")
  parser.add_argument("--avifile", help="AVI file")
  parser.add_argument("--frame", type=int, default=0, help="Frame to patch with BMP file (default: 0)")

  args = parser.parse_args()
  bmpfilename = args.bmpfile
  avifilename = args.avifile

  ValidParameters = True

  if not args.bmpfile:
    ValidParameters = False
    print("ERROR: BMP input file not specified") 
  elif not os.path.isfile(bmpfilename):
    ValidParameters = False
    print("ERROR: BMP file not found")
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
    avibuffer = avifile.read()
    bmpfilesize = os.path.getsize(bmpfilename)
    bmpbuffer = (ctypes.c_byte * bmpfilesize)()
    bmpfile = open(bmpfilename, 'rb')
    bmpbuffer = bmpfile.read()
    ErrorCode = BMPoperations.CheckValidFormat(bmpbuffer)
    if ErrorCode != BMPoperations.ERROR_NONE:
      ValidParameters = False
      print("Error in BMP file - code", ErrorCode, "- refer to BMPoperations.py for definition")
    ErrorCode = AVIoperations.CheckValidFormat(avibuffer)
    if ErrorCode != AVIoperations.ERROR_NONE:
      ValidParemters = False
      print("Error in AVI file - code", ErrorCode, "- refer to AVIoperations.py for definition")
    if BMPoperations.ReadXresolution(bmpbuffer) != AVIoperations.ReadWidth(avibuffer):
      ValidParameters = False
      print("Width mismatch")
    if BMPoperations.ReadYresolution(bmpbuffer) != AVIoperations.ReadHeight(avibuffer):
      ValidParameters = False
      print("Height mismatch")
    BitDepth = AVIoperations.ReadBitDepth(avibuffer)
    if BMPoperations.ReadBitDepth(bmpbuffer) != BitDepth:
      ValidParameters = False
      print("Bit depth mismatch")
    FrameCount = AVIoperations.ReadFrameCount(avibuffer)
    if frame < 0 or frame >= FrameCount:
      ValidParameters = False
      print("Frame is not within 0 to", (FrameCount - 1))
    if ValidParameters == True:
      PatchedAVI = (ctypes.c_byte * avifilesize)()
      for ByteToTransfer in range (avifilesize):
        PatchedAVI[ByteToTransfer] = avibuffer[ByteToTransfer]
      avifile.close()
      PatchedAVI = AVIoperations.WriteBMP(frame, bmpbuffer, PatchedAVI)
      AVIfile = open(avifilename, 'wb')
      AVIfile.write(PatchedAVI)
      AVIfile.close()
      print("Frame write complete")
      if BitDepth != 24 and BitDepth != 16:
        print("WARNING: Palette in AVI file has not been changed")