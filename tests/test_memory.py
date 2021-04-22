from wasmer import Instance, Module, Store, Memory, MemoryType, Buffer, Uint8Array, Int8Array, Uint16Array, Int16Array, Uint32Array, Int32Array
import ctypes
import gc
import inspect
import os
import pytest

here = os.path.dirname(os.path.realpath(__file__))
TEST_BYTES = open(here + '/tests.wasm', 'rb').read()

def instance():
    return Instance(Module(Store(), TEST_BYTES))

def test_constructor():
    store = Store()
    memory_type = MemoryType(3, shared=False)
    memory = Memory(store, memory_type)

    assert memory.size == 3

def test_export():
    assert isinstance(instance().exports.memory, Memory)

def test_type():
    type = instance().exports.memory.type

    assert isinstance(type, MemoryType)
    assert type.minimum == 17
    assert type.maximum == None
    assert type.shared == False
    assert str(type) == 'MemoryType(minimum: 17, maximum: None, shared: false)'

def test_size():
    assert instance().exports.memory.size == 17

def test_data_size():
    assert instance().exports.memory.data_size == 1114112

def test_memory_buffer():
    memory = instance().exports.memory.buffer
    assert isinstance(memory, Buffer)

def test_is_a_class():
    assert inspect.isclass(Memory)
    assert inspect.isclass(Uint8Array)
    assert inspect.isclass(Int8Array)
    assert inspect.isclass(Uint16Array)
    assert inspect.isclass(Int16Array)
    assert inspect.isclass(Uint32Array)
    assert inspect.isclass(Int32Array)
    assert inspect.isclass(Buffer)

def test_bytes_per_element():
    memory = instance().exports.memory

    assert memory.uint8_view().bytes_per_element ==  1
    assert memory.int8_view().bytes_per_element ==  1
    assert memory.uint16_view().bytes_per_element ==  2
    assert memory.int16_view().bytes_per_element ==  2
    assert memory.uint32_view().bytes_per_element ==  4
    assert memory.int32_view().bytes_per_element ==  4

@pytest.mark.xfail()
def test_cannot_construct():
    assert isinstance(Uint8Array(0), Uint8Array)

def test_length():
    assert len(instance().exports.memory.uint8_view()) == (
        1114112
    )

def test_get_index():
    memory = instance().exports.memory.uint8_view()
    index = 7
    value = 42
    memory[index] = value

    assert memory[index] == value

def test_get_integer_out_of_range_too_large():
    with pytest.raises(IndexError) as context_manager:
        memory = instance().exports.memory.uint8_view()
        memory[len(memory) + 1]

    exception = context_manager.value
    assert str(exception) == (
        'Out of bound: Maximum index 1114113 is larger than the memory size 1114112'
    )

def test_get_integer_out_of_range_negative():
    with pytest.raises(IndexError) as context_manager:
        memory = instance().exports.memory.uint8_view()
        memory[-1]

    exception = context_manager.value
    assert str(exception) == (
        'Out of bound: Index cannot be negative'
    )

def test_get_slice():
    memory = instance().exports.memory.uint8_view()
    index = 7
    memory[index    ] = 1
    memory[index + 1] = 2
    memory[index + 2] = 3

    assert memory[index:index + 3] == [1, 2, 3]

def test_get_slice_out_of_range_empty():
    with pytest.raises(IndexError) as context_manager:
        memory = instance().exports.memory.uint8_view()
        memory[2:1]

    exception = context_manager.value
    assert str(exception) == (
        'Slice `2:1` cannot be empty'
    )

def test_get_slice_out_of_range_invalid_step():
    with pytest.raises(IndexError) as context_manager:
        memory = instance().exports.memory.uint8_view()
        memory[1:7:2]

    exception = context_manager.value
    assert str(exception) == (
        'Slice must have a step of 1 for now; given 2'
    )

def test_get_invalid_index():
    with pytest.raises(ValueError) as context_manager:
        memory = instance().exports.memory.uint8_view()
        memory['a']

    exception = context_manager.value
    assert str(exception) == (
        'Only integers and slices are valid to represent an index'
    )

def test_set_single_value():
    memory = instance().exports.memory.uint8_view()

    assert memory[7] == 0
    memory[7] = 42
    assert memory[7] == 42

def test_set_list():
    memory = instance().exports.memory.uint8_view()

    memory[7:12] = [1, 2, 3, 4, 5]
    assert memory[7:12] == [1, 2, 3, 4, 5]

def test_set_bytes():
    memory = instance().exports.memory.uint8_view()

    memory[7:12] = bytes(b'abcde')
    assert memory[7:12] == [97, 98, 99, 100, 101]

def test_set_bytearray():
    memory = instance().exports.memory.uint8_view()

    memory[7:12] = bytearray(b'abcde')
    assert memory[7:12] == [97, 98, 99, 100, 101]

def test_set_values_with_slice_and_step():
    memory = instance().exports.memory.uint8_view()

    memory[7:12:2] = [1, 2, 3, 4, 5]
    assert memory[7:12] == [1, 0, 2, 0, 3]

