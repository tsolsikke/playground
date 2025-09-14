from playground.p002_utils import vectors_dir, results_dir


def test_vectors_dir_exists():
    path = vectors_dir()
    assert path.name == "vectors"


def test_results_dir_creates(monkeypatch, tmp_path):
    monkeypatch.setenv("PLAYGROUND_ROOT", str(tmp_path))
    path = results_dir()
    assert path.exists()
    assert path.name == "results"
