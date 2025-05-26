<h1 align="center">Places of Worship DB</h1>

![Project Status](https://img.shields.io/badge/status-in--development-yellow)

> **Note**: This project is under active development and should not be considered ready for use.

A collector of geographical and temporal data of religious places of worship from various sources, published to a database.  Based on [a similar project developed by University of Auckland's Centre for e-Research](https://github.com/UoA-eResearch/religion/tree/1a4c2495ae9e059a7e2e1f4fd34cccb7b3be8995).

---

## Quick Start

Compile:
```bash
$ just run    # All-in-one build and run script, including updating generated const file
$ just build  # Or build it into a binary
```

Run:
```bash
$ ./places-of-worship     # TODO: command-line interface yet to be determined
$ ./places-of-worship -h  # help command coming soon™!
```

## Project Structure

Internal library files are in the `internal/` directory.  Command-line tools are in the `cmd/` subdirectory.  The primary command line tool at time of writing simply persists the relevant data from various sources.<sup><a href="https://go.dev/doc/modules/layout">[1]</a>, <a href="https://reddit.com/r/golang/comments/17nx2cz">[2]</a></sup>
