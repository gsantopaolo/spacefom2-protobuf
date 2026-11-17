#!/usr/bin/env sh
# Regenerate the bindings and data, then build and test every language.
# Run from the repository root: sh samples/test-all.sh
# Needs protoc 36.2, buf, protoc-gen-go v1.36.12, Python 3.11+, Go, Node 26,
# Java 17+ with Maven, .NET 10+ and CMake (see samples/README.md).
set -eu

buf generate --template samples/buf.gen.yaml
python samples/python/writer.py

echo "== python";     python samples/python/reader.py && python -m pytest -q samples/python
echo "== go";         (cd samples && go vet ./... && go run ./go && go test ./...)
echo "== typescript"; (cd samples && npm run -s typecheck && npm run -s reader && npm test)
echo "== java";       (cd samples/java && mvn -q -B test exec:java)
echo "== csharp";     (cd samples/csharp && dotnet run --project Reader && dotnet test --project Tests)
echo "== cpp";        (cd samples/cpp && cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
                        && cmake --build build -j && ctest --test-dir build --output-on-failure)

git status --porcelain -- samples/generated samples/data
