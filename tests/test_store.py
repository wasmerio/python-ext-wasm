from wasmer import engine, target, Store, Module, Instance
import itertools
import os
import platform
import pytest

here = os.path.dirname(os.path.realpath(__file__))
TEST_BYTES = open(here + '/tests.wasm', 'rb').read()

def test_store_defaults():
    store = Store()

    assert store.engine_name == 'jit'
    assert store.compiler_name == 'cranelift'

@pytest.mark.skipif(platform.system() == 'Windows', reason = 'temp')
def test_store_with_various_engines_and_compilers():
    host_triple = target.Triple.host()
    is_aarch64 = host_triple.architecture == 'aarch64'
    exclude_native = is_aarch64
    
    compilers = [None]
    engines = [
        engine.JIT,
        engine.Native
    ]
    results = [
        (None, 'jit'),
        (None, 'native'),
    ]

    try:
        import wasmer_compiler_cranelift

        compilers.append(wasmer_compiler_cranelift.Compiler)
        results.append(('cranelift', 'jit'))
        results.append(('cranelift', 'native'))
    except ImportError:
        pass

    try:
        import wasmer_compiler_llvm

        compilers.append(wasmer_compiler_llvm.Compiler)
        results.append(('llvm', 'jit'))
        results.append(('llvm', 'native'))
    except ImportError:
        pass

    try:
        import wasmer_compiler_singlepass

        compilers.append(wasmer_compiler_singlepass.Compiler)
        results.append(('singlepass', 'jit'))
        results.append(('singlepass', 'native'))
    except ImportError:
        pass

    for ((compiler, engine_), expected) in itertools.zip_longest(itertools.product(compilers, engines), results):
        if exclude_native and engine_ == engine.Native:
            continue

        store = Store(engine_(compiler))

        assert store.compiler_name == expected[0]
        assert store.engine_name == expected[1]

        if compiler != None:
            module = Module(store, TEST_BYTES)
            instance = Instance(module)

            assert instance.exports.sum(1, 2)
