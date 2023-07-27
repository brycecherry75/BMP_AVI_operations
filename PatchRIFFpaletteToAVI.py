import argparse, struct, sys, os, ctypes, AVIoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--avifile", help="AVI file to patch")
  parser.add_argument("--palettefile", help="BMP palette file")
  args = parser.parse_args()
  avifilename = args.avifile
  palettefilename = args.palettefile

  ValidParameters = True

  if not args.avifile:
    ValidParameters = False
    print("AVI file not specified")
  elif not os.path.isfile(avifilename):
    ValidParameters = False
    print("AVI file not found")
  if not args.palettefile:
    ValidParameters = False
    print("Palette file not specified")
  elif not os.path.isfile(palettefilename):
    ValidParameters = False
    print("BMP palette file not found")

  if ValidParameters == True:
    avifilesize = os.path.getsize(avifilename)
    avibuffer = (ctypes.c_byte * avifilesize)()
    avifile = open(avifilename, 'rb')
    avibuffer = avifile.read(avifilesize)

    palettefilesizeRIFF = os.path.getsize(palettefilename)
    palettebufferRIFF = (ctypes.c_byte * palettefilesizeRIFF)()
    palettefileRIFF = open(palettefilename, 'rb')
    palettebufferRIFF = palettefileRIFF.read(palettefilesizeRIFF)

    ErrorCode = AVIoperations.CheckValidPaletteFormat(palettebufferRIFF)
    if ErrorCode == AVIoperations.ERROR_NONE:
      ErrorCode = AVIoperations.CheckValidFormat(avibuffer)
      if ErrorCode == AVIoperations.ERROR_NONE:
        BMPpaletteSize = AVIoperations.ReadPaletteSizeInRIFFfile(palettebufferRIFF)
        PaletteSize = (1 << AVIoperations.ReadBitDepth(avibuffer))
        if PaletteSize == BMPpaletteSize:
          PatchedFileBuffer = (ctypes.c_byte * avifilesize)()
          for ByteToTransfer in range (avifilesize):
            PatchedFileBuffer[ByteToTransfer] = avibuffer[ByteToTransfer]
          palettebuffer = (ctypes.c_byte * (PaletteSize * 3))()
          palettebuffer = AVIoperations.ReadRIFFpalette(palettebuffer, palettebufferRIFF)
          PatchedFileBuffer = AVIoperations.WritePalette(palettebuffer, PatchedFileBuffer)
          avifile.close()
          avifile = open(avifilename, 'wb')
          avifile.write(PatchedFileBuffer)
          avifile.close()
          print("Palette patch complete")
        else:
          print("AVI file does not have a paleette or palette size of AVI file and palette file mismatch")
      else:
        print("AVI file error code", ErrorCode, "- refer to AVIoperations.py for definition")
    else:
      print("BMP palette error code", ErrorCode, "- refer to AVIoperations.py for definition")
    avifile.close()
    palettefileRIFF.close()