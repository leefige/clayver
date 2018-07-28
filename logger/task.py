class Task:
    def __init__(self):
        self.__running = False
        self.__paused = False

    def isRunning(self):
        return self.__running

    def isPaused(self):
        return self.__paused

    def terminate(self):
        self.__running = False
    
    # blocked
    def pause(self):
        self.__paused = True

    def resume(self):
        self.__paused = False

    def run(self):
        if self.__running:
            return
        self.__running = True
        self._enter()

        # spin
        while self.isRunning():
            # spin
            while self.isPaused():
                if not self.isRunning():
                    break
            self._func()

        self._exit()
        self.__running = False
    
    # Override this function as the main function of task
    def _func(self):
        pass

    # Override this function as enter
    def _enter(self):
        pass

    # Override this function as exit
    def _exit(self):
        pass