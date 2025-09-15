CC      := gcc
CFLAGS  := -std=c17 -O2 -Wall -Wextra -Iinclude
LDFLAGS :=
BIN_DIR := bin

# すべてのソースとオブジェクト
SRC_ALL := $(wildcard src/*.c)
OBJ_ALL := $(SRC_ALL:.c=.o)

# アプリ側の main.c を分離
APP_MAIN := $(wildcard src/main.c)
APP_OBJ  := $(APP_MAIN:.c=.o)

# テスト用には main.o を除外したオブジェクトを使う
OBJ      := $(filter-out $(APP_OBJ),$(OBJ_ALL))

# 推奨: サニタイザ
SAN     ?= -fsanitize=address,undefined -fno-omit-frame-pointer

.PHONY: all clean run test

# main.c があるときだけ実行バイナリを作る。無ければオブジェクトだけ作る
ifeq ($(APP_MAIN),)
all: $(OBJ)
else
all: $(BIN_DIR)/play-cli
endif

$(BIN_DIR)/play-cli: $(OBJ) $(APP_OBJ)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) $(SAN) -o $@ $^ $(LDFLAGS)

src/%.o: src/%.c include/p002_utils.h
	$(CC) $(CFLAGS) $(SAN) -c -o $@ $<

# ---- Tests ----
TEST_BIN := $(BIN_DIR)/test_all
TEST_SRC := $(wildcard tests/test_*.c)

test: $(TEST_BIN)
	./$(TEST_BIN)

# ★ テストは OBJ（= main.o 除外済み）＋ テストコード（= こちらに test の main がある）
$(TEST_BIN): $(TEST_SRC) $(OBJ)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) $(SAN) -o $@ $(TEST_SRC) $(OBJ) $(LDFLAGS)

clean:
	rm -rf $(BIN_DIR) src/*.o
