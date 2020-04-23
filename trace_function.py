import gdb

tracepoint_function   = {}
function_callnum      = {}
tpfc = {}

class TracepointFunction(gdb.Breakpoint):
  def __init__(self, tty, *args):
    super().__init__(*args, type=gdb.BP_BREAKPOINT)
    self.silent = True
    self.function_name = args
    self.tty = tty
    tracepoint_function[self.function_name] = {}
    function_callnum[self.function_name] = 0

  def stop(self):
    cmd_arg   = "info args"
    cmd_stack = "info stack" 
    raw_args = gdb.execute(cmd_arg, self.tty, True)
    fc_stack = gdb.execute(cmd_stack, self.tty, True)

    fc_args = {}
    for l in raw_args.split("\n"):
      a = l.split(" = ")
      if len(a) == 2:
        fc_args[a[0]] = a[1]
    
    
    call_num = function_callnum[self.function_name]

    if not call_num in tracepoint_function[self.function_name]:
        tracepoint_function[self.function_name][call_num] = '0'
    
    tracepoint_function[self.function_name][call_num] = str(fc_args) + '\n' + 'stack:' + str(fc_stack) + '\n'
    function_callnum[self.function_name] = call_num + 1

    # do not stop
    return False

class TraceFunction(gdb.Command):
  """
  Trace a function arg and stack
  """

  def __init__(self):
    super().__init__("trace_function", gdb.COMMAND_USER)

  def invoke(self, args, tty):
    try:
      # global tracepoint_function
      # global tpfc
      tpfc[args] = TracepointFunction(tty, args)
    except Exception as e:
      print(e)
      print("Usage: trace_function [function_name]")


def finish(event):
  with open("trace_funtion.txt", "w") as file:
    for t in tracepoint_function.keys():
        file.write(f'function name {t} \n')
        for call_time, stack in tracepoint_function[t].items():
            file.write(f"Call_time : {call_time} \nArgs_Stack: {stack}")
            file.write('\n\n')

  for t in tracepoint_function.keys():
    print(f"Tracepoint {t}:")
    for call_time, stack in tracepoint_function[t].items():
      print(f"\tCall_time: '{call_time}' \n  Args_Stack: {stack}")


gdb.events.exited.connect(finish)
TraceFunction()
