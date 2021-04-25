from wasmer import engine, Store, Module, Instance
from wasmer_compiler_cranelift import Compiler as Cranelift
from wasmer_compiler_llvm import Compiler as LLVM
from wasmer_compiler_singlepass import Compiler as Singlepass

TEST_BYTES = open('benchmarks/nbody.wasm', 'rb').read()

def test_benchmark_headless_time_nbody_cranelift_jit(benchmark):
    store = Store(engine.JIT(Cranelift))
    module = Module(store, TEST_BYTES)
    serialized = module.serialize()

    @benchmark
    def bench():
        deserialized = Module.deserialize(store, serialized)
        _ = Instance(deserialized)

def test_benchmark_headless_time_nbody_cranelift_native(benchmark):
    store = Store(engine.Native(Cranelift))
    module = Module(store, TEST_BYTES)
    serialized = module.serialize()

    @benchmark
    def bench():
        deserialized = Module.deserialize(store, serialized)
        _ = Instance(deserialized)

def test_benchmark_headless_time_nbody_llvm_jit(benchmark):
    store = Store(engine.JIT(LLVM))
    module = Module(store, TEST_BYTES)
    serialized = module.serialize()

    @benchmark
    def bench():
        deserialized = Module.deserialize(store, serialized)
        _ = Instance(deserialized)

def test_benchmark_headless_time_nbody_llvm_native(benchmark):
    store = Store(engine.Native(LLVM))
    module = Module(store, TEST_BYTES)
    serialized = module.serialize()

    @benchmark
    def bench():
        deserialized = Module.deserialize(store, serialized)
        _ = Instance(deserialized)

def test_benchmark_headless_time_nbody_singlepass_jit(benchmark):
    store = Store(engine.JIT(Singlepass))
    module = Module(store, TEST_BYTES)
    serialized = module.serialize()

    @benchmark
    def bench():
        deserialized = Module.deserialize(store, serialized)
        _ = Instance(deserialized)

def test_benchmark_headless_time_nbody_singlepass_native(benchmark):
    store = Store(engine.Native(Singlepass))
    module = Module(store, TEST_BYTES)
    serialized = module.serialize()

    @benchmark
    def bench():
        deserialized = Module.deserialize(store, serialized)
        _ = Instance(deserialized)
