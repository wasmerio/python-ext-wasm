from wasmer import engine, wat2wasm, Store, Module, Instance
from wasmer_compiler_cranelift import Compiler

TEST_BYTES = wat2wasm(
    """
    (module
        (memory 16)
        (export "memory" (memory 0)))
    """
)

def test_benchmark_memory_view_int8_get(benchmark):
    store = Store(engine.JIT(Compiler))
    module = Module(store, TEST_BYTES)
    instance = Instance(module)
    memory = instance.exports.memory.uint8_view()

    def bench():
        _ = memory[0]

    benchmark(bench)

def test_benchmark_memory_view_memoryview_get(benchmark):
    store = Store(engine.JIT(Compiler))
    module = Module(store, TEST_BYTES)
    instance = Instance(module)
    memory = memoryview(instance.exports.memory.buffer)

    def bench():
        _ = memory[0]

    benchmark(bench)

def test_benchmark_memory_view_bytearray_get(benchmark):
    store = Store(engine.JIT(Compiler))
    module = Module(store, TEST_BYTES)
    instance = Instance(module)
    memory = bytearray(instance.exports.memory.buffer)

    def bench():
        _ = memory[0]

    benchmark(bench)
