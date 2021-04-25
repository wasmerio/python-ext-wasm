from wasmer import engine, Store, Module
from wasmer_compiler_cranelift import Compiler as Cranelift
from wasmer_compiler_llvm import Compiler as LLVM
from wasmer_compiler_singlepass import Compiler as Singlepass

TEST_BYTES = open('benchmarks/nbody.wasm', 'rb').read()

def test_benchmark_compilation_time_nbody_cranelift_jit(benchmark):
    store = Store(engine.JIT(Cranelift))

    @benchmark
    def bench():
        _ = Module(store, TEST_BYTES)

def test_benchmark_compilation_time_nbody_cranelift_native(benchmark):
    store = Store(engine.Native(Cranelift))

    @benchmark
    def bench():
        _ = Module(store, TEST_BYTES)

def test_benchmark_compilation_time_nbody_llvm_jit(benchmark):
    store = Store(engine.JIT(LLVM))

    @benchmark
    def bench():
        _ = Module(store, TEST_BYTES)

def test_benchmark_compilation_time_nbody_llvm_native(benchmark):
    store = Store(engine.Native(LLVM))

    @benchmark
    def bench():
        _ = Module(store, TEST_BYTES)

def test_benchmark_compilation_time_nbody_singlepass_jit(benchmark):
    store = Store(engine.JIT(Singlepass))

    @benchmark
    def bench():
        _ = Module(store, TEST_BYTES)

def test_benchmark_compilation_time_nbody_singlepass_native(benchmark):
    store = Store(engine.Native(Singlepass))

    @benchmark
    def bench():
        _ = Module(store, TEST_BYTES)
