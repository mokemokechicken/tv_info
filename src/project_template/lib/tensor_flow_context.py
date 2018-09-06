class TensorflowContext:
    graph = None
    session = None

    def __init__(self, enable=True):
        self.enable = enable
        if not self.enable:
            return

        import tensorflow as tf

        self.graph = tf.Graph()
        self.session = tf.Session(graph=self.graph)

    def __call__(self):
        return TensorFlowContextClosure(self)

    def wrap(self, func, *args, **kwargs):
        with self():
            return func(*args, **kwargs)


class TensorFlowContextClosure:
    _graph_cm = None
    _session_cm = None

    def __init__(self, context: TensorflowContext):
        self.context = context

    def __enter__(self):
        if not self.context.enable:
            return
        self._graph_cm = self.context.graph.as_default()
        self._graph_cm.__enter__()
        self._session_cm = self.context.session.as_default()
        self._session_cm.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.context.enable:
            return False

        ret1 = self._session_cm.__exit__(exc_type, exc_val, exc_tb)
        ret2 = self._graph_cm.__exit__(exc_type, exc_val, exc_tb)

        self._session_cm = None
        self._graph_cm = None
        return ret1 and ret2
