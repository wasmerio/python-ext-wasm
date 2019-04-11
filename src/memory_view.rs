//! The `Buffer` Python object to build WebAssembly values.

use crate::Shell;
use cpython::{PyObject, PyResult, Python};
use std::mem::size_of;
use wasmer_runtime::memory::Memory;

macro_rules! memory_view {
    ($class_name:ident over $wasm_type:ty, with $constructor_name:ident) => {
        /// A `MemoryView` Python object represents a view over the memory
        /// of a WebAssembly instance.
        py_class!(pub class $class_name |py| {
            data memory: Shell<Memory>;
            data offset: usize;

            def length(&self) -> PyResult<usize> {
                let offset = *self.offset(py);

                Ok(self.memory(py).view::<$wasm_type>()[offset..].len() / size_of::<$wasm_type>())
            }

            def get(&self, index: usize) -> PyResult<$wasm_type> {
                let offset = *self.offset(py);
                let index = index / size_of::<$wasm_type>();

                Ok(self.memory(py).view::<$wasm_type>()[offset + index].get() as $wasm_type)
            }

            def set(&self, index: usize, value: $wasm_type) -> PyResult<PyObject> {
                let offset = *self.offset(py);
                let index = index / size_of::<$wasm_type>();

                self.memory(py).view::<$wasm_type>()[offset + index].set(value);

                Ok(Python::None(py))
            }
        });

        /// Construct a `MemoryView` Python object.
        pub fn $constructor_name(py: Python, memory: Memory, offset: usize) -> $class_name {
            $class_name::create_instance(py, Shell::new(memory), offset).unwrap()
        }
    };
}

memory_view!(Uint8MemoryView over u8, with new_uint8_memory_view);
memory_view!(Int8MemoryView over i8, with new_int8_memory_view);
memory_view!(Uint16MemoryView over u16, with new_uint16_memory_view);
memory_view!(Int16MemoryView over i16, with new_int16_memory_view);
memory_view!(Uint32MemoryView over u32, with new_uint32_memory_view);
memory_view!(Int32MemoryView over i32, with new_int32_memory_view);