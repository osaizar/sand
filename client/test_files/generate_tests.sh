#!/bin/bash

dd if=/dev/random of=2 bs=1 count=2
dd if=/dev/random of=4 bs=1 count=4
dd if=/dev/random of=8 bs=1 count=8
dd if=/dev/random of=16 bs=1 count=16
dd if=/dev/random of=32 bs=1 count=32
dd if=/dev/random of=64 bs=1 count=64
dd if=/dev/random of=128 bs=1 count=128
dd if=/dev/random of=256 bs=1 count=256
dd if=/dev/random of=16K bs=1024 count=16

