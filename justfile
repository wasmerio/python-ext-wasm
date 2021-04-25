# Install the environment to develop the extension.
prelude:
	#!/usr/bin/env bash
	set -x

	pip3 install virtualenv
	virtualenv .env
	if test -d .env/bin/; then source .env/bin/activate; else source .env/Scripts/activate; fi
	pip3 install maturin pytest pytest-benchmark twine git+https://github.com/Hywan/pdoc@submodule-for-extension

	which maturin
	maturin --version
	which python
	python --version
	which python-config
	python-config --abiflags || true
	uname -a
	pwd
	ls -l .env

build_features := ""

# Compile and install all the Python packages.
build-all rust_target='':
	just build api {{rust_target}}
	just build compiler-cranelift {{rust_target}}
	just build compiler-llvm {{rust_target}}
	just build compiler-singlepass {{rust_target}}

# Compile and install the Python package. Run with `--set build_features` to compile with specific Cargo features.
build package='api' rust_target='':
        #!/usr/bin/env bash
        export PYTHON_SYS_EXECUTABLE=$(which python)

        # The `compiler-singlepass` package has specific rules.
        if test "{{ package }}" = "compiler-singlepass"; then
                # `compiler-singlepass` only works on x86_64 for the moment.
                if [[ "{{ rust_target }}" != x86_64* ]]; then
                        echo "Skip, target '{{ rust_target }}' not supported for package '{{ package }}'"
                        exit 0
                fi
        fi

        # The `compiler-llvm` package has specific rules.
        if test "{{ package }}" = "compiler-llvm"; then
                # `compiler-llvm` does not work on Windows for the moment.
                if [[ "{{ rust_target }}" == *windows* ]]; then
                        echo "Skip, target '{{ rust_target }}' not supported for package '{{ package }}'"
                        exit 0
                fi
        fi

        build_features="{{build_features}}"
        build_args=""

        if test ! -z "${build_features}"; then
                build_args="--no-default-features --features ${build_features}"
        fi

        if test ! -z "{{ rust_target }}"; then
                build_args="${build_args} --target {{ rust_target }}"
        fi

        echo "Build arguments: ${build_args}"

        cd packages/{{package}}/

        maturin develop --binding-crate pyo3 --release --strip --cargo-extra-args="${build_args}"

# Build all the wheels.
build-all-wheels python_version rust_target:
	just build-wheel api {{python_version}} {{rust_target}}
	just build-wheel compiler-cranelift {{python_version}} {{rust_target}}
	just build-wheel compiler-llvm {{python_version}} {{rust_target}}
	just build-wheel compiler-singlepass {{python_version}} {{rust_target}}

# Build the wheel of a specific package.
build-wheel package python_version rust_target:
        #!/usr/bin/env bash
        export PYTHON_SYS_EXECUTABLE=$(which python)

        # The `compiler-singlepass` package has specific rules.
        if test "{{ package }}" = "compiler-singlepass"; then
                # `compiler-singlepass` only works on x86_64 for the moment.
                if [[ "{{ rust_target }}" != x86_64* ]]; then
                        echo "Skip, target '{{ rust_target }}' not supported for package '{{ package }}'"
                        exit 0
                fi
        fi

        # The `compiler-llvm` package has specific rules.
        if test "{{ package }}" = "compiler-llvm"; then
                # `compiler-llvm` does not work on Windows for the moment.
                if [[ "{{ rust_target }}" == *windows* ]]; then
                        echo "Skip, target '{{ rust_target }}' not supported for package '{{ package }}'"
                        exit 0
                fi
        fi

        build_features="{{build_features}}"
        build_args=""

        if test ! -z "${build_features}"; then
                build_args="--no-default-features --features ${build_features}"
        fi

        echo "Build arguments: ${build_args}"

        cd packages/{{package}}

        maturin build --bindings pyo3 --release --target "{{ rust_target }}" --strip --cargo-extra-args="${build_args}" --interpreter "{{python_version}}"

# Create a distribution of wasmer that can be installed anywhere (it will fail on import)
build-any-wheel:
	mkdir -p ./target/wheels/
	cp packages/api/README.md packages/any/api_README.md
	cd packages/any/ && pip3 wheel . --wheel-dir ../../target/wheels/

# Run the tests.
test files='tests':
	@py.test -v -s {{files}}

# Run the benchmarks.
benchmark files='benchmarks':
	@for BENCH in {{files}}/*.py; do py.test -v -s $BENCH; done

# Generate the documentation.
doc:
	@pdoc --html --output-dir docs/api --force \
		wasmer \
		wasmer_compiler_cranelift \
		wasmer_compiler_llvm \
		wasmer_compiler_singlepass

publish repository +WHEELS:
	twine upload --username wasmer --repository {{repository}} --skip-existing {{WHEELS}}

publish-any repository='testpypi':
	twine upload --username wasmer --repository {{repository}} target/wheels/wasmer-*-py3-none-any.whl

# Compile a Rust program to Wasm.
compile-wasm FILE='examples/simple':
	#!/usr/bin/env bash
	set -euo pipefail
	rustc --target wasm32-unknown-unknown -O --crate-type=cdylib {{FILE}}.rs -o {{FILE}}.raw.wasm
	wasm-gc {{FILE}}.raw.wasm {{FILE}}.wasm
	wasm-opt -Os --strip-producers {{FILE}}.wasm -o {{FILE}}.opt.wasm
	mv {{FILE}}.opt.wasm {{FILE}}.wasm
	rm {{FILE}}.raw.wasm

# Local Variables:
# mode: makefile
# End:
# vim: set ft=make :
