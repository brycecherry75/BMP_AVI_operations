import argparse, struct, sys, os, ctypes, AVIoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--avifile", help="AVI file to check")
  args = parser.parse_args()
  if args.avifile:
    avifilename = args.avifile
    if os.path.isfile(avifilename):
      avifilesize = os.path.getsize(avifilename)
      avibuffer = (ctypes.c_byte * avifilesize)()
      avifile = open(avifilename, 'rb')
      avibuffer = avifile.read(avifilesize)
      Width = AVIoperations.ReadWidth(avibuffer)
      Height =  AVIoperations.ReadHeight(avibuffer)
      FrameCount = AVIoperations.ReadFrameCount(avibuffer)
      FrameRate = AVIoperations.ReadFrameRate(avibuffer)
      BitDepth = AVIoperations.ReadBitDepth(avibuffer)
      print("Width:", Width)
      print("Height:", Height)
      print("Frame count:", FrameCount)
      print("Frame rate per second:", FrameRate)
      print("Bit depth:", BitDepth)
      print("Expected line length with padding:", AVIoperations.CalculateLineLength(Width, BitDepth))
      print("Expected frame size without header:", AVIoperations.CalculateFrameSize(Width, Height, BitDepth))
      print("Expected file size:", AVIoperations.CalculateFileSize(Width, Height, BitDepth, FrameCount))
      print("Expected end of file padding byte count:", AVIoperations.CalculateEOFpaddingBytes(Width, Height, BitDepth, FrameCount))
      print("Expected index data size:", AVIoperations.CalculateIndexDataSize(FrameCount, BitDepth))
      ErrorCode = AVIoperations.CheckValidFormat(avibuffer)
      avifile.close()
      if ErrorCode == AVIoperations.ERROR_NONE:
        print("No errors found")
      else:
        print("Error code", ErrorCode, "- refer to AVIoperations.py for definition")
    else:
      print("ERROR:", avifile, "not found")
  else:
    print("ERROR: AVI file not specified")