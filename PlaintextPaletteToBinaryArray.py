import csv

def ConvertPlaintextPaletteFileToBinaryArray(PaletteFile, ColoursInPalette, PaletteArray):
  FirstRGBvalueFound = False
  ValidRGBvalues = True
  RGBvaluesCounted = 0
  fields = []
  rows = []
  with open(PaletteFile, 'r') as csvfile:
    RGBentryReader = csv.reader(csvfile)
    for row in RGBentryReader:
      rows.append(row)
    LineCount = RGBentryReader.line_num
    
    for row in rows[:LineCount]:
      for col in row:
        value = ("%10s"%col)
        value = value.split(sep=None, maxsplit=3)
        if FirstRGBvalueFound == False and len(value) == 3 and value[0].isnumeric() and value[1].isnumeric() and value[2].isnumeric():
          FirstRGBvalueFound = True
        if FirstRGBvalueFound == True:
          if RGBvaluesCounted == ColoursInPalette:
            break
          if len(value) == 3 and value[0].isnumeric() and value[1].isnumeric() and value[2].isnumeric():
            PaletteArray[(RGBvaluesCounted * 3)] = int(value[0])
            PaletteArray[((RGBvaluesCounted * 3) + 1)] = int(value[1])
            PaletteArray[((RGBvaluesCounted * 3) + 2)] = int(value[2])
            RGBvaluesCounted += 1
          else:
            ValidRGBvalues = False
            break
      if ValidRGBvalues == False:
        break
  return PaletteArray

def CountRGBvalues(PaletteFile):
  FirstRGBvalueFound = False
  ValidRGBvalues = True
  RGBvaluesCounted = 0
  fields = []
  rows = []
  with open(PaletteFile, 'r') as csvfile:
    RGBentryReader = csv.reader(csvfile)
    for row in RGBentryReader:
      rows.append(row)
    LineCount = RGBentryReader.line_num
    for row in rows[:LineCount]:
      for col in row:
        value = ("%10s"%col)
        value = value.split(sep=None, maxsplit=3)
        if FirstRGBvalueFound == False and len(value) == 3 and value[0].isnumeric() and value[1].isnumeric() and value[2].isnumeric():
          FirstRGBvalueFound = True
        if FirstRGBvalueFound == True:
          if RGBvaluesCounted == 256:
            break
          if len(value) == 3 and value[0].isnumeric() and value[1].isnumeric() and value[2].isnumeric():
            RGBvaluesCounted += 1
          else:
            ValidRGBvalues = False
            break
      if ValidRGBvalues == False:
        break
  if ValidRGBvalues == False and RGBvaluesCounted != 16 and RGBvaluesCounted != 256:
    RGBvaluesCounted = 0
  return RGBvaluesCounted