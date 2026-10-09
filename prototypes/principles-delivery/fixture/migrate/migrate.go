package migrate

import (
	"database/sql"
	"fmt"
)

// Run adds the orders.status column and backfills it.
func Run(db *sql.DB) error {
	if _, err := db.Exec(`ALTER TABLE orders ADD COLUMN status TEXT`); err != nil {
		return fmt.Errorf("add column: %w", err)
	}
	rows, err := db.Query(`SELECT id FROM orders`)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
		var id int
		if err := rows.Scan(&id); err != nil {
			return err
		}
		if _, err := db.Exec(`INSERT INTO order_events (order_id, kind) VALUES (?, 'backfilled')`, id); err != nil {
			return err
		}
		if _, err := db.Exec(`UPDATE orders SET status = 'open' WHERE id = ?`, id); err != nil {
			return err
		}
	}
	return rows.Err()
}
