def tail(f_name, n_lines=10, break_key=''):
  # initialize output list
  tail_lines = []
  with open(f_name, 'rb') as f:
    # go to position EOF-2
    # os.SEEK_END is 2
    f.seek(-2, 2)
    # save current absolute position in the file
    last_position = f.tell()
    # read lines until requested number of lines is read
    while len(tail_lines) < n_lines:
      # read one char at a time until a newline char is found
      while f.read(1) != b'\n':
        # check if there is still space to go back 2 chars
        if f.tell() > 2:
          # os.SEEK_CUR is 1
          f.seek(-2, 1)
        # if cursor is in the first 2 chars, go to start of file, read first line, and return
        else:
          f.seek(0)
          tail_lines.append(f.readline().decode().strip('\n'))
          return tail_lines[::-1]
      # save current absolute position
      last_position = f.tell()
      # read one line and append its text representation to output list
      line = f.readline().decode().strip('\n')
      tail_lines.append(line)
      # if break_key in line, return
      if break_key and break_key in line:
        return tail_lines[::-1]
      # set cursor to one char ahead of previous saved position
      f.seek(last_position-2, 0)
  # return reversed list
  return tail_lines[::-1]

if __name__ == "__main__":
  t = tail('input_data.txt', 20)
  print('Read {} lines:\n{}'.format(len(t), '\n'.join(t)))

