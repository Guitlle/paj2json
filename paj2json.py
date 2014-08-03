import re

def parsePaj(inputLines):
  # states for loop
  VERT_COUNT = 1
  VERT_DESC = 2
  LINK_DEF = 4

  # variables
  expecting = None
  prop_name = ""
  skip_index = False
  prop_type = None
  counter = 0
  vertices = []
  links = []
  link_dir = None
  vert_props_lookup = []

  for index, line in enumerate(inputLines):
    line = line.strip()
    if line.startswith("%"):
      continue

    if expecting == VERT_COUNT:
      if line.startswith("*vertices"):
        nvertices = int(line.rsplit(" ").pop())
        counter = 0
        expecting = VERT_DESC
      else:
        raise Exception("expecting vertices count at line %d" % (index) )
      continue

    elif expecting == VERT_DESC:
      # if vertex object has not been set, append it
      try:
        vertices[counter]
      except:
        vertices.append({})

      # skip the indexes
      if skip_index:
        splitted = re.split("^\s*\d+ ", line)
        content = splitted[1]
      else:
        content = line

      # remove trailing double quotes from strings definitions
      if prop_type == str or line[0] == "\"":
        content = content.strip()[1:-1]
        
      if prop_type == None:
        try:
          # maybe it is a float ? ? ?
          content = float(content)
        except:
          pass
        vertices[counter][prop_name] = content
      else:
        vertices[counter][prop_name] = prop_type(content)
        
      # increase counter
      counter += 1
      if counter >= nvertices:
        counter = 0
        expecting = None
      
      continue

    elif expecting == LINK_DEF:
      if not line:
        expecting = None
        continue
      data = re.split("\s+",line.strip())
      newlink = { "source": int(data[0]) - 1, "target": int(data[1]) - 1 }
      newlink["dir"] = link_dir
      datalen = len(data)
      if datalen > 2:
        newlink["weight"] = float(data[2])
      if datalen > 3:
        newlink["color"] = data[3]
      if datalen > 4:
        newlink["ltype"] = data[3]
      if datalen > 5:
        newlink["time"] = data[3]

      links.append(newlink)
      continue

    if line.startswith("*"):
      # this is a descriptor
      if line.startswith("*partition"):
        matches = re.match('\*partition (\w+)', line);
        matched_groups = matches.groups()
        expecting = VERT_COUNT
        prop_name = "part_" + matched_groups[0]
        prop_type = int
        skip_index = False
        continue

      elif line.startswith("*vector"):
        matches = re.match('\*vector (\w+)', line);
        matched_groups = matches.groups()
        expecting = VERT_COUNT
        prop_name = "v_" + matched_groups[0]
        prop_type = None
        skip_index = False
        continue

      elif line.startswith("*vertices"):
        nvertices = int(line.rsplit(" ").pop())
        counter = 0
        expecting = VERT_DESC
        prop_name = "name"
        prop_type = str
        skip_index = True
        continue

      elif line.startswith("*edges"):
        link_dir = False
        expecting = LINK_DEF
        continue
      elif line.startswith("*arcs"):
        link_dir = True
        expecting = LINK_DEF
        continue
    # ignore everything else
    continue
  return { "links": links, "vertices": vertices }
  
if __name__ == "__main__":
  import argparse
  import json
  parser = argparse.ArgumentParser()
  parser.add_argument("input", help="input pajek file", type=str)
  args = parser.parse_args()
  inputLines = open(args.input, 'r')
  
  print json.dumps(parsePaj(inputLines));
  