import argparse, struct, sys, os, ctypes, BMPoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--bmpfile", help="BMP file to patch")
  parser.add_argument("--palettefile", help="BMP palette file")
  args = parser.parse_args()
  bmpfilename = args.bmpfile
  palettefilename = args.palettefile

  ValidParameters = True

  if not args.bmpfile:
    ValidParameters = False
    print("BMP file not specified")
  elif not os.path.isfile(bmpfilename):
    ValidParameters = False
    print("BMP image file not found")
  if not args.palettefile:
    ValidParameters = False
    print("Palette file not specified")
  elif not os.path.isfile(palettefilename):
    ValidParameters = False
    print("BMP palette file not found")

  if ValidParameters == True:
    bmpfilesize = os.path.getsize(bmpfilename)
    bmpbuffer = (ctypes.c_byte * bmpfilesize)()
    bmpfile = open(bmpfilename, 'rb')
    bmpbuffer = bmpfile.read(bmpfilesize)

    palettefilesizeRIFF = os.path.getsize(palettefilename)
    palettebufferRIFF = (ctypes.c_byte * palettefilesizeRIFF)()
    palettefileRIFF = open(palettefilename, 'rb')
    palettebufferRIFF = palettefileRIFF.read(palettefilesizeRIFF)

    ErrorCode = BMPoperations.CheckValidPaletteFormat(palettebufferRIFF)
    if ErrorCode == BMPoperations.ERROR_NONE:
      ErrorCode = BMPoperations.CheckValidFormat(bmpbuffer)
      if ErrorCode == BMPoperations.ERROR_NONE:
        BMPpaletteSize = BMPoperations.ReadPaletteSizeInRIFFfile(palettebufferRIFF)
        PaletteSize = (1 << BMPoperations.ReadBitDepth(bmpbuffer))
        if PaletteSize == BMPpaletteSize:
          PatchedFileBuffer = (ctypes.c_byte * bmpfilesize)()
          for ByteToTransfer in range (bmpfilesize):
            PatchedFileBuffer[ByteToTransfer] = bmpbuffer[ByteToTransfer]
          palettebuffer = (ctypes.c_byte * (PaletteSize * 3))()
          palettebuffer = BMPoperations.ReadRIFFpalette(palettebuffer, palettebufferRIFF)
          PatchedFileBuffer = BMPoperations.WritePalette(palettebuffer, PatchedFileBuffer)
          bmpfile.close()
          bmpfile = open(bmpfilename, 'wb')
          bmpfile.write(PatchedFileBuffer)
          bmpfile.close()
          print("Palette patch complete")
        else:
          print("Palette size of BMP file and palette file mismatch")
      else:
        print("BMP file error code", ErrorCode, "- refer to BMPoperations.py for definition")
    else:
      print("BMP palette error code", ErrorCode, "- refer to BMPoperations.py for definition")
    bmpfile.close()
    palettefileRIFF.close()