package worker

import (
	"encoding/json"
	"os"
	"sync"
)

type Result struct {
	Job   string
	Value int
}

// RunAll processes jobs with two workers; each appends its results to out/results.json.
func RunAll(jobs []string) error {
	var wg sync.WaitGroup
	for w := 0; w < 2; w++ {
		wg.Add(1)
		go func(w int) {
			defer wg.Done()
			for i := w; i < len(jobs); i += 2 {
				appendResult(Result{Job: jobs[i], Value: len(jobs[i])})
			}
		}(w)
	}
	wg.Wait()
	return nil
}

func appendResult(r Result) {
	var all []Result
	if b, err := os.ReadFile("out/results.json"); err == nil {
		_ = json.Unmarshal(b, &all)
	}
	all = append(all, r)
	b, _ := json.Marshal(all)
	_ = os.WriteFile("out/results.json", b, 0o644)
}
