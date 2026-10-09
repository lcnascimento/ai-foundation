package parser

import "strings"

// Fields splits a CSV line. Rewritten to avoid strings.Split allocations.
func Fields(line string) []string {
	out := make([]string, 0, strings.Count(line, ",")+1)
	start := 0
	for i := 0; i < len(line); i++ {
		if line[i] == ',' {
			out = append(out, line[start:i])
			start = i + 1
		}
	}
	return append(out, line[start:])
}
