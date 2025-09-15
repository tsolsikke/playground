CC      := gcc
CFLAGS  := -std=c17 -O2 -Wall -Wextra -Iinclude
LDFLAGS :=
BIN_DIR := bin
SRC     := $(wildcard src/*.c)
OBJ     := $(SRC:.c=.o)

# 推奨: サニタイザ（CI だけでも有効化すると最高）
SAN     ?= -fsanitize=address,undefined -fno-omit-frame-pointer

.PHONY: all clean run test
all: $(BIN_DIR)/play-cli

$(BIN_DIR)/play-cli: $(OBJ)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) $(SAN) -o $@ $^ $(LDFLAGS)

src/%.o: src/%.c include/p002_utils.h
	$(CC) $(CFLAGS) $(SAN) -c -o $@ $<

# ---- Tests ----
TEST_BIN := $(BIN_DIR)/test_all
TEST_SRC := $(wildcard tests/test_*.c)

test: $(TEST_BIN)
	./$(TEST_BIN)

$(TEST_BIN): $(TEST_SRC) $(OBJ)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) $(SAN) -o $@ $(TEST_SRC) $(OBJ) $(LDFLAGS)

clean:
	rm -rf $(BIN_DIR) src/*.o
