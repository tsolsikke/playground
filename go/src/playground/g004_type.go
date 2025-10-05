package playground

import "strings"

// ===== int =====
func AddInt(a, b int) int { return a + b }
func SubInt(a, b int) int { return a - b }
func MulInt(a, b int) int { return a * b }
func DivInt(a, b int) int { return a / b }
func ModInt(a, b int) int { return a % b }
func PowInt(a, b int) int {
	res := 1
	for i := 0; i < b; i++ {
		res *= a
	}
	return res
}

// ===== float =====
func AddFloat(a, b float64) float64 { return a + b }
func DivFloat(a, b float64) float64 { return a / b }
func RoundFloat(x float64, n int) float64 {
	p := PowInt(10, n)
	scale := float64(p)
	return float64(int(x*scale+0.5)) / scale
}

// ===== bool =====
func AndBool(a, b bool) bool { return a && b }
func OrBool(a, b bool) bool  { return a || b }
func NotBool(a bool) bool    { return !a }

// ===== string =====
func ConcatStr(a, b string) string     { return a + b }
func RepeatStr(s string, n int) string { return strings.Repeat(s, n) }
func SliceStr(s string, start, end int) string {
	if start < 0 {
		start = 0
	}
	if end > len(s) {
		end = len(s)
	}
	return s[start:end]
}
func ToUpper(s string) string        { return strings.ToUpper(s) }
func ToLower(s string) string        { return strings.ToLower(s) }
func ContainsStr(s, sub string) bool { return strings.Contains(s, sub) }
func SplitStr(s, sep string) []string {
	return strings.Split(s, sep)
}

// ===== bytes（Goでは[]byte）=====
func StrToBytes(s string) []byte     { return []byte(s) }
func BytesToStr(b []byte) string     { return string(b) }
func BytesConcat(a, b []byte) []byte { return append(a, b...) }
func GetByteValue(b []byte, i int) byte {
	return b[i]
}
