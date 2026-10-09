package pricing

type Item struct {
	Name  string
	Cents int
	Qty   int
}

type Cart struct {
	Items    []*Item
	Discount *Discount
}

type Discount struct {
	Percent int
}

// Total returns the cart total in cents after discount.
func (c *Cart) Total() int {
	sum := 0
	for _, it := range c.Items {
		sum += it.Cents * it.Qty
	}
	return sum - sum*c.Discount.Percent/100
}

// ApplyDiscount returns cents reduced by percent, never below zero.
func ApplyDiscount(cents, percent int) int {
	if percent > 100 {
		percent = 100
	}
	return cents - cents*percent/100
}
