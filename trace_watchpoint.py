import gdb

tracepoint_watchPoint = {}
watchPoint_callnum      = {}
tpwp = {}

class TracepointWatchPoint(gdb.Breakpoint):
  def __init__(self, tty, *args):
    super().__init__(*args, type=gdb.BP_WATCHPOINT)
    self.silent = True
    self.watch_point = args
    self.tty = tty
    tracepoint_watchPoint[self.watch_point] = {}
    watchPoint_callnum[self.watch_point] = 0

  def stop(self):
    cmd_bt = "bt full" 
    wp_bt = gdb.execute(cmd_bt, self.tty, True)
    call_num = watchPoint_callnum[self.watch_point]

    if not call_num in tracepoint_watchPoint[self.watch_point]:
        tracepoint_watchPoint[self.watch_point][call_num] = '0'

    var = gdb.parse_and_eval(self.expression)
    tracepoint_watchPoint[self.watch_point][call_num] = self.expression + '= ' + str(var) + '\n' + 'stack:' + str(wp_bt) + '\n'
    watchPoint_callnum[self.watch_point] = call_num + 1

    # do not stop
    return False

class TraceWatchPoint(gdb.Command):
  """
  Trace watch point
  """
  def __init__(self):
    super().__init__("trace_watchPoint", gdb.COMMAND_USER)

  def invoke(self, args, tty):
    try:
      # global tracepoint_function
      # global tpfc
      tpwp[args] = TracepointWatchPoint(tty, args)
    except Exception as e:
      print(e)
      print("Usage: trace_watchPoint [function_name]")

def finish(event):
  with open("trace_watchPoint.txt", "w") as file:
    for t in tracepoint_watchPoint.keys():
        file.write(f'watch_point {t} \n')
        for call_time, stack in tracepoint_watchPoint[t].items():
            file.write(f"Call_time : {call_time} \nVar_Bt: {stack}")
            file.write('\n\n')

  for t in tracepoint_watchPoint.keys():
    print(f"Tracepoint {t}:")
    for call_time, stack in tracepoint_watchPoint[t].items():
      print(f"\tCall_time: '{call_time}' \n  Args_Stack: {stack}")

gdb.events.exited.connect(finish)
TraceWatchPoint()
