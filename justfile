# -*- mode: just -*-

# Define binary name using current directory name
output_dir := "bin"
bin_name := file_stem(justfile_dir())
target_bin := output_dir / bin_name

# Define Go flags
go := "go"
goos := env("GOOS", `go env GOARCH`)
goarch := env("GOARCH", `go env GOARCH`)
go_test := go + " test " + env("GO_FLAGS", "-race")
go_build := go + " build " + env("GO_FLAGS", "")

# Add GOPATH to PATH variable
go_path := env("GOPATH", `go env GOPATH`)
export PATH := go_path / "bin" + ":" + env("PATH")

run: build
    {{target_bin}}

# TODO: Generate data
# generate:
#     go generate

# Build the project and write the resulting binary to the "bin/" directory
build:
    mkdir -p {{output_dir}}
    {{go_build}} -o {{target_bin}} ./cmd/powdata

# Run `go fmt` and `go vet`
fmt: vet
    go fmt ./...

[private]
vet:
    go vet ./...

# Update project dependencies
up:
    go get -u ./...
    go mod tidy

# Run tests
test:
    {{go_test}} ./...

# TODO: Generate documentation
# doc: get-godoc
#     # go doc ./...
#     # TODO: open localhost until press ctrl + c
#     # TODO: document this project, including internal/
#     godoc -http=:6060
#     open http://localhost:6060
# 
# [private, unix]
# get-godoc:
#     command -v godoc || go install golang.org/x/tools/cmd/godoc@latest