def test_set_out_of_range():
    with pytest.raises(IndexError) as context_manager:
        memory = instance().exports.memory.uint8_view()
        memory[len(memory) + 1] = 42

    exception = context_manager.value
    assert str(exception) == (
        'Out of bound: Absolute index 1114113 is larger than the memory size 1114112'
    )

def test_hello_world():
    exports = instance().exports
    pointer = exports.string()
    memory = exports.memory.uint8_view(pointer)
    nth = 0
    string = ''

    while (0 != memory[nth]):
        string += chr(memory[nth])
        nth += 1

    assert string == 'Hello, World!'

def test_memory_views_share_the_same_buffer():
    memory = instance().exports.memory
    int8 = memory.int8_view()
    int16 = memory.int16_view()
    int32 = memory.int32_view()

    int8[0] = 0b00000001
    int8[1] = 0b00000100
    int8[2] = 0b00010000
    int8[3] = 0b01000000

    byte_array = bytearray(memory.buffer)

    assert int8[0] == 0b00000001
    assert int8[1] == 0b00000100
    assert int8[2] == 0b00010000
    assert int8[3] == 0b01000000
    assert int16[0] == 0b0000010000000001
    assert int16[1] == 0b0100000000010000
    assert int32[0] == 0b01000000000100000000010000000001
    assert byte_array[0] == 0b00000001
    assert byte_array[1] == 0b00000100
    assert byte_array[2] == 0b00010000
    assert byte_array[3] == 0b01000000

def test_memory_grow():
    memory = instance().exports.memory
    int8 = memory.int8_view()

    old_memory_length = len(int8)

    assert old_memory_length == 1114112

    memory.grow(1)

    memory_length = len(int8)

    assert memory_length == 1179648
    assert memory_length - old_memory_length == 65536

def test_memory_grow_too_much():
    with pytest.raises(RuntimeError) as context_manager:
        instance().exports.memory.grow(100000)

    exception = context_manager.value
    assert str(exception) == (
        'The memory could not grow: current size 17 pages, requested increase: 100000 pages'
    )

def test_memory_buffer_memoryview():
    memory = instance().exports.memory

    int8 = memory.int8_view()
    int8[0] = 1
    int8[1] = 2
    int8[2] = 3

    memory_view = memoryview(memory.buffer)

    assert memory_view.nbytes == 1114112
    assert memory_view.readonly == False
    assert memory_view.format == 'B'
    assert memory_view.itemsize == 1
    assert memory_view.ndim == 1
    assert memory_view.shape == (1114112,)
    assert memory_view.strides == (1,)
    assert memory_view.suboffsets == ()
    assert memory_view.c_contiguous == True
    assert memory_view.f_contiguous == True
    assert memory_view.contiguous == True
    assert memory_view[0:3].tolist() == [1, 2, 3]

def test_memory_buffer_bytearray():
    memory = instance().exports.memory

    int8 = memory.int8_view()
    int8[0] = 1
    int8[1] = 2
    int8[2] = 3
    int8[3] = 0x57
    int8[4] = 0x61
    int8[5] = 0x73
    int8[6] = 0x6d
    int8[7] = 0x65
    int8[8] = 0x72

    byte_array = bytearray(memory.buffer)

    assert len(byte_array) == 1114112
    assert byte_array[0:3] == b'\x01\x02\x03'
    assert byte_array[3:9].decode() == 'Wasmer'

def test_memory_buffer_supports_ctypes():
    c_uint8_4 = ctypes.c_uint8 * 4

    memory = instance().exports.memory

    arr = c_uint8_4.from_buffer(memory.buffer)
    arr[0] = 0b00000001
    arr[1] = 0b00000100
    arr[2] = 0b00010000
    arr[3] = 0b01000000

    byte_array = bytearray(memory.buffer)
    assert byte_array[0] == 0b00000001
    assert byte_array[1] == 0b00000100
    assert byte_array[2] == 0b00010000
    assert byte_array[3] == 0b01000000

def test_memory_buffer_supports_keeps_object_alive():
    """Overwrites a buffer's memory to segfault for incorrect ownership.

    The buffer protocol requires the buffer view to keep the owner of the
    memory ("buffer" in the example below) alive while the buffer is accessed.
    The memoryview object only stores the buffer view and does not keep an
    extra reference to the owner (in contrast to numpy arrays). Hence it relies
    on correct use of the buffer protocol.

    In case of incorrect ownership semantics, the write operation below would
    write into free'd memory. Depending on architecture, this operation will
    lead to a segfault.
    """
    buffer = instance().exports.memory.buffer
    view = memoryview(buffer)

    # delete the buffer and call the GC to force the buffer view held inside
    # the view object to be the only reference to the buffer object
    del buffer
    gc.collect()

    val = bytes([42] * 1024)
    for i in range(len(view) // 1024):
        view[i * 1024:(i + 1) * 1024] = val
