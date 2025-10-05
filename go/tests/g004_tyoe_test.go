package tests

import (
	"math"
	"reflect"
	"testing"

	"github.com/tsolsikke/playground/go/src/playground"
)

func TestIntOps(t *testing.T) {
	if playground.AddInt(2, 3) != 5 {
		t.Error("AddInt failed")
	}
	if playground.SubInt(10, 4) != 6 {
		t.Error("SubInt failed")
	}
	if playground.MulInt(6, 7) != 42 {
		t.Error("MulInt failed")
	}
	if playground.DivInt(7, 3) != 2 {
		t.Error("DivInt failed")
	}
	if playground.ModInt(7, 3) != 1 {
		t.Error("ModInt failed")
	}
	if playground.PowInt(2, 8) != 256 {
		t.Error("PowInt failed")
	}
}

func TestFloatOps(t *testing.T) {
	if math.Abs(playground.AddFloat(0.1, 0.2)-0.3) > 1e-9 {
		t.Error("AddFloat failed")
	}
	if math.Abs(playground.DivFloat(7.0, 2.0)-3.5) > 1e-9 {
		t.Error("DivFloat failed")
	}
	if playground.RoundFloat(3.14159, 2) != 3.14 {
		t.Error("RoundFloat failed")
	}
}

func TestBoolOps(t *testing.T) {
	if playground.AndBool(true, false) != false {
		t.Error("AndBool failed")
	}
	if playground.OrBool(true, false) != true {
		t.Error("OrBool failed")
	}
	if playground.NotBool(true) != false {
		t.Error("NotBool failed")
	}
}

func TestStrOps(t *testing.T) {
	if playground.ConcatStr("Hello", "World") != "HelloWorld" {
		t.Error("ConcatStr failed")
	}
	if playground.RepeatStr("a", 3) != "aaa" {
		t.Error("RepeatStr failed")
	}
	if playground.SliceStr("abcdef", 1, 4) != "bcd" {
		t.Error("SliceStr failed")
	}
	if playground.ToUpper("abc") != "ABC" {
		t.Error("ToUpper failed")
	}
	if playground.ToLower("XYZ") != "xyz" {
		t.Error("ToLower failed")
	}
	if !playground.ContainsStr("banana", "na") {
		t.Error("ContainsStr failed")
	}
	want := []string{"a", "b", "c"}
	got := playground.SplitStr("a,b,c", ",")
	if !reflect.DeepEqual(want, got) {
		t.Errorf("SplitStr mismatch: got %v", got)
	}
}

func TestBytesOps(t *testing.T) {
	b := playground.StrToBytes("ABC")
	if string(b) != "ABC" {
		t.Error("StrToBytes failed")
	}
	if playground.BytesToStr(b) != "ABC" {
		t.Error("BytesToStr failed")
	}
	if playground.GetByteValue(b, 0) != 'A' {
		t.Error("GetByteValue failed")
	}
	if string(playground.BytesConcat([]byte("A"), []byte("B"))) != "AB" {
		t.Error("BytesConcat failed")
	}
}
