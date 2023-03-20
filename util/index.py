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
  while conf.lower().find("y") == -1 and conf.lower().find("n") == -1:
    print(sentence, end=" ")
    conf = input()
  if conf.lower().find("y") != -1:
    return True
  return False

def selectOptions(options, sentence) -> int:
  selected = -1
  while selected < 0 or selected >= len(options):
    for i in range(len(options)):
      print(f"{i}. {options[i]}")
    print(sentence, end="")
    selected = int(input())
  return selected
