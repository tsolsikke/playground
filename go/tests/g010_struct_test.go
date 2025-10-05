package tests

import (
	"reflect"
	"testing"

	"github.com/tsolsikke/playground/go/src/playground"
)

func TestPersonBasic(t *testing.T) {
	p, err := playground.NewPerson("Taro", "Yamada", 20)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if p.FullName() != "Taro Yamada" {
		t.Fatalf("fullname mismatch: %q", p.FullName())
	}
	if !playground.EqualPerson(p, playground.ClonePerson(p)) {
		t.Fatalf("clone should be equal")
	}

	// 誕生日
	p.HaveBirthday()
	if p.Age != 21 {
		t.Fatalf("age after birthday = %d", p.Age)
	}
}

func TestNewPersonValidation(t *testing.T) {
	if _, err := playground.NewPerson("A", "B", -1); err == nil {
		t.Fatalf("negative age must be error")
	}
}

func TestEmbeddingAndMethods(t *testing.T) {
	p, _ := playground.NewPerson("Hanako", "Suzuki", 30)
	e := playground.Employee{
		Person: p,
		ID:     "E100",
		Dept:   "R&D",
	}
	label := e.Label()
	if label == "" || label[0] == '[' {
		t.Fatalf("label looks wrong: %q", label)
	}
	// 埋め込みメソッドの昇格確認
	if e.FullName() != "Hanako Suzuki" {
		t.Fatalf("promoted method failed: %q", e.FullName())
	}
}

func TestMoveToAndRename(t *testing.T) {
	e := playground.Employee{ID: "E1", Dept: "Ops"}
	// Addr が nil でも安全に更新される
	playground.MoveTo(&e, "Tokyo", "100-0001")
	if e.Addr == nil || e.Addr.City != "Tokyo" || e.Addr.Zip != "100-0001" {
		t.Fatalf("move failed: %+v", e.Addr)
	}
	playground.Rename(&e, "Ken", "Sato")
	if e.FullName() != "Ken Sato" {
		t.Fatalf("rename failed: %q", e.FullName())
	}
}

func TestJSONRoundTrip(t *testing.T) {
	p, _ := playground.NewPerson("Aki", "Ito", 28)
	e := playground.Employee{
		Person: p,
		ID:     "E9",
		Dept:   "QA",
		Addr:   &playground.Address{City: "Osaka", Zip: "540-0000"},
	}
	b, err := playground.MarshalEmployee(e)
	if err != nil {
		t.Fatalf("marshal err: %v", err)
	}
	got, err := playground.UnmarshalEmployee(b)
	if err != nil {
		t.Fatalf("unmarshal err: %v", err)
	}
	if !reflect.DeepEqual(e, got) {
		t.Fatalf("roundtrip mismatch:\nwant=%+v\ngot =%+v", e, got)
	}
}

func TestUniqueByID(t *testing.T) {
	makeEmp := func(id, first string) playground.Employee {
		p, _ := playground.NewPerson(first, "", 0)
		return playground.Employee{Person: p, ID: id, Dept: "X"}
	}
	in := []playground.Employee{
		makeEmp("A", "a1"),
		makeEmp("B", "b1"),
		makeEmp("A", "a2"), // dup
		makeEmp("", "z1"),
		makeEmp("", "z2"), // dup of empty id
	}
	out := playground.UniqueByID(in)
	ids := make([]string, 0, len(out))
	for _, e := range out {
		ids = append(ids, e.ID)
	}
	// 先勝ちで A, B, "" の3つが残る
	if len(out) != 3 || ids[0] != "A" || ids[1] != "B" || ids[2] != "" {
		t.Fatalf("unexpected unique result: %+v", ids)
	}
}
