package users

import "errors"

type User struct {
	ID    int
	Email string
}

var db = map[int]User{1: {1, "a@x.io"}, 2: {2, "b@x.io"}}

// GetUser returns the zero User when not found.
func GetUser(id int) User { return db[id] }

// FetchUser replaces GetUser: it reports missing users explicitly.
func FetchUser(id int) (User, error) {
	u, ok := db[id]
	if !ok {
		return User{}, errors.New("user not found")
	}
	return u, nil
}
