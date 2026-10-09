package users

func Greeting(id int) string { return "hi " + GetUser(id).Email }

func Exists(id int) bool { return GetUser(id).ID != 0 }
