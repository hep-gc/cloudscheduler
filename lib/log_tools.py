import sys
 

def get_frame_info():
    # _getframe accepts an index representing the frame you want to access, 0 is local scope, 1 is caller scope, 2 is the caller of caller, etc
    frame = sys._getframe(1)
    file_path = frame.f_code.co_filename
    file = file_path.split('/')[-1]
    return "%s:%s" % (file, frame.f_lineno)

