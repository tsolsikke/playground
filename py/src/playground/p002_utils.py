from pathlib import Path
import os


def get_root() -> Path:
    # 環境変数があればそれを優先（CI で渡す）
    if "PLAYGROUND_ROOT" in os.environ:
        return Path(os.environ["PLAYGROUND_ROOT"]).resolve()
    # テスト/実行時もファイル位置から2つ上がルート（py/src → ルート）
    return Path(__file__).resolve().parents[2]


def vectors_dir() -> Path:
    return get_root() / "data" / "vectors"


def results_dir() -> Path:
    d = get_root() / "data" / "results"
    d.mkdir(parents=True, exist_ok=True)
    return d
