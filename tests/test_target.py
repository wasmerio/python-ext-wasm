from wasmer import engine, target, Store, Module
from wasmer_compiler_cranelift import Compiler
import itertools
import os
import platform
import pytest

def test_triple():
    triple = target.Triple('x86_64-apple-darwin')

    assert str(triple) == 'x86_64-apple-darwin'
    assert triple.architecture == 'x86_64'
    assert triple.vendor == 'apple'
    assert triple.operating_system == 'darwin'
    assert triple.binary_format == 'macho'
    assert triple.environment == 'unknown'
    assert triple.endianness == 'little'
    assert triple.pointer_width == 8
    assert triple.default_calling_convention == 'system_v'

def test_cpu_features():
    cpu_features = target.CpuFeatures()
    cpu_features.add('sse2')
    cpu_features.add('sse3')
    cpu_features.add('ssse3')
    cpu_features.add('sse4.1')
    cpu_features.add('sse4.2')
    cpu_features.add('popcnt')
    cpu_features.add('avx')
    cpu_features.add('bmi')
    cpu_features.add('bmi2')
    cpu_features.add('avx2')
    cpu_features.add('avx512dq')
    cpu_features.add('avx512vl')
    cpu_features.add('lzcnt')

def test_target():
    triple = target.Triple.host()
    cpu_features = target.CpuFeatures()
    target_ = target.Target(triple, cpu_features)

def test_target_with_default_cpu_features():
    triple = target.Triple.host()
    target_ = target.Target(triple)

@pytest.mark.skipif(platform.system() == 'Windows', reason = '`clang` is not found on the CI for the moment')
def test_cross_compilation_roundtrip():
    triple = target.Triple('x86_64-linux-musl')
    cpu_features = target.CpuFeatures()
    cpu_features.add('sse2')

    target_ = target.Target(triple, cpu_features)

    engine_ = engine.Native(Compiler, target_)
    store = Store(engine_)

    module = Module(
        store,
        """
        (module
          (type $sum_t (func (param i32 i32) (result i32)))
          (func $sum_f (type $sum_t) (param $x i32) (param $y i32) (result i32)
            local.get $x
            local.get $y
            i32.add)
          (export "sum" (func $sum_f)))
        """
    )

    assert isinstance(module, Module)
