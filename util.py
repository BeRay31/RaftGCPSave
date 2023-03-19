def openAndReadFile(file):
  file1 = open(file, 'r')
  Lines = file1.readlines()
  toPrint = []
  for line in Lines:
    toPrint.append(line.strip())
  file1.close()
  return toPrint

def confirmationInput(sentence) -> bool:
  print(sentence, end=" ")
  conf = input()
  if conf.lower().find("y") != -1:
    return True
  return False
