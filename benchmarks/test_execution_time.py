from wasmer import engine, Store, Module, Instance
from wasmer_compiler_cranelift import Compiler as Cranelift
from wasmer_compiler_llvm import Compiler as LLVM
from wasmer_compiler_singlepass import Compiler as Singlepass

TEST_BYTES = open('benchmarks/nbody.wasm', 'rb').read()

N = 100000

def test_benchmark_execution_time_nbody_cranelift_jit(benchmark):
    store = Store(engine.JIT(Cranelift))
    module = Module(store, TEST_BYTES)
    instance = Instance(module)
    main = instance.exports.main

    @benchmark
    def bench():
        _ = main(N)

def test_benchmark_execution_time_nbody_cranelift_native(benchmark):
    store = Store(engine.Native(Cranelift))
    module = Module(store, TEST_BYTES)
    instance = Instance(module)
    main = instance.exports.main

    @benchmark
    def bench():
        _ = main(N)

def test_benchmark_execution_time_nbody_llvm_jit(benchmark):
    store = Store(engine.JIT(LLVM))
    module = Module(store, TEST_BYTES)
    instance = Instance(module)
    main = instance.exports.main

    @benchmark
    def bench():
        _ = main(N)

def test_benchmark_execution_time_nbody_llvm_native(benchmark):
    store = Store(engine.Native(LLVM))
    module = Module(store, TEST_BYTES)
    instance = Instance(module)
    main = instance.exports.main

    @benchmark
    def bench():
        _ = main(N)

def test_benchmark_execution_time_nbody_singlepass_jit(benchmark):
    store = Store(engine.JIT(Singlepass))
    module = Module(store, TEST_BYTES)
    instance = Instance(module)
    main = instance.exports.main

    @benchmark
    def bench():
        _ = main(N)

def test_benchmark_execution_time_nbody_singlepass_native(benchmark):
    store = Store(engine.Native(Singlepass))
    module = Module(store, TEST_BYTES)
    instance = Instance(module)
    main = instance.exports.main

    @benchmark
    def bench():
        _ = main(N)
