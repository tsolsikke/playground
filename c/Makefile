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

# ---- Tests (split per file) ----
# tests/test_*.c → bin/tests/test_* という “個別実行ファイル” にする
TEST_SRC  := $(wildcard tests/test_*.c)
TEST_BINS := $(patsubst tests/%.c,$(BIN_DIR)/tests/%,$(TEST_SRC))

test: $(TEST_BINS)
	@rc=0; \
	for t in $(TEST_BINS); do \
	  echo "== RUN $$t =="; \
	  "$$t" || rc=$$?; \
	done; \
	exit $$rc

# 個別ビルドルール：各テストは OBJ（= ライブラリ群、main.oは除外済み）とリンク
$(BIN_DIR)/tests/%: tests/%.c $(OBJ)
	@mkdir -p $(BIN_DIR)/tests
	$(CC) $(CFLAGS) $(SAN) -o $@ $^ $(LDFLAGS)

clean:
	rm -rf $(BIN_DIR) src/*.o
