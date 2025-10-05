package playground

import (
	"encoding/json"
	"errors"
	"fmt"
)

// Person: 素の構造体（比較可能なフィールドのみなので == 比較OK）
type Person struct {
	First string `json:"first"`
	Last  string `json:"last"`
	Age   int    `json:"age"`
}

// NewPerson: いわゆるコンストラクタ的関数（バリデーション付き）
func NewPerson(first, last string, age int) (Person, error) {
	if age < 0 {
		return Person{}, errors.New("age must be >= 0")
	}
	return Person{First: first, Last: last, Age: age}, nil
}

// FullName: 値レシーバ（読み取り専用な計算系は値レシーバが自然）
func (p Person) FullName() string {
	switch {
	case p.First == "" && p.Last == "":
		return ""
	case p.First == "":
		return p.Last
	case p.Last == "":
		return p.First
	default:
		return p.First + " " + p.Last
	}
}

// HaveBirthday: ポインタレシーバ（受け手を更新）
func (p *Person) HaveBirthday() {
	if p == nil {
		return
	}
	p.Age++
}

// ClonePerson: 値コピーを返す（shallow copyだが、ここでは十分）
func ClonePerson(p Person) Person {
	return p
}

// EqualPerson: フィールドが比較可能なので == で良い
func EqualPerson(a, b Person) bool {
	return a == b
}

// Address: 埋め込む用の別構造体
type Address struct {
	City string `json:"city"`
	Zip  string `json:"zip"`
}

// Employee: 構造体の埋め込み（匿名フィールド）＋追加フィールド
type Employee struct {
	Person          // 埋め込み：p.FullName() などを e.FullName() で呼べる
	ID     string   `json:"id"`
	Dept   string   `json:"dept"`
	Addr   *Address `json:"addr,omitempty"` // 省略可能
}

// Label: 埋め込みを利用したメソッド
func (e Employee) Label() string {
	name := e.FullName() // Personのメソッドが昇格して呼べる
	if name == "" {
		name = "(no name)"
	}
	return fmt.Sprintf("%s[%s/%s]", name, e.ID, e.Dept)
}

// MoveTo: 住所を安全に更新（nilなら作ってから代入）
func MoveTo(e *Employee, city, zip string) {
	if e == nil {
		return
	}
	if e.Addr == nil {
		e.Addr = &Address{}
	}
	e.Addr.City = city
	e.Addr.Zip = zip
}

// Rename: 氏名変更
func Rename(e *Employee, first, last string) {
	if e == nil {
		return
	}
	e.Person.First = first
	e.Person.Last = last
}

// MarshalEmployee / UnmarshalEmployee: JSON入出力（タグ確認用）
func MarshalEmployee(e Employee) ([]byte, error) {
	return json.Marshal(e)
}

func UnmarshalEmployee(data []byte) (Employee, error) {
	var e Employee
	err := json.Unmarshal(data, &e)
	return e, err
}

// UniqueByID: ID重複を除去（先勝ち）。空IDもキーとして扱う。
func UniqueByID(in []Employee) []Employee {
	seen := make(map[string]struct{}, len(in))
	out := make([]Employee, 0, len(in))
	for _, e := range in {
		if _, ok := seen[e.ID]; ok {
			continue
		}
		seen[e.ID] = struct{}{}
		out = append(out, e)
	}
	return out
}
